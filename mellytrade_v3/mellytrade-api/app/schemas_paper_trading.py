"""PAPER-M4-001 — Paper trading domain model schemas.

Defines the four core types for the simulation layer:

  PaperOrder    — a simulated order derived from a validated signal
  PaperPosition — an open simulated position carrying unrealised P&L
  PaperFill     — a simulated fill event recording when a position opened
  PaperRun      — a paper trading session collecting orders, positions, fills

Safety invariants enforced by this module (must never be weakened):
  paper_only             = True   (Literal — cannot be overridden)
  dry_run                = True   (Literal — cannot be overridden)
  live_orders_blocked    = True   (Literal — cannot be overridden)
  requires_human_review  = True   (Literal — cannot be overridden)
  execution_enabled      = False  (Literal — cannot be overridden)
  max_risk_pct           <= 1.0   (Schema constraint)
  stop_loss              required on PaperOrder and PaperPosition
  take_profit            required on PaperOrder and PaperPosition

Forbidden fields — these must NEVER appear in any schema in this module:
  order_id, fill_id, execution_id, broker_order_id, ibkr_order_id,
  mt5_ticket, account_id, broker_account_id, credential, secret,
  token, api_key, password.

No route is wired from this module.  No broker, MT5, IBKR, or any live
execution adapter is imported or referenced here.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ---------------------------------------------------------------------------
# Shared types
# ---------------------------------------------------------------------------

PaperDirection = Literal["BUY", "SELL"]
PaperOrderStatus = Literal["pending", "open", "closed", "cancelled", "rejected"]
PaperPositionStatus = Literal["open", "closed"]


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# PaperOrder
# ---------------------------------------------------------------------------


class PaperOrder(BaseModel):
    """A simulated paper order derived from a validated signal decision.

    This is NOT a real broker order.  It carries no broker order ID,
    execution ID, or any live-execution reference.  The ``paper_order_id``
    is a locally-scoped identifier only.

    Geometry invariants:
      BUY:  stop_loss  < entry_price  < take_profit
      SELL: take_profit < entry_price < stop_loss
    """

    model_config = ConfigDict(extra="forbid")

    # --- paper-scoped identity (never a broker/execution/account ID) ---
    paper_order_id: str = Field(default_factory=lambda: _new_id("po"), min_length=1)
    created_at: datetime = Field(default_factory=_now_utc)

    # --- trade parameters ---
    symbol: str = Field(..., min_length=1, max_length=16)
    direction: PaperDirection
    quantity: float = Field(..., gt=0)
    entry_price: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    take_profit: float = Field(..., gt=0)

    # --- risk ---
    max_risk_pct: float = Field(..., gt=0, le=1.0)

    # --- status ---
    status: PaperOrderStatus = "pending"

    # --- rejection reason (populated when status == "rejected") ---
    rejection_reason: str | None = None

    # --- safety flags (Literal — cannot be overridden by callers) ---
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    execution_enabled: Literal[False] = False

    @model_validator(mode="after")
    def _validate_sl_tp_geometry(self) -> "PaperOrder":
        if self.direction == "BUY":
            if self.stop_loss >= self.entry_price:
                raise ValueError(
                    "PaperOrder BUY: stop_loss must be strictly below entry_price"
                )
            if self.take_profit <= self.entry_price:
                raise ValueError(
                    "PaperOrder BUY: take_profit must be strictly above entry_price"
                )
        else:  # SELL
            if self.stop_loss <= self.entry_price:
                raise ValueError(
                    "PaperOrder SELL: stop_loss must be strictly above entry_price"
                )
            if self.take_profit >= self.entry_price:
                raise ValueError(
                    "PaperOrder SELL: take_profit must be strictly below entry_price"
                )
        return self


# ---------------------------------------------------------------------------
# PaperFill
# ---------------------------------------------------------------------------


class PaperFill(BaseModel):
    """A simulated fill event recording when a paper order was filled.

    This is NOT a real broker fill.  ``paper_fill_id`` is locally scoped —
    it is not a broker fill_id, execution_id, or any live-execution reference.
    """

    model_config = ConfigDict(extra="forbid")

    # --- paper-scoped identity ---
    paper_fill_id: str = Field(default_factory=lambda: _new_id("pf"), min_length=1)
    paper_order_ref: str = Field(..., min_length=1)
    fill_timestamp: datetime = Field(default_factory=_now_utc)

    # --- fill details ---
    symbol: str = Field(..., min_length=1, max_length=16)
    direction: PaperDirection
    fill_price: float = Field(..., gt=0)
    quantity: float = Field(..., gt=0)

    # --- safety flags ---
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    execution_enabled: Literal[False] = False


# ---------------------------------------------------------------------------
# PaperPosition
# ---------------------------------------------------------------------------


class PaperPosition(BaseModel):
    """An open (or closed) simulated paper position.

    Derived from a filled PaperOrder.  Carries the risk parameters (stop_loss,
    take_profit, max_risk_pct) for display and audit purposes.  The unrealised
    P&L field is simulation-only and carries no financial or accounting weight.
    """

    model_config = ConfigDict(extra="forbid")

    # --- paper-scoped identity ---
    paper_position_id: str = Field(
        default_factory=lambda: _new_id("pp"), min_length=1
    )
    paper_order_ref: str = Field(..., min_length=1)
    opened_at: datetime = Field(default_factory=_now_utc)
    closed_at: datetime | None = None

    # --- position details ---
    symbol: str = Field(..., min_length=1, max_length=16)
    direction: PaperDirection
    quantity: float = Field(..., gt=0)
    entry_price: float = Field(..., gt=0)
    current_price: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    take_profit: float = Field(..., gt=0)

    # --- simulated P&L (not real money) ---
    unrealized_pnl: float = 0.0

    # --- risk ---
    max_risk_pct: float = Field(..., gt=0, le=1.0)

    # --- status ---
    status: PaperPositionStatus = "open"

    # --- safety flags ---
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    execution_enabled: Literal[False] = False


# ---------------------------------------------------------------------------
# PaperDecisionPreviewOut
# ---------------------------------------------------------------------------


class PaperDecisionPreviewOut(BaseModel):
    """Response schema for GET /paper/decision/preview.

    All six safety flags are Literal constants — they can never be
    overridden by callers or the service layer.  ``preview_order`` is
    ``None`` when the decision is blocked; it is a full ``PaperOrder``
    object (paper-scoped, no broker fields) when the decision is allowed.

    No fills, positions, runs, DB writes, or broker calls are made.
    """

    model_config = ConfigDict(extra="forbid")

    allowed: bool
    reason: str

    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    execution_enabled: Literal[False] = False

    preview_order: PaperOrder | None = None


# ---------------------------------------------------------------------------
# PaperRun
# ---------------------------------------------------------------------------


class PaperRun(BaseModel):
    """A paper trading session — a named collection of orders, fills, and positions.

    A run groups all paper activity for a single simulation scenario.  It
    carries summary statistics and the full safety flag set.  Individual
    orders/positions/fills within a run each carry their own safety flags.
    """

    model_config = ConfigDict(extra="forbid")

    # --- run identity ---
    run_id: str = Field(default_factory=lambda: _new_id("run"), min_length=1)
    started_at: datetime = Field(default_factory=_now_utc)
    ended_at: datetime | None = None

    # --- summary statistics (simulation-only counts, no financial claims) ---
    total_signals: int = Field(default=0, ge=0)
    accepted_signals: int = Field(default=0, ge=0)
    rejected_signals: int = Field(default=0, ge=0)
    open_positions_count: int = Field(default=0, ge=0)
    closed_positions_count: int = Field(default=0, ge=0)

    # --- configured risk cap for this run ---
    max_risk_pct: float = Field(default=1.0, gt=0, le=1.0)

    # --- collections ---
    orders: List[PaperOrder] = Field(default_factory=list)
    positions: List[PaperPosition] = Field(default_factory=list)
    fills: List[PaperFill] = Field(default_factory=list)

    # --- safety flags ---
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    execution_enabled: Literal[False] = False
