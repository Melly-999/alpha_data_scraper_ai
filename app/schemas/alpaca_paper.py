"""Alpaca Paper Trading Demo Schemas.

READ-ONLY, paper-only, fallback-first response models for Alpaca Paper Trading.

Safety contract:
- paper_only: Literal[True]
- dry_run: Literal[True]
- read_only: Literal[True]
- live_orders_blocked: Literal[True]
- execution_enabled: Literal[False]
- requires_human_review: Literal[True]

No credentials, API keys, account IDs, or network calls.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AlpacaPaperSafetyFlags(BaseModel):
    """Safety flags required on all Alpaca Paper responses."""

    model_config = ConfigDict(extra="forbid")

    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    execution_enabled: Literal[False] = False
    requires_human_review: Literal[True] = True


class AlpacaPaperAccount(BaseModel):
    """Paper account preview (no credentials)."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["active"] = "active"
    account_type: Literal["paper"] = "paper"
    currency: Literal["USD"] = "USD"
    buying_power: float = Field(default=25000.0, description="Starting paper account")
    cash: float = Field(default=25000.0)
    equity: float = 25000.0
    portfolio_value: float = 25000.0


class AlpacaPaperAccountPreview(AlpacaPaperSafetyFlags):
    """Account status preview endpoint response."""

    account: AlpacaPaperAccount


class AlpacaPaperMarketHours(BaseModel):
    """Market trading hours."""

    model_config = ConfigDict(extra="forbid")

    open: str = Field(default="09:30", description="Market open time (ET)")
    close: str = Field(default="16:00", description="Market close time (ET)")


class AlpacaPaperMarketClockData(BaseModel):
    """Current market clock state."""

    model_config = ConfigDict(extra="forbid")

    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    is_open: bool = False
    next_open: str | None = None
    next_close: str | None = None
    trading_hours: AlpacaPaperMarketHours = Field(
        default_factory=AlpacaPaperMarketHours
    )


class AlpacaPaperMarketClock(AlpacaPaperSafetyFlags):
    """Market clock endpoint response."""

    clock: AlpacaPaperMarketClockData


class AlpacaPaperWatchlistItem(BaseModel):
    """Single watchlist symbol."""

    model_config = ConfigDict(extra="forbid")

    symbol: str
    name: str = ""
    last_quote_time: str | None = None
    last_quote: dict | None = None


class AlpacaPaperWatchlist(BaseModel):
    """Watchlist preview data."""

    model_config = ConfigDict(extra="forbid")

    watchlists_count: int = 1
    items_count: int = 0
    default_items: list[AlpacaPaperWatchlistItem] = Field(default_factory=list)


class AlpacaPaperWatchlistPreview(AlpacaPaperSafetyFlags):
    """Watchlist preview endpoint response."""

    watchlist: AlpacaPaperWatchlist


class AlpacaPaperStatus(AlpacaPaperSafetyFlags):
    """Alpaca Paper Trading status endpoint response."""

    message: Literal[
        "Alpaca Paper Trading Demo — read-only, no credentials, fallback data"
    ] = "Alpaca Paper Trading Demo — read-only, no credentials, fallback data"
    version: Literal["0.1.0"] = "0.1.0"
    features: list[str] = Field(
        default_factory=lambda: [
            "GET /alpaca-paper/status",
            "GET /alpaca-paper/account-preview",
            "GET /alpaca-paper/market-clock",
            "GET /alpaca-paper/watchlist-preview",
        ]
    )
