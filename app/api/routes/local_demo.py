from __future__ import annotations

from fastapi import APIRouter

from app.schemas.local_demo import (
    LocalDemoBacktestSummary,
    LocalDemoBacktestSummaryResponse,
    LocalDemoInvestmentPortfolio,
    LocalDemoInvestmentResponse,
    LocalDemoSignalFeedResponse,
)

router = APIRouter(tags=["local-demo"])


@router.get("/backtest/summary", response_model=LocalDemoBacktestSummaryResponse)
def backtest_summary() -> LocalDemoBacktestSummaryResponse:
    return LocalDemoBacktestSummaryResponse(
        summary=LocalDemoBacktestSummary(
            runs=0,
            last_run_at=None,
            status="not_available",
            message="Backtest summary is not available in local source-only beta.",
        )
    )


@router.get("/investment", response_model=LocalDemoInvestmentResponse)
def investment() -> LocalDemoInvestmentResponse:
    return LocalDemoInvestmentResponse(
        portfolio=LocalDemoInvestmentPortfolio(
            positions_count=0,
            cash=None,
            equity=None,
            currency=None,
            status="not_connected",
        ),
        message=(
            "Investment dashboard is local-demo only and provides no "
            "personalized recommendations."
        ),
    )


@router.get("/signals/feed", response_model=LocalDemoSignalFeedResponse)
def signals_feed() -> LocalDemoSignalFeedResponse:
    return LocalDemoSignalFeedResponse(
        signals=[],
        risk_allowed=False,
        message=(
            "Signal feed is empty in local source-only beta. Use scanner "
            "preview for advisory demo output."
        ),
    )
