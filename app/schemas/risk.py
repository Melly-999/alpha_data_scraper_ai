from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

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
