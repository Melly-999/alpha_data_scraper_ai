from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import BlockedReason, ClaudeStatus, DataSource, Direction


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
    score: int | None = None
    inputs: list[str] = Field(default_factory=list)


class SignalProvenance(BaseModel):
    market_data_source: DataSource
    signal_source: DataSource
    validation_source: str
    confidence_source: str
    fallback: bool
    generated_at: datetime
    cache_age_seconds: int = 0


class SignalDetail(SignalSummary):
    reasoning: str
    technicals: Technicals
    timeframes: dict[str, str]
    risk_gate_results: list[RiskGateResult] = Field(default_factory=list)
    technical_input_summary: list[str] = Field(default_factory=list)
    confidence_explainer: str | None = None
    ai_validation_status: str | None = None
    provenance: SignalProvenance


class SignalReasoning(BaseModel):
    signal_id: str
    reasoning: str
    technical_factors: list[str]
    sentiment_context: str | None = None
    claude_response: str | None = None
    risk_gate_results: list[RiskGateResult]
    blocked_reason: BlockedReason | None = None
    eligible: bool
    confidence_explainer: str | None = None
    provenance: SignalProvenance
