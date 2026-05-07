"""Read-only data assembly for the MellyTrade V1 Terminal UI.

Every function returns deterministic, safe fallback data derived from the
running Settings posture. No external API calls, no broker calls, no
config mutation, no secrets — this layer mirrors what the frontend would
otherwise hardcode locally, just centralized server-side.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from .config import Settings
from .terminal_schemas import (
    BacktestSummaryResponse,
    IBKRPermissions,
    IBKRStatus,
    MarketItem,
    MarketOverviewResponse,
    MT5StatusResponse,
    NewsItem,
    NewsSentimentResponse,
    PositionItem,
    PositionsResponse,
    RiskPolicyResponse,
    RiskStatusResponse,
    SafetyFlags,
    SignalFeedResponse,
    SignalItem,
    TerminalEvent,
    TerminalEventsResponse,
    TerminalSummary,
    WatchlistResponse,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ibkr_status() -> IBKRStatus:
    return IBKRStatus(
        status="paper",
        data_freshness="paper-feed",
        latency_ms=0,
        diagnostics=[
            "Paper adapter is read-only",
            "Execution endpoints are disabled",
            "Live execution denied by safety posture",
        ],
        permissions=IBKRPermissions(),
    )


def get_terminal_summary(settings: Settings) -> TerminalSummary:
    return TerminalSummary(
        backend="online",
        safety=SafetyFlags(),
        broker=_ibkr_status(),
        updated_at=_utcnow(),
    )


def get_market_overview() -> MarketOverviewResponse:
    return [
        MarketItem(
            symbol="EURUSD",
            price=1.0784,
            change_pct=0.18,
            signal="HOLD",
            confidence=61,
        ),
        MarketItem(
            symbol="GBPUSD",
            price=1.2532,
            change_pct=-0.11,
            signal="WATCH",
            confidence=55,
        ),
        MarketItem(
            symbol="USDJPY",
            price=156.42,
            change_pct=0.24,
            signal="HOLD",
            confidence=58,
        ),
        MarketItem(
            symbol="XAUUSD",
            price=2318.8,
            change_pct=-0.32,
            signal="WATCH",
            confidence=63,
        ),
    ]


def get_watchlist() -> WatchlistResponse:
    return [
        MarketItem(
            symbol="EURUSD",
            price=1.0784,
            change_pct=0.18,
            signal="HOLD",
            confidence=61,
        ),
        MarketItem(
            symbol="GBPUSD",
            price=1.2532,
            change_pct=-0.11,
            signal="WATCH",
            confidence=55,
        ),
        MarketItem(
            symbol="USDJPY",
            price=156.42,
            change_pct=0.24,
            signal="HOLD",
            confidence=58,
        ),
    ]


def get_signal_feed() -> SignalFeedResponse:
    return [
        SignalItem(
            id="sig-eurusd-hold",
            symbol="EURUSD",
            direction="HOLD",
            confidence=61,
            timeframe="M5/H1",
            reason="Mixed momentum; risk gate remains conservative.",
        ),
        SignalItem(
            id="sig-xauusd-hold",
            symbol="XAUUSD",
            direction="HOLD",
            confidence=63,
            timeframe="M15/H1",
            reason="Volatility elevated; waiting for confirmation.",
        ),
    ]


def get_risk_status(settings: Settings) -> RiskStatusResponse:
    # Hard-clamp to 1.0 even if env mis-set; the schema also enforces le=1.0.
    max_risk = min(float(settings.max_risk_percent), 1.0)
    return RiskStatusResponse(max_risk_per_trade_pct=max_risk)


def get_risk_policy(settings: Settings) -> RiskPolicyResponse:
    return RiskPolicyResponse(
        min_confidence=float(settings.min_confidence),
        daily_loss_cap_pct=3.0,
        open_position_cap=3,
    )


def get_backtest_summary() -> BacktestSummaryResponse:
    return BacktestSummaryResponse(
        win_rate=0.0,
        max_drawdown_pct=0.0,
        profit_factor=0.0,
        sample_size=0,
    )


def get_news_sentiment() -> NewsSentimentResponse:
    return [
        NewsItem(
            id="news-fallback-1",
            headline="Fallback sentiment active; live news feed disabled.",
            source="MellyTrade",
            sentiment="neutral",
            impact="low",
            time="now",
        ),
    ]


def get_positions() -> PositionsResponse:
    return [
        PositionItem(
            id="flat-eurusd",
            symbol="EURUSD",
            side="flat",
            quantity=0,
            pnl=0,
            source="fallback",
        ),
    ]


def get_mt5_status() -> MT5StatusResponse:
    return MT5StatusResponse(
        connected=False,
        mode="synthetic",
        data_freshness="fallback",
    )


def get_terminal_events() -> TerminalEventsResponse:
    events: List[TerminalEvent] = [
        TerminalEvent(
            id="backend_started",
            event="backend_started",
            severity="success",
            time="boot",
        ),
        TerminalEvent(
            id="dry_run_active",
            event="dry_run_active",
            severity="success",
            time="boot",
        ),
        TerminalEvent(
            id="read_only_mode_confirmed",
            event="read_only_mode_confirmed",
            severity="success",
            time="boot",
        ),
        TerminalEvent(
            id="autotrade_disabled",
            event="autotrade_disabled",
            severity="success",
            time="boot",
        ),
        TerminalEvent(
            id="live_orders_blocked",
            event="live_orders_blocked",
            severity="success",
            time="boot",
        ),
        TerminalEvent(
            id="ibkr_paper_read_only",
            event="ibkr_paper_read_only",
            severity="info",
            time="boot",
        ),
        TerminalEvent(
            id="fallback_data_active",
            event="fallback_data_active",
            severity="warning",
            time="boot",
        ),
        TerminalEvent(
            id="smoke_passed",
            event="smoke_passed",
            severity="success",
            time="boot",
        ),
    ]
    return events
