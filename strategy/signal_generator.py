from __future__ import annotations

import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd

# ── Market regime ─────────────────────────────────────────────────────────────


class MarketRegime(str, Enum):
    """Market regime classification driven by ADX and directional indicators.

    TRENDING_UP   — ADX ≥ 20 and +DI > -DI (bulls in control)
    TRENDING_DOWN — ADX ≥ 20 and -DI ≥ +DI (bears in control)
    RANGING       — ADX < 20 (no dominant trend; mean-reversion conditions)
    """

    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"


def detect_regime(adx: float, plus_di: float, minus_di: float) -> MarketRegime:
    """Classify market regime.

    ADX < 20  → ranging (Wilder's original threshold).
    ADX ≥ 20  → trending; direction from +DI vs -DI comparison.
    """
    if adx < 20:
        return MarketRegime.RANGING
    return (
        MarketRegime.TRENDING_UP if plus_di >= minus_di else MarketRegime.TRENDING_DOWN
    )


# ── Adaptive confidence ───────────────────────────────────────────────────────


def _adaptive_confidence(
    base_confidence: float,
    atr_pct: float,
    regime: MarketRegime,
) -> float:
    """Scale confidence by volatility and regime reliability.

    Volatility penalty:
        High ATR → noisier price action → less reliable signals.
        Max penalty capped at 25 % to avoid over-penalising volatile assets.

    Regime factor:
        Trending markets → momentum signals are more reliable → slight boost.
        Ranging markets  → false breakouts are common → slight penalty.
    """
    vol_penalty = min(atr_pct * 8.0, 0.25)
    vol_factor = 1.0 - vol_penalty

    regime_factor = (
        1.08
        if regime in (MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN)
        else 0.92
    )

    return float(np.clip(base_confidence * vol_factor * regime_factor, 33.0, 85.0))


# ── Signal result ─────────────────────────────────────────────────────────────


@dataclass
class SignalResult:
    signal: str
    confidence: float
    score: int
    reasons: list[str]
    regime: MarketRegime = MarketRegime.RANGING


# ── Core signal generation ────────────────────────────────────────────────────


def generate_signal(
    latest: pd.Series,
    lstm_delta: float,
    lstm_uncertainty: float = 0.0,
) -> SignalResult:
    """Generate a BUY / SELL / HOLD signal from indicator values.

    Args:
        latest:           Row from an ``add_indicators()``-enriched DataFrame.
        lstm_delta:       LSTM predicted price delta (positive = up).
        lstm_uncertainty: Ensemble std-dev from ``LSTMPipeline.prediction_uncertainty()``.
                          Non-zero values reduce the LSTM score weight when models disagree.

    Scoring logic
    -------------
    Each indicator contributes ±1 or ±2 to a running score.
    BUY if score ≥ 2, SELL if score ≤ -2, else HOLD.

    New vs original indicators:
        Original : RSI, Stochastic, MACD histogram, Bollinger position, LSTM delta
        New      : ADX regime (+DI / -DI), OBV z-score, VWAP deviation
    """
    score = 0
    reasons: list[str] = []

    # Helper to safely extract float with default
    def get_float(key: str, default: float = 0.0) -> float:
        try:
            return float(latest.get(key, default))
        except (TypeError, ValueError):
            warnings.warn(
                f"Could not convert '{key}' to float, using default {default}",
                UserWarning,
            )
            return default

    # ── RSI ───────────────────────────────────────────────────────────────────
    rsi = get_float("rsi", 50.0)
    if rsi < 35:
        score += 1
        reasons.append(f"RSI oversold ({rsi:.1f})")
    elif rsi > 65:
        score -= 1
        reasons.append(f"RSI overbought ({rsi:.1f})")

    # ── Stochastic ────────────────────────────────────────────────────────────
    stoch_k = get_float("stoch_k", 50.0)
    stoch_d = get_float("stoch_d", 50.0)
    if stoch_k < 20 and stoch_k > stoch_d:
        score += 1
        reasons.append(f"Stochastic bullish crossover (K={stoch_k:.1f})")
    elif stoch_k > 80 and stoch_k < stoch_d:
        score -= 1
        reasons.append(f"Stochastic bearish crossover (K={stoch_k:.1f})")

    # ── MACD histogram ────────────────────────────────────────────────────────
    macd_hist = get_float("macd_hist", 0.0)
    if macd_hist > 0:
        score += 1
        reasons.append("MACD histogram positive")
    else:
        score -= 1
        reasons.append("MACD histogram negative")

    # ── Bollinger Bands ───────────────────────────────────────────────────────
    bb_pos = get_float("bb_pos", 0.5)
    if bb_pos < 0.2:
        score += 1
        reasons.append(f"Price near lower BB (pos={bb_pos:.2f})")
    elif bb_pos > 0.8:
        score -= 1
        reasons.append(f"Price near upper BB (pos={bb_pos:.2f})")

    # ── LSTM delta ────────────────────────────────────────────────────────────
    # Weight = 2 normally; reduced to 1 when ensemble uncertainty is high
    # and the predicted delta is small relative to uncertainty.
    # Also, ignore weight reduction if |delta| is below noise floor (1e-6)
    lstm_weight = 2
    if lstm_uncertainty > 0 and abs(lstm_delta) > 1e-6:
        if lstm_uncertainty > 2 * abs(lstm_delta):
            lstm_weight = 1
            reasons.append(
                f"LSTM weight reduced due to high uncertainty (Δ={lstm_delta:.5f}, unc={lstm_uncertainty:.5f})"
            )
    if lstm_delta > 0:
        score += lstm_weight
        unc_note = (
            f", uncertainty={lstm_uncertainty:.5f}" if lstm_uncertainty > 0 else ""
        )
        reasons.append(f"LSTM predicts upside (Δ={lstm_delta:.5f}{unc_note})")
    elif lstm_delta < 0:
        score -= lstm_weight
        unc_note = (
            f", uncertainty={lstm_uncertainty:.5f}" if lstm_uncertainty > 0 else ""
        )
        reasons.append(f"LSTM predicts downside (Δ={lstm_delta:.5f}{unc_note})")

    # ── NEW: ADX regime ───────────────────────────────────────────────────────
    adx = get_float("adx", 0.0)
    plus_di = get_float("plus_di", 0.0)
    minus_di = get_float("minus_di", 0.0)
    regime = detect_regime(adx, plus_di, minus_di)

    if regime == MarketRegime.TRENDING_UP:
        score += 1
        reasons.append(
            f"ADX trending up (+DI={plus_di:.1f} > -DI={minus_di:.1f}, ADX={adx:.1f})"
        )
    elif regime == MarketRegime.TRENDING_DOWN:
        score -= 1
        reasons.append(
            f"ADX trending down (-DI={minus_di:.1f} > +DI={plus_di:.1f}, ADX={adx:.1f})"
        )
    else:
        reasons.append(f"Market ranging — ADX={adx:.1f} (< 20)")

    # ── NEW: OBV z-score (volume confirmation) ────────────────────────────────
    obv_z = get_float("obv_z", 0.0)
    if obv_z > 1.0:
        score += 1
        reasons.append(f"OBV bullish volume surge (z={obv_z:.2f})")
    elif obv_z < -1.0:
        score -= 1
        reasons.append(f"OBV bearish volume surge (z={obv_z:.2f})")

    # ── NEW: VWAP deviation (price vs fair value) ─────────────────────────────
    # Fixed thresholds: 2% deviation (was 0.05% which was too sensitive)
    vwap_dev = get_float("vwap_dev", 0.0)
    if vwap_dev < -2.0:
        score += 1
        reasons.append(
            f"Price significantly below VWAP ({vwap_dev:+.2f}%) — potential mean-reversion up"
        )
    elif vwap_dev > 2.0:
        score -= 1
        reasons.append(
            f"Price significantly above VWAP ({vwap_dev:+.2f}%) — potential mean-reversion down"
        )

    # ── Decision ──────────────────────────────────────────────────────────────
    if score >= 2:
        signal = "BUY"
    elif score <= -2:
        signal = "SELL"
    else:
        signal = "HOLD"

    # ── Adaptive confidence ───────────────────────────────────────────────────
    base_confidence = float(np.clip(50 + (score * 8), 33, 85))
    atr_pct = get_float("atr_pct", 0.0)
    confidence = _adaptive_confidence(base_confidence, atr_pct, regime)

    return SignalResult(
        signal=signal,
        confidence=confidence,
        score=score,
        reasons=reasons,
        regime=regime,
    )


def signal_to_dict(result: SignalResult) -> dict[str, Any]:
    return {
        "signal": result.signal,
        "confidence": round(result.confidence, 2),
        "score": result.score,
        "reasons": result.reasons,
        "regime": result.regime.value,
    }
