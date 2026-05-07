"""Read-only response schemas for the MellyTrade V1 Terminal UI.

Every model surfaces the safety posture (dry_run / auto_trade / read_only)
so the dashboard can render guardrails without a second round-trip. There
are no input schemas: terminal endpoints are GET-only.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field

SignalDirection = Literal["BUY", "SELL", "HOLD", "WATCH"]
PositionSide = Literal["long", "short", "flat"]
NewsSentiment = Literal["positive", "negative", "neutral"]
NewsImpact = Literal["high", "medium", "low"]
EventSeverity = Literal["info", "warning", "success"]
BackendMode = Literal["online", "fallback"]
BrokerStatus = Literal["connected", "disconnected", "degraded", "paper", "read-only"]
PermissionState = Literal["allowed", "denied"]
MT5Mode = Literal["synthetic", "paper", "offline"]


class SafetyFlags(BaseModel):
    """Locked-on safety posture surfaced to every terminal response."""

    read_only: Literal[True] = True
    dry_run: Literal[True] = True
    auto_trade: Literal[False] = False
    live_orders_blocked: Literal[True] = True


class IBKRPermissions(BaseModel):
    market_data: PermissionState = "allowed"
    account_read: PermissionState = "allowed"
    positions_read: PermissionState = "allowed"
    orders: Literal["denied"] = "denied"
    live_execution: Literal["denied"] = "denied"


class IBKRStatus(BaseModel):
    name: Literal["IBKR Paper"] = "IBKR Paper"
    status: BrokerStatus
    read_only: Literal[True] = True
    execution_enabled: Literal[False] = False
    data_freshness: str
    latency_ms: int = Field(ge=0)
    diagnostics: List[str]
    permissions: IBKRPermissions = Field(default_factory=IBKRPermissions)


class TerminalSummary(BaseModel):
    terminal: str = "MellyTrade V1 Terminal"
    mode: Literal["read-only"] = "read-only"
    backend: BackendMode = "online"
    safety: SafetyFlags = Field(default_factory=SafetyFlags)
    broker: IBKRStatus
    updated_at: datetime


class MarketItem(BaseModel):
    symbol: str
    price: float
    change_pct: float
    signal: SignalDirection
    confidence: float = Field(ge=0, le=100)


MarketOverviewResponse = List[MarketItem]
WatchlistResponse = List[MarketItem]


class SignalItem(BaseModel):
    id: str
    symbol: str
    direction: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(ge=0, le=100)
    timeframe: str
    reason: str


SignalFeedResponse = List[SignalItem]


class RiskStatusResponse(BaseModel):
    """Current risk gate state for the dashboard.

    `max_risk_per_trade_pct` is enforced <= 1.0 by Settings and re-asserted
    here so the Terminal UI cannot accidentally render an unsafe value.
    """

    max_risk_per_trade_pct: float = Field(le=1.0, gt=0)
    dry_run: Literal[True] = True
    auto_trade: Literal[False] = False
    read_only: Literal[True] = True
    stop_loss_required: Literal[True] = True
    take_profit_required: Literal[True] = True
    live_orders_blocked: Literal[True] = True


class RiskPolicyResponse(BaseModel):
    min_confidence: float = Field(ge=0, le=100)
    daily_loss_cap_pct: float = Field(ge=0)
    open_position_cap: int = Field(ge=0)
    execution_enabled: Literal[False] = False
    requires_stop_loss: Literal[True] = True
    requires_take_profit: Literal[True] = True
    live_orders_blocked: Literal[True] = True


class BacktestSummaryResponse(BaseModel):
    win_rate: float = Field(ge=0, le=1)
    max_drawdown_pct: float = Field(ge=0)
    profit_factor: float = Field(ge=0)
    sample_size: int = Field(ge=0)


class NewsItem(BaseModel):
    id: str
    headline: str
    source: str
    sentiment: NewsSentiment
    impact: NewsImpact
    time: str


NewsSentimentResponse = List[NewsItem]


class PositionItem(BaseModel):
    id: str
    symbol: str
    side: PositionSide
    quantity: float = Field(ge=0)
    pnl: float
    source: Literal["paper", "fallback"] = "fallback"


PositionsResponse = List[PositionItem]


class MT5StatusResponse(BaseModel):
    connected: bool
    mode: MT5Mode
    data_freshness: str
    read_only: Literal[True] = True
    execution_enabled: Literal[False] = False


class TerminalEvent(BaseModel):
    id: str
    event: str
    severity: EventSeverity
    time: str


TerminalEventsResponse = List[TerminalEvent]
