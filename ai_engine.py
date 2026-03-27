"""
AI Engine - Central orchestrator for multi-source trading signal generation.
Combines multi-timeframe analysis, news sentiment, and risk management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple
import logging
import threading
import time

from multi_timeframe import MultiTimeframeAnalyzer, MultiTimeframeResult
from news_sentiment import SentimentAnalyzer, SentimentScore
from indicators import add_indicators
from mt5_fetcher import batch_fetch
import pandas as pd

logger = logging.getLogger("AIEngine")


@dataclass
class EngineConfig:
    """AI Engine configuration."""
    symbols: List[str] = field(default_factory=lambda: ["EURUSD", "GBPUSD", "USDJPY"])
    timeframe: str = "M5"
    bars: int = 100
    lookback_m1: int = 50
    lookback_m5: int = 100
    lookback_h1: int = 240
    use_news_sentiment: bool = True
    newsapi_key: Optional[str] = None
    news_weight: float = 0.15  # 15% of final signal
    multiframe_weight: float = 0.85  # 85% of final signal
    min_confidence_threshold: int = 60
    update_interval_seconds: int = 300


@dataclass
class UnifiedSignal:
    """Unified trading signal from all sources."""
    symbol: str
    timestamp: datetime
    primary_signal: str  # "BUY", "SELL", "HOLD"
    primary_confidence: float  # 0-100
    multiframe_result: Optional[MultiTimeframeResult] = None
    sentiment_score: Optional[SentimentScore] = None
    news_signal: Optional[str] = None
    composite_score: float = 0.0  # Weighted combination
    reasoning: List[str] = field(default_factory=list)
    ready_for_trade: bool = False

    def __str__(self) -> str:
        return (
            f"[{self.symbol}] {self.primary_signal} @ {self.primary_confidence:.0f}% "
            f"| Composite: {self.composite_score:.2f}"
        )


class AIEngine:
    """Central AI trading engine orchestrating all analysis modules."""

    def __init__(self, config: EngineConfig):
        self.config = config
        self.symbols = config.symbols
        self.multiframe_analyzer = {
            sym: MultiTimeframeAnalyzer(sym) for sym in self.symbols
        }
        self.sentiment_analyzer = (
            SentimentAnalyzer(config.newsapi_key) if config.use_news_sentiment else None
        )
        self.last_signals: Dict[str, UnifiedSignal] = {}
        self.signal_history: Dict[str, List[UnifiedSignal]] = {sym: [] for sym in self.symbols}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start_realtime(self):
        """Start real-time analysis loop."""
        if self._thread and self._thread.is_alive():
            logger.warning("Engine already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._realtime_loop, daemon=True)
        self._thread.start()
        logger.info("AI Engine started (realtime mode)")

    def stop_realtime(self):
        """Stop real-time analysis loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("AI Engine stopped")

    def _realtime_loop(self):
        """Main real-time analysis loop."""
        while self._running:
            try:
                signals = self.analyze_all()
                with self._lock:
                    for sym, sig in signals.items():
                        self.last_signals[sym] = sig
                        self.signal_history[sym].append(sig)
                        # Keep only last 1000 signals per symbol
                        if len(self.signal_history[sym]) > 1000:
                            self.signal_history[sym].pop(0)

                logger.debug(f"Analysis complete: {len(signals)} signals generated")
                time.sleep(self.config.update_interval_seconds)

            except Exception as e:
                logger.error(f"Realtime loop error: {e}", exc_info=True)
                time.sleep(10)  # Back off on error

    def analyze_all(self) -> Dict[str, UnifiedSignal]:
        """Analyze all configured symbols and return unified signals."""
        signals: Dict[str, UnifiedSignal] = {}

        # Fetch data for all symbols (single MT5 session)
        try:
            raw_data = batch_fetch(
                symbols=self.symbols,
                timeframe=self.config.timeframe,
                bars=self.config.bars,
            )
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return signals

        # Fetch sentiment once (if enabled)
        sentiment_map: Dict[str, SentimentScore] = {}
        if self.sentiment_analyzer:
            try:
                sentiment_map = self.sentiment_analyzer.analyze_sentiment(
                    include_forexfactory=True, include_newsapi=True
                )
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")

        # Analyze each symbol
        for symbol in self.symbols:
            try:
                sig = self._analyze_symbol(symbol, raw_data.get(symbol), sentiment_map)
                signals[symbol] = sig
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")

        return signals

    def _analyze_symbol(
        self,
        symbol: str,
        ohlc_data: Optional[pd.DataFrame],
        sentiment_map: Dict[str, SentimentScore],
    ) -> UnifiedSignal:
        """Analyze single symbol using all available sources."""
        timestamp = datetime.now(timezone.utc)
        reasoning: List[str] = []

        # 1. Multi-timeframe analysis
        multiframe_result = self._get_multiframe_signal(symbol, ohlc_data)
        if multiframe_result:
            reasoning.append(
                f"Weighted: {multiframe_result.weighted_signal} "
                f"({multiframe_result.weighted_confidence:.0f}%)"
            )
            reasoning.append(
                f"Confirmation: {multiframe_result.confirmation_signal} "
                f"(strength {multiframe_result.confirmation_strength}/3)"
            )

        # 2. News sentiment analysis
        sentiment_score = sentiment_map.get(symbol.replace("USD", "").split(symbol[-3:])[0])
        news_signal = None
        if sentiment_score and self.sentiment_analyzer:
            news_signal = self.sentiment_analyzer.get_currency_signal(symbol, sentiment_score)
            reasoning.append(f"News sentiment: {sentiment_score.average_sentiment:.2f} → {news_signal}")

        # 3. Composite signal generation
        primary_signal, primary_conf = self._generate_composite_signal(
            multiframe_result, news_signal, sentiment_score
        )

        # 4. Composite score (weighted)
        composite_score = self._calculate_composite_score(
            multiframe_result, sentiment_score
        )

        ready_for_trade = (
            primary_signal in ["BUY", "SELL"]
            and primary_conf >= self.config.min_confidence_threshold
        )

        if ready_for_trade:
            reasoning.append(f"✓ READY FOR TRADE (confidence: {primary_conf:.0f}%)")

        return UnifiedSignal(
            symbol=symbol,
            timestamp=timestamp,
            primary_signal=primary_signal,
            primary_confidence=primary_conf,
            multiframe_result=multiframe_result,
            sentiment_score=sentiment_score,
            news_signal=news_signal,
            composite_score=composite_score,
            reasoning=reasoning,
            ready_for_trade=ready_for_trade,
        )

    def _get_multiframe_signal(
        self, symbol: str, ohlc_data: Optional[pd.DataFrame]
    ) -> Optional[MultiTimeframeResult]:
        """Get multi-timeframe signal for symbol."""
        if ohlc_data is None or len(ohlc_data) == 0:
            logger.warning(f"No OHLC data for {symbol}")
            return None

        try:
            # Compute indicators for main timeframe
            df_indicators = add_indicators(ohlc_data)

            # Extract latest values
            latest = df_indicators.iloc[-1]
            from_indicators = {
                "M5": {
                    "rsi": float(latest.get("rsi", 50)),
                    "macd_hist": float(latest.get("macd_hist", 0)),
                    "bb_position": float(latest.get("bb_pos", 50)),
                    "slope": self._compute_slope(df_indicators["close"]),
                }
            }

            # For M1/H1 you would fetch separate data - placeholder here
            from_indicators["M1"] = from_indicators["M5"]  # Placeholder
            from_indicators["H1"] = from_indicators["M5"]  # Placeholder

            analyzer = self.multiframe_analyzer[symbol]
            return analyzer.analyze(from_indicators)

        except Exception as e:
            logger.error(f"Multiframe analysis failed for {symbol}: {e}")
            return None

    def _generate_composite_signal(
        self,
        multiframe_result: Optional[MultiTimeframeResult],
        news_signal: Optional[str],
        sentiment_score: Optional[SentimentScore],
    ) -> Tuple[str, float]:
        """Generate composite signal from all sources."""
        if not multiframe_result:
            return "HOLD", 50.0

        # Start with multiframe signal
        signal = multiframe_result.weighted_signal
        confidence = multiframe_result.weighted_confidence

        # Adjust by news sentiment
        if news_signal and sentiment_score:
            avg_sentiment = sentiment_score.average_sentiment
            if news_signal == "BUY" and signal == "BUY":
                confidence = min(100, confidence + 5)  # Boost
            elif news_signal == "BUY" and signal == "SELL":
                signal = "HOLD"  # Conflict
                confidence = 50
            elif news_signal == "SELL" and signal == "SELL":
                confidence = min(100, confidence + 5)
            elif news_signal == "SELL" and signal == "BUY":
                signal = "HOLD"
                confidence = 50

        return signal, confidence

    def _calculate_composite_score(
        self,
        multiframe_result: Optional[MultiTimeframeResult],
        sentiment_score: Optional[SentimentScore],
    ) -> float:
        """Calculate weighted composite score (-1 to 1)."""
        score = 0.0
        weights_sum = 0.0

        # Multiframe contribution
        if multiframe_result:
            mf_score = 0.0
            if multiframe_result.weighted_signal == "BUY":
                mf_score = multiframe_result.weighted_confidence / 100
            elif multiframe_result.weighted_signal == "SELL":
                mf_score = -(multiframe_result.weighted_confidence / 100)

            score += mf_score * self.config.multiframe_weight
            weights_sum += self.config.multiframe_weight

        # Sentiment contribution
        if sentiment_score:
            sent_score = sentiment_score.average_sentiment
            score += sent_score * self.config.news_weight
            weights_sum += self.config.news_weight

        if weights_sum > 0:
            score /= weights_sum

        return score

    def get_last_signal(self, symbol: str) -> Optional[UnifiedSignal]:
        """Get last computed signal for symbol."""
        with self._lock:
            return self.last_signals.get(symbol)

    def get_all_last_signals(self) -> Dict[str, UnifiedSignal]:
        """Get all last computed signals."""
        with self._lock:
            return dict(self.last_signals)

    def get_signal_history(self, symbol: str, limit: int = 100) -> List[UnifiedSignal]:
        """Get recent signal history for symbol."""
        with self._lock:
            return self.signal_history.get(symbol, [])[-limit:]

    def get_statistics(self) -> Dict[str, Dict]:
        """Get engine statistics."""
        stats = {}
        with self._lock:
            for symbol in self.symbols:
                history = self.signal_history.get(symbol, [])
                if not history:
                    continue

                buy_count = sum(1 for s in history if s.primary_signal == "BUY")
                sell_count = sum(1 for s in history if s.primary_signal == "SELL")
                hold_count = sum(1 for s in history if s.primary_signal == "HOLD")
                trade_ready = sum(1 for s in history if s.ready_for_trade)

                avg_confidence = (
                    sum(s.primary_confidence for s in history) / len(history)
                    if history
                    else 0.0
                )

                stats[symbol] = {
                    "total_signals": len(history),
                    "buys": buy_count,
                    "sells": sell_count,
                    "holds": hold_count,
                    "trade_ready": trade_ready,
                    "avg_confidence": avg_confidence,
                    "last_signal_time": history[-1].timestamp if history else None,
                }

        return stats

    @staticmethod
    def _compute_slope(close: pd.Series, lookback: int = 15) -> float:
        """Compute price slope."""
        if len(close) < lookback:
            return 0.0
        import numpy as np

        x = np.arange(lookback)
        y = close.iloc[-lookback:].values
        try:
            slope = float(np.polyfit(x, y, 1)[0] * 100)
            return slope
        except Exception:
            return 0.0
