"""PAPER-RUN-API-001 — GET /api/paper/run/preview.

Paper-only, read-only, deterministic simulation preview.

This endpoint:
- Returns a synthetic paper run preview for the given trade setup parameters.
- Never executes orders.
- Never calls real broker adapters (MT5, IBKR, or any real exchange API).
- Never creates paper fills, paper positions, or live trades.
- Never writes to any database or file.
- Never reads from any external network service.
- Never returns account_id, broker_order_id, execution_id, trade_id,
  secret, token, api_key, or password.
- Always returns paper_only=true, dry_run=true, read_only=true,
  live_orders_blocked=true, requires_human_review=true,
  execution_enabled=false.
- Returns allowed=false with a descriptive reason when geometry or risk
  checks fail.  This is an HTTP 200 response, not an error.

No POST, PUT, PATCH, or DELETE routes are wired in this file.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas.paper_run_preview import PaperRunPreviewResponse
from app.services.paper_run_preview_service import generate_paper_run_preview

router = APIRouter(tags=["paper-run-preview"])

_SUMMARY = (
    "Paper run preview — read-only, dry-run, simulation-only, no broker execution"
)

_DESCRIPTION = (
    "PAPER-RUN-API-001 — GET-only paper run preview endpoint. "
    "Returns a deterministic, locally-generated paper run simulation preview "
    "for the given trade setup parameters. "
    "\n\n"
    "**What this endpoint does NOT do:** "
    "No live trading. No broker execution. No MT5/IBKR order routing. "
    "No order placement of any kind. No database writes. No network calls. "
    "No POST/PUT/PATCH/DELETE routes. "
    "Read-only and dry-run-only. "
    "\n\n"
    "**Validation rules:** "
    "max_risk_pct must not exceed 1.0 (capped at 1% per trade). "
    "confidence must be 0–100. "
    "BUY geometry: stop_loss must be less than entry_price, "
    "which must be less than take_profit. "
    "SELL geometry: take_profit must be less than entry_price, "
    "which must be less than stop_loss. "
    "Validation failures return allowed=false (HTTP 200), not an error. "
    "\n\n"
    "**Safety invariants (always enforced):** "
    "paper_only=true, dry_run=true, read_only=true, "
    "live_orders_blocked=true, requires_human_review=true, "
    "execution_enabled=false. "
    "\n\n"
    "When validation passes: returns allowed=true with a paper_run preview "
    "containing one simulated order, fill, and position — all paper-scoped "
    "with paper_* prefixed IDs, no broker or account IDs. "
    "When validation fails: returns allowed=false with paper_run=null and "
    "a descriptive reason. "
    "Human review is always required."
)


@router.get(
    "/paper/run/preview",
    response_model=PaperRunPreviewResponse,
    summary=_SUMMARY,
    description=_DESCRIPTION,
    operation_id="get_paper_run_preview",
)
def get_paper_run_preview(
    symbol: str = Query(min_length=1, max_length=32),
    side: str = Query(pattern="^(BUY|SELL)$"),
    quantity: float = Query(gt=0),
    entry_price: float = Query(gt=0),
    stop_loss: float = Query(gt=0),
    take_profit: float = Query(gt=0),
    confidence: float = Query(ge=0.0, le=100.0),
    max_risk_pct: float = Query(gt=0, le=100.0),
) -> PaperRunPreviewResponse:
    """Return a paper-only run simulation preview for the given trade parameters.

    Read-only.  Dry-run-only.  No broker calls, no network I/O,
    no MT5/IBKR, no live order placement, no database writes.

    Returns ``allowed=true`` with a synthetic paper_run on success, or
    ``allowed=false`` with ``paper_run=null`` on geometry or risk failure
    (HTTP 200 in both cases — not an error response).
    Safety flags are always present in the response.
    """
    return generate_paper_run_preview(
        symbol=symbol,
        side=side,
        quantity=quantity,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        confidence=confidence,
        max_risk_pct=max_risk_pct,
    )
