from __future__ import annotations

from fastapi import APIRouter

from app.schemas.market import MarketItem
from app.services.market_overview import MarketOverviewService

router = APIRouter(tags=["market"])

_market_overview_service = MarketOverviewService()


@router.get("/market/overview", response_model=list[MarketItem])
def market_overview() -> list[MarketItem]:
    """Read-only market overview for the Terminal V1 dashboard.

    Returns a static advisory-only list of watched instruments with display
    labels (HOLD/WATCH/BUY/SELL) and confidence scores. GET-only. Performs no
    mutation, no broker connection, and no order placement. Labels are
    informational — this endpoint does not trigger trade execution.
    """
    return _market_overview_service.get_overview()
