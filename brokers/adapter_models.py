"""Typed models shared by the safe broker adapter abstraction.

These are intentionally separate from the legacy ``brokers.base`` /
``brokers.broker_interface`` modules so the safety-first paper adapter
path does not have to import any code that requires ``ib_insync`` or
other heavy optional dependencies at import time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class BrokerHealth:
    """Adapter health snapshot. Always safe to serialise."""

    adapter: str
    mode: str  # "paper" | "live" | "disabled"
    connected: bool
    host: str
    port: int
    client_id: int
    read_only: bool
    supports_live_orders: bool
    last_error: str | None = None
    status: str = "ok"
    timestamp: str = field(default_factory=_utcnow_iso)


@dataclass(frozen=True)
class BrokerAccountSnapshot:
    """Account snapshot returned by an adapter.

    A *disconnected* snapshot is returned when the adapter cannot talk to
    a real broker; values are zeroed and ``connected`` is ``False`` so
    the FastAPI surface can never crash on missing credentials.
    """

    adapter: str
    connected: bool
    account: str | None = None
    currency: str = "USD"
    net_liquidation: float = 0.0
    cash: float = 0.0
    buying_power: float = 0.0
    last_error: str | None = None
    timestamp: str = field(default_factory=_utcnow_iso)


@dataclass(frozen=True)
class BrokerExecutionReport:
    """Result of submitting an :class:`ExecutionDecision` to an adapter.

    ``dry_run`` is the only mode supported by the v1 IBKR paper adapter;
    no field on this object can cause a real order to be placed.
    """

    adapter: str
    broker: str
    dry_run: bool
    accepted: bool
    decision_id: str | None = None
    signal_id: str | None = None
    symbol: str | None = None
    direction: str | None = None
    confidence: float | None = None
    quantity: float | None = None
    sl: float | None = None
    tp: float | None = None
    reason: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=_utcnow_iso)


@dataclass(frozen=True)
class ExecutionDecision:
    """Lightweight ``SignalCandidate -> ExecutionDecision`` shape.

    The full execution pipeline lives in :mod:`execution.execution_manager`;
    this dataclass is the minimum the broker adapter layer needs and is
    intentionally decoupled so adapters can be unit tested without the
    rest of the stack.
    """

    decision_id: str
    signal_id: str | None
    symbol: str
    direction: str
    confidence: float
    dry_run: bool = True
    quantity: float | None = None
    sl: float | None = None
    tp: float | None = None
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
