"""Alpaca Paper order SUBMIT SANDBOX schemas.

ALPACA-PAPER-ORDER-SUBMIT-SANDBOX-001 — request/response models for the
**backend-only, multi-gated, paper-only** order submission sandbox.

This surface can submit a single small order to Alpaca **Paper** only when every
explicit gate is satisfied. It is **not** live trading, **not** frontend UX, and
**not** autotrading. It is blocked by default.

Safety semantics encoded in the response:
- ``paper_only=true``, ``live_trading=false``, ``live_orders_blocked=true``,
  ``dry_run=true``, ``read_only_posture_preserved=true``,
  ``execution_enabled=false`` (no *live* execution), ``requires_human_review=true``.
- A submitted **paper** order does not change the global dry-run / live-orders
  posture: paper submission is a separate, manually-gated sandbox path.
- No ``account_id`` / raw ``broker_order_id`` / ``api_key`` / ``secret`` /
  ``token`` is ever represented. Only a redacted order id is returned.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class AlpacaPaperOrderSubmitSandboxRequest(BaseModel):
    """Input for a gated paper order submission attempt.

    ``side`` / ``order_type`` / ``time_in_force`` / ``source`` are plain strings
    so invalid values are reported as a blocked response (HTTP 200) rather than a
    parse error. Provide exactly one of ``quantity`` / ``notional``.
    ``entry_price`` / ``stop_loss`` / ``take_profit`` are required (risk geometry
    is validated even though only the entry order is submitted — no bracket/OCO).
    """

    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1, max_length=32)
    side: str = Field(description="BUY or SELL")
    order_type: str = Field(default="market", description="market or limit")
    time_in_force: str = Field(default="day", description="day/gtc/ioc/fok/opg/cls")
    quantity: Optional[float] = Field(default=None)
    notional: Optional[float] = Field(default=None)
    limit_price: Optional[float] = Field(
        default=None, description="Required only for order_type=limit"
    )
    entry_price: Optional[float] = Field(default=None, description="Reference price")
    stop_loss: Optional[float] = Field(default=None)
    take_profit: Optional[float] = Field(default=None)
    max_risk_pct: float = Field(description="Per-trade risk; capped at 1.0")
    confirm_paper_order: bool = Field(
        default=False, description="Must be true to attempt a paper submission"
    )
    source: str = Field(
        default="", description='Must be "manual_sandbox" to attempt submission'
    )
    client_order_id_prefix: Optional[str] = Field(
        default=None, max_length=32, description="Optional safe prefix for our id"
    )
    dry_run_preview_only: bool = Field(
        default=False,
        description="If true, exercise all gates but never submit (no Alpaca call)",
    )


class AlpacaPaperOrderSubmitSandboxResponse(BaseModel):
    """Result of a gated paper order submission attempt."""

    model_config = ConfigDict(extra="forbid")

    accepted: bool
    submitted_to_alpaca_paper: bool = False
    blocked_reason: Optional[str] = None

    # Safety posture — locked.
    paper_only: Literal[True] = True
    live_trading: Literal[False] = False
    live_orders_blocked: Literal[True] = True
    dry_run: Literal[True] = True
    read_only_posture_preserved: Literal[True] = True
    execution_enabled: Literal[False] = False
    requires_human_review: Literal[True] = True

    # Whether submission was actually enabled (all gates satisfied).
    order_submission_enabled: bool = False

    # Redacted identifiers only — never a raw broker order id / account id.
    redacted_order_id: Optional[str] = None
    client_order_id: Optional[str] = None
    order_status: Optional[str] = None

    message: str = (
        "Paper sandbox only — blocked by default; submits to Alpaca Paper only "
        "when every explicit gate is satisfied. Not live trading."
    )
