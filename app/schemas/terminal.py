from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

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


# --- Terminal Summary (API-001) -------------------------------------------
#
# Read-only terminal summary for the Terminal V1 dashboard. Matches the
# TerminalSummary TypeScript type in frontend/src/lib/terminalApi.ts so the
# frontend receives a shape-compatible response instead of a 404 fallback.
# All safety fields are Literal so response_model validation enforces them.


class TerminalSafetyState(BaseModel):
    """Mirrors the frontend SafetyState type. All fields are locked Literals."""

    model_config = ConfigDict(extra="forbid")

    read_only: Literal[True] = True
    dry_run: Literal[True] = True
    auto_trade: Literal[False] = False
    live_orders_blocked: Literal[True] = True


class TerminalBrokerPermissions(BaseModel):
    """Read-only IBKR Paper adapter permission map. Orders/execution always denied."""

    model_config = ConfigDict(extra="forbid")

    market_data: Literal["allowed"] = "allowed"
    account_read: Literal["allowed"] = "allowed"
    positions_read: Literal["allowed"] = "allowed"
    orders: Literal["denied"] = "denied"
    live_execution: Literal["denied"] = "denied"


class TerminalBrokerStatus(BaseModel):
    """Mirrors the frontend IBKRStatus type. Execution is always disabled."""

    model_config = ConfigDict(extra="forbid")

    name: Literal["IBKR Paper"] = "IBKR Paper"
    status: Literal["connected", "disconnected", "degraded", "paper", "read-only"] = (
        "degraded"
    )
    read_only: Literal[True] = True
    execution_enabled: Literal[False] = False
    data_freshness: str = "safe-degraded"
    latency_ms: int = 0
    diagnostics: list[str] = Field(default_factory=list)
    permissions: TerminalBrokerPermissions = Field(
        default_factory=TerminalBrokerPermissions
    )

    @field_validator("latency_ms")
    @classmethod
    def _non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("latency_ms must be >= 0")
        return v


class TerminalSummaryResponse(BaseModel):
    """Response schema for GET /terminal/summary.

    Advisory-only, read-only. No execution semantics, no broker calls,
    no order routing. Matches the TerminalSummary TypeScript type so
    the frontend receives a valid shape instead of returning the local
    fallback.
    """

    model_config = ConfigDict(extra="forbid")

    terminal: str = "MellyTrade V1 Terminal"
    mode: Literal["read-only"] = "read-only"
    backend: Literal["online", "fallback"] = "fallback"
    safety: TerminalSafetyState = Field(default_factory=TerminalSafetyState)
    broker: TerminalBrokerStatus = Field(default_factory=TerminalBrokerStatus)
    updated_at: datetime
