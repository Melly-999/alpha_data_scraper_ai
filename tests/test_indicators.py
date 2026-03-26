from __future__ import annotations

import pandas as pd

from indicators import add_indicators


def test_add_indicators_has_expected_columns(sample_ohlcv: pd.DataFrame) -> None:
    out = add_indicators(sample_ohlcv)
    expected = {
        "rsi",
        "stoch_k",
        "stoch_d",
        "macd",
        "macd_signal",
        "macd_hist",
        "bb_middle",
        "bb_upper",
        "bb_lower",
        "bb_pos",
    }
    assert expected.issubset(set(out.columns))
    assert len(out) > 0


def test_add_indicators_no_nan_after_cleanup(sample_ohlcv: pd.DataFrame) -> None:
    out = add_indicators(sample_ohlcv)
    assert out.isna().sum().sum() == 0
