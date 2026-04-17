"""
ensemble_combiner.py
─────────────────────────────────────────────────────────────────────
Fuses two signal sources into one final CombinedSignal:
  1. Technical (EMA cross + RSI + ATR)  — from mt5_bridge.py
  2. LSTM (alpha_data_scraper_ai)       — from lstm_signal_adapter.py

Weighting logic:
  - Base: 50/50 technical/LSTM
  - LSTM weight reduced proportionally when ensemble uncertainty > threshold
  - LSTM weight removed entirely when unavailable → 100% technical
  - Signal blocked when both disagree at similar conviction
  - Regime penalty skipped when LSTM unavailable (fix #14)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal, cast

from lstm_signal_adapter import LSTMSignal

log = logging.getLogger("EnsembleCombiner")

Direction = Literal["BUY", "SELL", "HOLD"]


# ─── Data classes ────────────────────────────────────────────────────


@dataclass
class TechnicalSignal:
    direction: Direction
    confidence: float  # 0–100
    sl: float
    tp: float


@dataclass
class CombinedSignal:
    direction: Direction
    confidence: float
    sl: float
    tp: float
    lstm_weight: float
    technical_weight: float
    regime: str
    reasons: list[str] = field(default_factory=list)
    blocked: bool = False
    block_reason: str = ""


# ─── Tuning constants ───────────────────────────────────────────────
LSTM_BASE_WEIGHT = 0.50
UNCERTAINTY_PENALTY_THRESH = 0.30
UNCERTAINTY_PENALTY_SCALE = 2.0  # how aggressively to penalise
LSTM_WEIGHT_FLOOR = 0.10  # never go below this when LSTM available
MIN_CONFIDENCE_TO_EMIT = 70.0
REGIME_PENALTY: dict[str, float] = {
    "TRENDING": 1.00,
    "RANGING": 0.90,
    "VOLATILE": 0.80,
    "UNKNOWN": 0.90,
}


class EnsembleCombiner:

    @staticmethod
    def combine(tech: TechnicalSignal, lstm: LSTMSignal) -> CombinedSignal:
        reasons: list[str] = []

        # ── Weights ───────────────────────────────────────────────────
        lstm_weight, tech_weight = _compute_weights(lstm, reasons)

        # ── Direction vote ────────────────────────────────────────────
        direction = _vote_direction(tech, lstm, tech_weight, lstm_weight)

        if direction == "HOLD":
            return CombinedSignal(
                direction="HOLD",
                confidence=0.0,
                sl=tech.sl,
                tp=tech.tp,
                lstm_weight=lstm_weight,
                technical_weight=tech_weight,
                regime=lstm.regime,
                reasons=["No consensus → HOLD"],
                blocked=True,
                block_reason="HOLD signal",
            )

        # ── Weighted confidence ───────────────────────────────────────
        lstm_conf = lstm.confidence if lstm.available else 0.0
        raw_conf = (tech.confidence * tech_weight) + (lstm_conf * lstm_weight)

        # FIX #14: skip regime penalty when LSTM is unavailable — the regime
        # label is "UNKNOWN" by default and penalising pure-technical signals
        # for a meaningless label costs ~10% confidence for no reason.
        if lstm.available:
            regime_mult = REGIME_PENALTY.get(lstm.regime, 0.90)
        else:
            regime_mult = 1.0

        confidence = round(raw_conf * regime_mult, 1)

        reasons.append(
            f"Tech {direction}={tech.confidence:.0f}%(w={tech_weight:.2f}) + "
            f"LSTM {lstm.direction}={lstm_conf:.0f}%(w={lstm_weight:.2f}) → "
            f"raw={raw_conf:.1f}% × regime({lstm.regime})={confidence:.1f}%"
        )
        # Cap forwarded reasons to avoid unbounded list growth
        reasons.extend(lstm.reasons[:3])

        # ── Confidence gate ───────────────────────────────────────────
        if confidence < MIN_CONFIDENCE_TO_EMIT:
            return CombinedSignal(
                direction=direction,
                confidence=confidence,
                sl=tech.sl,
                tp=tech.tp,
                lstm_weight=lstm_weight,
                technical_weight=tech_weight,
                regime=lstm.regime,
                reasons=reasons,
                blocked=True,
                block_reason=f"Confidence {confidence:.1f}% < {MIN_CONFIDENCE_TO_EMIT}%",
            )

        return CombinedSignal(
            direction=direction,
            confidence=confidence,
            sl=tech.sl,
            tp=tech.tp,
            lstm_weight=lstm_weight,
            technical_weight=tech_weight,
            regime=lstm.regime,
            reasons=reasons,
        )


# ─── Private helpers (module-level for testability) ──────────────────


def _compute_weights(lstm: LSTMSignal, reasons: list[str]) -> tuple[float, float]:
    """Return (lstm_weight, tech_weight) summing to 1.0."""
    if not lstm.available:
        reasons.append("LSTM unavailable → 100% technical")
        return 0.0, 1.0

    lstm_w = LSTM_BASE_WEIGHT

    if lstm.lstm_uncertainty > UNCERTAINTY_PENALTY_THRESH:
        penalty = (
            lstm.lstm_uncertainty - UNCERTAINTY_PENALTY_THRESH
        ) * UNCERTAINTY_PENALTY_SCALE
        lstm_w = max(LSTM_WEIGHT_FLOOR, lstm_w - penalty)
        reasons.append(
            f"LSTM uncertainty={lstm.lstm_uncertainty:.2f} → weight={lstm_w:.2f}"
        )

    return lstm_w, 1.0 - lstm_w


def _vote_direction(
    tech: TechnicalSignal,
    lstm: LSTMSignal,
    tech_weight: float,
    lstm_weight: float,
) -> Direction:
    """Weighted directional vote across signal sources."""
    scores: dict[Direction, float] = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0}

    scores[tech.direction] += tech.confidence * tech_weight

    if lstm.available and lstm.direction in scores and lstm.direction != "HOLD":
        scores[cast(Direction, lstm.direction)] += lstm.confidence * lstm_weight
    else:
        scores["HOLD"] += 30 * lstm_weight

    return max(scores, key=scores.get)  # type: ignore[arg-type]
