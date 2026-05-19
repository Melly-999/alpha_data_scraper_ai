"""PDS-001 — Paper-only TradeTicket schema.

Trade tickets are advisory paper-only drafts used for decision support.
They carry no execution intent and cannot trigger live orders, broker calls,
MT5/IBKR routing, or any order-placement mechanism.

Safety constants that must never change in this module:
  paper_only             = True
  dry_run                = True
  read_only              = True
  live_orders_blocked    = True
  requires_human_review  = True
  broker_execution_allowed = False
  risk_allowed           = False
  execution_mode         = "paper_only_draft"
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TradeSide(str, Enum):
    long = "long"
    short = "short"


class EntryType(str, Enum):
    market_simulated = "market_simulated"
    limit_retest = "limit_retest"
    breakout = "breakout"
    pullback = "pullback"
    manual = "manual"


class TicketStatus(str, Enum):
    draft = "draft"
    validated = "validated"
    rejected = "rejected"


class RiskValidationStatus(str, Enum):
    not_checked = "not_checked"
    passed = "passed"
    failed = "failed"


class TradeTicketDraft(BaseModel):
    """Paper-only trade ticket draft for decision support.

    This schema cannot represent a live order.  All safety fields are
    hard-coded to their required values and will raise ValidationError if
    any caller attempts to override them.
    """

    model_config = ConfigDict(extra="forbid")

    # --- identity ---
    ticket_id: str = Field(min_length=1, max_length=128)
    symbol: str = Field(min_length=1, max_length=32)

    # --- trade intent ---
    side: TradeSide
    entry_type: EntryType
    timeframe: str = Field(min_length=1, max_length=8)
    entry_price: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    take_profit_1: float = Field(gt=0)
    take_profit_2: float | None = Field(default=None, gt=0)

    # --- risk metrics ---
    risk_pct: float = Field(gt=0, le=1.0)
    confidence: float = Field(ge=0, le=100)

    # --- narrative ---
    reason: str = Field(min_length=1, max_length=1024)
    setup_notes: str | None = None

    # --- provenance ---
    scanner_signal_id: str | None = None
    source: str = "manual_or_scanner"
    status: TicketStatus = TicketStatus.draft
    risk_validation_status: RiskValidationStatus = RiskValidationStatus.not_checked

    # --- immutable safety contract ---
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    risk_allowed: Literal[False] = False
    broker_execution_allowed: Literal[False] = False
    execution_mode: Literal["paper_only_draft"] = "paper_only_draft"

    # ------------------------------------------------------------------
    # Field validators
    # ------------------------------------------------------------------

    @field_validator("symbol")
    @classmethod
    def _normalise_symbol(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("symbol must not be blank")
        return stripped.upper()

    @field_validator("timeframe")
    @classmethod
    def _require_timeframe(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("timeframe must not be blank")
        return stripped

    @field_validator("reason")
    @classmethod
    def _require_reason(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("reason must not be blank")
        return stripped

    # ------------------------------------------------------------------
    # Cross-field geometry validator (long/short price relationships)
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_price_geometry(self) -> TradeTicketDraft:
        side = self.side
        entry = self.entry_price
        sl = self.stop_loss
        tp1 = self.take_profit_1
        tp2 = self.take_profit_2

        if side == TradeSide.long:
            if sl >= entry:
                raise ValueError(
                    "long setup: stop_loss must be below entry_price"
                )
            if tp1 <= entry:
                raise ValueError(
                    "long setup: take_profit_1 must be above entry_price"
                )
            if tp2 is not None and tp2 <= entry:
                raise ValueError(
                    "long setup: take_profit_2 must be above entry_price"
                )
        else:  # short
            if sl <= entry:
                raise ValueError(
                    "short setup: stop_loss must be above entry_price"
                )
            if tp1 >= entry:
                raise ValueError(
                    "short setup: take_profit_1 must be below entry_price"
                )
            if tp2 is not None and tp2 >= entry:
                raise ValueError(
                    "short setup: take_profit_2 must be below entry_price"
                )

        return self
