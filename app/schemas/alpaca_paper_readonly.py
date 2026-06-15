"""Alpaca Paper read-only adapter schemas.

ALPACA-PAPER-READONLY-ADAPTER-001 — sanitized, read-only preview models for the
optional Alpaca Paper read-only adapter.

Safety contract (always enforced, never overridable from the API surface):
- paper_only / dry_run / read_only / live_orders_blocked / requires_human_review
  are all True; execution_enabled is False (inherited from
  ``AlpacaPaperSafetyFlags``).
- order_placement_enabled is False.
- No credentials, API keys, account IDs, broker order IDs, or execution IDs are
  ever represented in these models.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.alpaca_paper import AlpacaPaperSafetyFlags


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AlpacaPaperReadOnlyPosition(BaseModel):
    """A single sanitized read-only paper position.

    Only display-safe fields are represented. No account_id, asset_id,
    broker_order_id, or execution_id is ever included.
    """

    model_config = ConfigDict(extra="forbid")

    symbol: str
    qty: float = 0.0
    market_value: float = 0.0
    unrealized_pl: float = 0.0
    side: Literal["long", "short", "unknown"] = "unknown"


class AlpacaPaperPositionsPreview(AlpacaPaperSafetyFlags):
    """GET-only sanitized positions preview for the Alpaca Paper read-only adapter.

    ``mode`` is ``paper_readonly`` when a read-only client (real paper or
    injected) is in use, or ``degraded_demo`` when running without credentials /
    read-only enablement. In both cases the safety flags above hold and no order
    placement is possible.
    """

    model_config = ConfigDict(extra="forbid")

    provider: Literal["alpaca_paper"] = "alpaca_paper"
    mode: Literal["paper_readonly", "degraded_demo"] = "degraded_demo"
    connected: bool = False
    order_placement_enabled: Literal[False] = False
    paper_simulated: Literal[True] = True
    redacted: Literal[True] = True
    source: Literal["alpaca_paper_readonly", "fallback"] = "fallback"
    count: int = 0
    positions: list[AlpacaPaperReadOnlyPosition] = Field(default_factory=list)
    last_updated: str = Field(default_factory=_utc_now_iso)
    note: str = (
        "Read-only Alpaca paper positions preview. No order placement, no "
        "execution, no credentials exposed."
    )
