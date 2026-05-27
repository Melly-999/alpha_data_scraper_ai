"""PAPER-RUN-API-001 — Schemas for GET /api/paper/run/preview.

Read-only, paper-only, deterministic simulation preview endpoint.

Safety constants that must never change in this module:
  paper_only             = True
  dry_run                = True
  read_only              = True
  live_orders_blocked    = True
  requires_human_review  = True
  execution_enabled      = False

Forbidden fields — must never appear in any schema in this module:
  account_id, broker_account_id, order_id, execution_id, broker_order_id,
  ibkr_order_id, mt5_ticket, trade_id, credential, secret, token, api_key,
  password.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# PaperRunPreviewOrder
# ---------------------------------------------------------------------------


class PaperRunPreviewOrder(BaseModel):
    """A paper-only simulated order in the preview run.

    ``paper_order_id`` is a locally-generated paper-scoped identifier.
    It is NOT a broker order ID, fill ID, execution ID, or account ID.
    """

    model_config = ConfigDict(extra="forbid")

    # paper-scoped identity (no broker/account/execution IDs)
    paper_order_id: str = Field(min_length=1, max_length=160)
    created_at: str  # ISO 8601 UTC

    # trade setup (no execution fields)
    symbol: str = Field(min_length=1, max_length=32)
    direction: Literal["BUY", "SELL"]
    quantity: float = Field(gt=0)
    entry_price: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    take_profit: float = Field(gt=0)
    max_risk_pct: float = Field(gt=0, le=1.0)
    status: Literal["pending", "open", "closed", "cancelled", "rejected"] = "open"
    rejection_reason: str | None = None

    # immutable safety contract
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    execution_enabled: Literal[False] = False


# ---------------------------------------------------------------------------
# PaperRunPreviewFill
# ---------------------------------------------------------------------------


class PaperRunPreviewFill(BaseModel):
    """A paper-only simulated fill in the preview run.

    ``paper_fill_id`` is a locally-generated paper-scoped identifier.
    It is NOT a broker fill ID, execution ID, or account ID.
    """

    model_config = ConfigDict(extra="forbid")

    paper_fill_id: str = Field(min_length=1, max_length=160)
    paper_order_ref: str = Field(min_length=1, max_length=160)
    fill_timestamp: str  # ISO 8601 UTC
    symbol: str = Field(min_length=1, max_length=32)
    direction: Literal["BUY", "SELL"]
    fill_price: float = Field(gt=0)
    quantity: float = Field(gt=0)

    # immutable safety contract
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    execution_enabled: Literal[False] = False


# ---------------------------------------------------------------------------
# PaperRunPreviewPosition
# ---------------------------------------------------------------------------


class PaperRunPreviewPosition(BaseModel):
    """A paper-only simulated position in the preview run.

    ``paper_position_id`` is a locally-generated paper-scoped identifier.
    It is NOT a broker position ID, execution ID, or account ID.
    """

    model_config = ConfigDict(extra="forbid")

    paper_position_id: str = Field(min_length=1, max_length=160)
    paper_order_ref: str = Field(min_length=1, max_length=160)
    opened_at: str  # ISO 8601 UTC
    closed_at: str | None = None
    symbol: str = Field(min_length=1, max_length=32)
    direction: Literal["BUY", "SELL"]
    quantity: float = Field(gt=0)
    entry_price: float = Field(gt=0)
    current_price: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    take_profit: float = Field(gt=0)
    unrealized_pnl: float
    max_risk_pct: float = Field(gt=0, le=1.0)
    status: Literal["open", "closed"] = "open"

    # immutable safety contract
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    execution_enabled: Literal[False] = False


# ---------------------------------------------------------------------------
# PaperRunPreviewRun
# ---------------------------------------------------------------------------


class PaperRunPreviewRun(BaseModel):
    """A paper-only simulated run summary for preview.

    ``run_id`` is a locally-generated paper-scoped identifier.
    It is NOT a broker order ID, execution ID, or account ID.
    """

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1, max_length=160)
    started_at: str  # ISO 8601 UTC
    ended_at: str | None = None
    total_signals: int = Field(ge=0)
    accepted_signals: int = Field(ge=0)
    rejected_signals: int = Field(ge=0)
    open_positions_count: int = Field(ge=0)
    closed_positions_count: int = Field(ge=0)
    max_risk_pct: float = Field(gt=0, le=1.0)
    orders: list[PaperRunPreviewOrder] = Field(default_factory=list)
    fills: list[PaperRunPreviewFill] = Field(default_factory=list)
    positions: list[PaperRunPreviewPosition] = Field(default_factory=list)

    # immutable safety contract
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    execution_enabled: Literal[False] = False


# ---------------------------------------------------------------------------
# PaperRunPreviewResponse (top-level)
# ---------------------------------------------------------------------------


class PaperRunPreviewResponse(BaseModel):
    """Top-level response for GET /api/paper/run/preview.

    Always includes all six safety flags.  ``paper_run`` is None when
    ``allowed=False`` (geometry or risk check blocked the simulation).
    """

    model_config = ConfigDict(extra="forbid")

    allowed: bool
    reason: str = Field(min_length=1, max_length=2048)
    paper_run: PaperRunPreviewRun | None = None

    # immutable safety contract
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    execution_enabled: Literal[False] = False
