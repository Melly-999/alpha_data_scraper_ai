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
from app.schemas.alpaca_paper_order_draft import (
    AlpacaPaperOrderDraftRequest,
    AlpacaPaperOrderDraftResponse,
)
from app.schemas.alpaca_paper_order_preview import AlpacaPaperOrderPreviewResponse
from app.schemas.alpaca_paper_order_submit_sandbox import (
    AlpacaPaperOrderSubmitSandboxRequest,
    AlpacaPaperOrderSubmitSandboxResponse,
)
from app.schemas.alpaca_paper_readonly import AlpacaPaperPositionsPreview
from app.services.alpaca_paper_demo import AlpacaPaperDemoService
from app.services.alpaca_paper_order_draft_service import (
    build_alpaca_paper_order_draft,
)
from app.services.alpaca_paper_order_preview_service import (
    generate_alpaca_paper_order_preview,
)
from app.services.alpaca_paper_order_submit_sandbox_service import (
    AlpacaPaperOrderSubmitSandboxService,
)
from app.services.alpaca_paper_readonly_adapter import AlpacaPaperReadOnlyAdapter

router = APIRouter(tags=["alpaca-paper"])
service = AlpacaPaperDemoService()
# Default adapter: no injected client -> degraded_demo unless read-only is
# explicitly enabled for a paper environment with credentials present.
readonly_adapter = AlpacaPaperReadOnlyAdapter()
# Default submit sandbox: no injected client -> blocked unless every explicit
# paper-only gate is satisfied (env flags + ACK + credentials + confirmation).
submit_sandbox_service = AlpacaPaperOrderSubmitSandboxService()


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
    "/alpaca-paper/positions-preview",
    response_model=AlpacaPaperPositionsPreview,
    summary="Alpaca paper positions preview — GET-only, read-only, sanitized",
    operation_id="get_alpaca_paper_positions_preview",
)
def get_positions_preview() -> AlpacaPaperPositionsPreview:
    """Get a sanitized, read-only Alpaca paper positions preview.

    GET-only. No order placement / cancellation / replacement, no broker
    execution, no credentials exposed. Returns a safe ``degraded_demo`` preview
    when read-only access is not explicitly enabled or credentials are absent;
    otherwise returns sanitized paper positions from a read-only client.
    """
    return readonly_adapter.get_positions_preview()


_ORDER_DRAFT_DESCRIPTION = (
    "ALPACA-PAPER-ORDER-DRAFT-001 — build a LOCAL paper order draft. "
    "This endpoint validates the submitted trade parameters and returns a "
    "structured draft object for human review. "
    "\n\n"
    "**What this endpoint does NOT do:** It does NOT submit the order to Alpaca "
    "or any broker, does NOT place / cancel / replace any order, makes NO Alpaca "
    "SDK calls, NO network I/O, and NO database writes. The POST verb only means "
    "it accepts a request body — no external broker state is mutated. "
    "\n\n"
    "**Safety invariants (always enforced):** draft_only=true, "
    "order_submission_enabled=false, execution_enabled=false, "
    "live_orders_blocked=true, dry_run=true, read_only=true, "
    "requires_human_review=true, max_risk_pct <= 1.0. "
    "Validation failures return valid=false (HTTP 200), not an error. "
    "The returned draft_id is a local paper-scoped id (paper-draft-*), never a "
    "broker order id."
)


@router.post(
    "/alpaca-paper/order-draft",
    response_model=AlpacaPaperOrderDraftResponse,
    summary="Alpaca paper order DRAFT — local-only, not submitted to Alpaca",
    description=_ORDER_DRAFT_DESCRIPTION,
    operation_id="post_alpaca_paper_order_draft",
)
def post_alpaca_paper_order_draft(
    request: AlpacaPaperOrderDraftRequest,
) -> AlpacaPaperOrderDraftResponse:
    """Build a local-only Alpaca paper order draft.

    Validates input and returns a draft for human review. Never submits to
    Alpaca, never calls a broker/network, never executes. Returns
    ``valid=false`` (HTTP 200) on validation failure.
    """
    return build_alpaca_paper_order_draft(request)


_SUBMIT_SANDBOX_DESCRIPTION = (
    "ALPACA-PAPER-ORDER-SUBMIT-SANDBOX-001 — backend-only, multi-gated, "
    "PAPER-ONLY order submission sandbox for local/manual testing. "
    "\n\n"
    "**Blocked by default.** A real Alpaca **Paper** submission is attempted ONLY "
    "when every explicit gate is satisfied: ALPACA_ENV=paper, "
    "ALPACA_PAPER_ORDER_SUBMIT_ENABLED=true, the acknowledgement env gate, "
    "Alpaca paper credentials present, request confirm_paper_order=true, and "
    "source='manual_sandbox' — plus the standard draft risk validation and "
    "conservative sandbox size caps. If any gate fails, no Alpaca call is made "
    "and a safe blocked response (HTTP 200) is returned. "
    "\n\n"
    "**This is NOT live trading.** No live endpoint, no autotrade, no frontend "
    "control, no cancellation/replacement, no bracket/OCO. live_orders_blocked "
    "and dry_run remain true; only a paper order may be submitted, and only a "
    "redacted order id is returned (never a raw broker order id, account id, or "
    "credential)."
)


@router.post(
    "/alpaca-paper/order-submit-sandbox",
    response_model=AlpacaPaperOrderSubmitSandboxResponse,
    summary="Alpaca paper order submit SANDBOX — gated, paper-only, not live",
    description=_SUBMIT_SANDBOX_DESCRIPTION,
    operation_id="post_alpaca_paper_order_submit_sandbox",
)
def post_alpaca_paper_order_submit_sandbox(
    request: AlpacaPaperOrderSubmitSandboxRequest,
) -> AlpacaPaperOrderSubmitSandboxResponse:
    """Attempt a gated, paper-only order submission for manual sandbox testing.

    Blocked by default; submits to Alpaca Paper only when every gate is
    satisfied. Never live trading, never frontend-triggered. Returns a safe
    blocked response (HTTP 200) on any gate/validation failure.
    """
    return submit_sandbox_service.submit(request)


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
