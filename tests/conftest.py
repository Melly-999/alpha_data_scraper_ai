from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_ohlcv() -> pd.DataFrame:
    rng = np.random.default_rng(123)
    n = 260
    close = 1.1 + np.cumsum(rng.normal(0.0, 0.001, size=n))
    open_ = np.roll(close, 1)
    open_[0] = close[0]
    high = np.maximum(open_, close) + np.abs(rng.normal(0.0003, 0.0001, size=n))
    low = np.minimum(open_, close) - np.abs(rng.normal(0.0003, 0.0001, size=n))
    volume = rng.integers(100, 1000, size=n)

    return pd.DataFrame(
        {
            "time": pd.date_range("2025-01-01", periods=n, freq="5min"),
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )
