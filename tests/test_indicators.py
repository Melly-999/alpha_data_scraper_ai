from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from indicators import _ema, _rsi, _stochastic, add_indicators

# ---------------------------------------------------------------------------
# Existing tests
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# _ema — exponential moving average
# ---------------------------------------------------------------------------


def test_ema_output_length_matches_input() -> None:
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    result = _ema(s, span=3)
    assert len(result) == len(s)


def test_ema_first_value_equals_first_input() -> None:
    """With adjust=False the first EMA value equals the first data point."""
    s = pd.Series([10.0, 20.0, 30.0])
    result = _ema(s, span=3)
    assert result.iloc[0] == pytest.approx(10.0)


def test_ema_converges_toward_constant_series() -> None:
    """For a constant series every EMA value should equal that constant."""
    val = 5.0
    s = pd.Series([val] * 20)
    result = _ema(s, span=5)
    assert result.iloc[-1] == pytest.approx(val)


def test_ema_span_1_equals_series() -> None:
    """EMA with span=1 is 100% weight on current value → equals the series."""
    s = pd.Series([1.0, 3.0, 7.0, 2.0])
    result = _ema(s, span=1)
    pd.testing.assert_series_equal(result, s, check_names=False)


# ---------------------------------------------------------------------------
# _rsi — relative strength index
# ---------------------------------------------------------------------------


def test_rsi_values_in_range(sample_ohlcv: pd.DataFrame) -> None:
    rsi = _rsi(sample_ohlcv["close"], period=14)
    valid = rsi.dropna()
    assert (valid >= 0).all() and (valid <= 100).all()


def test_rsi_all_gains_approaches_100() -> None:
    """Strictly increasing close prices → RSI should be high (near 100)."""
    close = pd.Series(np.arange(1.0, 51.0))  # 50 strictly increasing values
    rsi = _rsi(close, period=14)
    # After enough periods the RSI saturates close to 100
    assert rsi.iloc[-1] > 90


def test_rsi_all_losses_approaches_0() -> None:
    """Strictly decreasing close prices → RSI should be low (near 0)."""
    close = pd.Series(np.arange(50.0, 0.0, -1.0))
    rsi = _rsi(close, period=14)
    assert rsi.iloc[-1] < 10


def test_rsi_output_length_matches_input(sample_ohlcv: pd.DataFrame) -> None:
    rsi = _rsi(sample_ohlcv["close"], period=14)
    assert len(rsi) == len(sample_ohlcv)


# ---------------------------------------------------------------------------
# _stochastic — stochastic oscillator
# ---------------------------------------------------------------------------


def test_stochastic_returns_two_series(sample_ohlcv: pd.DataFrame) -> None:
    k, d = _stochastic(sample_ohlcv["high"], sample_ohlcv["low"], sample_ohlcv["close"])
    assert isinstance(k, pd.Series)
    assert isinstance(d, pd.Series)


def test_stochastic_k_values_in_range(sample_ohlcv: pd.DataFrame) -> None:
    k, _ = _stochastic(sample_ohlcv["high"], sample_ohlcv["low"], sample_ohlcv["close"])
    valid = k.dropna()
    assert (valid >= 0).all() and (valid <= 100).all()


def test_stochastic_d_values_in_range(sample_ohlcv: pd.DataFrame) -> None:
    _, d = _stochastic(sample_ohlcv["high"], sample_ohlcv["low"], sample_ohlcv["close"])
    valid = d.dropna()
    assert (valid >= 0).all() and (valid <= 100).all()


def test_stochastic_uniform_prices_no_error() -> None:
    """When high == low (zero range) the epsilon guard prevents ZeroDivisionError."""
    n = 30
    price = pd.Series([1.0] * n)
    k, d = _stochastic(price, price, price, period=14)
    assert not k.isna().all()  # should produce *some* numeric result


def test_stochastic_output_length_matches_input(sample_ohlcv: pd.DataFrame) -> None:
    k, d = _stochastic(sample_ohlcv["high"], sample_ohlcv["low"], sample_ohlcv["close"])
    assert len(k) == len(sample_ohlcv)
    assert len(d) == len(sample_ohlcv)


# ---------------------------------------------------------------------------
# add_indicators — edge cases
# ---------------------------------------------------------------------------


def test_add_indicators_too_few_rows_returns_empty() -> None:
    """A 5-row frame cannot produce enough history; result should be empty."""
    rng = np.random.default_rng(0)
    n = 5
    close = 1.0 + rng.normal(0, 0.001, n)
    df = pd.DataFrame(
        {
            "time": pd.date_range("2025-01-01", periods=n, freq="5min"),
            "open": close,
            "high": close + 0.001,
            "low": close - 0.001,
            "close": close,
            "volume": [100] * n,
        }
    )
    out = add_indicators(df)
    assert len(out) == 0


def test_add_indicators_rsi_in_range(sample_ohlcv: pd.DataFrame) -> None:
    out = add_indicators(sample_ohlcv)
    assert out["rsi"].between(0, 100).all()


def test_add_indicators_bb_pos_in_range(sample_ohlcv: pd.DataFrame) -> None:
    out = add_indicators(sample_ohlcv)
    assert out["bb_pos"].between(0, 1).all()


def test_add_indicators_stoch_in_range(sample_ohlcv: pd.DataFrame) -> None:
    out = add_indicators(sample_ohlcv)
    assert out["stoch_k"].between(0, 100).all()
    assert out["stoch_d"].between(0, 100).all()
