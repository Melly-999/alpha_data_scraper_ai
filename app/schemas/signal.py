from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import BlockedReason, ClaudeStatus, Direction


class RiskGateResult(BaseModel):
    gate: str
    passed: bool
    value: float | int | str | None = None
    threshold: float | int | str | None = None
    remaining_seconds: int | None = None
    detail: str | None = None


class SignalSummary(BaseModel):
    id: str
    symbol: str
    direction: Direction
    confidence: int
    mtf_alignment: int
    mtf_total: int
    sentiment_score: float | None = None
    claude_status: ClaudeStatus
    regime: str
    sl: float | None = None
    tp: float | None = None
    entry: float | None = None
    rr: float | None = None
    eligible: bool
    blocked: bool
    blocked_reason: BlockedReason | None = None
    cooldown_remaining: int | None = None
    timestamp: datetime


class Technicals(BaseModel):
    rsi: float | None = None
    macd: str | None = None
    atr: float | None = None
    ema20: float | None = None
    ema50: float | None = None


class SignalDetail(SignalSummary):
    reasoning: str
    technicals: Technicals
    timeframes: dict[str, str]
    risk_gate_results: list[RiskGateResult] = Field(default_factory=list)


class SignalReasoning(BaseModel):
    signal_id: str
    reasoning: str
    technical_factors: list[str]
    sentiment_context: str | None = None
    claude_response: str | None = None
    risk_gate_results: list[RiskGateResult]
