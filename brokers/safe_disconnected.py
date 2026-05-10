# brokers/safe_disconnected.py
"""BRK-002 — :class:`SafeDisconnectedBrokerAdapter`.

Default, safety-first broker adapter used as the fallback before any
real broker integration (MT5, IBKR, ...) is wired up.

Design contract:

* Implements the read-only :class:`brokers.protocol.BrokerAdapter` only.
* Represents a *disconnected* broker — no network, no credentials, no
  SDKs.
* Cannot place, cancel, modify, or close orders. Has no method names
  shaped like execution.
* Standard library only. Does not import :mod:`MetaTrader5`,
  :mod:`ib_insync`, :mod:`ibapi`, :mod:`alpaca`, :mod:`ccxt`,
  :mod:`requests`, :mod:`httpx`, or :mod:`websockets`.

Future broker adapters (IBKR Paper read-only, MT5 read-only, ...) will
implement the same protocol but talk to a real connection. This adapter
exists so the rest of the system can always assume *some* read-only
adapter is available without compromising safety when no broker is
configured.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping

ADAPTER_ID: str = "safe-disconnected"

_SAFETY_NOTE_CAPABILITIES: str = (
    "SafeDisconnectedBrokerAdapter is a disconnected, read-only fallback "
    "adapter. It cannot place, cancel, modify, or close orders, and it "
    "never connects to a broker."
)
_SAFETY_NOTE_STATUS: str = (
    "Safe state: no broker connection. Adapter is read-only and execution "
    "is blocked."
)
_SAFETY_NOTE_ACCOUNT: str = (
    "No broker connected; account snapshot is a safe zero-valued placeholder."
)


class SafeDisconnectedBrokerAdapter:
    """Read-only adapter representing a disconnected, non-executable broker.

    Implements :class:`brokers.protocol.BrokerAdapter`. Public surface is
    intentionally limited to ``adapter_id``, :meth:`capabilities`,
    :meth:`status`, :meth:`account_snapshot`, and :meth:`positions`.
    """

    adapter_id: str = ADAPTER_ID

    def capabilities(self) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "adapter_id": ADAPTER_ID,
                "read_only": True,
                "paper": False,
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
                "degraded_reason": "No broker connection configured",
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


__all__ = ["SafeDisconnectedBrokerAdapter", "ADAPTER_ID"]
