"""MOBILE-AI-006 — Tests for the Mobile AI typed schemas.

Schema-only contract tests: confirm valid construction, that safety flags
are Literal-locked (cannot be weakened), that the 1% risk ceiling holds, and
that unknown fields are rejected (extra="forbid").

Payloads are built as dicts and unpacked with ``**`` (matching the existing
schema-test convention) so that string values are coerced to enums by
Pydantic at runtime.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.mobile_ai import (
    ChartAnalysisResult,
    FomoGuardState,
    JournalEntry,
    PaperGamePlan,
    RiskAssessment,
    WeeklyReview,
)

# ---------------------------------------------------------------------------
# Payload builders
# ---------------------------------------------------------------------------


def _chart_analysis(**overrides) -> dict:
    base = dict(
        instrument="XAUUSD",
        timeframe="M15",
        trading_style="Intraday / paper only",
        market_bias="Neutral-Bullish",
        trend="Bullish short-term",
        key_levels=["Support 2,318-2,322", "Resistance 2,341-2,346"],
        momentum="Improving",
        volatility="High",
        pattern="Retest continuation candidate",
        confirmation_checklist=["M15 close confirms", "Retest holds"],
    )
    base.update(overrides)
    return base


def _paper_game_plan(**overrides) -> dict:
    base = dict(
        scenario="Long only if confirmed",
        entry_zone="2,322 - 2,326",
        invalidation="M15 candle close below 2,316",
        take_profit_1="2,341",
        take_profit_2="2,352",
        max_risk_per_trade_pct=1.0,
    )
    base.update(overrides)
    return base


def _risk_assessment(**overrides) -> dict:
    base = dict(
        safety_score=82,
        risk_per_trade_pct=1.0,
        stop_loss_present=True,
        take_profit_present=True,
        overtrading_risk="Medium",
        news_risk="High",
    )
    base.update(overrides)
    return base


def _journal_entry(**overrides) -> dict:
    base = dict(
        instrument="XAUUSD",
        timeframe="M15",
        setup="Retest continuation",
        bias="Neutral-Bullish",
        risk_pct=0.5,
        status="Pending review",
        emotion_tag="Calm",
        plan="Wait for retest confirmation",
        outcome="Not reviewed yet",
    )
    base.update(overrides)
    return base


def _fomo_guard(**overrides) -> dict:
    base = dict(
        active=True,
        repeated_analysis_count=4,
        cooldown_minutes=15,
        recommendation="Wait for the next M15 candle close before reviewing again.",
        repeated_analysis="High",
        candle_close_discipline="Medium",
        news_risk_awareness="High",
        overtrading_risk="Medium",
    )
    base.update(overrides)
    return base


def _weekly_review(**overrides) -> dict:
    base = dict(
        best_setup="Retest continuation",
        best_behavior="Waited for candle close",
        mistake_avoided="Breakout fakeout",
        highest_risk_pattern="Analyzing same asset repeatedly",
        next_focus="Fewer low-quality analyses, more confirmed retests",
        discipline_score=78,
        overtrading_risk="Medium",
        review_completion="7/10",
        paper_only_compliance_pct=100,
    )
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Valid construction
# ---------------------------------------------------------------------------


def test_chart_analysis_result_valid() -> None:
    result = ChartAnalysisResult(**_chart_analysis())
    assert result.analysis_only is True
    assert result.not_financial_advice is True
    assert result.disclaimer == "Analysis only. Not financial advice."


def test_paper_game_plan_valid() -> None:
    plan = PaperGamePlan(**_paper_game_plan())
    assert plan.status == "PAPER_ONLY"
    assert plan.paper_only is True
    assert plan.live_orders_blocked is True
    assert plan.broker_execution is False
    assert plan.requires_human_review is True


def test_risk_assessment_valid() -> None:
    risk = RiskAssessment(**_risk_assessment())
    assert risk.human_review_required is True
    assert risk.paper_only is True


def test_journal_entry_valid() -> None:
    entry = JournalEntry(**_journal_entry())
    assert entry.paper_only is True
    assert entry.status.value == "Pending review"


def test_fomo_guard_state_valid() -> None:
    state = FomoGuardState(**_fomo_guard())
    assert state.executes_trades is False
    assert state.paper_only is True
    assert state.behavior_feedback_only is True


def test_weekly_review_valid() -> None:
    review = WeeklyReview(**_weekly_review())
    assert review.paper_only is True
    assert review.paper_only_compliance_pct == 100


# ---------------------------------------------------------------------------
# Safety locks cannot be weakened
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "field,value",
    [
        ("paper_only", False),
        ("live_orders_blocked", False),
        ("broker_execution", True),
        ("requires_human_review", False),
    ],
)
def test_paper_game_plan_safety_flags_locked(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        PaperGamePlan(**_paper_game_plan(**{field: value}))


def test_fomo_guard_cannot_execute_trades() -> None:
    with pytest.raises(ValidationError):
        FomoGuardState(**_fomo_guard(executes_trades=True))


# ---------------------------------------------------------------------------
# Risk ceiling (<= 1%)
# ---------------------------------------------------------------------------


def test_paper_game_plan_rejects_risk_above_one_percent() -> None:
    with pytest.raises(ValidationError):
        PaperGamePlan(**_paper_game_plan(max_risk_per_trade_pct=1.5))


def test_risk_assessment_rejects_risk_above_one_percent() -> None:
    with pytest.raises(ValidationError):
        RiskAssessment(**_risk_assessment(risk_per_trade_pct=2.0))


def test_journal_entry_rejects_risk_above_one_percent() -> None:
    with pytest.raises(ValidationError):
        JournalEntry(**_journal_entry(risk_pct=5.0))


# ---------------------------------------------------------------------------
# extra="forbid"
# ---------------------------------------------------------------------------


def test_unknown_fields_rejected() -> None:
    with pytest.raises(ValidationError):
        RiskAssessment(**_risk_assessment(execute_now=True))
