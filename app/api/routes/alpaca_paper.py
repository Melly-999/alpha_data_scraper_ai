"""Alpaca Paper Trading Demo Routes.

GET-only, paper-only routes for Alpaca Paper Trading fallback integration.

Routes:
- GET /alpaca-paper/status
- GET /alpaca-paper/account-preview
- GET /alpaca-paper/market-clock
- GET /alpaca-paper/watchlist-preview

No POST/PUT/PATCH/DELETE allowed.
No credentials required.
No broker execution.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.alpaca_paper import (
    AlpacaPaperAccountPreview,
    AlpacaPaperMarketClock,
    AlpacaPaperStatus,
    AlpacaPaperWatchlistPreview,
)
from app.services.alpaca_paper_demo import AlpacaPaperDemoService

router = APIRouter(tags=["alpaca-paper"])
service = AlpacaPaperDemoService()


@router.get("/alpaca-paper/status", response_model=AlpacaPaperStatus)
def get_status() -> AlpacaPaperStatus:
    """Get Alpaca Paper Trading status.

    Returns HTTP 200 with demo status and available endpoints.
    """
    return service.get_status()


@router.get("/alpaca-paper/account-preview", response_model=AlpacaPaperAccountPreview)
def get_account_preview() -> AlpacaPaperAccountPreview:
    """Get paper account preview.

    Returns HTTP 200 with demo account data (no credentials).
    """
    return service.get_account_preview()


@router.get("/alpaca-paper/market-clock", response_model=AlpacaPaperMarketClock)
def get_market_clock() -> AlpacaPaperMarketClock:
    """Get market clock state.

    Returns HTTP 200 with trading hours and market status.
    """
    return service.get_market_clock()


@router.get(
    "/alpaca-paper/watchlist-preview", response_model=AlpacaPaperWatchlistPreview
)
def get_watchlist_preview() -> AlpacaPaperWatchlistPreview:
    """Get watchlist preview.

    Returns HTTP 200 with empty watchlist structure.
    """
    return service.get_watchlist_preview()
