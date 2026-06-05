"""MOBILE-AI-006 — Mobile AI typed schemas (paper-only, analysis-only).

These Pydantic models describe the data contract behind the frontend-only
Mobile AI mock surface (`/mobile`): AI chart review, paper game plan, risk
assessment, setup journal, FOMO guard, and weekly review.

They are *schemas only*. This module:
  * defines no API routes / endpoints,
  * performs no AI provider calls,
  * performs no database / persistence writes,
  * carries no execution intent and cannot represent a live order.

Safety constants that must never change in this module:
  analysis_only          = True
  paper_only             = True
  read_only              = True
  live_orders_blocked    = True
  broker_execution       = False
  requires_human_review  = True
  max_risk_per_trade_pct <= 1.0

Every model uses ``extra="forbid"`` so callers cannot smuggle extra fields,
and all safety flags are ``Literal``-locked so they cannot be weakened.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Shared disclaimer used across mobile AI payloads.
ANALYSIS_DISCLAIMER = "Analysis only. Not financial advice."


class MarketBias(str, Enum):
    NEUTRAL = "Neutral"
    NEUTRAL_BULLISH = "Neutral-Bullish"
    NEUTRAL_BEARISH = "Neutral-Bearish"
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    MIXED = "Mixed"
    VOLATILE = "Volatile"
    RANGE = "Range"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class OutcomeStatus(str, Enum):
    PENDING_REVIEW = "Pending review"
    TP1 = "TP1"
    TP2 = "TP2"
    SL = "SL"
    SKIPPED = "Skipped"
    INVALIDATED = "Invalidated"
    STILL_WAITING = "Still waiting"


class _MobileAIBase(BaseModel):
    """Base config: reject unknown fields on every mobile AI model."""

    model_config = ConfigDict(extra="forbid")


class ChartAnalysisResult(_MobileAIBase):
    """AI chart review output (analysis only, no trading instruction)."""

    instrument: str = Field(min_length=1, max_length=32)
    timeframe: str = Field(min_length=1, max_length=8)
    trading_style: str = Field(min_length=1, max_length=64)
    market_bias: MarketBias
    trend: str = Field(min_length=1, max_length=64)
    key_levels: list[str] = Field(default_factory=list)
    momentum: str = Field(min_length=1, max_length=64)
    volatility: RiskLevel
    pattern: str = Field(min_length=1, max_length=128)
    confirmation_checklist: list[str] = Field(default_factory=list)

    # Safety locks
    analysis_only: Literal[True] = True
    not_financial_advice: Literal[True] = True
    disclaimer: str = ANALYSIS_DISCLAIMER


class PaperGamePlan(_MobileAIBase):
    """Paper / simulation-only game plan. Cannot place or route an order."""

    scenario: str = Field(min_length=1, max_length=256)
    entry_zone: str = Field(min_length=1, max_length=128)
    invalidation: str = Field(min_length=1, max_length=256)
    take_profit_1: str = Field(min_length=1, max_length=64)
    take_profit_2: str | None = Field(default=None, max_length=64)
    max_risk_per_trade_pct: float = Field(default=1.0, ge=0.0, le=1.0)

    # Safety locks
    status: Literal["PAPER_ONLY"] = "PAPER_ONLY"
    paper_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    broker_execution: Literal[False] = False
    requires_human_review: Literal[True] = True

    @field_validator("max_risk_per_trade_pct")
    @classmethod
    def _max_risk_ceiling(cls, v: float) -> float:
        if v > 1.0:
            raise ValueError("max_risk_per_trade_pct must be <= 1.0")
        return v


class RiskAssessment(_MobileAIBase):
    """Behavior / risk summary for a reviewed setup (display only)."""

    safety_score: int = Field(ge=0, le=100)
    risk_per_trade_pct: float = Field(ge=0.0, le=1.0)
    stop_loss_present: bool
    take_profit_present: bool
    overtrading_risk: RiskLevel
    news_risk: RiskLevel

    # Safety locks
    human_review_required: Literal[True] = True
    paper_only: Literal[True] = True

    @field_validator("risk_per_trade_pct")
    @classmethod
    def _risk_ceiling(cls, v: float) -> float:
        if v > 1.0:
            raise ValueError("risk_per_trade_pct must be <= 1.0")
        return v


class JournalEntry(_MobileAIBase):
    """Saved setup journal entry (review/learning record, not an order)."""

    instrument: str = Field(min_length=1, max_length=32)
    timeframe: str = Field(min_length=1, max_length=8)
    setup: str = Field(min_length=1, max_length=128)
    bias: MarketBias
    risk_pct: float = Field(ge=0.0, le=1.0)
    status: OutcomeStatus
    emotion_tag: str = Field(min_length=1, max_length=64)
    plan: str = Field(min_length=1, max_length=256)
    outcome: str = Field(min_length=1, max_length=256)

    # Safety locks
    paper_only: Literal[True] = True

    @field_validator("risk_pct")
    @classmethod
    def _risk_ceiling(cls, v: float) -> float:
        if v > 1.0:
            raise ValueError("risk_pct must be <= 1.0")
        return v


class FomoGuardState(_MobileAIBase):
    """FOMO guard behavior-feedback state (does not execute trades)."""

    active: bool
    repeated_analysis_count: int = Field(ge=0)
    cooldown_minutes: int = Field(ge=0)
    recommendation: str = Field(min_length=1, max_length=256)
    repeated_analysis: RiskLevel
    candle_close_discipline: RiskLevel
    news_risk_awareness: RiskLevel
    overtrading_risk: RiskLevel

    # Safety locks
    executes_trades: Literal[False] = False
    paper_only: Literal[True] = True
    behavior_feedback_only: Literal[True] = True


class WeeklyReview(_MobileAIBase):
    """Weekly learning / coach summary (display only)."""

    best_setup: str = Field(min_length=1, max_length=128)
    best_behavior: str = Field(min_length=1, max_length=128)
    mistake_avoided: str = Field(min_length=1, max_length=128)
    highest_risk_pattern: str = Field(min_length=1, max_length=128)
    next_focus: str = Field(min_length=1, max_length=256)
    discipline_score: int = Field(ge=0, le=100)
    overtrading_risk: RiskLevel
    review_completion: str = Field(min_length=1, max_length=16)
    paper_only_compliance_pct: int = Field(ge=0, le=100)

    # Safety locks
    paper_only: Literal[True] = True


class ScreenshotAnalysisPreview(_MobileAIBase):
    """Analysis-only preview returned by the screenshot upload endpoint.

    Wraps the existing chart-review, paper-plan, and risk schemas and echoes
    the locked safety posture. The uploaded image is never stored and no AI
    provider is called: ``stored`` and ``provider_used`` are Literal-locked to
    ``False``. This payload carries no execution intent.
    """

    chart_analysis: ChartAnalysisResult
    paper_game_plan: PaperGamePlan
    risk_assessment: RiskAssessment

    # Echoed / locked safety posture
    analysis_only: Literal[True] = True
    paper_only: Literal[True] = True
    live_orders_blocked: Literal[True] = True
    broker_execution: Literal[False] = False
    requires_human_review: Literal[True] = True
    stored: Literal[False] = False
    provider_used: Literal[False] = False
    disclaimer: str = ANALYSIS_DISCLAIMER
