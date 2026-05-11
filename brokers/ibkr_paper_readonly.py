# brokers/ibkr_paper_readonly.py
"""IBKR-001 / IBKR-002 — :class:`IBKRPaperReadOnlyAdapter`.

Skeleton + safe status fallback for the read-only IBKR Paper adapter
behind the :class:`brokers.protocol.BrokerAdapter` protocol.
Disconnected-safe by default; later IBKR tasks (IBKR-005 / IBKR-006)
will replace the safe zero-state outputs with mock-backed snapshots.

Design contract:

* Read-only. No execution / order / risk-mutation method names exist
  on this adapter. Specifically, no ``connect`` / ``disconnect`` /
  ``place_order`` / ``cancel_order`` / ``modify_order`` / ``execute`` /
  ``buy`` / ``sell`` / ``reqMktData`` / ``reqPositions`` method is
  added — the adapter only *reads* the state of an externally injected
  client.
* No broker SDK imports. Standard library only. The legacy
  :mod:`brokers.ibkr_paper` module (unrelated to this read-only
  adapter) still handles the pre-existing paper flow; this module
  intentionally does not touch it.
* No network calls. The constructor stores an
  :class:`brokers.ibkr_config.IBKRPaperConfig` and an optional opaque
  read-only client; it never opens a socket, never reads credentials,
  and never reads environment secrets.
* Not registered in the default broker registry. A later IBKR task
  will wire registration so the default surface stays
  ``safe-disconnected`` only for the duration of the skeleton.
* All returned payloads validate cleanly against the BRK-003 schemas
  (``BrokerCapabilities`` / ``BrokerStatus`` / ``BrokerAccountSnapshot``
  / ``BrokerPosition``). Capabilities pin every execution flag to
  ``False`` and ``live_orders_blocked`` to ``True``; the BRK-003 model
  validators reject anything else.

IBKR-002 introduces an optional ``readonly_client`` parameter so tests
(and later, mocked sessions) can prove the adapter surfaces a
``connected=True`` paper-read-only status without weakening any safety
flag. If the injected client reports any unsafe property —
``paper=False``, ``read_only=False``, ``execution_enabled=True``, or
``live_orders_blocked=False`` — the adapter degrades safely and refuses
to call itself connected.

The legacy paper adapter in :mod:`brokers.ibkr_paper` is unrelated and
remains untouched.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping

from .ibkr_config import IBKRPaperConfig

ADAPTER_ID: str = "ibkr-paper"

_SAFETY_NOTE_CAPABILITIES: str = (
    "IBKRPaperReadOnlyAdapter is a read-only Interactive Brokers Paper "
    "adapter. It cannot place, cancel, modify, or close orders. Execution "
    "is blocked at the schema and protocol layer."
)
_SAFETY_NOTE_DISCONNECTED: str = (
    "Safe state: IBKR Paper read-only adapter is not connected to a TWS "
    "or IB Gateway paper session. Adapter is read-only and execution is "
    "blocked."
)
_SAFETY_NOTE_CONNECTED: str = (
    "IBKR Paper read-only adapter is in connected paper read-only mode. "
    "Execution is still blocked at the schema and protocol layer; the "
    "adapter exposes no order placement or cancellation surface."
)
_SAFETY_NOTE_UNSAFE_CLIENT: str = (
    "Injected IBKR paper client reported an unsafe state "
    "(paper/read-only/execution flags violated the read-only contract). "
    "Adapter degraded safely; execution remains blocked."
)
_SAFETY_NOTE_ACCOUNT: str = (
    "No IBKR Paper session connected; account snapshot is a safe "
    "zero-valued placeholder."
)
_SAFETY_NOTE_ACCOUNT_CONNECTED: str = (
    "IBKR Paper read-only account snapshot from connected paper session. "
    "Execution is blocked; the adapter exposes no order placement or "
    "cancellation surface."
)
_SAFETY_NOTE_ACCOUNT_UNSAFE_CLIENT: str = (
    "Injected IBKR paper client violated read-only safety flags; account "
    "snapshot fell back to safe zero-valued placeholder. Execution remains "
    "blocked."
)
_SAFETY_NOTE_ACCOUNT_MALFORMED: str = (
    "Injected IBKR paper client returned a malformed account snapshot "
    "(non-numeric or unreadable values); fell back to safe zero-valued "
    "placeholder. Execution remains blocked."
)

# Whitelisted, schema-aligned numeric fields the adapter is willing to
# surface from an injected client. Any other field on the client's
# account payload (``account_id``, ``account``, ``username``,
# ``password``, ``token``, ``secret``, ``api_key``, ``credential(s)``,
# ``order_id``, ``execution_id``, ...) is silently dropped on the way
# through; only ``currency`` and these three numerics make it out.
_ALLOWED_NUMERIC_ACCOUNT_FIELDS: tuple[str, ...] = (
    "cash",
    "equity",
    "buying_power",
)

# Required safety flags an injected client must report. Each must be the
# canonical value below or the adapter will refuse to surface the client
# as "connected" and will degrade instead.
_REQUIRED_CLIENT_SAFETY_FLAGS: tuple[tuple[str, bool], ...] = (
    ("paper", True),
    ("read_only", True),
    ("execution_enabled", False),
    ("live_orders_blocked", True),
)


def _read_flag(client: object, name: str) -> object:
    """Read a safety flag from a duck-typed client.

    Looks up ``client.<name>`` as an attribute. We *do not* call any
    method on the client beyond a possible no-arg ``is_connected()``
    accessor for the connection flag — there is no way for this lookup
    to place an order, cancel an order, or otherwise mutate broker
    state.
    """
    return getattr(client, name, None)


def _client_is_safe(client: object) -> bool:
    for name, expected in _REQUIRED_CLIENT_SAFETY_FLAGS:
        if _read_flag(client, name) is not expected:
            return False
    return True


def _read_client_account_payload(client: object) -> Mapping[str, Any] | None:
    """Pull a read-only account payload from a duck-typed client.

    Tries the canonical zero-arg accessor ``client.account_snapshot()``
    first. Falls back to ``client.get_account_snapshot()`` and finally
    to a plain ``client.account_summary`` attribute, in that order, so
    tests and later mocked clients can pick whichever shape they
    prefer. Returns ``None`` if no payload is available or if the
    accessor raises — the adapter callers degrade safely to a zero
    snapshot in that case.

    This helper is strictly read-only. No method beyond a zero-arg
    accessor is invoked, and the result is consumed as a mapping;
    there is no way for this lookup to place an order, cancel an
    order, or mutate broker state.
    """
    for accessor_name in ("account_snapshot", "get_account_snapshot"):
        accessor = getattr(client, accessor_name, None)
        if callable(accessor):
            try:
                payload = accessor()
            except Exception:
                return None
            if isinstance(payload, Mapping):
                return payload
            # Non-mapping return → degrade safely.
            return None

    payload = getattr(client, "account_summary", None)
    if isinstance(payload, Mapping):
        return payload
    return None


def _coerce_account_payload(
    payload: Mapping[str, Any],
) -> Mapping[str, Any] | None:
    """Convert a raw client payload into the BRK-003 account snapshot
    shape. Returns ``None`` if any numeric field is unreadable.

    Only whitelisted fields are surfaced — sensitive or execution-shaped
    keys on the source payload are dropped on the way through.
    """
    out: dict[str, Any] = {}
    currency = payload.get("currency", "USD")
    if not isinstance(currency, str) or not currency:
        currency = "USD"
    out["currency"] = currency

    for name in _ALLOWED_NUMERIC_ACCOUNT_FIELDS:
        raw = payload.get(name, 0.0)
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return None
        # Reject NaN / inf so the schema only sees real numbers.
        if value != value or value in (float("inf"), float("-inf")):
            return None
        out[name] = value
    return out


def _client_reports_connected(client: object) -> bool:
    flag = _read_flag(client, "connected")
    if isinstance(flag, bool):
        return flag
    # Optional zero-arg accessor; we accept it only because some
    # duck-typed fakes prefer that shape. The accessor returns a bool;
    # it does not, and must not, open a network session.
    accessor = getattr(client, "is_connected", None)
    if callable(accessor):
        try:
            value = accessor()
        except Exception:
            return False
        return bool(value) is True and value is True
    return False


class IBKRPaperReadOnlyAdapter:
    """Read-only adapter for Interactive Brokers Paper.

    Implements :class:`brokers.protocol.BrokerAdapter`. Constructor
    accepts an optional :class:`IBKRPaperConfig` and an optional
    duck-typed read-only ``readonly_client``. The adapter never opens
    a connection; the injected client is read only for its self-reported
    state. Any unsafe state from the client causes the adapter to
    degrade.
    """

    adapter_id: str = ADAPTER_ID

    def __init__(
        self,
        config: IBKRPaperConfig | None = None,
        readonly_client: object | None = None,
    ) -> None:
        self._config: IBKRPaperConfig = config or IBKRPaperConfig()
        self._client: object | None = readonly_client

    # ------------------------------------------------------------------
    # Read-only protocol surface
    # ------------------------------------------------------------------
    @property
    def config(self) -> IBKRPaperConfig:
        return self._config

    @property
    def has_client(self) -> bool:
        """True iff a read-only client object has been injected."""
        return self._client is not None

    def capabilities(self) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "adapter_id": ADAPTER_ID,
                "read_only": True,
                "paper": True,
                "execution_enabled": False,
                "live_orders_blocked": True,
                "can_place_orders": False,
                "can_cancel_orders": False,
                "can_modify_orders": False,
                "supports_account_snapshot": True,
                "supports_positions": True,
                "safety_note": _SAFETY_NOTE_CAPABILITIES,
            }
        )

    def status(self) -> Mapping[str, Any]:
        # 1. No client → safe disconnected/degraded baseline.
        client = self._client
        if client is None:
            return MappingProxyType(
                {
                    "adapter_id": ADAPTER_ID,
                    "connected": False,
                    "degraded": True,
                    "degraded_reason": "IBKR paper connection not configured",
                    "read_only": True,
                    "execution_enabled": False,
                    "live_orders_blocked": True,
                    "safety_note": _SAFETY_NOTE_DISCONNECTED,
                }
            )

        # 2. Client present but reports an unsafe state → degrade.
        if not _client_is_safe(client):
            return MappingProxyType(
                {
                    "adapter_id": ADAPTER_ID,
                    "connected": False,
                    "degraded": True,
                    "degraded_reason": (
                        "Injected IBKR paper client violated read-only "
                        "safety flags"
                    ),
                    "read_only": True,
                    "execution_enabled": False,
                    "live_orders_blocked": True,
                    "safety_note": _SAFETY_NOTE_UNSAFE_CLIENT,
                }
            )

        # 3. Client present and safe — surface its connection flag.
        if _client_reports_connected(client):
            return MappingProxyType(
                {
                    "adapter_id": ADAPTER_ID,
                    "connected": True,
                    "degraded": False,
                    "degraded_reason": None,
                    "read_only": True,
                    "execution_enabled": False,
                    "live_orders_blocked": True,
                    "safety_note": _SAFETY_NOTE_CONNECTED,
                }
            )

        # 4. Safe client but not connected (e.g. session not started yet).
        return MappingProxyType(
            {
                "adapter_id": ADAPTER_ID,
                "connected": False,
                "degraded": True,
                "degraded_reason": (
                    "IBKR paper client is configured but reports a "
                    "non-connected state"
                ),
                "read_only": True,
                "execution_enabled": False,
                "live_orders_blocked": True,
                "safety_note": _SAFETY_NOTE_DISCONNECTED,
            }
        )

    def account_snapshot(self) -> Mapping[str, Any]:
        client = self._client

        # 1. No client → safe zero baseline (matches IBKR-001 behavior).
        if client is None:
            return self._safe_zero_account_snapshot(_SAFETY_NOTE_ACCOUNT)

        # 2. Client present but reports an unsafe state → safe zeros and
        # a clear safety_note. We never surface a snapshot derived from
        # an unsafe client.
        if not _client_is_safe(client):
            return self._safe_zero_account_snapshot(
                _SAFETY_NOTE_ACCOUNT_UNSAFE_CLIENT
            )

        # 3. Client present and safe — pull the read-only payload. The
        # helper returns None on missing / non-mapping / accessor-error
        # paths, which we degrade to safe zeros.
        payload = _read_client_account_payload(client)
        if payload is None:
            return self._safe_zero_account_snapshot(_SAFETY_NOTE_ACCOUNT)

        coerced = _coerce_account_payload(payload)
        if coerced is None:
            # Malformed numeric data — refuse to surface it.
            return self._safe_zero_account_snapshot(
                _SAFETY_NOTE_ACCOUNT_MALFORMED
            )

        return MappingProxyType(
            {
                "adapter_id": ADAPTER_ID,
                "currency": coerced["currency"],
                "cash": coerced["cash"],
                "equity": coerced["equity"],
                "buying_power": coerced["buying_power"],
                "read_only": True,
                "safety_note": _SAFETY_NOTE_ACCOUNT_CONNECTED,
            }
        )

    @staticmethod
    def _safe_zero_account_snapshot(safety_note: str) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "adapter_id": ADAPTER_ID,
                "currency": "USD",
                "cash": 0.0,
                "equity": 0.0,
                "buying_power": 0.0,
                "read_only": True,
                "safety_note": safety_note,
            }
        )

    def positions(self) -> list[Mapping[str, Any]]:
        return []


__all__ = ["IBKRPaperReadOnlyAdapter", "ADAPTER_ID"]
