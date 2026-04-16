from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import numpy as np
import pandas as pd

try:
    import MetaTrader5 as mt5  # type: ignore
except Exception:  # pragma: no cover - optional runtime dependency
    mt5 = None

# Base prices for synthetic fallback per symbol (approximate mid-market)
_SYNTHETIC_BASE: dict[str, float] = {
    "EURUSD": 1.08,
    "GBPUSD": 1.27,
    "USDJPY": 150.5,
    "AUDUSD": 0.65,
    "EURJPY": 162.5,
    "XAUUSD": 2050.0,
    "WTI": 78.0,  # WTI crude oil (USD/barrel)
    "NVDA": 850.0,  # NVIDIA stock
    "GOOGL": 175.0,  # Alphabet/Google stock
    "USTECH100": 18500.0,  # NASDAQ 100 index
}


def batch_fetch(
    symbols: list[str],
    timeframe: str = "M5",
    bars: int = 700,
) -> dict[str, pd.DataFrame]:
    """Fetch OHLCV data for multiple symbols in a single MT5 session.

    Opens MT5 once, fetches all symbols sequentially, then shuts down.
    Falls back to per-symbol synthetic data when MT5 is unavailable or a
    symbol cannot be fetched.
    """
    if bars < 120:
        bars = 120

    results: dict[str, pd.DataFrame] = {}

    tf_map = {
        "M1": mt5.TIMEFRAME_M1 if mt5 else None,
        "M5": mt5.TIMEFRAME_M5 if mt5 else None,
        "M15": mt5.TIMEFRAME_M15 if mt5 else None,
        "H1": mt5.TIMEFRAME_H1 if mt5 else None,
    }
    tf_value = tf_map.get(timeframe.upper())

    mt5_ok = mt5 is not None and mt5.initialize()
    try:
        for idx, sym in enumerate(symbols):
            df: Optional[pd.DataFrame] = None
            if mt5_ok and tf_value is not None:
                try:
                    rates = mt5.copy_rates_from_pos(sym, tf_value, 0, bars)
                    if rates is not None:
                        frame = pd.DataFrame(rates)
                        if not frame.empty:
                            frame["time"] = pd.to_datetime(frame["time"], unit="s")
                            df = frame[
                                ["time", "open", "high", "low", "close", "tick_volume"]
                            ].rename(columns={"tick_volume": "volume"})
                except Exception:
                    df = None
            if df is None or df.empty:
                df = _synthetic_rates(sym, bars=bars, seed=42 + idx)
            results[sym] = df
    finally:
        if mt5_ok:
            mt5.shutdown()

    return results


def _synthetic_rates(symbol: str, bars: int = 700, seed: int = 42) -> pd.DataFrame:
    base = _SYNTHETIC_BASE.get(symbol, 1.0)
    # Scale volatility for JPY-pairs and gold
    vol = 0.0012 if base < 5 else (0.12 if base < 200 else 1.5)
    drift = 0.00005 if base < 5 else (0.005 if base < 200 else 0.05)

    rng = np.random.default_rng(seed)
    returns = rng.normal(loc=drift, scale=vol, size=bars)
    close = base + np.cumsum(returns)

    spread = vol * 0.35
    high_spread = np.abs(rng.normal(spread, spread * 0.35, size=bars))
    low_spread = np.abs(rng.normal(spread, spread * 0.35, size=bars))
    open_ = np.roll(close, 1)
    open_[0] = close[0]
    high = np.maximum(open_, close) + high_spread
    low = np.minimum(open_, close) - low_spread
    volume = rng.integers(100, 1200, size=bars)

    start = datetime.now(timezone.utc) - timedelta(minutes=5 * bars)
    time = pd.date_range(start=start, periods=bars, freq="5min")

    return pd.DataFrame(
        {
            "time": time,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


@dataclass
class MT5Fetcher:
    symbol: str = "EURUSD"
    timeframe: str = "M5"
    seed: int = 42
    last_time: pd.Timestamp | None = None

    def get_latest_rates(self, bars: int = 600) -> pd.DataFrame:
        """Return OHLCV candles from MT5 when available, otherwise synthetic data."""
        if bars < 120:
            bars = 120

        live = self._fetch_from_mt5(bars)
        if live is not None and not live.empty:
            self.last_time = pd.to_datetime(live["time"]).max()
            return live
        synthetic = _synthetic_rates(self.symbol, bars=bars, seed=self.seed)
        self.last_time = pd.to_datetime(synthetic["time"]).max()
        return synthetic

    def get_new_rates(self, bars: int = 5) -> pd.DataFrame:
        """Return only candles newer than the last successful fetch."""
        bars = max(int(bars), 1)
        previous_last_time = self.last_time
        latest = self.get_latest_rates(bars=max(120, bars))
        if previous_last_time is None:
            return latest.tail(bars).reset_index(drop=True)

        time_col = pd.to_datetime(latest["time"])
        new_rows = latest[time_col > previous_last_time].copy()
        if not new_rows.empty:
            self.last_time = pd.to_datetime(new_rows["time"]).max()
        return new_rows.reset_index(drop=True)

    def _fetch_from_mt5(self, bars: int) -> Optional[pd.DataFrame]:
        if mt5 is None:
            return None

        tf_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "H1": mt5.TIMEFRAME_H1,
        }
        timeframe_value = tf_map.get(self.timeframe.upper(), mt5.TIMEFRAME_M5)

        if not mt5.initialize():
            return None
        try:
            rates = mt5.copy_rates_from_pos(self.symbol, timeframe_value, 0, bars)
            if rates is None:
                return None
            frame = pd.DataFrame(rates)
            if frame.empty:
                return None
            frame["time"] = pd.to_datetime(frame["time"], unit="s")
            return frame[
                ["time", "open", "high", "low", "close", "tick_volume"]
            ].rename(columns={"tick_volume": "volume"})
        finally:
            mt5.shutdown()
