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


@dataclass
class MT5Fetcher:
    symbol: str = "EURUSD"
    timeframe: str = "M5"
    seed: int = 42

    def get_latest_rates(self, bars: int = 600) -> pd.DataFrame:
        """Return OHLCV candles from MT5 when available, otherwise synthetic data."""
        if bars < 120:
            bars = 120

        live = self._fetch_from_mt5(bars)
        if live is not None and not live.empty:
            return live
        return self._synthetic_rates(bars)

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

    def _synthetic_rates(self, bars: int) -> pd.DataFrame:
        rng = np.random.default_rng(self.seed)
        returns = rng.normal(loc=0.00005, scale=0.0012, size=bars)
        close = 1.08 + np.cumsum(returns)

        high_spread = np.abs(rng.normal(0.0004, 0.00015, size=bars))
        low_spread = np.abs(rng.normal(0.0004, 0.00015, size=bars))
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
