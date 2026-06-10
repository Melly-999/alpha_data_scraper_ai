"""ALPACA-PAPER-ORDER-PREVIEW-003 — Schemas for GET /api/alpaca-paper/order-preview.

GET-only, paper-only, never-submitted Alpaca Paper order preview.

Safety constants that must never change in this module:
  paper_only             = True
  dry_run                = True
  read_only              = True
  live_orders_blocked    = True
  requires_human_review  = True
  execution_enabled      = False
  submitted              = False

Forbidden fields — must never appear in any schema in this module:
  account_id, broker_account_id, order_id, execution_id, broker_order_id,
  live_account, live_trading, autotrade, api_key, secret, token, password.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.alpaca_paper import AlpacaPaperSafetyFlags


class AlpacaPaperOrderPreviewOrder(BaseModel):
    """A paper-only, never-submitted Alpaca order preview.

    ``paper_order_id`` is a locally-generated paper-scoped identifier with
    the ``paper-alpaca-`` prefix.  It is NOT a broker order ID, fill ID,
    execution ID, account ID, or live Alpaca order ID.

    ``run_id`` uses the ``paper-alpaca-run-`` prefix and identifies the
    preview run this order belongs to.
    """

    model_config = ConfigDict(extra="forbid")

    # paper-scoped identity (no broker/account/execution IDs)
    paper_order_id: str = Field(min_length=1, max_length=160)
    run_id: str = Field(min_length=1, max_length=160)
    created_at: str  # ISO 8601 UTC

    # trade setup (no execution fields)
    symbol: str = Field(min_length=1, max_length=32)
    direction: Literal["BUY", "SELL"]
    quantity: float = Field(gt=0)
    entry_price: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    take_profit: float = Field(gt=0)
    max_risk_pct: float = Field(gt=0, le=1.0)
    status: Literal["preview"] = "preview"

    # Alpaca-paper-specific literals
    fill_type: Literal["simulated"] = "simulated"
    broker: Literal["alpaca-paper-demo"] = "alpaca-paper-demo"
    submitted: Literal[False] = False
    label: Literal["Preview only — not submitted"] = "Preview only — not submitted"

    # immutable safety contract
    paper_only: Literal[True] = True
    dry_run: Literal[True] = True
    read_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    requires_human_review: Literal[True] = True
    execution_enabled: Literal[False] = False


class AlpacaPaperOrderPreviewResponse(AlpacaPaperSafetyFlags):
    """Top-level response for GET /api/alpaca-paper/order-preview.

    Always includes all six safety flags, ``submitted=False``, ``label``,
    and ``broker``.  ``order`` is None when ``allowed=False`` (geometry or
    risk check blocked the preview).
    """

    allowed: bool
    reason: str = Field(min_length=1, max_length=2048)
    order: AlpacaPaperOrderPreviewOrder | None = None

    # top-level Alpaca-paper-specific literals
    submitted: Literal[False] = False
    label: Literal["Preview only — not submitted"] = "Preview only — not submitted"
    broker: Literal["alpaca-paper-demo"] = "alpaca-paper-demo"
