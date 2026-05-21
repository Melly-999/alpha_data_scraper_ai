from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SignalQualityCounts(BaseModel):
    """Per-action and quality breakdown of scanned signals."""

    model_config = ConfigDict(extra="forbid")

    total_signals: int = Field(ge=0)
    watch_count: int = Field(ge=0)
    hold_count: int = Field(ge=0)
    long_setup_count: int = Field(ge=0)
    short_setup_count: int = Field(ge=0)
    no_trade_count: int = Field(ge=0)
    average_confidence: float = Field(ge=0.0, le=100.0)
    high_confidence_count: int = Field(ge=0)
    stale_count: int = Field(ge=0, default=0)
    fresh_count: int = Field(ge=0)
    risk_blocked_count: int = Field(ge=0)
    human_review_required_count: int = Field(ge=0)


class SignalQualityMetrics(BaseModel):
    """Aggregate quality assessment — advisory only."""

    model_config = ConfigDict(extra="forbid")

    label: Literal[
        "safe_fallback",
        "low",
        "moderate",
        "high",
    ] = "safe_fallback"
    score: float = Field(ge=0.0, le=100.0)
    confidence_band: Literal["low", "medium", "high"] = "low"
    freshness: Literal["fallback", "live", "stale"] = "fallback"
    risk_posture: Literal["blocked", "watch_only", "dry_run_only"] = "blocked"

    @field_validator("score")
    @classmethod
    def _score_ceiling(cls, v: float) -> float:
        if v > 100.0:
            raise ValueError("score must be <= 100.0")
        return v


class SignalQualitySummaryResponse(BaseModel):
    """Read-only advisory signal quality summary for the Terminal V1 dashboard.

    Aggregates scanner results into a quality snapshot.  All safety-critical
    fields are Literal-typed and cannot be weakened by callers.  No execution
    semantics, no broker routing, no order placement.
    """

    model_config = ConfigDict(extra="forbid")

    # Safety envelope — Literal-locked
    status: Literal["ok", "degraded"] = "ok"
    mode: Literal["read_only"] = "read_only"
    read_only: Literal[True] = True
    dry_run: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    execution_mode: Literal["dry_run_only"] = "dry_run_only"
    requires_human_review: Literal[True] = True
    risk_allowed: Literal[False] = False
    source: Literal["signal_quality_summary"] = "signal_quality_summary"

    # Payload
    summary: SignalQualityCounts
    quality: SignalQualityMetrics
    notes: list[str] = Field(
        default_factory=lambda: [
            "Read-only advisory signal quality summary.",
            "No order execution or broker routing is available.",
        ]
    )
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
