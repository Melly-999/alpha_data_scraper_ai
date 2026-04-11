"""Download OHLC market data."""

from __future__ import annotations

import logging

import pandas as pd
import yfinance as yf

from core.config import DEFAULT_TIMEFRAME

logger = logging.getLogger("trading.data")

# yfinance forex tickers use "=X"
_YF_FOREX_SUFFIX = "=X"

_TIMEFRAME_TO_INTERVAL: dict[str, str] = {
    "M1": "1m",
    "M5": "5m",
    "M15": "15m",
    "M30": "30m",
    "H1": "1h",
    "D1": "1d",
}


def _yahoo_ticker(symbol: str) -> str:
    s = symbol.strip().upper()
    if s.endswith(_YF_FOREX_SUFFIX):
        return s
    if "/" in s:
        base, quote = s.split("/", 1)
        return f"{base.strip()}{quote.strip()}{_YF_FOREX_SUFFIX}"
    if len(s) == 6 and s.isalpha():
        return f"{s[:3]}{s[3:]}{_YF_FOREX_SUFFIX}"
    return s


def fetch_ohlc(
    symbol: str,
    timeframe: str | None = None,
    *,
    bars: int = 120,
    period: str = "30d",
) -> pd.DataFrame:
    """
    Fetch recent OHLC bars for ``symbol`` (e.g. EURUSD or EUR/USD).

    Intraday history is limited by Yahoo; ``period`` may need widening for
    smaller intervals.
    """
    tf = timeframe or DEFAULT_TIMEFRAME
    interval = _TIMEFRAME_TO_INTERVAL.get(tf)
    if interval is None:
        raise ValueError(
            f"Unsupported timeframe {tf!r}; use one of {sorted(_TIMEFRAME_TO_INTERVAL)}"
        )

    ticker = _yahoo_ticker(symbol)
    logger.info(
        "Fetching OHLC ticker=%s interval=%s period=%s", ticker, interval, period
    )

    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        progress=False,
        auto_adjust=False,
    )
    if df.empty:
        raise RuntimeError(f"No data returned for {ticker}")

    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()
    time_col = next((c for c in ("Datetime", "Date", "index") if c in df.columns), None)
    if time_col and time_col != "datetime":
        df = df.rename(columns={time_col: "datetime"})

    df = df.dropna(subset=["Open", "High", "Low", "Close"], how="any")
    df = df.tail(max(bars, 11))

    return df[["Open", "High", "Low", "Close"]].copy()
