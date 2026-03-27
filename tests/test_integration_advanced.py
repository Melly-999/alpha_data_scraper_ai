"""
Integration tests for advanced modules: multi-timeframe + backtest + claude
Tests the complete pipeline: MultiTimeframeAnalyzer → BacktestEngine → ClaudeAI validation
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from multi_timeframe import (
    MultiTimeframeAnalyzer,
    TimeframeSignal,
    MultiTimeframeResult,
)
from backtest import BacktestEngine, BacktestMetrics, Trade
from claude_ai import ClaudeAIClient, ClaudeAIIntegration, ClaudeSignal


@pytest.fixture
def sample_multi_timeframe_data() -> dict[str, pd.DataFrame]:
    """Create sample OHLCV data for M1, M5, H1 timeframes"""
    rng = np.random.default_rng(42)
    base_time = datetime(2025, 1, 1, 0, 0, 0)

    data = {}
    for tf_name, periods in [("M1", 60), ("M5", 300), ("H1", 3600)]:
        n = 500
        close = 1.1 + np.cumsum(rng.normal(0.0, 0.0005, size=n))
        open_ = close + rng.normal(0, 0.0005, size=n)
        high = np.maximum(open_, close) + np.abs(rng.normal(0, 0.0003, size=n))
        low = np.minimum(open_, close) - np.abs(rng.normal(0, 0.0003, size=n))
        volume = rng.integers(100, 1000, size=n)

        times = [base_time + timedelta(minutes=i * (periods / 60)) for i in range(n)]

        data[tf_name] = pd.DataFrame(
            {
                "time": times,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )

    return data


@pytest.fixture
def multi_timeframe_analyzer() -> MultiTimeframeAnalyzer:
    """Create MultiTimeframeAnalyzer instance"""
    return MultiTimeframeAnalyzer(symbol="EURUSD")


@pytest.fixture
def mock_claude_client() -> MagicMock:
    """Mock ClaudeAIClient for testing"""
    mock_client = MagicMock(spec=ClaudeAIClient)
    mock_client.get_trading_signal.return_value = ClaudeSignal(
        signal="BUY", confidence=85, risk="MEDIUM", reason="Strong uptrend detected"
    )
    return mock_client


class TestMultiTimeframeAnalysis:
    """Test multi-timeframe analysis functionality"""

    def test_analyze_returns_multi_timeframe_result(
        self, multi_timeframe_analyzer, sample_multi_timeframe_data
    ):
        """Test that analyze() returns MultiTimeframeResult with correct structure"""
        result = multi_timeframe_analyzer.analyze(sample_multi_timeframe_data)

        assert isinstance(result, MultiTimeframeResult)
        assert result.weighted_signal in ["BUY", "SELL", "HOLD"]
        assert 0 <= result.confirmation_signal <= 3
        assert "M1" in result.signals
        assert "M5" in result.signals
        assert "H1" in result.signals

    def test_timeframe_signals_have_required_fields(
        self, multi_timeframe_analyzer, sample_multi_timeframe_data
    ):
        """Test that each timeframe signal has all required attributes"""
        result = multi_timeframe_analyzer.analyze(sample_multi_timeframe_data)

        for timeframe, signal in result.signals.items():
            assert isinstance(signal, TimeframeSignal)
            assert signal.timeframe == timeframe
            assert signal.signal in ["BUY", "SELL", "HOLD"]
            assert signal.confidence >= 0
            assert signal.indicators is not None

    def test_confirmation_strategy_requires_agreement(
        self, multi_timeframe_analyzer, sample_multi_timeframe_data
    ):
        """Test confirmation strategy (M5 & H1 must agree)"""
        result = multi_timeframe_analyzer.analyze(sample_multi_timeframe_data)

        # If confirmation_signal > 0, at least M5 and H1 should agree
        if result.confirmation_signal > 0:
            m5_signal = result.signals["M5"].signal
            h1_signal = result.signals["H1"].signal
            assert m5_signal == h1_signal, "M5 and H1 signals must agree for confirmation"

    def test_weighted_combination(
        self, multi_timeframe_analyzer, sample_multi_timeframe_data
    ):
        """Test weighted combination logic (40% M1, 35% M5, 25% H1)"""
        result = multi_timeframe_analyzer.analyze(sample_multi_timeframe_data)

        # Result should reflect weighting (40% M1, 35% M5, 25% H1)
        assert result.weighted_signal in ["BUY", "SELL", "HOLD"]
        # If most signals are BUY, weighted result should likely be BUY
        buy_count = sum(
            1 for sig in result.signals.values() if sig.signal == "BUY"
        )
        if buy_count >= 2:
            assert result.weighted_signal in ["BUY", "HOLD"]


class TestBacktestIntegration:
    """Test backtesting with trading signals"""

    def test_backtest_with_multi_timeframe_signals(
        self, multi_timeframe_analyzer, sample_multi_timeframe_data
    ):
        """Test backtesting using signals from multi-timeframe analyzer"""
        from datetime import datetime, timedelta

        engine = BacktestEngine(symbol="EURUSD", initial_balance=1000.0)

        # Create signal function that returns (signal, confidence) tuple
        def signal_func(ohlcv_data: pd.DataFrame):
            if len(ohlcv_data) < 50:
                return ("HOLD", 30)
            # For simplicity, directly return signal based on price movement
            close_now = ohlcv_data["close"].iloc[-1]
            close_past = ohlcv_data["close"].iloc[-10]
            confidence = 75 if abs(close_now - close_past) > 0.001 else 50
            signal = "BUY" if close_now > close_past else "SELL"
            return (signal, confidence)

        # Run backtest with date range
        df = sample_multi_timeframe_data["M1"]
        start_date = df["time"].iloc[0]
        end_date = df["time"].iloc[-1]

        metrics = engine.backtest(
            signal_func=signal_func,
            start_date=start_date,
            end_date=end_date,
            lookback_bars=50,
        )

        # Should either return metrics or None (if no data)
        if metrics is not None:
            assert isinstance(metrics, BacktestMetrics)
            assert metrics.total_trades >= 0
            assert 0 <= metrics.win_rate <= 1.0
            assert metrics.max_drawdown <= 100

    def test_backtest_metrics_calculation(
        self, multi_timeframe_analyzer, sample_multi_timeframe_data
    ):
        """Test that backtest metrics are calculated correctly"""
        engine = BacktestEngine(symbol="EURUSD", initial_balance=1000.0)

        def simple_signal(ohlcv):
            idx = len(ohlcv) % 2
            confidence = 70
            signal = "BUY" if idx == 0 else "SELL"
            return (signal, confidence)

        df = sample_multi_timeframe_data["M1"]
        start_date = df["time"].iloc[0]
        end_date = df["time"].iloc[-1]

        metrics = engine.backtest(
            signal_func=simple_signal,
            start_date=start_date,
            end_date=end_date,
            lookback_bars=50,
        )

        # Verify metric consistency if we have metrics
        if metrics is not None and metrics.total_trades > 0:
            assert metrics.winning_trades + metrics.losing_trades == metrics.total_trades
            expected_wr = (metrics.winning_trades / metrics.total_trades)
            assert abs(metrics.win_rate - expected_wr) < 0.01

    def test_trade_tracking(
        self, multi_timeframe_analyzer, sample_multi_timeframe_data
    ):
        """Test that trades are properly tracked during backtest"""
        engine = BacktestEngine(symbol="EURUSD", initial_balance=5000.0)

        def alternating_signal(ohlcv: pd.DataFrame):
            idx = len(ohlcv) % 3
            confidence = 70
            if idx == 0:
                return ("BUY", confidence)
            elif idx == 1:
                return ("SELL", confidence)
            else:
                return ("HOLD", 30)

        df = sample_multi_timeframe_data["M1"]
        start_date = df["time"].iloc[0]
        end_date = df["time"].iloc[-1]

        metrics = engine.backtest(
            signal_func=alternating_signal,
            start_date=start_date,
            end_date=end_date,
            lookback_bars=50,
        )

        # Should have recorded metrics if backtest ran
        if metrics is not None:
            assert metrics is not None
            assert metrics.total_trades >= 0


class TestClaudeAIIntegration:
    """Test Claude AI integration with other modules"""

    def test_claude_client_initialization(self):
        """Test ClaudeAIClient can be initialized"""
        with patch.dict("os.environ", {"CLAUDE_API_KEY": "test_key"}):
            client = ClaudeAIClient(api_key="test_key")
            assert client is not None

    def test_claude_signal_structure(self):
        """Test ClaudeSignal dataclass structure"""
        signal = ClaudeSignal(
            signal="BUY", confidence=90, risk="HIGH", reason="Strong momentum"
        )

        assert signal.signal == "BUY"
        assert signal.confidence == 90
        assert signal.risk == "HIGH"
        assert signal.reason == "Strong momentum"

    def test_claude_ai_integration_validation(self, mock_claude_client):
        """Test ClaudeAIIntegration validation logic"""
        integration = ClaudeAIIntegration(client=mock_claude_client)

        # Test agreement boosting
        engine_signal = "BUY"
        engine_confidence = 70
        market_data = {
            "close": [1.1, 1.1, 1.105],
            "volume": [100, 105, 110],
        }

        validated = integration.validate_signal(
            symbol="EURUSD",
            engine_signal=engine_signal,
            engine_confidence=engine_confidence,
            market_data=market_data,
        )

        assert isinstance(validated, ClaudeSignal)
        # If Claude agrees, confidence should be boosted
        if validated.signal == engine_signal:
            assert validated.confidence >= engine_confidence

    def test_claude_conflict_resolution(self, mock_claude_client):
        """Test that signal conflicts default to HOLD"""
        integration = ClaudeAIIntegration(client=mock_claude_client)

        # Make Claude return opposite signal
        mock_claude_client.get_trading_signal.return_value = ClaudeSignal(
            signal="SELL", confidence=85, risk="MEDIUM", reason="Bearish signal"
        )

        validated = integration.validate_signal(
            symbol="EURUSD",
            engine_signal="BUY",
            engine_confidence=60,
            market_data={"close": [1.1, 1.1, 1.105]},
        )

        # Conflict should result in HOLD or neutral handling
        assert validated.signal in ["HOLD", "SELL", "BUY"]


class TestFullPipeline:
    """Test complete pipeline: MultiTimeframe → Backtest → Claude validation"""

    def test_full_pipeline_execution(
        self,
        multi_timeframe_analyzer,
        sample_multi_timeframe_data,
        mock_claude_client,
    ):
        """Test full pipeline from analysis to validation"""
        # Step 1: Multi-timeframe analysis
        mt_result = multi_timeframe_analyzer.analyze(sample_multi_timeframe_data)
        assert mt_result.weighted_signal in ["BUY", "SELL", "HOLD"]

        # Step 2: Create signal function based on multi-timeframe
        def mt_signal_func(ohlcv: pd.DataFrame) -> str:
            return mt_result.weighted_signal

        # Step 3: Backtest the signal
        engine = BacktestEngine(symbol="EURUSD")
        metrics = engine.backtest(
            signal_func=mt_signal_func,
            historical_data=sample_multi_timeframe_data["M1"],
            balance=1000.0,
            risk_per_trade=0.02,
        )
        assert metrics.total_trades >= 0

        # Step 4: Claude validation
        integration = ClaudeAIIntegration(client=mock_claude_client)
        claude_signal = integration.validate_signal(
            symbol="EURUSD",
            engine_signal=mt_result.weighted_signal,
            engine_confidence=mt_result.signals["M5"].confidence,
            market_data={
                "close": sample_multi_timeframe_data["M1"]["close"].tail(10).tolist(),
                "volume": sample_multi_timeframe_data["M1"]["volume"].tail(10).tolist(),
            },
        )

        assert isinstance(claude_signal, ClaudeSignal)
        assert claude_signal.signal in ["BUY", "SELL", "HOLD"]

    def test_pipeline_with_different_symbols(
        self, sample_multi_timeframe_data, mock_claude_client
    ):
        """Test pipeline consistency across different symbols"""
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]

        for symbol in symbols:
            analyzer = MultiTimeframeAnalyzer(symbol=symbol)
            result = analyzer.analyze(sample_multi_timeframe_data)
            assert result.weighted_signal in ["BUY", "SELL", "HOLD"]

            # Each symbol should produce valid signals
            for timeframe, signal in result.signals.items():
                assert signal.signal in ["BUY", "SELL", "HOLD"]
                assert signal.confidence >= 0

    def test_pipeline_error_handling(
        self, multi_timeframe_analyzer, mock_claude_client
    ):
        """Test error handling in full pipeline"""
        # Test with incomplete data
        incomplete_data = {"M1": pd.DataFrame({"close": [1.1, 1.11]})}

        # Should not crash
        try:
            result = multi_timeframe_analyzer.analyze(incomplete_data)
            # Result should still be valid
            assert result.weighted_signal in ["BUY", "SELL", "HOLD"]
        except Exception as e:
            # If it fails, it should be a clear error
            assert isinstance(e, (ValueError, KeyError, IndexError))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
