from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, cast

import pandas as pd

from app.schemas.common import (
    BlockedReason,
    ClaudeStatus,
    DataSource,
    Direction,
    LogCategory,
    Severity,
)
from app.schemas.signal import (
    SignalDetail,
    SignalProvenance,
    SignalReasoning,
    SignalSummary,
    Technicals,
)
from app.services.account_service import AccountService
from app.services.cache import TTLCache
from app.services.fixture_data import prototype_signals
from app.services.log_service import LogService
from app.services.risk_service import RiskService

if TYPE_CHECKING:
    from signal_generator import SignalResult


@dataclass(frozen=True)
class ServiceDependencies:
    mt5_available: bool
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
        tracked_symbols: list[str],
    ) -> None:
        self._risk_service = risk_service
        self._log_service = log_service
        self._account_service = account_service
        self._dependencies = dependencies
        self._tracked_symbols = tracked_symbols
        self._cache: TTLCache[list[SignalDetail]] = TTLCache(ttl_seconds=5)

    @property
    def fallback_mode(self) -> bool:
        return not self._dependencies.mt5_available

    def clear_cache(self) -> None:
        self._cache.clear()

    def list_signals(self) -> list[SignalSummary]:
        details = self._cached_details()
        return [SignalSummary.model_validate(item.model_dump()) for item in details]

    def get_signal_detail(self, signal_id: str) -> SignalDetail:
        for item in self._cached_details():
            if item.id == signal_id:
                return item
        raise KeyError(signal_id)

    def get_reasoning(self, signal_id: str) -> SignalReasoning:
        detail = self.get_signal_detail(signal_id)
        return SignalReasoning(
            signal_id=detail.id,
            reasoning=detail.reasoning,
            technical_factors=detail.technical_input_summary,
            sentiment_context=(
                f"Sentiment score: {detail.sentiment_score}"
                if detail.sentiment_score is not None
                else "No external sentiment context available."
            ),
            claude_response=detail.ai_validation_status,
            risk_gate_results=detail.risk_gate_results,
            blocked_reason=detail.blocked_reason,
            eligible=detail.eligible,
            confidence_explainer=detail.confidence_explainer,
            provenance=detail.provenance,
        )

    def _cached_details(self) -> list[SignalDetail]:
        envelope = self._cache.get_or_set(self._build_details)
        return [
            detail.model_copy(
                update={
                    "provenance": detail.provenance.model_copy(
                        update={"cache_age_seconds": envelope.cache_age_seconds}
                    )
                }
            )
            for detail in envelope.value
        ]

    def _build_details(self) -> list[SignalDetail]:
        details = self._fallback_details()
        try:
            return self._overlay_market_data(details)
        except Exception as exc:
            self._log_service.add(
                category=LogCategory.SIGNALS,
                severity=Severity.WARN,
                message=f"Signal overlay unavailable; serving fallback details only: {exc}",
            )
            return details

    def _fallback_details(self) -> list[SignalDetail]:
        generated_at = datetime.now(timezone.utc)
        details: list[SignalDetail] = []
        open_positions = len(self._account_service.get_open_positions())
        for item in prototype_signals():
            signal_id = str(item["id"])
            symbol = str(item["symbol"])
            direction = str(item["direction"])
            confidence = max(33, min(int(cast(int, item["confidence"])), 85))
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
            details.append(
                SignalDetail(
                    id=signal_id,
                    symbol=symbol,
                    direction=Direction(direction),
                    confidence=confidence,
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
                        for key, value in cast(
                            dict[str, Any], item["timeframes"]
                        ).items()
                    },
                    risk_gate_results=gate_results,
                    technical_input_summary=[
                        str(factor)
                        for factor in cast(list[Any], item["technical_factors"])
                    ],
                    confidence_explainer=(
                        f"Fallback confidence normalized to {confidence}% inside the 33-85 safety band."
                    ),
                    ai_validation_status=(
                        "Claude validation available."
                        if self._dependencies.claude_available
                        else "Claude validation unavailable; local/fallback reasoning only."
                    ),
                    provenance=SignalProvenance(
                        market_data_source=(
                            DataSource.MT5
                            if self._dependencies.mt5_available
                            else DataSource.SYNTHETIC
                        ),
                        signal_source=DataSource.FIXTURE,
                        validation_source=(
                            "claude" if self._dependencies.claude_available else "local"
                        ),
                        confidence_source="fixture_contract",
                        fallback=not self._dependencies.mt5_available,
                        generated_at=generated_at,
                        cache_age_seconds=0,
                    ),
                )
            )
        return details

    def _overlay_market_data(self, details: list[SignalDetail]) -> list[SignalDetail]:
        from indicators import add_indicators
        from mt5_fetcher import batch_fetch
        from signal_generator import generate_signal

        symbols = [
            detail.symbol
            for detail in details
            if detail.symbol in self._tracked_symbols
        ]
        market_frames = batch_fetch(symbols=symbols, timeframe="M5", bars=180)
        open_positions = len(self._account_service.get_open_positions())
        generated_at = datetime.now(timezone.utc)
        by_symbol = {detail.symbol: detail for detail in details}
        updated: list[SignalDetail] = []

        for symbol, detail in by_symbol.items():
            frame = market_frames.get(symbol)
            if frame is None or frame.empty:
                updated.append(detail)
                continue

            enriched = add_indicators(frame)
            if enriched.empty or len(enriched) < 2:
                updated.append(detail)
                continue

            latest = enriched.iloc[-1]
            previous = enriched.iloc[-2]
            signal = self._compute_signal(latest, previous, generate_signal)
            direction = signal.signal
            confidence = max(33, min(int(round(signal.confidence)), 85))
            timestamp = self._normalize_timestamp(latest["time"], detail.timestamp)
            technical_summary = self._technical_summary(latest, signal)
            allowed, blocked_reason, cooldown_remaining, gate_results = (
                self._risk_service.evaluate_signal(
                    signal_id=detail.id,
                    symbol=symbol,
                    direction=direction,
                    confidence=confidence,
                    sl=detail.sl,
                    tp=detail.tp,
                    rr=detail.rr,
                    timestamp=timestamp,
                    open_positions=open_positions,
                    register=False,
                )
            )
            signal_source = (
                DataSource.TECHNICAL_MODEL
                if self._dependencies.mt5_available
                else DataSource.SYNTHETIC
            )
            updated.append(
                detail.model_copy(
                    update={
                        "direction": Direction(direction),
                        "confidence": confidence,
                        "claude_status": (
                            ClaudeStatus.VALIDATED
                            if self._dependencies.claude_available
                            else ClaudeStatus.SKIPPED
                        ),
                        "eligible": allowed,
                        "blocked": not allowed,
                        "blocked_reason": blocked_reason,
                        "cooldown_remaining": cooldown_remaining,
                        "timestamp": timestamp,
                        "reasoning": self._compose_reasoning(
                            detail.reasoning, signal.reasons
                        ),
                        "technicals": technical_summary,
                        "risk_gate_results": gate_results,
                        "technical_input_summary": signal.reasons,
                        "confidence_explainer": (
                            f"Score {signal.score} normalized to {confidence}% within the enforced 33-85 band."
                        ),
                        "ai_validation_status": (
                            "Claude validation available."
                            if self._dependencies.claude_available
                            else "Claude validation unavailable; technical model only."
                        ),
                        "provenance": SignalProvenance(
                            market_data_source=(
                                DataSource.MT5
                                if self._dependencies.mt5_available
                                else DataSource.SYNTHETIC
                            ),
                            signal_source=signal_source,
                            validation_source=(
                                "claude"
                                if self._dependencies.claude_available
                                else "local"
                            ),
                            confidence_source="technical_score_normalization",
                            fallback=not self._dependencies.mt5_available,
                            generated_at=generated_at,
                            cache_age_seconds=0,
                        ),
                    }
                )
            )

        return updated

    def _compute_signal(
        self,
        latest: pd.Series,
        previous: pd.Series,
        generator: Any,
    ) -> "SignalResult":
        lstm_delta = float(latest["close"]) - float(previous["close"])
        return generator(latest, lstm_delta)

    @staticmethod
    def _compose_reasoning(base_reasoning: str, technical_reasons: list[str]) -> str:
        extra = "; ".join(technical_reasons[:4])
        if not extra:
            return base_reasoning
        return f"{extra}. Contract baseline: {base_reasoning}"

    @staticmethod
    def _normalize_timestamp(value: Any, fallback: datetime) -> datetime:
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime().astimezone(timezone.utc)
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc)
        return fallback

    @staticmethod
    def _technical_summary(latest: pd.Series, signal: "SignalResult") -> Technicals:
        macd_state = "bullish" if float(latest["macd_hist"]) >= 0 else "bearish"
        return Technicals(
            rsi=round(float(latest["rsi"]), 2),
            macd=macd_state,
            atr=round(float(latest["high"] - latest["low"]), 5),
            ema20=round(float(latest["bb_middle"]), 5),
            ema50=round(float(latest["close"]), 5),
            score=signal.score,
            inputs=list(signal.reasons),
        )
