from __future__ import annotations

from app.schemas.signal_quality import (
    SignalQualityCounts,
    SignalQualityMetrics,
    SignalQualitySummaryResponse,
)
from app.schemas.signal_scanner import SignalAction
from app.services.signal_scanner import scan_symbols

# Default symbols scanned for the quality summary — mirrors the scanner preview default.
_SUMMARY_SYMBOLS: tuple[str, ...] = (
    "AAPL",
    "NVDA",
    "MSFT",
    "TSLA",
    "EURUSD",
    "XAUUSD",
)

_HIGH_CONFIDENCE_THRESHOLD: float = 70.0


def _derive_label(
    score: float,
) -> str:
    if score >= 70.0:
        return "high"
    if score >= 50.0:
        return "moderate"
    if score > 0.0:
        return "low"
    return "safe_fallback"


def _derive_confidence_band(avg: float) -> str:
    if avg >= 70.0:
        return "high"
    if avg >= 50.0:
        return "medium"
    return "low"


class SignalQualitySummaryService:
    """Read-only advisory service that derives a quality snapshot from the scanner.

    No network calls, no broker calls, no persistence, no writes, no execution
    semantics.  Safe to call from any GET handler.
    """

    def get_summary(self) -> SignalQualitySummaryResponse:
        batch = scan_symbols(_SUMMARY_SYMBOLS)
        results = batch.results

        total = len(results)
        watch_count = sum(1 for r in results if r.action == SignalAction.WATCH)
        hold_count = sum(1 for r in results if r.action == SignalAction.HOLD)
        long_setup_count = sum(
            1 for r in results if r.action == SignalAction.LONG_SETUP
        )
        short_setup_count = sum(
            1 for r in results if r.action == SignalAction.SHORT_SETUP
        )
        no_trade_count = sum(1 for r in results if r.action == SignalAction.NO_TRADE)

        confidences = [r.confidence for r in results]
        average_confidence = sum(confidences) / total if total > 0 else 0.0
        high_confidence_count = sum(
            1 for c in confidences if c >= _HIGH_CONFIDENCE_THRESHOLD
        )

        # All scanner results carry risk_allowed=False and requires_human_review=True
        # by Literal schema constraint — no need to re-read per row.
        risk_blocked_count = total
        human_review_required_count = total
        fresh_count = total
        stale_count = 0

        score = round(average_confidence, 2)
        label = _derive_label(score)
        confidence_band = _derive_confidence_band(average_confidence)

        counts = SignalQualityCounts(
            total_signals=total,
            watch_count=watch_count,
            hold_count=hold_count,
            long_setup_count=long_setup_count,
            short_setup_count=short_setup_count,
            no_trade_count=no_trade_count,
            average_confidence=score,
            high_confidence_count=high_confidence_count,
            stale_count=stale_count,
            fresh_count=fresh_count,
            risk_blocked_count=risk_blocked_count,
            human_review_required_count=human_review_required_count,
        )

        quality = SignalQualityMetrics(
            label=label,  # type: ignore[arg-type]
            score=score,
            confidence_band=confidence_band,  # type: ignore[arg-type]
            freshness="live",
            risk_posture="blocked",
        )

        return SignalQualitySummaryResponse(
            status="ok",
            summary=counts,
            quality=quality,
        )
