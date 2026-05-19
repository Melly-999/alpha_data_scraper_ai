"""PAPER-001B / PAPER-002B — GET-only paper sandbox endpoints.

GET /api/paper/sandbox/preview   (PAPER-001B)
GET /api/paper/sandbox/history   (PAPER-002B)

Both endpoints are read-only, dry-run-only, and simulation-only.
They will be consumed by the PAPER-001C and PAPER-002C frontend panels.

These endpoints:
- Return in-memory paper sandbox state / audit history snapshots.
- Return explicit empty-state responses when no records exist.
- Never execute orders.
- Never call real broker adapters (MT5, IBKR, or any real exchange API).
- Never create paper fills, paper positions, or live trades.
- Never return order_id, fill_id, execution_id, broker_order_id, or
  any live execution field.
- Never return account_id, credentials, secrets, tokens, or API keys.
- Always return paper_only=true, dry_run=true, read_only=true,
  live_orders_blocked=true, requires_human_review=true,
  risk_allowed=false, broker_execution_allowed=false,
  execution_mode=dry_run_only.

No POST, PUT, PATCH, or DELETE routes are wired in this file.
No frontend UI is implemented here (deferred to PAPER-001C / PAPER-002C).
"""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.paper_sandbox import PaperSandboxState
from app.schemas.paper_sandbox_history import PaperAuditHistory
from app.services.paper_sandbox import get_paper_sandbox
from app.services.paper_sandbox_history import get_paper_sandbox_history

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
    no MT5/IBKR, no live order placement.

    Returns an explicit empty PaperSandboxState (count=0, entries=[])
    when no sandbox records have been submitted.  Safety flags are
    always present in the response regardless of state contents.
    """
    return get_paper_sandbox().get_state()


# ---------------------------------------------------------------------------
# PAPER-002B — GET /api/paper/sandbox/history
# ---------------------------------------------------------------------------

_HISTORY_SUMMARY = (
    "Paper sandbox audit/activity history — read-only, dry-run, simulation-only"
)

_HISTORY_DESCRIPTION = (
    "PAPER-002B — GET-only paper sandbox audit/activity history endpoint. "
    "Returns the current in-memory history snapshot for AI Workspace display. "
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
    "Returns an explicit empty-state response (count=0, events=[]) when "
    "no audit events have been recorded. All safety flags are always "
    "present in the response regardless of history contents. "
    "\n\n"
    "Intended for read-only display in the PAPER-002C AI Workspace panel."
)


@router.get(
    "/paper/sandbox/history",
    response_model=PaperAuditHistory,
    summary=_HISTORY_SUMMARY,
    description=_HISTORY_DESCRIPTION,
    operation_id="get_paper_sandbox_history",
)
def get_paper_sandbox_history_endpoint() -> PaperAuditHistory:
    """Return the current in-memory paper sandbox audit/activity history.

    Read-only.  Dry-run-only.  No broker calls, no network I/O,
    no MT5/IBKR, no live order placement.

    Returns an explicit empty PaperAuditHistory (count=0, events=[])
    when no audit events have been recorded.  Safety flags are
    always present in the response regardless of history contents.
    """
    return get_paper_sandbox_history().get_history()
