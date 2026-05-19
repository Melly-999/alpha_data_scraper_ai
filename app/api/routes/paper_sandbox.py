"""PAPER-001B — GET-only paper sandbox preview endpoint.

GET /api/paper/sandbox/preview

Read-only, dry-run-only sandbox state preview for AI Workspace display.
This endpoint will be consumed by the PAPER-001C frontend panel.

This endpoint:
- Returns the current in-memory PaperSandboxState (entries, count,
  safety flags).
- Returns an explicit empty-state response when no records exist.
- Never executes orders.
- Never calls real broker adapters (MT5, IBKR, or any real exchange API).
- Never creates paper fills or paper positions.
- Never returns order_id, fill_id, execution_id, broker_order_id, or
  any live execution field.
- Always returns paper_only=true, dry_run=true, read_only=true,
  live_orders_blocked=true, requires_human_review=true,
  risk_allowed=false, broker_execution_allowed=false,
  execution_mode=dry_run_only.

No POST, PUT, PATCH, or DELETE routes are wired in this file.
No frontend UI is implemented here (deferred to PAPER-001C).
"""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.paper_sandbox import PaperSandboxState
from app.services.paper_sandbox import get_paper_sandbox

router = APIRouter(tags=["paper-sandbox"])

_SUMMARY = (
    "Paper sandbox state preview — read-only, dry-run, simulation-only"
)

_DESCRIPTION = (
    "PAPER-001B — GET-only paper sandbox preview endpoint. "
    "Returns the current in-memory sandbox state for AI Workspace display. "
    "\n\n"
    "**What this endpoint does NOT do:** "
    "No live trading. No broker execution. No MT5/IBKR order routing. "
    "No order placement of any kind. No POST/PUT/PATCH/DELETE routes. "
    "Read-only and dry-run-only. "
    "\n\n"
    "**Safety invariants (always enforced):** "
    "paper_only=true, dry_run=true, read_only=true, "
    "live_orders_blocked=true, execution_mode=dry_run_only, "
    "broker_execution_allowed=false, risk_allowed=false, "
    "requires_human_review=true. "
    "\n\n"
    "Returns an explicit empty-state response (count=0, entries=[]) when "
    "no sandbox records have been submitted. All safety flags are always "
    "present in the response regardless of state contents. "
    "\n\n"
    "Intended for read-only display in the PAPER-001C AI Workspace panel."
)


@router.get(
    "/paper/sandbox/preview",
    response_model=PaperSandboxState,
    summary=_SUMMARY,
    description=_DESCRIPTION,
    operation_id="get_paper_sandbox_preview",
)
def get_paper_sandbox_preview() -> PaperSandboxState:
    """Return the current in-memory paper sandbox state.

    Read-only.  Dry-run-only.  No broker calls, no network I/O,
    no MT5/IBKR, no Supabase, no live order placement.

    Returns an explicit empty PaperSandboxState (count=0, entries=[])
    when no sandbox records have been submitted.  Safety flags are
    always present in the response regardless of state contents.
    """
    return get_paper_sandbox().get_state()
