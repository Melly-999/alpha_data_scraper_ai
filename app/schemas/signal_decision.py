from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

DecisionType = Literal["dry_run_allowed", "blocked", "watch_only", "no_action"]
RiskStatus = Literal["pass", "warn", "blocked", "unknown"]
DecisionDirection = Literal["BUY", "SELL", "HOLD", "UNKNOWN"]


class SignalDecisionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    timestamp: datetime
    symbol: str
    direction: DecisionDirection
    confidence: float
    source: str
    strategy: str
    risk_status: RiskStatus
    decision: DecisionType
    blocked_reason: str | None = None
    dry_run: bool = True
    auto_trade: bool = False
    read_only: bool = True
    stop_loss_required: bool = True
    take_profit_required: bool = True
    max_risk_per_trade: float = 0.01
    metadata: dict[str, Any] = Field(default_factory=dict)


class SignalDecisionHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool = True
    auto_trade: bool = False
    read_only: bool = True
    total: int
    decisions: list[SignalDecisionRecord]
    generated_at: datetime
    degraded: bool
    fallback: bool
