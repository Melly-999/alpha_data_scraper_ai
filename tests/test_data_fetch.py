"""Unit tests for data/fetch.py."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

# Inject a stub for yfinance before data.fetch is imported so the module
# loads cleanly in environments where yfinance is not installed.
if "yfinance" not in sys.modules:
    sys.modules["yfinance"] = MagicMock()

from data.fetch import _yahoo_ticker, fetch_ohlc  # noqa: E402

# ---------------------------------------------------------------------------
# _yahoo_ticker — ticker format conversions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "symbol, expected",
    [
        # 6-char alpha → append =X
        ("EURUSD", "EURUSD=X"),
        ("GBPUSD", "GBPUSD=X"),
        ("USDJPY", "USDJPY=X"),
        # slash-separated → collapse + append =X
        ("EUR/USD", "EURUSD=X"),
        ("GBP/USD", "GBPUSD=X"),
        # Already has suffix — idempotent
        ("EURUSD=X", "EURUSD=X"),
        # Whitespace is stripped and uppercased
        ("eurusd", "EURUSD=X"),
        (" EURUSD ", "EURUSD=X"),
        # Non-forex equity — passes through as-is
        ("AAPL", "AAPL"),
        ("SPY", "SPY"),
    ],
)
def test_yahoo_ticker_conversion(symbol: str, expected: str) -> None:
    assert _yahoo_ticker(symbol) == expected


# ---------------------------------------------------------------------------
# fetch_ohlc — invalid timeframe
# ---------------------------------------------------------------------------


def test_fetch_ohlc_invalid_timeframe_raises() -> None:
    with pytest.raises(ValueError, match="Unsupported timeframe"):
        fetch_ohlc("EURUSD", timeframe="W1")


def test_fetch_ohlc_invalid_timeframe_message_includes_valid_options() -> None:
    with pytest.raises(ValueError, match="D1"):
        fetch_ohlc("EURUSD", timeframe="INVALID")


# ---------------------------------------------------------------------------
# fetch_ohlc — empty data raises RuntimeError
# ---------------------------------------------------------------------------


def test_fetch_ohlc_empty_response_raises_runtime_error() -> None:
    with patch("data.fetch.yf.download", return_value=pd.DataFrame()):
        with pytest.raises(RuntimeError):
            fetch_ohlc("EURUSD", timeframe="H1")


# ---------------------------------------------------------------------------
# fetch_ohlc — normal response returns correct columns
# ---------------------------------------------------------------------------


def _mock_ohlc_df(n: int = 50) -> pd.DataFrame:
    """Minimal yfinance-style response (flat columns, DatetimeIndex)."""
    idx = pd.date_range("2025-01-01", periods=n, freq="1h")
    return pd.DataFrame(
        {
            "Open": [1.1] * n,
            "High": [1.11] * n,
            "Low": [1.09] * n,
            "Close": [1.10] * n,
            "Adj Close": [1.10] * n,
            "Volume": [1000] * n,
        },
        index=idx,
    )


def test_fetch_ohlc_returns_ohlc_columns_only() -> None:
    with patch("data.fetch.yf.download", return_value=_mock_ohlc_df()):
        df = fetch_ohlc("EURUSD", timeframe="H1", bars=30)
    assert list(df.columns) == ["Open", "High", "Low", "Close"]


def test_fetch_ohlc_respects_bars_limit() -> None:
    with patch("data.fetch.yf.download", return_value=_mock_ohlc_df(n=100)):
        df = fetch_ohlc("EURUSD", timeframe="H1", bars=30)
    assert len(df) <= 30


def test_fetch_ohlc_minimum_11_rows_enforced() -> None:
    """bars=1 → tail(max(1, 11)) = tail(11)."""
    with patch("data.fetch.yf.download", return_value=_mock_ohlc_df(n=50)):
        df = fetch_ohlc("EURUSD", timeframe="H1", bars=1)
    assert len(df) == 11


def test_fetch_ohlc_no_nan_rows() -> None:
    with patch("data.fetch.yf.download", return_value=_mock_ohlc_df()):
        df = fetch_ohlc("EURUSD", timeframe="H1")
    assert df[["Open", "High", "Low", "Close"]].isna().sum().sum() == 0


# ---------------------------------------------------------------------------
# fetch_ohlc — multi-index column handling
# ---------------------------------------------------------------------------


def _mock_multiindex_df(n: int = 30) -> pd.DataFrame:
    """Simulate yfinance multi-ticker response with MultiIndex columns."""
    idx = pd.date_range("2025-01-01", periods=n, freq="1h")
    cols = pd.MultiIndex.from_tuples(
        [
            ("Open", "EURUSD=X"),
            ("High", "EURUSD=X"),
            ("Low", "EURUSD=X"),
            ("Close", "EURUSD=X"),
            ("Adj Close", "EURUSD=X"),
            ("Volume", "EURUSD=X"),
        ]
    )
    data = [[1.10, 1.11, 1.09, 1.10, 1.10, 1000]] * n
    return pd.DataFrame(data, columns=cols, index=idx)


def test_fetch_ohlc_flattens_multiindex_columns() -> None:
    with patch("data.fetch.yf.download", return_value=_mock_multiindex_df()):
        df = fetch_ohlc("EURUSD", timeframe="H1")
    assert not isinstance(df.columns, pd.MultiIndex)
    assert "Open" in df.columns


# ---------------------------------------------------------------------------
# fetch_ohlc — default timeframe from config
# ---------------------------------------------------------------------------


def test_fetch_ohlc_uses_default_timeframe_when_none_given() -> None:
    """Should not raise for the valid default timeframe from config."""
    with patch("data.fetch.yf.download", return_value=_mock_ohlc_df()):
        df = fetch_ohlc("EURUSD", timeframe=None)
    assert len(df) > 0
