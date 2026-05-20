from __future__ import annotations

from fastapi import APIRouter

from app.schemas.market import MarketItem
from app.services.watchlist import WatchlistService

router = APIRouter(tags=["watchlist"])

_watchlist_service = WatchlistService()


@router.get("/watchlist", response_model=list[MarketItem])
def watchlist() -> list[MarketItem]:
    """Read-only watchlist for the Terminal V1 dashboard.

    Returns a static advisory-only list of watched instruments with display
    labels (HOLD/WATCH) and confidence scores. GET-only. Performs no mutation,
    no broker connection, and no order placement. Labels are informational —
    this endpoint does not trigger trade execution.
    """
    return _watchlist_service.get_watchlist()
