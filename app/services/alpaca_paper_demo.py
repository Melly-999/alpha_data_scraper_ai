"""Alpaca Paper Trading Demo Service.

Fallback-first, static-data-only service for Alpaca Paper Trading.

Rules:
- No network calls
- No credentials
- No Alpaca SDK
- No broker calls
- No order execution
- No file writes
- No database writes
- Static/demo data only
"""

from __future__ import annotations

from app.schemas.alpaca_paper import (
    AlpacaPaperAccount,
    AlpacaPaperAccountPreview,
    AlpacaPaperMarketClock,
    AlpacaPaperMarketClockData,
    AlpacaPaperStatus,
    AlpacaPaperWatchlist,
    AlpacaPaperWatchlistPreview,
)


class AlpacaPaperDemoService:
    """Fallback-first Alpaca Paper Trading demo service.

    Provides static demo data only. No network calls, no credentials,
    no broker integration.
    """

    def get_status(self) -> AlpacaPaperStatus:
        """Get Alpaca Paper Trading status.

        Returns:
            AlpacaPaperStatus: Static status response with safety flags.
        """
        return AlpacaPaperStatus()

    def get_account_preview(self) -> AlpacaPaperAccountPreview:
        """Get paper account preview.

        Returns:
            AlpacaPaperAccountPreview: Account overview with default demo values.
        """
        account = AlpacaPaperAccount()
        return AlpacaPaperAccountPreview(account=account)

    def get_market_clock(self) -> AlpacaPaperMarketClock:
        """Get market clock state.

        Returns:
            AlpacaPaperMarketClock: Current market hours and status.
        """
        clock_data = AlpacaPaperMarketClockData()
        return AlpacaPaperMarketClock(clock=clock_data)

    def get_watchlist_preview(self) -> AlpacaPaperWatchlistPreview:
        """Get watchlist preview.

        Returns:
            AlpacaPaperWatchlistPreview: Empty watchlist with structure.
        """
        watchlist = AlpacaPaperWatchlist(
            watchlists_count=0, items_count=0, default_items=[]
        )
        return AlpacaPaperWatchlistPreview(watchlist=watchlist)
