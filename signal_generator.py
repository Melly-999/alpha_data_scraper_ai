from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class SignalResult:
    signal: str
    confidence: float
    score: int
    reasons: list[str]


def generate_signal(latest: pd.Series, lstm_delta: float) -> SignalResult:
    score = 0
    reasons: list[str] = []

    if latest["rsi"] < 35:
        score += 1
        reasons.append("RSI oversold")
    elif latest["rsi"] > 65:
        score -= 1
        reasons.append("RSI overbought")

    if latest["stoch_k"] < 20 and latest["stoch_k"] > latest["stoch_d"]:
        score += 1
        reasons.append("Stochastic bullish crossover")
    elif latest["stoch_k"] > 80 and latest["stoch_k"] < latest["stoch_d"]:
        score -= 1
        reasons.append("Stochastic bearish crossover")

    if latest["macd_hist"] > 0:
        score += 1
        reasons.append("MACD histogram positive")
    else:
        score -= 1
        reasons.append("MACD histogram negative")

    bb_pos = float(latest["bb_pos"])
    if bb_pos < 0.2:
        score += 1
        reasons.append("Price near lower Bollinger band")
    elif bb_pos > 0.8:
        score -= 1
        reasons.append("Price near upper Bollinger band")

    if lstm_delta > 0:
        score += 2
        reasons.append("LSTM predicts upside")
    elif lstm_delta < 0:
        score -= 2
        reasons.append("LSTM predicts downside")

    if score >= 2:
        signal = "BUY"
    elif score <= -2:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = float(np.clip(50 + (score * 8), 33, 85))
    return SignalResult(
        signal=signal, confidence=confidence, score=score, reasons=reasons
    )


def signal_to_dict(result: SignalResult) -> dict[str, Any]:
    return {
        "signal": result.signal,
        "confidence": round(result.confidence, 2),
        "score": result.score,
        "reasons": result.reasons,
    }
