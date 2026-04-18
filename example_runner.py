#!/usr/bin/env python
"""
Example runner: Complete trading pipeline
AIEngine → Multi-timeframe → News Sentiment → Claude AI → Backtest → Execution

This script demonstrates the full workflow of the trading system:
1. Fetch market data for multiple symbols
2. Run multi-timeframe analysis (M1/M5/H1)
3. Get news sentiment analysis
4. Use AIEngine to generate unified signals
5. Validate signals with Claude AI
6. Run backtest to validate strategy
7. Execute trades (demo mode)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None  # For non-Windows systems

from ai_engine import AIEngine, EngineConfig
from multi_timeframe import MultiTimeframeAnalyzer
from news_sentiment import ForexFactoryScraper, NewsAPIClient
from backtest import BacktestEngine, BacktestMetrics
from claude_ai import ClaudeAIClient, ClaudeAIIntegration
from calculator import position_size

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("trading_pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class TradingPipelineRunner:
    """Complete trading pipeline orchestrator"""

    def __init__(
        self,
        symbols: list[str],
        config_file: str = "config.json",
        api_keys: dict[str, str] | None = None,
    ):
        """
        Initialize pipeline runner

        Args:
            symbols: List of trading symbols (e.g., ["EURUSD", "GBPUSD"])
            config_file: Path to config file
            api_keys: Dict with 'claude_api_key' and 'newsapi_key'
        """
        self.symbols = symbols
        self.config = self._load_config(config_file)
        self.api_keys = api_keys or {}
        self.backtest_results: dict[str, BacktestMetrics] = {}

        logger.info(f"Pipeline initialized with symbols: {symbols}")

        # Initialize MT5 if available
        self._init_mt5()

    def _load_config(self, config_file: str) -> dict[str, Any]:
        """Load configuration from file"""
        if Path(config_file).exists():
            with open(config_file, encoding="utf-8") as f:
                return json.load(f)
        return {
            "timeframes": ["M1", "M5", "H1"],
            "weights": {"M1": 0.4, "M5": 0.35, "H1": 0.25},
            "backtest_days": 5,
            "balance": 1000.0,
            "risk_per_trade": 0.02,
            "demo_mode": True,
        }

    def _init_mt5(self) -> bool:
        """Initialize MetaTrader5 connection"""
        if mt5 is None:
            logger.warning("MetaTrader5 not available (non-Windows system)")
            return False

        if not mt5.initialize():
            logger.error("Failed to initialize MT5")
            return False

        logger.info(f"MT5 initialized. Account: {mt5.account_info()}")
        return True

    def step_1_fetch_market_data(self) -> dict[str, dict]:
        """
        Step 1: Fetch current market data for all symbols
        Returns dict: {symbol -> {timeframe -> OHLCV data}}
        """
        logger.info("=" * 60)
        logger.info("STEP 1: Fetching Market Data")
        logger.info("=" * 60)

        market_data = {}
        for symbol in self.symbols:
            logger.info(f"Fetching data for {symbol}")
            symbol_data = {}

            if mt5 is None:
                # Mock data for demo
                logger.info(f"  [DEMO] Using mock data for {symbol}")
                symbol_data["M1"] = self._get_mock_ohlcv(symbol, 100)
                symbol_data["M5"] = self._get_mock_ohlcv(symbol, 100)
                symbol_data["H1"] = self._get_mock_ohlcv(symbol, 100)
            else:
                # Real MT5 data
                try:
                    for tf in ["M1", "M5", "H1"]:
                        tf_val = getattr(mt5, f"TIMEFRAME_{tf}")
                        rates = mt5.copy_rates_symbol(symbol, tf_val, 0, 100)
                        symbol_data[tf] = self._convert_mt5_rates(rates)
                except Exception as e:
                    logger.error(f"Error fetching {symbol} {tf}: {e}")
                    symbol_data[tf] = self._get_mock_ohlcv(symbol, 100)

            market_data[symbol] = symbol_data
            logger.info(f"  ✓ Fetched {symbol}")

        return market_data

    def step_2_multi_timeframe_analysis(
        self, market_data: dict[str, dict]
    ) -> dict[str, Any]:
        """
        Step 2: Run multi-timeframe analysis (M1/M5/H1)
        Returns dict: {symbol -> analysis result}
        """
        logger.info("=" * 60)
        logger.info("STEP 2: Multi-Timeframe Analysis (M1/M5/H1)")
        logger.info("=" * 60)

        results = {}
        for symbol in self.symbols:
            logger.info(f"Analyzing {symbol}")
            analyzer = MultiTimeframeAnalyzer(symbol=symbol)

            try:
                indicators_by_tf = {
                    tf: self._frame_to_indicator_snapshot(frame)
                    for tf, frame in market_data[symbol].items()
                }
                result = analyzer.analyze(indicators_by_tf)
                results[symbol] = result
                logger.info(
                    f"  Weighted Signal: {result.weighted_signal} "
                    f"(Confirmation: {result.confirmation_signal})"
                )
                for tf, sig in result.signals.items():
                    logger.info(
                        f"    {tf}: {sig.signal} (confidence: {sig.confidence:.1f})"
                    )
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                results[symbol] = None

        return results

    def step_3_news_sentiment(self) -> dict[str, Any]:
        """
        Step 3: Fetch and analyze news sentiment
        Returns dict: {symbol -> sentiment analysis}
        """
        logger.info("=" * 60)
        logger.info("STEP 3: News Sentiment Analysis")
        logger.info("=" * 60)

        sentiment_results = {}
        newsapi_key = self.api_keys.get("newsapi_key")

        try:
            # ForexFactory economic calendar
            logger.info("Fetching ForexFactory economic calendar...")
            scraper = ForexFactoryScraper()
            calendar_events = scraper.fetch_calendar()
            logger.info(f"  ✓ Found {len(calendar_events)} events")

            # NewsAPI news
            if newsapi_key:
                logger.info("Fetching NewsAPI articles...")
                news_client = NewsAPIClient(api_key=newsapi_key)
                for symbol in self.symbols:
                    try:
                        news = news_client.fetch_forex_news(
                            currencies=[symbol[:3], symbol[3:6]], limit=10
                        )
                        sentiment_results[symbol] = news
                        logger.info(f"  ✓ {symbol}: {len(news)} articles")
                    except Exception as e:
                        logger.warning(f"Error fetching news for {symbol}: {e}")
                        sentiment_results[symbol] = []
            else:
                logger.warning("NewsAPI key not provided, skipping news sentiment")

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")

        return sentiment_results

    def step_4_ai_engine_unified_signals(self, mt_results: dict) -> dict[str, Any]:
        """
        Step 4: Use AIEngine to generate unified signals
        Returns dict: {symbol -> unified signal}
        """
        logger.info("=" * 60)
        logger.info("STEP 4: AI Engine Unified Signals")
        logger.info("=" * 60)

        engine_config = EngineConfig(
            symbols=self.symbols,
            timeframe="M1",
            weights=self.config.get("weights", {}),
            min_confidence_threshold=60,
            update_interval_seconds=60,
        )

        engine = AIEngine(config=engine_config)

        signal_map = engine.analyze_all()
        unified_signals = {}
        for symbol in self.symbols:
            logger.info(f"Generating unified signal for {symbol}")
            if symbol in signal_map:
                unified_signals[symbol] = signal_map[symbol]
                logger.info(f"  Signal: {signal_map[symbol].primary_signal}")
                logger.info(f"  Confidence: {signal_map[symbol].confidence:.1f}")
            else:
                logger.warning(f"No signal generated for {symbol}")

        return unified_signals

    def step_5_claude_validation(
        self, market_data: dict[str, dict], unified_signals: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Step 5: Validate signals with Claude AI
        Returns dict: {symbol -> claude validated signal}
        """
        logger.info("=" * 60)
        logger.info("STEP 5: Claude AI Validation")
        logger.info("=" * 60)

        claude_key = self.api_keys.get("claude_api_key")
        if not claude_key:
            logger.warning("Claude API key not provided, skipping Claude validation")
            return unified_signals

        try:
            claude_client = ClaudeAIClient(api_key=claude_key)
            claude_integration = ClaudeAIIntegration(client=claude_client)

            validated_signals = {}
            for symbol in self.symbols:
                logger.info(f"Validating {symbol} with Claude")

                if symbol not in unified_signals:
                    logger.warning(f"No signal to validate for {symbol}")
                    continue

                engine_signal = unified_signals[symbol]
                try:
                    validated = claude_integration.validate_signal(
                        symbol=symbol,
                        engine_signal=self._signal_value(engine_signal),
                        engine_confidence=self._signal_confidence(engine_signal),
                        market_data={
                            "close": (
                                market_data[symbol]["M1"]["close"].tail(10).tolist()
                                if "M1" in market_data[symbol]
                                else []
                            ),
                        },
                    )
                    validated_signals[symbol] = validated
                    logger.info(
                        f"  Claude Signal: {validated.signal} (conf: {validated.confidence})"
                    )
                except Exception as e:
                    logger.error(f"Error validating {symbol}: {e}")
                    validated_signals[symbol] = engine_signal

            return validated_signals

        except Exception as e:
            logger.error(f"Error initializing Claude: {e}")
            return unified_signals

    def step_6_backtesting(
        self, market_data: dict[str, dict], validated_signals: dict
    ) -> dict[str, BacktestMetrics]:
        """
        Step 6: Backtest signals on historical data
        Returns dict: {symbol -> backtest metrics}
        """
        logger.info("=" * 60)
        logger.info("STEP 6: Backtesting")
        logger.info("=" * 60)

        backtest_results = {}
        balance = self.config.get("balance", 1000.0)
        risk_pct = self.config.get("risk_per_trade", 0.02)

        for symbol in self.symbols:
            logger.info(f"Backtesting {symbol}")
            if symbol not in market_data:
                logger.warning(f"No market data for {symbol}")
                continue

            try:
                engine = BacktestEngine(symbol=symbol)

                # Create signal function from validated signal
                if symbol in validated_signals:
                    signal_val = self._signal_value(validated_signals[symbol])
                    confidence_val = self._signal_confidence(validated_signals[symbol])

                    def signal_func(ohlcv):
                        return signal_val, confidence_val

                else:

                    def signal_func(ohlcv):
                        return "HOLD", 50.0

                # Run backtest
                metrics = engine.backtest(
                    signal_func=signal_func,
                    historical_data=market_data[symbol].get("M1"),
                    balance=balance,
                    risk_per_trade=risk_pct,
                )

                backtest_results[symbol] = metrics
                logger.info("  Backtest Results:")
                logger.info(f"    Win Rate: {metrics.win_rate:.1f}%")
                logger.info(f"    Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
                logger.info(f"    Max Drawdown: {metrics.max_drawdown:.1f}%")
                logger.info(f"    Total Return: {metrics.total_return:.2f}%")

            except Exception as e:
                logger.error(f"Error backtesting {symbol}: {e}")

        self.backtest_results = backtest_results
        return backtest_results

    def step_7_execution_simulation(self, validated_signals: dict):
        """
        Step 7: Simulate trade execution (demo mode)
        """
        logger.info("=" * 60)
        logger.info("STEP 7: Trade Execution (Demo Mode)")
        logger.info("=" * 60)

        balance = self.config.get("balance", 1000.0)
        risk_pct = self.config.get("risk_per_trade", 0.02)

        for symbol, signal in validated_signals.items():
            signal_value = self._signal_value(signal)
            confidence = self._signal_confidence(signal)
            if signal_value == "HOLD":
                logger.info(f"{symbol}: HOLD (no action)")
                continue

            try:
                # Calculate position size
                lot_size = position_size(
                    balance=balance,
                    risk_pct=risk_pct,
                    sl_points=100,
                    point_value=10,
                )

                logger.info(f"{symbol}: {signal_value}")
                logger.info(f"  Confidence: {confidence}/100")
                logger.info(f"  Risk Level: {getattr(signal, 'risk', 'UNKNOWN')}")
                logger.info(f"  Lot Size: {lot_size:.2f}")
                logger.info(f"  Reason: {getattr(signal, 'reason', '')}")

                if not self.config.get("demo_mode", True):
                    logger.info(
                        f"  [EXECUTING] Would execute {signal_value} on {symbol}"
                    )
                    # Would execute here with actual MT5 order
                else:
                    logger.info(f"  [DEMO] Would execute {signal_value} on {symbol}")

            except Exception as e:
                logger.error(f"Error executing {symbol}: {e}")

    def run_full_pipeline(self) -> dict[str, Any]:
        """Execute complete pipeline"""
        logger.info("\n" + "=" * 60)
        logger.info("FULL TRADING PIPELINE")
        logger.info("=" * 60 + "\n")

        try:
            # Step 1: Fetch market data
            market_data = self.step_1_fetch_market_data()

            # Step 2: Multi-timeframe analysis
            mt_results = self.step_2_multi_timeframe_analysis(market_data)

            # Step 3: News sentiment
            sentiment_results = self.step_3_news_sentiment()

            # Step 4: AI Engine unified signals
            unified_signals = self.step_4_ai_engine_unified_signals(mt_results)

            # Step 5: Claude validation
            validated_signals = self.step_5_claude_validation(
                market_data, unified_signals
            )

            # Step 6: Backtesting
            backtest_results = self.step_6_backtesting(market_data, validated_signals)

            # Step 7: Execution simulation
            self.step_7_execution_simulation(validated_signals)

            # Summary
            self._print_summary(backtest_results)

            return {
                "market_data": market_data,
                "multi_timeframe_results": mt_results,
                "sentiment_results": sentiment_results,
                "unified_signals": unified_signals,
                "validated_signals": validated_signals,
                "backtest_results": backtest_results,
            }

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise

    def _print_summary(self, backtest_results: dict[str, BacktestMetrics]):
        """Print pipeline summary"""
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 60)

        for symbol, metrics in backtest_results.items():
            if metrics:
                logger.info(f"{symbol}:")
                logger.info(f"  Trades: {metrics.total_trades}")
                logger.info(f"  Win Rate: {metrics.win_rate:.1f}%")
                logger.info(f"  Sharpe: {metrics.sharpe_ratio:.2f}")
                logger.info(f"  Max DD: {metrics.max_drawdown:.1f}%")
                logger.info(f"  Return: {metrics.total_return:.2f}%")

    @staticmethod
    def _get_mock_ohlcv(symbol: str, periods: int):
        """Generate mock OHLCV data for demo"""
        import pandas as pd
        import numpy as np

        rng = np.random.default_rng(hash(symbol) % 1000)
        base_price = 1.1
        close = base_price + np.cumsum(rng.normal(0, 0.001, periods))
        open_ = close + rng.normal(0, 0.001, periods)
        high = np.maximum(open_, close) + np.abs(rng.normal(0, 0.0005, periods))
        low = np.minimum(open_, close) - np.abs(rng.normal(0, 0.0005, periods))
        volume = rng.integers(100, 1000, periods)

        return pd.DataFrame(
            {
                "time": pd.date_range("2025-01-01", periods=periods, freq="1min"),
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )

    @staticmethod
    def _convert_mt5_rates(rates):
        """Convert MT5 rates to DataFrame"""
        import pandas as pd

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df[["time", "open", "high", "low", "close", "tick_volume"]]

    @staticmethod
    def _frame_to_indicator_snapshot(frame):
        """Convert OHLCV candles into the dict expected by MTF analyzer."""
        return {
            "rsi": MultiTimeframeAnalyzer._compute_rsi(frame["close"]),
            "macd_hist": MultiTimeframeAnalyzer._compute_macd_hist(frame["close"]),
            "bb_position": MultiTimeframeAnalyzer._compute_bb_position(frame["close"]),
            "slope": MultiTimeframeAnalyzer._compute_slope(frame["close"]),
        }

    @staticmethod
    def _signal_value(signal: Any) -> str:
        return str(
            getattr(signal, "signal", getattr(signal, "primary_signal", "HOLD"))
        ).upper()

    @staticmethod
    def _signal_confidence(signal: Any) -> float:
        return float(
            getattr(
                signal,
                "confidence",
                getattr(signal, "primary_confidence", 50.0),
            )
        )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Complete Trading Pipeline: MTF -> Sentiment -> AIEngine -> Claude -> Backtest"
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["EURUSD", "GBPUSD"],
        help="Trading symbols",
    )
    parser.add_argument("--config", default="config.json", help="Config file path")
    parser.add_argument("--claude-key", help="Claude API key")
    parser.add_argument("--newsapi-key", help="NewsAPI key")
    parser.add_argument("--demo", action="store_true", default=True, help="Demo mode")

    args = parser.parse_args()

    api_keys = {}
    if args.claude_key:
        api_keys["claude_api_key"] = args.claude_key
    else:
        api_keys["claude_api_key"] = os.getenv("CLAUDE_API_KEY")

    if args.newsapi_key:
        api_keys["newsapi_key"] = args.newsapi_key
    else:
        api_keys["newsapi_key"] = os.getenv("NEWSAPI_KEY")

    runner = TradingPipelineRunner(
        symbols=args.symbols, config_file=args.config, api_keys=api_keys
    )

    try:
        runner.run_full_pipeline()
        logger.info("\n✓ Pipeline completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"\n✗ Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
