from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PortfolioRiskExposure(BaseModel):
    """Snapshot of current paper/read-only portfolio exposure — advisory only."""

    model_config = ConfigDict(extra="forbid")

    total_positions: int = Field(ge=0)
    open_positions: int = Field(ge=0)
    total_notional: float = Field(ge=0.0)
    gross_exposure_pct: float = Field(ge=0.0, le=100.0)
    net_exposure_pct: float = Field(ge=0.0, le=100.0)
    cash_buffer_pct: float = Field(ge=0.0, le=100.0)


class PortfolioRiskLimits(BaseModel):
    """Advisory risk limits — read-only display, no execution surface."""

    model_config = ConfigDict(extra="forbid")

    max_risk_per_trade_pct: float = Field(ge=0.0, le=1.0)
    max_portfolio_risk_pct: float = Field(ge=0.0, le=5.0)
    risk_used_pct: float = Field(ge=0.0)
    remaining_risk_capacity_pct: float = Field(ge=0.0)
    max_open_positions: int = Field(ge=0)


class PortfolioRiskPosture(BaseModel):
    """Safety posture snapshot — all execution fields are hard-blocked."""

    model_config = ConfigDict(extra="forbid")

    label: Literal["safe_fallback", "read_only", "risk_blocked", "dry_run_only"] = (
        "dry_run_only"
    )
    status: Literal["ok", "degraded"] = "ok"
    broker_execution_allowed: Literal[False] = False
    live_orders_blocked: Literal[True] = True
    risk_allowed: Literal[False] = False
    requires_human_review: Literal[True] = True


class PortfolioRiskSummaryResponse(BaseModel):
    """
    GET-only advisory portfolio risk summary response.

    All Literal safety fields are hard-typed to prevent drift.
    This endpoint never executes orders, calls brokers, or mutates state.
    """

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "degraded"] = "ok"
    mode: Literal["read_only"] = "read_only"
    read_only: Literal[True] = True
    dry_run: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    execution_mode: Literal["dry_run_only"] = "dry_run_only"
    requires_human_review: Literal[True] = True
    risk_allowed: Literal[False] = False
    source: Literal["portfolio_risk_summary"] = "portfolio_risk_summary"
    exposure: PortfolioRiskExposure
    limits: PortfolioRiskLimits
    posture: PortfolioRiskPosture
    notes: list[str] = Field(
        default_factory=lambda: [
            "Read-only portfolio risk summary.",
            "No order execution or broker routing is available.",
            "Risk capacity is advisory and dry-run only.",
        ]
    )
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
