from __future__ import annotations

import sys
import types

import numpy as np
import pandas as pd
import pytest


@pytest.fixture(scope="session", autouse=True)
def _stub_gui() -> None:
    """Stub the gui module so imports of main.py work without tkinter installed."""
    if "gui" not in sys.modules:
        stub = types.ModuleType("gui")
        stub.render_console = lambda *a, **k: None  # type: ignore
        stub.run_live_gui = lambda *a, **k: None  # type: ignore
        sys.modules["gui"] = stub


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
