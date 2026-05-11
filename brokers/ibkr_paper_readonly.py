# brokers/ibkr_paper_readonly.py
"""IBKR-001 — :class:`IBKRPaperReadOnlyAdapter`.

Skeleton / foundation for the read-only IBKR Paper adapter behind the
:class:`brokers.protocol.BrokerAdapter` protocol. Disconnected-safe by
default; later IBKR tasks (IBKR-002 / 005 / 006) will replace the safe
zero-state outputs with mock-backed snapshots derived from a real TWS
Paper session.

Design contract:

* Read-only. No execution / order / risk-mutation method names exist
  on this adapter.
* No broker SDK imports. Standard library only. The legacy
  :mod:`brokers.ibkr_paper` module (unrelated to this read-only
  adapter) still handles the pre-existing paper flow; this module
  intentionally does not touch it.
* No network calls. The constructor stores the
  :class:`brokers.ibkr_config.IBKRPaperConfig` but never opens a
  socket, never reads credentials, and never reads environment
  secrets.
* Not registered in the default broker registry. A later IBKR task
  will wire registration so the default surface stays
  ``safe-disconnected`` only for the duration of the skeleton.
* All returned payloads validate cleanly against the BRK-003 schemas
  (``BrokerCapabilities`` / ``BrokerStatus`` / ``BrokerAccountSnapshot``
  / ``BrokerPosition``). Capabilities pin every execution flag to
  ``False`` and ``live_orders_blocked`` to ``True``; the BRK-003 model
  validators reject anything else.

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
_SAFETY_NOTE_STATUS: str = (
    "Safe state: IBKR Paper read-only adapter is not connected to a TWS "
    "or IB Gateway paper session. Adapter is read-only and execution is "
    "blocked."
)
_SAFETY_NOTE_ACCOUNT: str = (
    "No IBKR Paper session connected; account snapshot is a safe "
    "zero-valued placeholder."
)


class IBKRPaperReadOnlyAdapter:
    """Read-only skeleton adapter for Interactive Brokers Paper.

    Implements :class:`brokers.protocol.BrokerAdapter`. Constructor takes
    an optional :class:`IBKRPaperConfig`; if omitted, the safe defaults
    on that config are used. The adapter never connects to TWS / IB
    Gateway from this module; later IBKR tasks will introduce a mocked
    client that fetches read-only state.
    """

    adapter_id: str = ADAPTER_ID

    def __init__(self, config: IBKRPaperConfig | None = None) -> None:
        # Defensive copy via dataclass replace-not-needed; the config is
        # frozen so we can keep the reference safely.
        self._config: IBKRPaperConfig = config or IBKRPaperConfig()

    # ------------------------------------------------------------------
    # Read-only protocol surface
    # ------------------------------------------------------------------
    @property
    def config(self) -> IBKRPaperConfig:
        return self._config

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
        return MappingProxyType(
            {
                "adapter_id": ADAPTER_ID,
                "connected": False,
                "degraded": True,
                "degraded_reason": "IBKR paper connection not configured",
                "read_only": True,
                "execution_enabled": False,
                "live_orders_blocked": True,
                "safety_note": _SAFETY_NOTE_STATUS,
            }
        )

    def account_snapshot(self) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "adapter_id": ADAPTER_ID,
                "currency": "USD",
                "cash": 0.0,
                "equity": 0.0,
                "buying_power": 0.0,
                "read_only": True,
                "safety_note": _SAFETY_NOTE_ACCOUNT,
            }
        )

    def positions(self) -> list[Mapping[str, Any]]:
        return []


__all__ = ["IBKRPaperReadOnlyAdapter", "ADAPTER_ID"]
