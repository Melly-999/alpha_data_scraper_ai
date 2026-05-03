from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

LifecycleDecision = Literal["dry_run_allowed", "blocked", "watch_only", "no_action"]
LifecycleDirection = Literal["BUY", "SELL", "HOLD", "UNKNOWN"]
LifecycleStepKey = Literal[
    "signal_received",
    "confidence_checked",
    "risk_checked",
    "broker_safety_checked",
    "dry_run_decision",
    "blocked_or_allowed_reason",
    "audit_event_reference",
]
LifecycleStepStatus = Literal[
    "received",
    "passed",
    "blocked",
    "allowed",
    "recorded",
    "skipped",
]


class SignalLifecycleStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: LifecycleStepKey
    label: str
    status: LifecycleStepStatus
    detail: str
    audit_event_id: str | None = None


class SignalLifecycleRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    signal_id: str
    decision_id: str
    audit_event_id: str
    timestamp: datetime
    symbol: str
    direction: LifecycleDirection
    confidence: float = Field(..., ge=0.0, le=1.0)
    decision: LifecycleDecision
    blocked_reason: str | None = None
    dry_run: bool = True
    auto_trade: bool = False
    read_only: bool = True
    supports_live_orders: bool = False
    dry_run_allowed: bool = False
    order_placed: bool = False
    max_risk_per_trade: float = Field(default=0.01, le=0.01)
    steps: list[SignalLifecycleStep]


class SignalLifecycleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool = True
    auto_trade: bool = False
    read_only: bool = True
    supports_live_orders: bool = False
    total: int
    lifecycle: list[SignalLifecycleRecord]
    generated_at: datetime
    degraded: bool
    fallback: bool
