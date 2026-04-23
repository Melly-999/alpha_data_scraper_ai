from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

from app.schemas.common import (
    BlockedReason,
    ClaudeStatus,
    Direction,
    LogCategory,
    Severity,
)
from app.schemas.signal import SignalDetail, SignalReasoning, SignalSummary, Technicals
from app.services.account_service import AccountService
from app.services.fixture_data import prototype_signals
from app.services.log_service import LogService
from app.services.risk_service import RiskService

if TYPE_CHECKING:
    from ai_engine import AIEngine


@dataclass(frozen=True)
class ServiceDependencies:
    claude_available: bool
    news_available: bool


class SignalService:
    def __init__(
        self,
        *,
        risk_service: RiskService,
        log_service: LogService,
        account_service: AccountService,
        dependencies: ServiceDependencies,
    ) -> None:
        self._risk_service = risk_service
        self._log_service = log_service
        self._account_service = account_service
        self._dependencies = dependencies

    @property
    def fallback_mode(self) -> bool:
        return not self._dependencies.news_available

    def _build_engine(self) -> "AIEngine":
        from ai_engine import AIEngine, EngineConfig

        return AIEngine(
            EngineConfig(
                symbols=["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
                timeframe="M5",
                bars=120,
                use_news_sentiment=self._dependencies.news_available,
                min_confidence_threshold=self._risk_service.get_config().min_confidence,
                update_interval_seconds=60,
            )
        )

    def _fallback_details(self) -> list[SignalDetail]:
        details: list[SignalDetail] = []
        open_positions = len(self._account_service.get_open_positions())
        for item in prototype_signals():
            signal_id = str(item["id"])
            symbol = str(item["symbol"])
            direction = str(item["direction"])
            confidence = int(cast(int, item["confidence"]))
            timestamp = cast(datetime, item["timestamp"])
            sl = cast(float | None, item.get("sl"))
            tp = cast(float | None, item.get("tp"))
            rr = cast(float | None, item.get("rr"))
            entry = cast(float | None, item.get("entry"))
            sentiment_score_raw = item.get("sentiment_score")
            sentiment_score = (
                float(cast(float, sentiment_score_raw))
                if sentiment_score_raw is not None
                else None
            )
            allowed, blocked_reason, cooldown_remaining, gate_results = (
                self._risk_service.evaluate_signal(
                    signal_id=signal_id,
                    symbol=symbol,
                    direction=direction,
                    confidence=confidence,
                    sl=sl,
                    tp=tp,
                    rr=rr,
                    timestamp=timestamp,
                    open_positions=open_positions,
                    register=False,
                )
            )
            if item["blocked_reason"] is not None:
                allowed = bool(cast(bool, item["eligible"]))
                blocked_reason = BlockedReason(str(item["blocked_reason"]))
                cooldown_remaining = (
                    int(cast(int, item["cooldown_remaining"]))
                    if item["cooldown_remaining"] is not None
                    else None
                )
            detail = SignalDetail(
                id=signal_id,
                symbol=symbol,
                direction=Direction(direction),
                confidence=max(33, min(confidence, 85)),
                mtf_alignment=int(cast(int, item["mtf_alignment"])),
                mtf_total=int(cast(int, item["mtf_total"])),
                sentiment_score=sentiment_score,
                claude_status=ClaudeStatus(str(item["claude_status"])),
                regime=str(item["regime"]),
                sl=sl,
                tp=tp,
                entry=entry,
                rr=rr,
                eligible=allowed,
                blocked=not allowed,
                blocked_reason=blocked_reason,
                cooldown_remaining=cooldown_remaining,
                timestamp=timestamp,
                reasoning=str(item["reasoning"]),
                technicals=Technicals.model_validate(
                    cast(dict[str, Any], item["technicals"])
                ),
                timeframes={
                    str(key): str(value)
                    for key, value in cast(dict[str, Any], item["timeframes"]).items()
                },
                risk_gate_results=gate_results,
            )
            details.append(detail)
        return details

    def _overlay_engine_data(self, details: list[SignalDetail]) -> list[SignalDetail]:
        try:
            engine = self._build_engine()
            signals = engine.analyze_all()
        except Exception as exc:
            self._log_service.add(
                category=LogCategory.SIGNALS,
                severity=Severity.WARN,
                message=f"AIEngine unavailable for API contract, using fallback signals: {exc}",
            )
            return details

        by_symbol = {detail.symbol: detail for detail in details}
        open_positions = len(self._account_service.get_open_positions())
        for symbol, signal in signals.items():
            if symbol not in by_symbol:
                continue
            confidence = max(33, min(int(round(signal.primary_confidence)), 85))
            existing = by_symbol[symbol]
            allowed, blocked_reason, cooldown_remaining, gate_results = (
                self._risk_service.evaluate_signal(
                    signal_id=existing.id,
                    symbol=symbol,
                    direction=signal.primary_signal,
                    confidence=confidence,
                    sl=existing.sl,
                    tp=existing.tp,
                    rr=existing.rr,
                    timestamp=signal.timestamp,
                    open_positions=open_positions,
                    register=False,
                )
            )
            by_symbol[symbol] = existing.model_copy(
                update={
                    "direction": Direction(signal.primary_signal),
                    "confidence": confidence,
                    "sentiment_score": getattr(
                        signal.sentiment_score,
                        "average_sentiment",
                        existing.sentiment_score,
                    ),
                    "claude_status": (
                        ClaudeStatus.VALIDATED
                        if self._dependencies.claude_available
                        else ClaudeStatus.SKIPPED
                    ),
                    "eligible": existing.eligible if existing.blocked else allowed,
                    "blocked": existing.blocked if existing.blocked else (not allowed),
                    "blocked_reason": (
                        existing.blocked_reason if existing.blocked else blocked_reason
                    ),
                    "cooldown_remaining": (
                        existing.cooldown_remaining
                        if existing.blocked
                        else cooldown_remaining
                    ),
                    "timestamp": signal.timestamp,
                    "reasoning": (
                        " ".join(signal.reasoning)
                        if signal.reasoning
                        else existing.reasoning
                    ),
                    "risk_gate_results": gate_results,
                }
            )
        return list(by_symbol.values())

    def list_signals(self) -> list[SignalSummary]:
        details = self._overlay_engine_data(self._fallback_details())
        return [SignalSummary.model_validate(item.model_dump()) for item in details]

    def get_signal_detail(self, signal_id: str) -> SignalDetail:
        for item in self._overlay_engine_data(self._fallback_details()):
            if item.id == signal_id:
                return item
        raise KeyError(signal_id)

    def get_reasoning(self, signal_id: str) -> SignalReasoning:
        detail = self.get_signal_detail(signal_id)
        return SignalReasoning(
            signal_id=detail.id,
            reasoning=detail.reasoning,
            technical_factors=[
                result.detail or result.gate for result in detail.risk_gate_results
            ],
            sentiment_context=(
                f"Sentiment score: {detail.sentiment_score}"
                if detail.sentiment_score is not None
                else "No external sentiment context available."
            ),
            claude_response=(
                "Claude validation available."
                if self._dependencies.claude_available
                else "Claude validation unavailable; fallback/local reasoning only."
            ),
            risk_gate_results=detail.risk_gate_results,
        )
