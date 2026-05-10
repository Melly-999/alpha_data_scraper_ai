"""Pydantic models for the safe broker FastAPI surface.

This module hosts two related groups of models:

* The legacy ``BrokerHealthResponse`` / ``BrokerAccountResponse`` /
  ``BrokerDryRunRequest`` / ``BrokerExecutionReportResponse`` models
  used by ``app/api/routes/broker.py`` for the existing safe broker
  surface. They are unchanged.
* The BRK-003 typed broker schemas — ``BrokerCapabilities``,
  ``BrokerStatus``, ``BrokerAccountSnapshot``, ``BrokerPosition`` —
  used by the read-only ``brokers.protocol.BrokerAdapter`` family
  (``SafeDisconnectedBrokerAdapter`` today; future MT5 / IBKR Paper
  read-only adapters tomorrow).

The BRK-003 schemas are deliberately strict (``extra="forbid"``):
they cannot grow execution-shaped fields silently. Validators reject
any combination that would represent an executable broker
(``execution_enabled=True``, ``live_orders_blocked=False``,
``can_place_orders=True`` ...). This keeps Terminal V1's safety
posture (``autotrade=false``, ``dry_run=true``, ``read_only=true``,
``live_orders_blocked=true``, max risk ≤ 1%) impossible to weaken
through this contract.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class BrokerHealthResponse(BaseModel):
    """Mirror of :class:`brokers.adapter_models.BrokerHealth`."""

    model_config = ConfigDict(extra="forbid")

    adapter: str
    mode: str
    connected: bool
    host: str
    port: int
    client_id: int
    read_only: bool
    supports_live_orders: bool
    last_error: str | None = None
    status: str = "ok"
    timestamp: str


class BrokerAccountResponse(BaseModel):
    """Mirror of :class:`brokers.adapter_models.BrokerAccountSnapshot`."""

    model_config = ConfigDict(extra="forbid")

    adapter: str
    connected: bool
    account: str | None = None
    currency: str = "USD"
    net_liquidation: float = 0.0
    cash: float = 0.0
    buying_power: float = 0.0
    last_error: str | None = None
    timestamp: str


class BrokerDryRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_id: str = Field(..., min_length=1, max_length=64)
    signal_id: str | None = Field(default=None, max_length=64)
    symbol: str = Field(..., min_length=1, max_length=32)
    direction: str = Field(..., pattern=r"^(BUY|SELL|HOLD)$")
    confidence: float = Field(..., ge=0.0, le=100.0)
    quantity: float | None = Field(default=None, ge=0.0)
    sl: float | None = None
    tp: float | None = None
    reason: str | None = Field(default=None, max_length=256)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrokerExecutionReportResponse(BaseModel):
    """Mirror of :class:`brokers.adapter_models.BrokerExecutionReport`."""

    model_config = ConfigDict(extra="forbid")

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
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: str


# ---------------------------------------------------------------------------
# BRK-003 — typed read-only broker schemas.
#
# These models describe what a read-only ``brokers.protocol.BrokerAdapter``
# returns. They are intentionally separate from the legacy
# ``BrokerHealthResponse`` / ``BrokerAccountResponse`` /
# ``BrokerExecutionReportResponse`` models above so the existing routes are
# untouched. Future GET-only broker endpoints will adopt these models.
#
# Forbidden by ``extra="forbid"``: any field with execution / order /
# credential semantics. The list is enforced as schema-level rejection;
# explicit field names are also covered by
# ``tests/app/test_broker_schemas.py`` to catch any future drift.
# ---------------------------------------------------------------------------


class BrokerCapabilities(BaseModel):
    """What a read-only broker adapter advertises it can do.

    Every flag related to execution must be ``False`` and
    ``live_orders_blocked`` must be ``True``. A model that violates this
    contract fails validation by design — Terminal V1's safety posture
    cannot be expressed as "executable".
    """

    model_config = ConfigDict(extra="forbid")

    read_only: bool = True
    paper: bool = False
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    can_place_orders: bool = False
    can_cancel_orders: bool = False
    can_modify_orders: bool = False
    supports_account_snapshot: bool = True
    supports_positions: bool = True
    safety_note: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def _enforce_read_only_safety(self) -> "BrokerCapabilities":
        if self.read_only is not True:
            raise ValueError("BrokerCapabilities.read_only must be True")
        if self.execution_enabled is not False:
            raise ValueError("BrokerCapabilities.execution_enabled must be False")
        if self.live_orders_blocked is not True:
            raise ValueError("BrokerCapabilities.live_orders_blocked must be True")
        if self.can_place_orders is not False:
            raise ValueError("BrokerCapabilities.can_place_orders must be False")
        if self.can_cancel_orders is not False:
            raise ValueError("BrokerCapabilities.can_cancel_orders must be False")
        if self.can_modify_orders is not False:
            raise ValueError("BrokerCapabilities.can_modify_orders must be False")
        return self


class BrokerStatus(BaseModel):
    """Health / connection snapshot for a read-only broker adapter."""

    model_config = ConfigDict(extra="forbid")

    adapter_id: str = Field(..., min_length=1, max_length=64)
    connected: bool
    degraded: bool = False
    degraded_reason: str | None = None
    read_only: bool = True
    execution_enabled: bool = False
    live_orders_blocked: bool = True
    last_heartbeat: datetime | None = None
    latency_ms: float | None = Field(default=None, ge=0.0)
    safety_note: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def _enforce_read_only_safety(self) -> "BrokerStatus":
        if self.read_only is not True:
            raise ValueError("BrokerStatus.read_only must be True")
        if self.execution_enabled is not False:
            raise ValueError("BrokerStatus.execution_enabled must be False")
        if self.live_orders_blocked is not True:
            raise ValueError("BrokerStatus.live_orders_blocked must be True")
        return self


class BrokerAccountSnapshot(BaseModel):
    """Account-level snapshot for a read-only broker adapter.

    Deliberately omits ``account_id`` / credentials / tokens. Zero
    values are explicitly allowed to support the safe disconnected
    state.
    """

    model_config = ConfigDict(extra="forbid")

    adapter_id: str = Field(..., min_length=1, max_length=64)
    currency: str = Field(..., min_length=1, max_length=8)
    cash: float
    equity: float
    buying_power: float
    read_only: bool = True
    safety_note: str = Field(..., min_length=1)
    as_of: datetime | None = None

    @field_validator("read_only")
    @classmethod
    def _enforce_read_only(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("BrokerAccountSnapshot.read_only must be True")
        return value


class BrokerPosition(BaseModel):
    """A single open position as seen by a read-only broker adapter.

    Deliberately omits ``order_id`` / ``execution_id`` / ``trade_id`` /
    ``account_id`` and any other field that would imply executable
    order context. Those are rejected by ``extra="forbid"``.
    """

    model_config = ConfigDict(extra="forbid")

    adapter_id: str = Field(..., min_length=1, max_length=64)
    symbol: str = Field(..., min_length=1, max_length=32)
    quantity: float
    average_price: float | None = None
    market_price: float | None = None
    unrealized_pnl: float | None = None
    currency: str | None = Field(default=None, max_length=8)
    read_only: bool = True
    safety_note: str | None = None

    @field_validator("read_only")
    @classmethod
    def _enforce_read_only(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("BrokerPosition.read_only must be True")
        return value
