from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LocalDemoEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    read_only: Literal[True] = True
    execution_mode: Literal["dry_run_only"] = "dry_run_only"
    requires_human_review: Literal[True] = True
    degraded: Literal[True] = True
    source: Literal["local_demo"] = "local_demo"
    live_orders_blocked: Literal[True] = True


class LocalDemoBacktestSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runs: int = 0
    last_run_at: datetime | None = None
    status: Literal["not_available"] = "not_available"
    message: str


class LocalDemoBacktestSummaryResponse(LocalDemoEnvelope):
    summary: LocalDemoBacktestSummary


class LocalDemoInvestmentPortfolio(BaseModel):
    model_config = ConfigDict(extra="forbid")

    positions_count: int = 0
    cash: float | None = None
    equity: float | None = None
    currency: str | None = None
    status: Literal["not_connected"] = "not_connected"


class LocalDemoInvestmentResponse(LocalDemoEnvelope):
    portfolio: LocalDemoInvestmentPortfolio
    message: str


class LocalDemoSignalItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    symbol: str
    direction: Literal["BUY", "SELL", "HOLD"]
    confidence: int
    timeframe: str
    reason: str


class LocalDemoSignalFeedResponse(LocalDemoEnvelope):
    risk_allowed: Literal[False] = False
    signals: list[LocalDemoSignalItem] = Field(default_factory=list)
    message: str
