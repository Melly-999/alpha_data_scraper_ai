from __future__ import annotations

import warnings

import numpy as np
import pandas as pd


# ── Core helpers ──────────────────────────────────────────────────────────────

def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(alpha=1 / period, adjust=False).mean()
    roll_down = down.ewm(alpha=1 / period, adjust=False).mean()
    rs = roll_up / (roll_down + 1e-12)
    return 100 - (100 / (1 + rs))


def _stochastic(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> tuple[pd.Series, pd.Series]:
    lowest_low = low.rolling(period).min()
    highest_high = high.rolling(period).max()
    k = 100 * ((close - lowest_low) / (highest_high - lowest_low + 1e-12))
    d = k.rolling(3).mean()
    return k, d


# ── New indicators ────────────────────────────────────────────────────────────

def _atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """Average True Range — normalised volatility measure.

    Uses Wilder's smoothing (EWM with alpha=1/period) for consistency
    with industry-standard ATR calculations.
    """
    prev_close = close.shift(1)
    true_range = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False).mean()


def _adx(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Average Directional Index with +DI / -DI.

    Returns:
        (adx, plus_di, minus_di)
        adx     — trend strength (0–100, >20 = trending, >40 = strong trend)
        plus_di — upward directional pressure
        minus_di — downward directional pressure
    """
    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

    # Set first row to NaN to avoid bias from zero-initialisation
    if len(plus_dm) > 0:
        plus_dm.iloc[0] = np.nan
        minus_dm.iloc[0] = np.nan

    atr = _atr(high, low, close, period)
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, adjust=False).mean() / (atr + 1e-12)
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, adjust=False).mean() / (atr + 1e-12)

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-12)
    adx = dx.ewm(alpha=1 / period, adjust=False).mean()
    return adx, plus_di, minus_di


def _obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On Balance Volume — cumulative volume weighted by price direction.

    Raw OBV is symbol-specific in magnitude so callers should normalise
    (e.g. rolling z-score) before using it as a cross-symbol feature.
    """
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()


def _vwap(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
) -> pd.Series:
    """Volume Weighted Average Price — intraday fair-value reference.

    Note: a true session-reset VWAP would require timestamp-based grouping.
    This cumulative approximation is standard for tick/bar-level data without
    explicit session boundaries.
    """
    typical_price = (high + low + close) / 3
    return (typical_price * volume).cumsum() / (volume.cumsum() + 1e-12)


# ── Public API ────────────────────────────────────────────────────────────────

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute all technical indicators and append as new columns.

    Original indicators (unchanged):
        rsi, stoch_k, stoch_d, macd, macd_signal, macd_hist,
        bb_middle, bb_upper, bb_lower, bb_pos

    New indicators:
        atr        — Average True Range (raw, in price units)
        atr_pct    — ATR as % of close (normalised for cross-symbol use)
        adx        — Trend strength (0–100)
        plus_di    — Upward directional indicator
        minus_di   — Downward directional indicator
        obv_z      — OBV rolling z-score (window=50); >1 = bullish surge
        vwap       — Volume Weighted Average Price
        vwap_dev   — (close − vwap) / vwap × 100; negative = below fair value
    """
    if len(df) < 2:
        warnings.warn("DataFrame has fewer than 2 rows; cannot compute indicators.", UserWarning)
        return df.copy()

    frame = df.copy()

    # ── Original ──────────────────────────────────────────────────────────────
    frame["rsi"] = _rsi(frame["close"], period=14)

    stoch_k, stoch_d = _stochastic(frame["high"], frame["low"], frame["close"], period=14)
    frame["stoch_k"] = stoch_k
    frame["stoch_d"] = stoch_d

    macd_fast = _ema(frame["close"], 12)
    macd_slow = _ema(frame["close"], 26)
    frame["macd"] = macd_fast - macd_slow
    frame["macd_signal"] = _ema(frame["macd"], 9)
    frame["macd_hist"] = frame["macd"] - frame["macd_signal"]

    # Performance: compute rolling close once
    roll_close = frame["close"].rolling(20, min_periods=1)
    frame["bb_middle"] = roll_close.mean()
    bb_std = roll_close.std()
    frame["bb_upper"] = frame["bb_middle"] + 2 * bb_std
    frame["bb_lower"] = frame["bb_middle"] - 2 * bb_std
    frame["bb_pos"] = (frame["close"] - frame["bb_lower"]) / (
        frame["bb_upper"] - frame["bb_lower"] + 1e-12
    )
    frame["bb_pos"] = frame["bb_pos"].clip(0, 1)

    # ── ATR ───────────────────────────────────────────────────────────────────
    frame["atr"] = _atr(frame["high"], frame["low"], frame["close"], period=14)
    frame["atr_pct"] = frame["atr"] / (frame["close"].abs() + 1e-12)

    # ── ADX ───────────────────────────────────────────────────────────────────
    adx, plus_di, minus_di = _adx(frame["high"], frame["low"], frame["close"], period=14)
    frame["adx"] = adx
    frame["plus_di"] = plus_di
    frame["minus_di"] = minus_di

    # ── OBV (z-score normalised) ──────────────────────────────────────────────
    obv_raw = _obv(frame["close"], frame["volume"])
    obv_mean = obv_raw.rolling(50, min_periods=10).mean()
    obv_std = obv_raw.rolling(50, min_periods=10).std()
    frame["obv_z"] = (obv_raw - obv_mean) / (obv_std + 1e-12)

    # ── VWAP deviation ────────────────────────────────────────────────────────
    frame["vwap"] = _vwap(frame["high"], frame["low"], frame["close"], frame["volume"])
    frame["vwap_dev"] = (frame["close"] - frame["vwap"]) / (frame["vwap"].abs() + 1e-12) * 100

    frame = frame.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)
    return frame
