from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import Mode


class ServiceDependencyStatus(BaseModel):
    active: bool
    detail: str | None = None
    latency_ms: int | None = None
    model: str | None = None
    last_update: str | None = None


class ApiStatus(BaseModel):
    healthy: bool
    uptime: str
    version: str
    fallback_mode: bool


class SystemStatus(BaseModel):
    mt5: ServiceDependencyStatus
    api: ApiStatus
    claude: ServiceDependencyStatus
    news: ServiceDependencyStatus
    symbol: str
    mode: Mode
    last_tick: str
    emergency_stop: bool


class WatchlistItem(BaseModel):
    symbol: str
    bid: float
    ask: float
    change: float
    signal: str
    confidence: int | None = None


class ActivityFeedItem(BaseModel):
    time: str
    type: str
    msg: str
    color: str


class EquityCurvePoint(BaseModel):
    x: int
    y: float


class AccountOverview(BaseModel):
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    drawdown: float
    daily_pnl: float
    daily_pnl_pct: float
    open_positions: int
    today_trades: int


class DashboardSummary(BaseModel):
    system_status: SystemStatus
    account: AccountOverview
    ready_signals: list["SignalSummary"]
    risk_status: "RiskStatus"
    watchlist: list[WatchlistItem]
    activity_feed: list[ActivityFeedItem]
    equity_curve: list[EquityCurvePoint]
    generated_at: datetime


from app.schemas.risk import RiskStatus  # noqa: E402
from app.schemas.signal import SignalSummary  # noqa: E402
