from __future__ import annotations

import numpy as np
import pandas as pd


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


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()

    frame["rsi"] = _rsi(frame["close"], period=14)

    stoch_k, stoch_d = _stochastic(
        frame["high"], frame["low"], frame["close"], period=14
    )
    frame["stoch_k"] = stoch_k
    frame["stoch_d"] = stoch_d

    macd_fast = _ema(frame["close"], 12)
    macd_slow = _ema(frame["close"], 26)
    frame["macd"] = macd_fast - macd_slow
    frame["macd_signal"] = _ema(frame["macd"], 9)
    frame["macd_hist"] = frame["macd"] - frame["macd_signal"]

    frame["bb_middle"] = frame["close"].rolling(20).mean()
    bb_std = frame["close"].rolling(20).std()
    frame["bb_upper"] = frame["bb_middle"] + 2 * bb_std
    frame["bb_lower"] = frame["bb_middle"] - 2 * bb_std
    frame["bb_pos"] = (frame["close"] - frame["bb_lower"]) / (
        frame["bb_upper"] - frame["bb_lower"] + 1e-12
    )
    frame["bb_pos"] = frame["bb_pos"].clip(0, 1)

    frame = frame.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)
    return frame
