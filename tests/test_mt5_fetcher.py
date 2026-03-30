import numpy as np
import pytest

import mt5_fetcher as fetcher_module
from mt5_fetcher import MT5DataFetcher


class _Tick:
    def __init__(self, bid, ask):
        self.bid = bid
        self.ask = ask


class _FakeMT5:
    TIMEFRAME_M1 = object()

    def __init__(self):
        self._initialized = False

    def initialize(self):
        self._initialized = True
        return True

    def symbol_select(self, symbol, enabled):
        return True

    def shutdown(self):
        self._initialized = False

    def symbol_info_tick(self, symbol):
        return _Tick(100.0, 100.2)

    def copy_rates_from_pos(self, symbol, timeframe, start, max_bars):
        dtype = [("time", "i8"), ("open", "f8"), ("high", "f8"), ("low", "f8"), ("close", "f8")]
        base = 1_700_000_000
        data = [
            (base + i * 60, 100.0 + i, 101.0 + i, 99.0 + i, 100.5 + i)
            for i in range(5)
        ]
        return np.array(data, dtype=dtype)

    def account_info(self):
        return {"equity": 1000}


@pytest.mark.mt5
def test_initialize_and_get_tick_with_mocked_mt5(monkeypatch):
    fake = _FakeMT5()
    monkeypatch.setattr(fetcher_module, "mt5", fake)

    fetcher = MT5DataFetcher("XAUUSD")
    assert fetcher.initialize() is True
    assert fetcher.get_tick() == (100.0, 100.2)


@pytest.mark.mt5
def test_get_new_bars_returns_dataframe_with_time(monkeypatch):
    fake = _FakeMT5()
    monkeypatch.setattr(fetcher_module, "mt5", fake)

    fetcher = MT5DataFetcher("XAUUSD")
    assert fetcher.initialize() is True
    rates, df = fetcher.get_new_bars(max_bars=5)

    assert rates is not None
    assert df is not None
    assert "time" in df.columns
