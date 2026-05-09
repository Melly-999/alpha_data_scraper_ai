from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

AuditSeverity = Literal["info", "success", "warning", "error", "safety"]


class AuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    timestamp: datetime
    type: str
    severity: AuditSeverity
    source: str
    message: str
    read_only: bool = True
    # Optional, short, human-readable explanation of the safety implication
    # of this event (one sentence). The Terminal V1 UI surfaces it next to
    # the message so operators can see *why* an event matters for safety
    # without inferring it from the type slug. Optional and nullable for
    # backwards compatibility — older callers and existing fixtures can
    # omit it.
    safety_note: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditEventFeedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool = True
    auto_trade: bool = False
    read_only: bool = True
    events: list[AuditEvent]
    degraded: bool
    fallback: bool
    generated_at: datetime


# --- Daily Trading Plan Preview (Task 4) -----------------------------------
#
# Read-only planning context for Terminal V1. Display-only: this is *not* a
# trading signal, *not* an order intent, and *not* a recommendation to
# execute. The schema deliberately omits any execution-shaped fields
# (quantity, lot size, order id, sl_pips, tp_pips, broker reference) so the
# response cannot be mistaken for an order ticket.

PlanBias = Literal["bullish", "bearish", "neutral", "wait"]
PlanRiskTier = Literal["low", "medium", "high"]
PlanSetupQuality = Literal["low", "medium", "high"]


class TradingPlanItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instrument: str
    bias: PlanBias
    setup_quality: PlanSetupQuality
    risk_tier: PlanRiskTier
    no_trade_condition: str
    setup_area: str | None = None
    notes: str | None = None


class TradingPlanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Safety preamble — mirrors AuditEventFeedResponse so frontend code can
    # treat them uniformly.
    dry_run: bool = True
    auto_trade: bool = False
    read_only: bool = True
    # Hard upper bound the planner displays for the operator. Never raised
    # by this endpoint — just reported. Keep at 1.0 to match the
    # repo-wide invariant enforced by tests/app/test_safety_invariants.py.
    max_risk_per_trade_pct: float = 1.0
    # Free-form one-line label so the UI can stamp "READ-ONLY PLAN PREVIEW"
    # over the card without hardcoding a string in the React tree.
    label: str = "READ-ONLY PLAN PREVIEW — NO ORDERS PLACED"
    items: list[TradingPlanItem]
    generated_at: datetime
