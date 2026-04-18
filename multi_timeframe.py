"""Multi-timeframe signal analysis: M1, M5, H1 with weighted and confirmation strategies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Tuple
import logging

import pandas as pd
import numpy as np

try:
    import MetaTrader5 as mt5  # type: ignore
except Exception:  # pragma: no cover - optional runtime dependency
    mt5 = None

logger = logging.getLogger("MultiTimeframe")


@dataclass
class TimeframeSignal:
    """Signal for a single timeframe."""

    timeframe: str  # "M1", "M5", "H1"
    signal: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0-100
    rsi: float
    macd_hist: float
    bb_position: float
    slope: float


@dataclass
class MultiTimeframeResult:
    """Combined multi-timeframe analysis result."""

    weighted_signal: str  # "BUY", "SELL", "HOLD"
    weighted_confidence: float
    confirmation_signal: str  # "BUY", "SELL", "HOLD"
    confirmation_strength: int  # 0-3 (how many timeframes agree)
    signals: Dict[str, TimeframeSignal]  # M1, M5, H1


class MultiTimeframeAnalyzer:
    """Analyze signals across M1, M5, H1 timeframes."""

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.weights = {"M1": 0.40, "M5": 0.35, "H1": 0.25}
        self.timeframes = {
            "M1": mt5.TIMEFRAME_M1 if mt5 else 1,
            "M5": mt5.TIMEFRAME_M5 if mt5 else 5,
            "H1": mt5.TIMEFRAME_H1 if mt5 else 16388,
        }

    def analyze(self, from_indicators: Dict[str, Dict]) -> MultiTimeframeResult:
        """
        Analyze signals from all 3 timeframes.

        Args:
            from_indicators: Dict with keys "M1", "M5", "H1", each containing
                            {"rsi", "macd_hist", "bb_position", "slope"}

        Returns:
            MultiTimeframeResult with weighted and confirmation signals.
        """
        signals = {}
        for tf in ["M1", "M5", "H1"]:
            if tf not in from_indicators:
                logger.warning(f"Missing indicator data for {tf}")
                continue
            ind = from_indicators[tf]
            signal, conf = self._generate_signal_for_tf(
                rsi=ind.get("rsi", 50),
                macd_hist=ind.get("macd_hist", 0),
                bb_pos=ind.get("bb_position", 0),
                slope=ind.get("slope", 0),
            )
            signals[tf] = TimeframeSignal(
                timeframe=tf,
                signal=signal,
                confidence=conf,
                rsi=ind.get("rsi", 50),
                macd_hist=ind.get("macd_hist", 0),
                bb_position=ind.get("bb_position", 0),
                slope=ind.get("slope", 0),
            )

        # Weighted combination
        weighted_sig, weighted_conf = self._weighted_combination(signals)

        # Confirmation strategy (M5 & H1 agreement)
        confirm_sig, confirm_strength = self._confirmation_strategy(signals)

        return MultiTimeframeResult(
            weighted_signal=weighted_sig,
            weighted_confidence=weighted_conf,
            confirmation_signal=confirm_sig,
            confirmation_strength=confirm_strength,
            signals=signals,
        )

    def _generate_signal_for_tf(
        self,
        rsi: float,
        macd_hist: float,
        bb_pos: float,
        slope: float,
    ) -> Tuple[str, float]:
        """Generate BUY/SELL/HOLD signal for a single timeframe based on indicators."""
        score = 0
        reasons = []

        # RSI: < 35 bullish, > 65 bearish
        if rsi < 35:
            score += 1
            reasons.append("RSI oversold")
        elif rsi > 65:
            score -= 1
            reasons.append("RSI overbought")

        # MACD histogram
        if macd_hist > 0:
            score += 1
            reasons.append("MACD positive")
        elif macd_hist < -0.001:
            score -= 1
            reasons.append("MACD negative")

        # Bollinger Bands position: < 20 bullish, > 80 bearish
        if bb_pos < 20:
            score += 1
            reasons.append("Price near BB lower")
        elif bb_pos > 80:
            score -= 1
            reasons.append("Price near BB upper")

        # Slope: positive = up, negative = down
        if slope > 0.5:
            score += 1
            reasons.append("Slope positive")
        elif slope < -0.5:
            score -= 1
            reasons.append("Slope negative")

        if score >= 2:
            signal = "BUY"
        elif score <= -2:
            signal = "SELL"
        else:
            signal = "HOLD"

        confidence = float(np.clip(50 + (score * 10), 33, 85))
        return signal, confidence

    def _weighted_combination(
        self, signals: Dict[str, TimeframeSignal]
    ) -> Tuple[str, float]:
        """
        Combine signals with weights: M1=40%, M5=35%, H1=25%.

        Returns:
            (combined_signal, combined_confidence)
        """
        buy_score = 0.0
        sell_score = 0.0
        total_weight = 0.0

        for tf in ["M1", "M5", "H1"]:
            if tf not in signals:
                continue
            sig = signals[tf]
            weight = self.weights[tf]
            total_weight += weight

            if sig.signal == "BUY":
                buy_score += weight * sig.confidence
            elif sig.signal == "SELL":
                sell_score += weight * sig.confidence

        if total_weight == 0:
            return "HOLD", 50.0

        # Normalize
        buy_score /= total_weight
        sell_score /= total_weight

        if buy_score > sell_score and buy_score > 55:
            return "BUY", min(buy_score, 85)
        elif sell_score > buy_score and sell_score > 55:
            return "SELL", min(sell_score, 85)
        else:
            return "HOLD", 50.0

    def _confirmation_strategy(
        self, signals: Dict[str, TimeframeSignal]
    ) -> Tuple[str, int]:
        """
        Confirmation: BUY/SELL only if M5 & H1 agree on direction.

        Returns:
            (confirmation_signal, strength) where strength = {0, 1, 2, 3}
            (0 = no agreement, 3 = all agree)
        """
        m1_sig = signals.get("M1", TimeframeSignal("M1", "HOLD", 50, 50, 0, 50, 0))
        m5_sig = signals.get("M5", TimeframeSignal("M5", "HOLD", 50, 50, 0, 50, 0))
        h1_sig = signals.get("H1", TimeframeSignal("H1", "HOLD", 50, 50, 0, 50, 0))

        # Confirmation requires M5 & H1 (higher timeframes) to agree
        m5_h1_buy = m5_sig.signal == "BUY" and h1_sig.signal == "BUY"
        m5_h1_sell = m5_sig.signal == "SELL" and h1_sig.signal == "SELL"

        if m5_h1_buy:
            strength = 2 + (1 if m1_sig.signal == "BUY" else 0)  # 2-3
            return "BUY", strength
        elif m5_h1_sell:
            strength = 2 + (1 if m1_sig.signal == "SELL" else 0)  # 2-3
            return "SELL", strength
        else:
            return "HOLD", 0

    def fetch_multi_timeframe_data(self, bars: int = 100) -> Optional[Dict[str, Dict]]:
        """
        Fetch OHLC data for M1, M5, H1 and compute indicators for each.

        Returns:
            Dict with keys "M1", "M5", "H1", each containing computed indicators.
        """
        if mt5 is None:
            logger.error("MetaTrader5 is unavailable")
            return None

        result = {}
        for tf_name, tf_enum in self.timeframes.items():
            rates = mt5.copy_rates_from_pos(self.symbol, tf_enum, 0, bars)
            if rates is None or len(rates) == 0:
                logger.error(f"No data for {tf_name}")
                return None

            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s")

            # Compute indicators
            indicators = {
                "rsi": self._compute_rsi(df["close"]),
                "macd_hist": self._compute_macd_hist(df["close"]),
                "bb_position": self._compute_bb_position(df["close"]),
                "slope": self._compute_slope(df["close"]),
            }
            result[tf_name] = indicators

        return result

    @staticmethod
    def _compute_rsi(close: pd.Series, period: int = 14) -> float:
        """Compute RSI for the latest bar."""
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not rsi.empty else 50.0

    @staticmethod
    def _compute_macd_hist(close: pd.Series) -> float:
        """Compute MACD histogram for latest bar."""
        ema_fast = close.ewm(span=12, adjust=False).mean()
        ema_slow = close.ewm(span=26, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        return float(hist.iloc[-1]) if not hist.empty else 0.0

    @staticmethod
    def _compute_bb_position(close: pd.Series, period: int = 20) -> float:
        """Compute Bollinger Band position (0-100) for latest bar."""
        sma = close.rolling(period).mean()
        std = close.rolling(period).std()
        bb_up = sma + 2 * std
        bb_low = sma - 2 * std
        denominator = bb_up - bb_low
        if denominator.iloc[-1] > 0:
            pos = (close.iloc[-1] - bb_low.iloc[-1]) / denominator.iloc[-1] * 100
            return float(np.clip(pos, 0, 100))
        return 50.0

    @staticmethod
    def _compute_slope(close: pd.Series, lookback: int = 15) -> float:
        """Compute price slope from polyfit for latest bars."""
        if len(close) < lookback:
            return 0.0
        x = np.arange(lookback)
        y = close.iloc[-lookback:].values
        try:
            slope = float(np.polyfit(x, y, 1)[0] * 100)
            return slope
        except Exception:
            return 0.0
