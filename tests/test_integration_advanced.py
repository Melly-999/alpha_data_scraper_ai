"""
Advanced integration tests for trading pipeline modules.

Tests multi_timeframe + backtest + claude_ai together using mocks.
No live network calls, no MetaTrader5 required — runs in CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional, Tuple
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Module-level stubs so tests run without MetaTrader5 installed on Linux CI
# ---------------------------------------------------------------------------
if "MetaTrader5" not in sys.modules:
    mt5_stub = MagicMock()
    mt5_stub.TIMEFRAME_M1 = 1
    mt5_stub.TIMEFRAME_M5 = 5
    mt5_stub.TIMEFRAME_H1 = 16388
    sys.modules["MetaTrader5"] = mt5_stub

from multi_timeframe import (  # noqa: E402
    MultiTimeframeAnalyzer,
    TimeframeSignal,
    MultiTimeframeResult,
)
from backtest import BacktestEngine, BacktestMetrics, Trade  # noqa: E402
from claude_ai import ClaudeAIClient, ClaudeAIIntegration, ClaudeSignal  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ohlcv(n: int = 300, seed: int = 42) -> pd.DataFrame:
    """Deterministic OHLCV DataFrame."""
    rng = np.random.default_rng(seed)
    close = 1.1 + np.cumsum(rng.normal(0.0, 0.0008, n))
    open_ = close + rng.normal(0, 0.0004, n)
    high = np.maximum(open_, close) + np.abs(rng.normal(0, 0.0003, n))
    low = np.minimum(open_, close) - np.abs(rng.normal(0, 0.0003, n))
    start = datetime(2025, 1, 1)
    return pd.DataFrame(
        {
            "time": [start + timedelta(minutes=i) for i in range(n)],
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": rng.integers(100, 1000, n),
        }
    )


def _make_indicators(
    rsi: float = 45.0,
    macd_hist: float = 0.001,
    bb_pos: float = 0.3,
    slope: float = 0.0002,
) -> Dict[str, float]:
    return {"rsi": rsi, "macd_hist": macd_hist, "bb_position": bb_pos, "slope": slope}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ohlcv() -> pd.DataFrame:
    return _make_ohlcv(300)


@pytest.fixture
def indicator_data() -> Dict[str, Dict]:
    """Pre-computed indicator data for M1/M5/H1 — no MT5 needed."""
    return {
        "M1": _make_indicators(rsi=42, macd_hist=0.002, bb_pos=0.25, slope=0.0003),
        "M5": _make_indicators(rsi=40, macd_hist=0.003, bb_pos=0.30, slope=0.0004),
        "H1": _make_indicators(rsi=38, macd_hist=0.004, bb_pos=0.20, slope=0.0005),
    }


@pytest.fixture
def bearish_indicator_data() -> Dict[str, Dict]:
    return {
        "M1": _make_indicators(rsi=72, macd_hist=-0.003, bb_pos=0.85, slope=-0.0005),
        "M5": _make_indicators(rsi=68, macd_hist=-0.002, bb_pos=0.80, slope=-0.0004),
        "H1": _make_indicators(rsi=70, macd_hist=-0.004, bb_pos=0.90, slope=-0.0006),
    }


@pytest.fixture
def mtf_analyzer() -> MultiTimeframeAnalyzer:
    return MultiTimeframeAnalyzer(symbol="EURUSD")


class TestMultiTimeframeAnalysis:
    """Test multi-timeframe analysis functionality"""


# ---------------------------------------------------------------------------
# 1. MultiTimeframeAnalyzer tests
# ---------------------------------------------------------------------------


class TestMultiTimeframeAnalysis:
    """Test multi-timeframe analysis functionality."""

    def test_returns_result_dataclass(self, mtf_analyzer, indicator_data):
        result = mtf_analyzer.analyze(indicator_data)
        assert isinstance(result, MultiTimeframeResult)

    def test_weighted_signal_is_valid(self, mtf_analyzer, indicator_data):
        result = mtf_analyzer.analyze(indicator_data)
        assert result.weighted_signal in {"BUY", "SELL", "HOLD"}

    def test_confirmation_signal_is_string(self, mtf_analyzer, indicator_data):
        result = mtf_analyzer.analyze(indicator_data)
        assert result.confirmation_signal in {"BUY", "SELL", "HOLD"}

    def test_confirmation_strength_range(self, mtf_analyzer, indicator_data):
        result = mtf_analyzer.analyze(indicator_data)
        assert 0 <= result.confirmation_strength <= 3

    def test_all_timeframes_present(self, mtf_analyzer, indicator_data):
        result = mtf_analyzer.analyze(indicator_data)
        for tf in ("M1", "M5", "H1"):
            assert tf in result.signals

    def test_each_signal_is_valid(self, mtf_analyzer, indicator_data):
        result = mtf_analyzer.analyze(indicator_data)
        for tf, sig in result.signals.items():
            assert isinstance(sig, TimeframeSignal)
            assert sig.timeframe == tf
            assert sig.signal in {"BUY", "SELL", "HOLD"}
            assert 0 <= sig.confidence <= 100

    def test_bullish_indicators_produce_buy_or_hold(self, mtf_analyzer, indicator_data):
        """Strongly oversold RSI + positive MACD should lean BUY, not SELL."""
        result = mtf_analyzer.analyze(indicator_data)
        assert result.weighted_signal in {"BUY", "HOLD"}

    def test_bearish_indicators_produce_sell_or_hold(self, mtf_analyzer, bearish_indicator_data):
        """Strongly overbought RSI + negative MACD should lean SELL, not BUY."""
        result = mtf_analyzer.analyze(bearish_indicator_data)
        assert result.weighted_signal in {"SELL", "HOLD"}

    def test_confirmation_requires_m5_h1_agreement(self, mtf_analyzer, indicator_data):
        """Confirmation signal only fires when M5 & H1 agree."""
        result = mtf_analyzer.analyze(indicator_data)
        if result.confirmation_signal != "HOLD":
            assert result.signals["M5"].signal == result.signals["H1"].signal

    def test_missing_h1_handled_gracefully(self, mtf_analyzer):
        """Partial indicator data (no H1) should not raise."""
        partial = {
            "M1": _make_indicators(),
            "M5": _make_indicators(),
        }
        result = mtf_analyzer.analyze(partial)
        assert result.weighted_signal in {"BUY", "SELL", "HOLD"}

    def test_different_symbols(self):
        """Analyzer instantiates for multiple symbols without error."""
        for sym in ("EURUSD", "GBPUSD", "USDJPY", "XAUUSD"):
            analyzer = MultiTimeframeAnalyzer(symbol=sym)
            result = analyzer.analyze(
                {
                    "M1": _make_indicators(),
                    "M5": _make_indicators(),
                    "H1": _make_indicators(),
                }
            )
            assert result.weighted_signal in {"BUY", "SELL", "HOLD"}

    def test_weights_sum_to_one(self, mtf_analyzer):
        total = sum(mtf_analyzer.weights.values())
        assert abs(total - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# 2. BacktestEngine tests (no MT5 — patches _fetch_historical_data)
# ---------------------------------------------------------------------------


class TestBacktestIntegration:
    """BacktestEngine.backtest() expects signal_func(df) → (signal, confidence)."""

    def _run(
        self,
        signal_fn: Callable[[pd.DataFrame], Tuple[str, float]],
        df: Optional[pd.DataFrame] = None,
        symbol: str = "EURUSD",
        balance: float = 1000.0,
    ) -> Optional[BacktestMetrics]:
        df = df if df is not None else _make_ohlcv()
        engine = BacktestEngine(symbol=symbol, initial_balance=balance)
        start = df["time"].iloc[0]
        end = df["time"].iloc[-1]
        with patch.object(engine, "_fetch_historical_data", return_value=df):
            return engine.backtest(
                signal_func=signal_fn,
                start_date=start,
                end_date=end,
                lookback_bars=50,
            )

    def test_returns_metrics_or_none(self, ohlcv):
        metrics = self._run(lambda df: ("BUY", 70), df=ohlcv)
        assert metrics is None or isinstance(metrics, BacktestMetrics)

    def test_win_rate_range(self, ohlcv):
        metrics = self._run(lambda df: ("BUY", 70), df=ohlcv)
        if metrics:
            assert 0.0 <= metrics.win_rate <= 1.0

    def test_max_drawdown_non_negative(self, ohlcv):
        metrics = self._run(lambda df: ("BUY", 70), df=ohlcv)
        if metrics:
            assert metrics.max_drawdown >= 0

    def test_trade_count_consistency(self, ohlcv):
        metrics = self._run(lambda df: ("BUY", 70), df=ohlcv)
        if metrics and metrics.total_trades > 0:
            assert metrics.winning_trades + metrics.losing_trades == metrics.total_trades

    def test_win_rate_formula(self, ohlcv):
        metrics = self._run(lambda df: ("BUY", 70), df=ohlcv)
        if metrics and metrics.total_trades > 0:
            expected = metrics.winning_trades / metrics.total_trades
            assert abs(metrics.win_rate - expected) < 0.01

    def test_hold_signal_no_trades(self, ohlcv):
        metrics = self._run(lambda df: ("HOLD", 50), df=ohlcv)
        if metrics:
            assert metrics.total_trades == 0

    def test_alternating_buy_sell(self, ohlcv):
        counter = {"n": 0}

        def alt(df):
            counter["n"] += 1
            return ("BUY", 75) if counter["n"] % 2 == 0 else ("SELL", 75)

        metrics = self._run(alt, df=ohlcv)
        assert metrics is None or isinstance(metrics, BacktestMetrics)

    def test_low_confidence_excluded(self, ohlcv):
        """Signals below 60% confidence threshold should not open positions."""
        metrics = self._run(lambda df: ("BUY", 30), df=ohlcv)
        if metrics:
            assert metrics.total_trades == 0

    def test_multiple_symbols_independent(self):
        for sym in ("EURUSD", "GBPUSD", "USDJPY"):
            df = _make_ohlcv(seed=hash(sym) % 1000)
            engine = BacktestEngine(symbol=sym, initial_balance=1000.0)
            start, end = df["time"].iloc[0], df["time"].iloc[-1]
            with patch.object(engine, "_fetch_historical_data", return_value=df):
                m = engine.backtest(
                    signal_func=lambda d: ("BUY", 75),
                    start_date=start,
                    end_date=end,
                    lookback_bars=50,
                )
            assert m is None or isinstance(m, BacktestMetrics)

    def test_summary_str_contains_key_fields(self, ohlcv):
        metrics = self._run(lambda df: ("BUY", 70), df=ohlcv)
        if metrics:
            summary = metrics.summary_str()
            assert "BACKTEST" in summary
            assert "Win Rate" in summary

    def test_backtest_with_multi_timeframe_signals(self, indicator_data, ohlcv):
        """Full flow: MTF → signal function → BacktestEngine."""
        analyzer = MultiTimeframeAnalyzer(symbol="EURUSD")
        mt_result = analyzer.analyze(indicator_data)
        chosen = mt_result.weighted_signal
        chosen_conf = mt_result.weighted_confidence

        def mt_signal_fn(df: pd.DataFrame) -> Tuple[str, float]:
            return (chosen, chosen_conf)

        engine = BacktestEngine(symbol="EURUSD", initial_balance=1000.0)
        start, end = ohlcv["time"].iloc[0], ohlcv["time"].iloc[-1]
        with patch.object(engine, "_fetch_historical_data", return_value=ohlcv):
            metrics = engine.backtest(
                signal_func=mt_signal_fn,
                start_date=start,
                end_date=end,
                lookback_bars=50,
            )
        assert metrics is None or isinstance(metrics, BacktestMetrics)


# ---------------------------------------------------------------------------
# 3. ClaudeAIClient tests (all network calls mocked)
# ---------------------------------------------------------------------------


class TestClaudeAIIntegration:
    """Test Claude AI client and integration layer."""

    def test_client_init_with_api_key(self):
        client = ClaudeAIClient(api_key="test-key")
        assert client.api_key == "test-key"

    def test_client_init_from_env(self, monkeypatch):
        monkeypatch.setenv("CLAUDE_API_KEY", "env-key")
        client = ClaudeAIClient()
        assert client.api_key == "env-key"

    def test_missing_key_raises(self, monkeypatch):
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        with pytest.raises(ValueError):
            ClaudeAIClient()

    def test_claude_signal_dataclass(self):
        sig = ClaudeSignal(signal="BUY", confidence=90, risk="HIGH", reason="Strong momentum")
        assert sig.signal == "BUY"
        assert sig.confidence == 90
        assert sig.risk == "HIGH"

    def test_get_signal_buy(self):
        raw = json.dumps({"signal": "BUY", "confidence": 80, "risk": "MEDIUM", "reason": "RSI oversold"})
        client = ClaudeAIClient(api_key="test")
        with patch.object(client, "_call_api", return_value=raw):
            sig = client.get_trading_signal({"symbol": "EURUSD", "rsi": 35.0})
        assert isinstance(sig, ClaudeSignal)
        assert sig.signal == "BUY"
        assert sig.confidence == 80

    def test_get_signal_sell(self):
        raw = json.dumps({"signal": "SELL", "confidence": 75, "risk": "MEDIUM", "reason": "RSI overbought"})
        client = ClaudeAIClient(api_key="test")
        with patch.object(client, "_call_api", return_value=raw):
            sig = client.get_trading_signal({"symbol": "GBPUSD", "rsi": 75.0})
        assert sig.signal == "SELL"
        assert sig.confidence == 75

    def test_api_error_returns_none(self):
        client = ClaudeAIClient(api_key="test")
        with patch.object(client, "_call_api", return_value=None):
            sig = client.get_trading_signal({"symbol": "EURUSD"})
        assert sig is None

    def test_malformed_json_returns_hold(self):
        client = ClaudeAIClient(api_key="test")
        with patch.object(client, "_call_api", return_value="not valid json"):
            sig = client.get_trading_signal({"symbol": "EURUSD"})
        assert sig is not None
        assert sig.signal == "HOLD"
        assert sig.risk == "HIGH"

    def test_markdown_wrapped_json_parsed(self):
        """Claude sometimes wraps JSON in markdown code fences."""
        raw = '```json\n{"signal":"BUY","confidence":70,"risk":"LOW","reason":"ok"}\n```'
        client = ClaudeAIClient(api_key="test")
        with patch.object(client, "_call_api", return_value=raw):
            sig = client.get_trading_signal({"symbol": "EURUSD"})
        assert sig.signal == "BUY"

    def test_portfolio_signal_batch(self):
        raw_buy = json.dumps({"signal": "BUY", "confidence": 80, "risk": "MEDIUM", "reason": "ok"})
        client = ClaudeAIClient(api_key="test")
        portfolio = {
            "EURUSD": {"symbol": "EURUSD", "rsi": 35},
            "GBPUSD": {"symbol": "GBPUSD", "rsi": 40},
            "USDJPY": {"symbol": "USDJPY", "rsi": 38},
        }
        with patch.object(client, "_call_api", return_value=raw_buy):
            sigs = client.get_portfolio_signal(portfolio)
        assert sigs is not None
        assert len(sigs) == 3
        for sym in portfolio:
            assert sym in sigs
            assert isinstance(sigs[sym], ClaudeSignal)

    def test_integration_disabled_passthrough(self):
        integration = ClaudeAIIntegration(enabled=False)
        sig, conf, reason = integration.validate_signal(
            symbol="EURUSD",
            engine_signal="BUY",
            engine_confidence=75.0,
            market_data={},
        )
        assert sig == "BUY"
        assert conf == 75.0

    def test_integration_agreement_boosts_confidence(self):
        raw = json.dumps({"signal": "BUY", "confidence": 80, "risk": "MEDIUM", "reason": "agrees"})
        integration = ClaudeAIIntegration(api_key="test", enabled=True)
        with patch.object(integration.client, "_call_api", return_value=raw):
            sig, conf, reason = integration.validate_signal(
                symbol="EURUSD",
                engine_signal="BUY",
                engine_confidence=65.0,
                market_data={"symbol": "EURUSD", "rsi": 35.0},
            )
        assert sig == "BUY"
        assert conf > 65.0

    def test_integration_conflict_returns_hold(self):
        raw = json.dumps({"signal": "SELL", "confidence": 75, "risk": "MEDIUM", "reason": "bearish"})
        integration = ClaudeAIIntegration(api_key="test", enabled=True)
        with patch.object(integration.client, "_call_api", return_value=raw):
            sig, conf, reason = integration.validate_signal(
                symbol="EURUSD",
                engine_signal="BUY",
                engine_confidence=70.0,
                market_data={"symbol": "EURUSD"},
            )
        assert sig == "HOLD"
        assert "Conflict" in reason

    def test_integration_claude_failure_falls_back(self):
        integration = ClaudeAIIntegration(api_key="test", enabled=True)
        with patch.object(integration.client, "_call_api", return_value=None):
            sig, conf, reason = integration.validate_signal(
                symbol="EURUSD",
                engine_signal="SELL",
                engine_confidence=60.0,
                market_data={},
            )
        assert sig == "SELL"
        assert conf == 60.0

    def test_integration_independent_signal(self):
        raw = json.dumps({"signal": "BUY", "confidence": 80, "risk": "MEDIUM", "reason": "ok"})
        integration = ClaudeAIIntegration(api_key="test", enabled=True)
        with patch.object(integration.client, "_call_api", return_value=raw):
            sig = integration.get_independent_signal({"symbol": "EURUSD", "rsi": 32})
        assert isinstance(sig, ClaudeSignal)
        assert sig.signal == "BUY"

    def test_integration_independent_signal_disabled(self):
        integration = ClaudeAIIntegration(enabled=False)
        assert integration.get_independent_signal({}) is None


# ---------------------------------------------------------------------------
# 4. Full pipeline integration test
# ---------------------------------------------------------------------------


class TestFullPipeline:
    """Multi-timeframe → Backtest → Claude — all with mocks."""

    def test_pipeline_produces_valid_output(self, indicator_data, ohlcv):
        # Step 1: multi-timeframe
        analyzer = MultiTimeframeAnalyzer(symbol="EURUSD")
        mt_result = analyzer.analyze(indicator_data)
        assert mt_result.weighted_signal in {"BUY", "SELL", "HOLD"}

        # Step 2: backtest using that signal
        engine = BacktestEngine(symbol="EURUSD", initial_balance=1000.0)
        chosen = mt_result.weighted_signal

        def mt_fn(df: pd.DataFrame) -> Tuple[str, float]:
            return (chosen, mt_result.weighted_confidence)

        start, end = ohlcv["time"].iloc[0], ohlcv["time"].iloc[-1]
        with patch.object(engine, "_fetch_historical_data", return_value=ohlcv):
            metrics = engine.backtest(
                signal_func=mt_fn,
                start_date=start,
                end_date=end,
                lookback_bars=50,
            )
        assert metrics is None or isinstance(metrics, BacktestMetrics)

        # Step 3: Claude validation
        raw = json.dumps(
            {"signal": chosen, "confidence": 78, "risk": "MEDIUM", "reason": "agrees"}
        )
        integration = ClaudeAIIntegration(api_key="test")
        with patch.object(integration.client, "_call_api", return_value=raw):
            final_sig, final_conf, reason = integration.validate_signal(
                symbol="EURUSD",
                engine_signal=chosen,
                engine_confidence=mt_result.weighted_confidence,
                market_data={"symbol": "EURUSD", "rsi": indicator_data["M1"]["rsi"]},
            )
        assert final_sig in {"BUY", "SELL", "HOLD"}
        assert isinstance(final_conf, float)

    def test_bearish_pipeline(self, bearish_indicator_data):
        analyzer = MultiTimeframeAnalyzer(symbol="GBPUSD")
        mt_result = analyzer.analyze(bearish_indicator_data)
        assert mt_result.weighted_signal in {"SELL", "HOLD"}

    def test_pipeline_holds_on_disagreement(self, indicator_data):
        """Engine says BUY, Claude says SELL → final must be HOLD."""
        raw = json.dumps(
            {"signal": "SELL", "confidence": 80, "risk": "HIGH", "reason": "counter"}
        )
        integration = ClaudeAIIntegration(api_key="test")
        with patch.object(integration.client, "_call_api", return_value=raw):
            final_sig, _, reason = integration.validate_signal(
                symbol="EURUSD",
                engine_signal="BUY",
                engine_confidence=70.0,
                market_data={"symbol": "EURUSD"},
            )
        assert final_sig == "HOLD"

    def test_pipeline_with_ten_symbols(self):
        symbols = [
            "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY",
            "XAUUSD", "WTI", "NVDA", "GOOGL", "USTECH100",
        ]
        for sym in symbols:
            analyzer = MultiTimeframeAnalyzer(symbol=sym)
            result = analyzer.analyze(
                {
                    "M1": _make_indicators(rsi=50, macd_hist=0.0, bb_pos=0.5, slope=0.0),
                    "M5": _make_indicators(rsi=50, macd_hist=0.0, bb_pos=0.5, slope=0.0),
                    "H1": _make_indicators(rsi=50, macd_hist=0.0, bb_pos=0.5, slope=0.0),
                }
            )
            assert result.weighted_signal in {"BUY", "SELL", "HOLD"}

    def test_pipeline_error_handling_incomplete_data(self, mtf_analyzer):
        """Incomplete dict (no H1) should not crash the pipeline."""
        partial = {
            "M1": _make_indicators(),
            "M5": _make_indicators(),
        }
        result = mtf_analyzer.analyze(partial)
        assert result.weighted_signal in {"BUY", "SELL", "HOLD"}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
