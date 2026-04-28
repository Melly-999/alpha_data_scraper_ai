"""Pydantic models for the safe broker FastAPI surface."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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
