"""OHLC-based trend and breakout signals."""

from __future__ import annotations

import pandas as pd

TREND_LOOKBACK = 20
TREND_HALF = 10


def _require_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).lower() for c in out.columns]
    needed = {"open", "high", "low", "close"}
    missing = needed - set(out.columns)
    if missing:
        raise ValueError(
            f"DataFrame must contain columns {sorted(needed)}, missing: {sorted(missing)}"
        )
    return out


def _mean_bar_range(window: pd.DataFrame) -> float:
    r = (window["high"] - window["low"]).astype(float)
    return float(r.mean()) if len(r) else 0.0


def _trend_20_before_last(df: pd.DataFrame) -> tuple[str, float]:
    """
    Last 20 candles *before* the latest bar (no lookahead on the signal bar).

    First 10 vs last 10: higher highs & higher lows → uptrend; lower highs &
    lower lows → downtrend; else sideways.

    Returns (direction, clarity) where clarity is 0–1 (stronger separation
    vs average bar range → clearer trend).
    """
    window = df.iloc[-(TREND_LOOKBACK + 1) : -1]
    if len(window) < TREND_LOOKBACK:
        return "sideways", 0.0

    early = window.iloc[:TREND_HALF]
    late = window.iloc[TREND_HALF:]

    e_hi, e_lo = float(early["high"].max()), float(early["low"].min())
    l_hi, l_lo = float(late["high"].max()), float(late["low"].min())

    tr = _mean_bar_range(window)
    if tr <= 0:
        tr = 1e-12

    up = l_hi > e_hi and l_lo > e_lo
    down = l_hi < e_hi and l_lo < e_lo

    if up and not down:
        hh = (l_hi - e_hi) / tr
        hl = (l_lo - e_lo) / tr
        clarity = min(1.0, max(0.0, hh + hl) / 6.0)
        return "up", clarity

    if down and not up:
        lh = (e_hi - l_hi) / tr
        ll = (e_lo - l_lo) / tr
        clarity = min(1.0, max(0.0, lh + ll) / 6.0)
        return "down", clarity

    return "sideways", 0.0


def _breakout_direction(df: pd.DataFrame) -> str | None:
    """Breakout vs high/low of the 10 candles before the latest bar (close-based)."""
    ref = df.iloc[-11:-1]
    if len(ref) < 10:
        return None

    hi = ref["high"].max()
    lo = ref["low"].min()
    close = float(df.iloc[-1]["close"])

    if close > hi:
        return "up"
    if close < lo:
        return "down"
    return None


def _confidence(
    signal: str,
    trend: str,
    trend_clarity: float,
    breakout: str | None,
    df: pd.DataFrame,
) -> int:
    if signal in ("BUY", "SELL"):
        ref = df.iloc[-11:-1]
        hi = ref["high"].max()
        lo = ref["low"].min()
        close = float(df.iloc[-1]["close"])
        if signal == "BUY" and hi > 0:
            excess = (close - hi) / hi
        elif signal == "SELL" and lo > 0:
            excess = (lo - close) / lo
        else:
            excess = 0.0
        base = 58
        bump_break = min(28, int(max(0.0, excess) * 800))
        bump_trend = int(min(22, trend_clarity * 22))
        return min(100, base + bump_break + bump_trend)

    if breakout is None:
        if trend == "sideways":
            return 25
        bump = int(min(12, trend_clarity * 12))
        return 40 + bump

    if trend == "sideways":
        return 35
    return 30


def generate_signal(df: pd.DataFrame) -> dict:
    """
    Trend: on the 20 candles before the last bar, split into two halves; higher
    highs & higher lows → uptrend, lower highs & lower lows → downtrend, else
    sideways.

    Breakout: last close vs max high / min low of the 10 candles before the last bar.

    Returns:
        {"signal": "BUY" | "SELL" | "HOLD", "confidence": int 0-100}
    """
    ohlc = _require_ohlc(df)

    min_len = max(11, TREND_LOOKBACK + 1)
    if len(ohlc) < min_len:
        return {"signal": "HOLD", "confidence": 0}

    trend, trend_clarity = _trend_20_before_last(ohlc)
    breakout = _breakout_direction(ohlc)

    if breakout == "up" and trend == "up":
        signal = "BUY"
    elif breakout == "down" and trend == "down":
        signal = "SELL"
    else:
        signal = "HOLD"

    conf = _confidence(signal, trend, trend_clarity, breakout, ohlc)
    return {"signal": signal, "confidence": conf}
