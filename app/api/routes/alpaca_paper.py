"""Alpaca Paper Trading Demo Routes.

GET-only, paper-only routes for Alpaca Paper Trading fallback integration.

Routes:
- GET /alpaca-paper/status
- GET /alpaca-paper/account-preview
- GET /alpaca-paper/market-clock
- GET /alpaca-paper/watchlist-preview
- GET /alpaca-paper/order-preview

No POST/PUT/PATCH/DELETE allowed.
No credentials required.
No broker execution.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas.alpaca_paper import (
    AlpacaPaperAccountPreview,
    AlpacaPaperMarketClock,
    AlpacaPaperStatus,
    AlpacaPaperWatchlistPreview,
)
from app.schemas.alpaca_paper_order_preview import AlpacaPaperOrderPreviewResponse
from app.services.alpaca_paper_demo import AlpacaPaperDemoService
from app.services.alpaca_paper_order_preview_service import (
    generate_alpaca_paper_order_preview,
)

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


_ORDER_PREVIEW_SUMMARY = (
    "Alpaca paper order preview — GET-only, never submitted, no broker execution"
)

_ORDER_PREVIEW_DESCRIPTION = (
    "ALPACA-PAPER-ORDER-PREVIEW-003 — GET-only Alpaca paper order preview. "
    "Returns a deterministic, locally-generated paper order preview for the "
    "given trade setup parameters. "
    "\n\n"
    "**What this endpoint does NOT do:** "
    "No live trading. No order submission. No broker execution. No Alpaca SDK "
    "calls. No network I/O. No database writes. No POST/PUT/PATCH/DELETE routes. "
    "Read-only and dry-run-only. "
    "\n\n"
    "**Validation rules:** "
    "max_risk_pct must not exceed 1.0 (capped at 1% per trade). "
    "BUY geometry: stop_loss < entry_price < take_profit. "
    "SELL geometry: take_profit < entry_price < stop_loss. "
    "Validation failures return allowed=false (HTTP 200), not an error. "
    "\n\n"
    "**Safety invariants (always enforced):** "
    "paper_only=true, dry_run=true, read_only=true, "
    "live_orders_blocked=true, requires_human_review=true, "
    "execution_enabled=false, submitted=false. "
    "\n\n"
    "When validation passes: returns allowed=true with an order preview "
    "containing paper-scoped IDs (paper-alpaca-* prefix), no broker IDs. "
    "When validation fails: returns allowed=false with order=null and a "
    "descriptive reason. Human review is always required."
)


@router.get(
    "/alpaca-paper/order-preview",
    response_model=AlpacaPaperOrderPreviewResponse,
    summary=_ORDER_PREVIEW_SUMMARY,
    description=_ORDER_PREVIEW_DESCRIPTION,
    operation_id="get_alpaca_paper_order_preview",
)
def get_alpaca_paper_order_preview(
    symbol: str = Query(min_length=1, max_length=32),
    side: str = Query(pattern="^(BUY|SELL)$"),
    quantity: float = Query(gt=0),
    entry_price: float = Query(gt=0),
    stop_loss: float = Query(gt=0),
    take_profit: float = Query(gt=0),
    max_risk_pct: float = Query(gt=0),
) -> AlpacaPaperOrderPreviewResponse:
    """Return a paper-only Alpaca order preview for the given trade parameters.

    Read-only.  Dry-run-only.  No broker calls, no network I/O, no order
    submission, no database writes.  submitted=false always.

    Returns ``allowed=true`` with a synthetic order preview on success, or
    ``allowed=false`` with ``order=null`` on geometry or risk failure
    (HTTP 200 in both cases — not an error response).
    Safety flags are always present in the response.
    """
    return generate_alpaca_paper_order_preview(
        symbol=symbol,
        side=side,
        quantity=quantity,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        max_risk_pct=max_risk_pct,
    )
