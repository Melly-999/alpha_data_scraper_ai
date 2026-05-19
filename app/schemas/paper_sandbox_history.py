"""PAPER-002A — In-memory paper sandbox activity/audit history schemas.

These schemas represent the paper-only sandbox audit/activity event log.
They carry no execution intent and cannot trigger live orders, broker calls,
MT5/IBKR routing, or any order-placement mechanism.

No route is wired in this file.  Route integration is deferred to PAPER-002B.
Frontend panel is deferred to PAPER-002C.

Safety constants that must never change in this module:
  paper_only             = True
  dry_run                = True
  read_only              = True
  live_orders_blocked    = True
  requires_human_review  = True
  broker_execution_allowed = False
  risk_allowed           = False
  execution_mode         = "dry_run_only"

Forbidden fields — these must never appear in any schema in this module:
  account_id, broker_account_id, order_id, execution_id, broker_order_id,
  ibkr_order_id, mt5_ticket, credential, secret, token, api_key, password.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Valid event types
# ---------------------------------------------------------------------------

VALID_EVENT_TYPES: frozenset[str] = frozenset({
    "sandbox_preview_requested",
    "sandbox_state_created",
    "sandbox_state_reset",
    "ticket_draft_observed",
    "safety_flags_checked",
    "human_review_required",
    "degraded_fallback_used",
    "unknown_paper_event",
})


# ---------------------------------------------------------------------------
# PaperAuditEvent
# ---------------------------------------------------------------------------

class PaperAuditEvent(BaseModel):
    """One paper-only sandbox audit/activity event.

    Event IDs are locally-scoped sequential identifiers (paper_audit_000001).
    They are NOT broker order IDs, fill IDs, execution IDs, or account IDs
    of any kind.

    Every event carries the full locked safety contract as fields.  The
    metadata dict is pre-sanitized by the service to exclude all forbidden
    fields before storage.
    """

    model_config = ConfigDict(extra="forbid")

    # --- local paper-scoped identity (no broker/execution IDs) ---
    event_id: str = Field(min_length=1, max_length=64)
    timestamp: str = Field(min_length=1, max_length=64)   # ISO 8601 UTC

    # --- event classification ---
    event_type: Literal[
        "sandbox_preview_requested",
        "sandbox_state_created",
        "sandbox_state_reset",
        "ticket_draft_observed",
        "safety_flags_checked",
        "human_review_required",
        "degraded_fallback_used",
        "unknown_paper_event",
    ]
    source: str = Field(min_length=1, max_length=128)
    severity: Literal["info", "warning", "blocked"] = "info"
    message: str = Field(min_length=1, max_length=512)

    # --- sanitized advisory context (no forbidden keys, no secrets) ---
    metadata: dict[str, Any] = Field(default_factory=dict)

    # --- immutable safety contract (always locked to safe values) ---
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    execution_mode: Literal["dry_run_only"] = "dry_run_only"
    requires_human_review: Literal[True] = True
    risk_allowed: Literal[False] = False
    broker_execution_allowed: Literal[False] = False


# ---------------------------------------------------------------------------
# PaperAuditHistory
# ---------------------------------------------------------------------------

class PaperAuditHistory(BaseModel):
    """Read-only snapshot of the current in-memory audit/activity history.

    Returned by the history service on request.  Never carries broker or
    account state — the history is purely local and simulation-only.

    ``count`` reflects the number of events in ``events``.
    """

    model_config = ConfigDict(extra="forbid")

    events: list[PaperAuditEvent] = Field(default_factory=list)
    count: int = Field(ge=0)

    # Safety snapshot — always locked to safe values
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    execution_mode: Literal["dry_run_only"] = "dry_run_only"
    requires_human_review: Literal[True] = True
    risk_allowed: Literal[False] = False
    broker_execution_allowed: Literal[False] = False
