"""GET-only HTTP routes for the MellyTrade V1 Terminal UI.

All endpoints are read-only by design. There is no input model, no POST,
no PUT/PATCH/DELETE, and no path that maps to broker execution. The router
is mounted under /api so the dashboard's `terminalApi.ts` client matches.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from . import terminal_service
from .config import Settings, get_settings
from .terminal_schemas import (
    BacktestSummaryResponse,
    MarketOverviewResponse,
    MT5StatusResponse,
    NewsSentimentResponse,
    PositionsResponse,
    RiskPolicyResponse,
    RiskStatusResponse,
    SignalFeedResponse,
    TerminalEventsResponse,
    TerminalSummary,
    WatchlistResponse,
)

router = APIRouter(prefix="/api", tags=["terminal"])


@router.get("/terminal/summary", response_model=TerminalSummary)
def terminal_summary(
    settings: Settings = Depends(get_settings),
) -> TerminalSummary:
    return terminal_service.get_terminal_summary(settings)


@router.get("/market/overview", response_model=MarketOverviewResponse)
def market_overview() -> MarketOverviewResponse:
    return terminal_service.get_market_overview()


@router.get("/watchlist", response_model=WatchlistResponse)
def watchlist() -> WatchlistResponse:
    return terminal_service.get_watchlist()


@router.get("/signals/feed", response_model=SignalFeedResponse)
def signals_feed() -> SignalFeedResponse:
    return terminal_service.get_signal_feed()


@router.get("/risk/status", response_model=RiskStatusResponse)
def risk_status(
    settings: Settings = Depends(get_settings),
) -> RiskStatusResponse:
    return terminal_service.get_risk_status(settings)


@router.get("/risk/policy", response_model=RiskPolicyResponse)
def risk_policy(
    settings: Settings = Depends(get_settings),
) -> RiskPolicyResponse:
    return terminal_service.get_risk_policy(settings)


@router.get("/backtest/summary", response_model=BacktestSummaryResponse)
def backtest_summary() -> BacktestSummaryResponse:
    return terminal_service.get_backtest_summary()


@router.get("/news/sentiment", response_model=NewsSentimentResponse)
def news_sentiment() -> NewsSentimentResponse:
    return terminal_service.get_news_sentiment()


@router.get("/positions", response_model=PositionsResponse)
def positions() -> PositionsResponse:
    return terminal_service.get_positions()


@router.get("/mt5/status", response_model=MT5StatusResponse)
def mt5_status() -> MT5StatusResponse:
    return terminal_service.get_mt5_status()


@router.get("/terminal/events", response_model=TerminalEventsResponse)
def terminal_events() -> TerminalEventsResponse:
    return terminal_service.get_terminal_events()
