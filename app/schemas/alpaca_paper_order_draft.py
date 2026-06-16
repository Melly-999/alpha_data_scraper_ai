"""Alpaca Paper order DRAFT schemas.

ALPACA-PAPER-ORDER-DRAFT-001 — request/response models for the **local-only**
Alpaca paper order draft surface.

A draft validates user input and returns a structured draft object. It is
**never** submitted to Alpaca, never reaches a broker, and never executes.

Safety contract (always enforced; inherited from ``AlpacaPaperSafetyFlags`` plus
the draft-specific flags here):
- paper_only / dry_run / read_only / live_orders_blocked / requires_human_review
  are True; execution_enabled is False.
- order_submission_enabled is False and draft_only is True.
- No broker_order_id / execution_id / account_id / api_key / secret / token is
  ever represented. The ``draft_id`` is a local, deterministic, paper-scoped id
  (``paper-draft-*`` prefix) — not a broker order id.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.alpaca_paper import AlpacaPaperSafetyFlags

OrderType = Literal["market", "limit", "stop", "stop_limit"]
TimeInForce = Literal["day", "gtc", "ioc", "fok", "opg", "cls"]


class AlpacaPaperOrderDraftRequest(BaseModel):
    """Input for a local paper order draft.

    ``side`` / ``order_type`` / ``time_in_force`` are plain strings so invalid
    values are reported as a *blocked draft* (HTTP 200, ``valid=false``) rather
    than a validation error. Provide exactly one of ``quantity`` / ``notional``.
    ``entry_price`` / ``stop_loss`` / ``take_profit`` are required for the risk
    geometry check.
    """

    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1, max_length=32)
    side: str = Field(description="BUY or SELL")
    order_type: str = Field(
        default="market", description="market/limit/stop/stop_limit"
    )
    time_in_force: str = Field(default="day", description="day/gtc/ioc/fok/opg/cls")
    quantity: Optional[float] = Field(default=None, description="Share quantity")
    notional: Optional[float] = Field(default=None, description="Notional amount")
    entry_price: Optional[float] = Field(default=None, description="Reference price")
    stop_loss: Optional[float] = Field(default=None)
    take_profit: Optional[float] = Field(default=None)
    max_risk_pct: float = Field(description="Requested per-trade risk; capped at 1.0")


class AlpacaPaperOrderDraft(BaseModel):
    """A validated, local paper order draft. Not a broker order."""

    model_config = ConfigDict(extra="forbid")

    draft_id: str
    created_at: str
    symbol: str
    side: Literal["BUY", "SELL"]
    order_type: OrderType
    time_in_force: TimeInForce
    quantity: Optional[float] = None
    notional: Optional[float] = None
    entry_price: float
    stop_loss: float
    take_profit: float
    max_risk_pct: float
    status: Literal["draft"] = "draft"


class AlpacaPaperOrderDraftResponse(AlpacaPaperSafetyFlags):
    """Response for ``POST /api/alpaca-paper/order-draft``.

    ``valid=true`` with a ``draft`` on success, or ``valid=false`` with
    ``draft=null`` and a descriptive ``reason`` on validation failure (HTTP 200
    in both cases — a blocked draft is not an error).
    """

    model_config = ConfigDict(extra="forbid")

    valid: bool
    draft_only: Literal[True] = True
    order_submission_enabled: Literal[False] = False
    message: Literal["Draft only — not submitted to Alpaca."] = (
        "Draft only — not submitted to Alpaca."
    )
    reason: str
    draft: Optional[AlpacaPaperOrderDraft] = None
