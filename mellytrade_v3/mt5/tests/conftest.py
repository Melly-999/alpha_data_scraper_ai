from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parent.parent  # mellytrade_v3/
for p in (str(PKG_ROOT),):
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture()
def ohlcv() -> pd.DataFrame:
    rng = np.random.default_rng(123)
    n = 120
    base = 1.10 + np.cumsum(rng.normal(0, 0.0003, n))
    high = base + np.abs(rng.normal(0, 0.0005, n))
    low = base - np.abs(rng.normal(0, 0.0005, n))
    open_ = base + rng.normal(0, 0.0002, n)
    close = base
    volume = rng.integers(100, 1000, n)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume}
    )
