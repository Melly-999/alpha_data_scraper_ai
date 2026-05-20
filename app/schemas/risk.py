from __future__ import annotations

from typing import Literal

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.common import BlockedReason, Severity


class RiskConfig(BaseModel):
    max_risk_per_trade: float
    max_daily_loss: float
    max_drawdown: float
    min_confidence: int
    min_rr: float
    max_open_positions: int
    max_lot_size: float
    cooldown_seconds: int
    allow_same_signal: bool
    dry_run: bool
    auto_trade: bool
    emergency_pause: bool


class RiskConfigUpdate(BaseModel):
    max_risk_per_trade: float | None = None
    max_daily_loss: float | None = None
    max_drawdown: float | None = None
    min_confidence: int | None = None
    min_rr: float | None = None
    max_open_positions: int | None = None
    max_lot_size: float | None = None
    cooldown_seconds: int | None = None
    allow_same_signal: bool | None = None
    dry_run: bool | None = None
    auto_trade: bool | None = None
    emergency_pause: bool | None = None


class RiskStatus(BaseModel):
    daily_loss_used: float
    daily_loss_limit: float
    drawdown_current: float
    drawdown_limit: float
    open_positions: int
    open_positions_limit: int
    trades_blocked: int
    trades_executed: int
    risk_exposure: float
    emergency_pause: bool


class RiskViolation(BaseModel):
    id: str
    type: BlockedReason
    signal_ref: str | None = None
    reason: str
    severity: Severity
    timestamp: datetime


class EmergencyStopResponse(BaseModel):
    stopped: bool
    timestamp: datetime
    config: RiskConfig
    violation: RiskViolation


class RiskPolicyResponse(BaseModel):
    """Read-only risk policy projection for the Terminal V1 dashboard.

    Fields match the frontend terminalApi.ts RiskPolicy type.  Additional
    safety fields are included for contract validation.  All safety-critical
    values are Literal-typed and cannot be weakened by callers.
    """

    model_config = ConfigDict(extra="forbid")

    # Frontend-compatible fields (matches terminalApi.ts RiskPolicy type)
    min_confidence: int = 70
    daily_loss_cap_pct: float = 3.0
    open_position_cap: int = 3
    execution_enabled: Literal[False] = False

    # Safety flags (Literal-locked)
    read_only: Literal[True] = True
    dry_run: Literal[True] = True
    auto_trade: Literal[False] = False
    live_orders_blocked: Literal[True] = True
    execution_mode: Literal["dry_run_only"] = "dry_run_only"
    broker_execution_enabled: Literal[False] = False
    requires_human_review: Literal[True] = True

    # Risk invariants
    max_risk_per_trade_pct: float = 1.0
    stop_loss_required: Literal[True] = True
    take_profit_required: Literal[True] = True

    safety_note: str = (
        "Read-only risk policy. No live orders or broker execution available."
    )

    @field_validator("max_risk_per_trade_pct")
    @classmethod
    def _max_risk_ceiling(cls, v: float) -> float:
        if v > 1.0:
            raise ValueError("max_risk_per_trade_pct must be <= 1.0")
        return v
