"""PDS-003 — Paper-only ticket draft endpoint.

POST /api/paper/tickets/draft

Paper-only decision support.  Exposes the PDS-002 TradeTicketDraftService
through a safe, read-only API route.

This endpoint:
- Creates and validates a TradeTicketDraft from scanner/manual input.
- Never executes orders.
- Never calls real broker adapters (MT5, IBKR, or any real exchange API).
- Never creates paper fills or paper positions yet.
- Never returns order_id, fill_id, execution_id, broker_order_id, or
  any live execution field.
- Always returns paper_only=true, dry_run=true, read_only=true,
  live_orders_blocked=true, requires_human_review=true,
  risk_allowed=false, broker_execution_allowed=false.
- Always requires human review before any simulated execution step.

The safety contract enforced by PAPER-GUARD-001 is invariant.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.services.trade_ticket_draft_service import (
    TradeTicketDraftInput,
    TradeTicketDraftResult,
    TradeTicketDraftService,
)

router = APIRouter(tags=["paper-sandbox"])

_svc = TradeTicketDraftService()

_SUMMARY = (
    "Create a paper-only simulated ticket draft "
    "(sandbox, dry_run, no broker execution, human review required)"
)

_DESCRIPTION = (
    "Paper-only sandbox endpoint (PDS-003). "
    "Validates a TradeTicketDraft from scanner or manual setup input "
    "using the PDS-002 TradeTicketDraftService. "
    "\n\n"
    "**What this endpoint does NOT do:** "
    "No live trading. No broker execution. No MT5/IBKR order routing. "
    "No paper fills yet. No paper positions yet. "
    "No order_id, fill_id, execution_id, broker_order_id returned. "
    "\n\n"
    "**Safety invariants (always enforced):** "
    "dry_run=true, read_only=true, live_orders_blocked=true, "
    "requires_human_review=true, risk_allowed=false, "
    "broker_execution_allowed=false, max_risk_pct<=1.0, "
    "stop_loss required, take_profit_1 required. "
    "\n\n"
    "Returns accepted=true with a validated draft on success, "
    "or accepted=false with rejection_reasons on validation failure. "
    "Always returns safety_contract. Human review is always required."
)


@router.post(
    "/paper/tickets/draft",
    response_model=TradeTicketDraftResult,
    summary=_SUMMARY,
    description=_DESCRIPTION,
    operation_id="create_paper_ticket_draft",
)
def create_paper_ticket_draft(body: TradeTicketDraftInput) -> TradeTicketDraftResult:
    """Create a paper-only ticket draft for human review.

    Returns accepted=true with a validated paper-only draft, or
    accepted=false with rejection reasons.  The safety_contract field
    is always present and always reflects the paper-only invariants.
    This function never calls any broker, network service, or database.
    """
    return _svc.create(body)
