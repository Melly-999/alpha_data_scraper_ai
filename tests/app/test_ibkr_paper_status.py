"""IBKR-002 — Tests for the IBKR Paper read-only status fallback path.

The adapter must:

* Default to a safe disconnected / degraded state when no client is
  injected.
* Surface ``connected=True`` only when an injected duck-typed client
  reports ``connected=True`` *and* every required safety flag is the
  canonical safe value (``paper=True``, ``read_only=True``,
  ``execution_enabled=False``, ``live_orders_blocked=True``).
* Degrade safely if the injected client reports any unsafe value.
* Never expose an order / execute / connect / disconnect method.
* Stay import-safe (no broker SDK or network module pulled in).
* Leave the default broker registry untouched (still safe-disconnected
  only).
"""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass

import pytest

from app.schemas.broker import BrokerStatus
from brokers.ibkr_paper_readonly import IBKRPaperReadOnlyAdapter


# ---------------------------------------------------------------------------
# Tiny duck-typed fake clients. None of them open a connection, perform
# network I/O, or import any broker SDK.
# ---------------------------------------------------------------------------
@dataclass
class _SafePaperClient:
    """Minimal read-only fake matching the canonical safety contract."""

    connected: bool = True
    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True


@dataclass
class _SafePaperClientViaAccessor:
    """Like ``_SafePaperClient`` but exposes ``is_connected()`` instead of
    a ``connected`` attribute. Proves the adapter accepts either shape.
    """

    paper: bool = True
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True

    def is_connected(self) -> bool:
        return True


# ---------------------------------------------------------------------------
# Test 1 — default adapter remains disconnected / degraded.
# ---------------------------------------------------------------------------
def test_default_adapter_is_disconnected_and_degraded() -> None:
    adapter = IBKRPaperReadOnlyAdapter()
    assert adapter.has_client is False

    status = adapter.status()
    assert status["connected"] is False
    assert status["degraded"] is True
    assert status["read_only"] is True
    assert status["execution_enabled"] is False
    assert status["live_orders_blocked"] is True
    assert "not configured" in status["degraded_reason"]


# ---------------------------------------------------------------------------
# Test 2 — default status validates with BrokerStatus.
# ---------------------------------------------------------------------------
def test_default_status_validates_into_schema() -> None:
    status = BrokerStatus(**dict(IBKRPaperReadOnlyAdapter().status()))
    assert status.adapter_id == "ibkr-paper"
    assert status.read_only is True
    assert status.execution_enabled is False
    assert status.live_orders_blocked is True


# ---------------------------------------------------------------------------
# Test 3 — safe paper client makes status connected=True.
# ---------------------------------------------------------------------------
def test_safe_client_makes_status_connected() -> None:
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=_SafePaperClient())
    status = adapter.status()
    assert status["connected"] is True
    assert status["degraded"] is False
    assert status["degraded_reason"] is None
    # Connected status still validates as BrokerStatus.
    BrokerStatus(**dict(status))


def test_safe_client_via_accessor_makes_status_connected() -> None:
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=_SafePaperClientViaAccessor())
    status = adapter.status()
    assert status["connected"] is True
    assert status["degraded"] is False


# ---------------------------------------------------------------------------
# Test 4 — connected status still has the safety flags locked.
# ---------------------------------------------------------------------------
def test_connected_status_still_safe() -> None:
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=_SafePaperClient())
    status = adapter.status()
    assert status["read_only"] is True
    assert status["execution_enabled"] is False
    assert status["live_orders_blocked"] is True
    assert "execution" in status["safety_note"].lower()


# ---------------------------------------------------------------------------
# Tests 5–8 — unsafe fake clients degrade safely.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "unsafe_kwargs",
    [
        {"paper": False},
        {"read_only": False},
        {"execution_enabled": True},
        {"live_orders_blocked": False},
    ],
    ids=[
        "paper-false",
        "read-only-false",
        "execution-enabled",
        "live-orders-not-blocked",
    ],
)
def test_unsafe_client_degrades_safely(unsafe_kwargs: dict[str, object]) -> None:
    client = _SafePaperClient(**unsafe_kwargs)  # type: ignore[arg-type]
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=client)
    status = adapter.status()

    # The adapter never surfaces the unsafe state; it always reports the
    # canonical safe values regardless of what the client claims.
    assert status["connected"] is False
    assert status["degraded"] is True
    assert status["read_only"] is True
    assert status["execution_enabled"] is False
    assert status["live_orders_blocked"] is True
    assert (
        "unsafe" in status["safety_note"].lower()
        or "violat" in (status["degraded_reason"] or "").lower()
    )


# ---------------------------------------------------------------------------
# Bonus — safe client reporting not-connected leaves the adapter degraded.
# ---------------------------------------------------------------------------
def test_safe_client_not_connected_stays_degraded() -> None:
    adapter = IBKRPaperReadOnlyAdapter(
        readonly_client=_SafePaperClient(connected=False)
    )
    status = adapter.status()
    assert status["connected"] is False
    assert status["degraded"] is True
    assert status["read_only"] is True
    assert status["execution_enabled"] is False
    assert status["live_orders_blocked"] is True


# ---------------------------------------------------------------------------
# Test 9 — adapter still exposes no forbidden execution-shaped method
# names, including connect / disconnect.
# ---------------------------------------------------------------------------
_FORBIDDEN_METHOD_NAMES: tuple[str, ...] = (
    "place_order",
    "cancel_order",
    "modify_order",
    "execute",
    "submit_order",
    "close_position",
    "open_position",
    "broker_execute",
    "enable_autotrade",
    "disable_dry_run",
    "change_config_runtime",
    "modify_risk_policy",
    "placeOrder",
    "cancelOrder",
    "reqMktData",
    "reqPositions",
    "buy",
    "sell",
    # IBKR-002 specific: no active connect / disconnect on the adapter.
    "connect",
    "disconnect",
)


def test_adapter_has_no_forbidden_methods() -> None:
    adapter = IBKRPaperReadOnlyAdapter(readonly_client=_SafePaperClient())
    surface = set(dir(adapter)) | set(dir(IBKRPaperReadOnlyAdapter))
    leaked = sorted(surface & set(_FORBIDDEN_METHOD_NAMES))
    assert not leaked, (
        "IBKRPaperReadOnlyAdapter must not expose forbidden " f"method(s): {leaked!r}"
    )


# ---------------------------------------------------------------------------
# Test 10 — module import is still SDK / network free.
# ---------------------------------------------------------------------------
_FORBIDDEN_IMPORT_PREFIXES: tuple[str, ...] = (
    "ib_insync",
    "ibapi",
    "MetaTrader5",
    "alpaca",
    "alpaca_trade_api",
    "ccxt",
    "requests",
    "httpx",
    "websocket",
    "websockets",
)


def test_module_import_pulls_no_broker_or_network_modules() -> None:
    for name in (
        "brokers.ibkr_paper_readonly",
        "brokers.ibkr_config",
    ):
        sys.modules.pop(name, None)

    before = set(sys.modules)
    importlib.import_module("brokers.ibkr_paper_readonly")
    after = set(sys.modules)

    newly_imported = after - before
    leaked = sorted(
        name
        for name in newly_imported
        if any(
            name == prefix or name.startswith(prefix + ".")
            for prefix in _FORBIDDEN_IMPORT_PREFIXES
        )
    )
    assert not leaked, (
        "brokers.ibkr_paper_readonly must be import-safe; unexpected "
        f"modules imported: {leaked!r}"
    )


# ---------------------------------------------------------------------------
# Test 11 — default registry includes IBKR paper but keeps safe default.
# ---------------------------------------------------------------------------
def test_default_registry_includes_ibkr_without_changing_default() -> None:
    from brokers.registry import create_default_registry
    from brokers.safe_disconnected import SafeDisconnectedBrokerAdapter

    registry = create_default_registry()
    assert set(registry.list_adapter_ids()) == {
        "safe-disconnected",
        "ibkr-paper",
    }
    assert registry.default_adapter_id == "safe-disconnected"
    assert isinstance(registry.get_default(), SafeDisconnectedBrokerAdapter)
    assert registry.get_optional("ibkr-paper") is not None


# ---------------------------------------------------------------------------
# Test 12 — IBKR-001 capabilities baseline still holds (sanity).
# ---------------------------------------------------------------------------
def test_capabilities_baseline_still_holds() -> None:
    from app.schemas.broker import BrokerCapabilities

    payload = dict(IBKRPaperReadOnlyAdapter().capabilities())
    payload.pop("adapter_id", None)
    caps = BrokerCapabilities(**payload)
    assert caps.read_only is True
    assert caps.paper is True
    assert caps.execution_enabled is False
    assert caps.live_orders_blocked is True
    assert caps.can_place_orders is False
    assert caps.can_cancel_orders is False
    assert caps.can_modify_orders is False
