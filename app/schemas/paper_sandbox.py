"""PAPER-001 — In-memory paper broker sandbox schemas.

These schemas represent the paper-only sandbox state and submission lifecycle.
They carry no execution intent and cannot trigger live orders, broker calls,
MT5/IBKR routing, or any order-placement mechanism.

No route is wired in this file.  Route integration is deferred to PAPER-003.

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

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.trade_ticket import EntryType, TradeSide


# ---------------------------------------------------------------------------
# PaperSandboxEntry
# ---------------------------------------------------------------------------

class PaperSandboxEntry(BaseModel):
    """One paper-only ticket record stored in the in-memory sandbox.

    Derived from a validated TradeTicketDraft.  Never carries broker IDs,
    account IDs, credentials, or execution state.  The ``sandbox_entry_id``
    field is a locally-generated paper-scoped identifier — it is NOT a
    broker order ID, fill ID, or execution ID of any kind.
    """

    model_config = ConfigDict(extra="forbid")

    # --- paper-scoped identity (no broker/account/execution IDs) ---
    sandbox_entry_id: str = Field(min_length=1, max_length=160)
    ticket_id: str = Field(min_length=1, max_length=128)

    # --- trade setup (copied from the ticket, no execution fields) ---
    symbol: str = Field(min_length=1, max_length=32)
    side: TradeSide
    entry_type: EntryType
    timeframe: str = Field(min_length=1, max_length=8)
    entry_price: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    take_profit_1: float = Field(gt=0)
    take_profit_2: float | None = Field(default=None, gt=0)
    risk_pct: float = Field(gt=0, le=1.0)
    confidence: float = Field(ge=0, le=100)
    reason: str = Field(min_length=1, max_length=1024)
    source: str
    submitted_at: str  # ISO 8601 UTC

    # --- immutable safety contract ---
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    risk_allowed: Literal[False] = False
    broker_execution_allowed: Literal[False] = False
    execution_mode: Literal["dry_run_only"] = "dry_run_only"


# ---------------------------------------------------------------------------
# PaperSandboxSubmitResult
# ---------------------------------------------------------------------------

class PaperSandboxSubmitResult(BaseModel):
    """Result of submitting a validated TradeTicketDraft to the sandbox.

    ``accepted=True`` means the draft passed all safety checks and was
    stored in the in-memory sandbox.  ``accepted=False`` means a safety
    or validation constraint blocked storage — ``rejection_reasons`` will
    explain why.

    The ``safety_contract`` field is always present regardless of acceptance.
    """

    model_config = ConfigDict(extra="forbid")

    accepted: bool
    entry: PaperSandboxEntry | None = None
    rejection_reasons: list[str] = Field(default_factory=list)
    safety_contract: dict[str, bool | str | float]


# ---------------------------------------------------------------------------
# PaperSandboxState
# ---------------------------------------------------------------------------

class PaperSandboxState(BaseModel):
    """Read-only snapshot of the current in-memory sandbox contents.

    Returned by the sandbox service on request.  Never carries broker or
    account state — the sandbox is purely local and simulation-only.
    """

    model_config = ConfigDict(extra="forbid")

    entries: list[PaperSandboxEntry] = Field(default_factory=list)
    count: int = Field(ge=0)

    # Safety snapshot — always locked to safe values
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    execution_mode: Literal["dry_run_only"] = "dry_run_only"
