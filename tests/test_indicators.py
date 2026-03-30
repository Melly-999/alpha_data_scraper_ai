import pandas as pd
import pytest

from indicators import IndicatorCalculator


def _indicators_cfg():
    return {
        "rsi_period": 14,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "bb_period": 20,
        "bb_std": 2,
        "stoch_period": 14,
        "stoch_k_smooth": 3,
    }


def test_calculate_all_returns_expected_keys():
    calc = IndicatorCalculator(_indicators_cfg())
    prices = pd.Series(range(1, 120), dtype=float)
    df = pd.DataFrame({"close": prices, "high": prices + 1, "low": prices - 1})

    result = calc.calculate_all(df)

    assert {"rsi", "macd_hist", "bb_position", "stoch_k", "stoch_d"} <= set(result.keys())


def test_rsi_is_in_valid_range():
    calc = IndicatorCalculator(_indicators_cfg())
    prices = pd.Series(range(1, 120), dtype=float)
    df = pd.DataFrame({"close": prices, "high": prices + 1, "low": prices - 1})

    result = calc.calculate_all(df)

    assert 0 <= result["rsi"] <= 100


@pytest.mark.slow
def test_rsi_series_length_matches_input():
    calc = IndicatorCalculator(_indicators_cfg())
    prices = pd.Series(range(1, 5000), dtype=float)
    series = calc.calculate_rsi_series(prices)
    assert len(series) == len(prices)
