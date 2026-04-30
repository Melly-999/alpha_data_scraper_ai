from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

Action = Literal["BUY", "SELL", "HOLD"]

AuditEventType = Literal[
    "signal_received",
    "signal_accepted",
    "signal_rejected",
    "risk_gate_failed",
    "cooldown_active",
    "dry_run_active",
    "read_only_mode_active",
    "live_orders_blocked",
    "mt5_connection_status",
]

AlertSeverity = Literal["info", "warning", "error", "success"]
ReportPeriod = Literal["daily", "weekly"]
RiskState = Literal["clear", "blocked", "watch"]


class SignalIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str = Field(..., min_length=3, max_length=16)
    action: Action
    confidence: float = Field(..., ge=0, le=100)
    risk_percent: float = Field(..., gt=0, le=100)
    entry_price: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    take_profit: float = Field(..., gt=0)
    source: str = Field(default="api", max_length=32)

    @model_validator(mode="after")
    def _validate_sl_tp(self) -> "SignalIn":
        if self.action == "BUY":
            if self.stop_loss >= self.entry_price:
                raise ValueError("BUY stop_loss must be below entry_price")
            if self.take_profit <= self.entry_price:
                raise ValueError("BUY take_profit must be above entry_price")
        elif self.action == "SELL":
            if self.stop_loss <= self.entry_price:
                raise ValueError("SELL stop_loss must be above entry_price")
            if self.take_profit >= self.entry_price:
                raise ValueError("SELL take_profit must be below entry_price")
        return self


class SignalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    symbol: str
    action: Action
    confidence: float
    risk_percent: float
    entry_price: float
    stop_loss: float
    take_profit: float
    source: str
    status: str
    reason: str


class SignalSummaryOut(BaseModel):
    """Dashboard-oriented signal view with safety context attached.

    Used by GET /signals so the trader UI can render gate decisions without
    a second round-trip. Live execution flags are always read-only here.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    symbol: str
    action: Action
    confidence: float
    confidence_clamped: float
    risk_pct: float
    entry_price: float
    stop_loss: float
    take_profit: float
    source: str
    status: str
    reason: str
    rejection_reason: Optional[str] = None
    dry_run: bool
    read_only: bool


class HealthOut(BaseModel):
    status: str = "ok"
    service: str = "mellytrade-api"
    version: str = "0.1.0"
    cooldown_seconds: int
    min_confidence: float
    max_risk_percent: float
    database: str
    dry_run: bool = True
    autotrade_enabled: bool = False
    read_only: bool = True
    live_orders_blocked: bool = True


class RiskGateStatus(BaseModel):
    name: str
    active: bool
    description: str


class RiskConfigOut(BaseModel):
    """Read-only snapshot of risk gates and safety posture."""

    min_confidence: float
    max_risk_percent: float
    cooldown_seconds: int
    dry_run: bool
    autotrade_enabled: bool
    read_only: bool
    live_orders_blocked: bool
    gates: List[RiskGateStatus]


class AuditEvent(BaseModel):
    type: AuditEventType
    timestamp: datetime
    severity: Literal["info", "warning", "error"] = "info"
    message: str
    detail: Optional[Dict[str, object]] = None
    signal_id: Optional[int] = None


class AuditOut(BaseModel):
    events: List[AuditEvent]
    dry_run: bool
    read_only: bool
    live_orders_blocked: bool


class AlertOut(BaseModel):
    id: str
    timestamp: datetime
    severity: AlertSeverity
    category: str
    title: str
    message: str
    source: str
    symbol: Optional[str] = None
    signal_id: Optional[int] = None
    read_only: bool
    metadata: Dict[str, object] = Field(default_factory=dict)


class ReportSignalCounts(BaseModel):
    total: int
    accepted: int
    rejected: int


class ReportOut(BaseModel):
    period: ReportPeriod
    generated_at: datetime
    window_start: datetime
    window_end: datetime
    safety_posture: HealthOut
    signal_counts: ReportSignalCounts
    alert_counts_by_severity: Dict[str, int]
    alert_counts_by_category: Dict[str, int]
    latest_audit_events: List[AuditEvent]
    risk_config_snapshot: RiskConfigOut
    markdown_summary: str
    read_only: bool


class WatchlistItemOut(BaseModel):
    symbol: str
    name: str
    asset_class: str
    last_price: float
    change_pct: float
    signal_status: str
    signal_confidence: Optional[float] = None
    alert_count: int
    risk_state: RiskState
    source: str
    generated_at: datetime
    read_only: bool


class RejectedOut(BaseModel):
    status: Literal["rejected"] = "rejected"
    reason: str
    detail: Optional[str] = None
