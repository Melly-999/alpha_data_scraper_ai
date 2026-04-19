"""Core Alpha AI orchestration interfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
import os
from typing import Any, Optional

from brokers.broker_factory import get_broker
from claude_ai import ClaudeAIIntegration
from indicators import add_indicators
from lstm_model import LSTMPipeline
from mt5_fetcher import batch_fetch
from signal_generator import generate_signal

logger = logging.getLogger(__name__)


@dataclass
class EngineConfig:
    """Configuration for the batch signal engine."""

    symbols: list[str] = field(default_factory=lambda: ["EURUSD"])
    timeframe: str = "M5"
    bars: int = 700
    lookback: int = 30
    epochs: int = 1
    weights: dict[str, float] = field(default_factory=dict)
    min_confidence_threshold: float = 70.0
    update_interval_seconds: int = 60


@dataclass
class UnifiedSignal:
    """Engine signal with compatibility aliases used by runners and tests."""

    symbol: str
    primary_signal: str
    confidence: float
    reasons: list[str] = field(default_factory=list)
    source: str = "local"

    @property
    def signal(self) -> str:
        return self.primary_signal

    @property
    def primary_confidence(self) -> float:
        return self.confidence


class AIEngine:
    """Generate local technical/LSTM signals for configured symbols."""

    feature_columns = [
        "close",
        "rsi",
        "stoch_k",
        "stoch_d",
        "macd_hist",
        "bb_pos",
        "volume",
    ]

    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config = config or EngineConfig()

    def analyze_all(self) -> dict[str, UnifiedSignal]:
        """Analyze all configured symbols and return one signal per symbol."""
        raw_data = batch_fetch(
            symbols=self.config.symbols,
            timeframe=self.config.timeframe,
            bars=self.config.bars,
        )
        return {
            symbol: self.generate_signal(symbol, raw)
            for symbol, raw in raw_data.items()
        }

    def generate_signal(
        self,
        symbol: str,
        raw_data: Any | None = None,
    ) -> UnifiedSignal:
        """Generate a single symbol signal with confidence clamped by SignalResult."""
        if raw_data is None:
            raw_data = batch_fetch(
                symbols=[symbol],
                timeframe=self.config.timeframe,
                bars=self.config.bars,
            )[symbol]

        data = add_indicators(raw_data)
        features = data[self.feature_columns]
        model = LSTMPipeline(
            lookback=self.config.lookback,
            epochs=self.config.epochs,
        )
        model.fit(features)
        lstm_delta = model.predict_next_delta(features, close_col_index=0)
        result = generate_signal(data.iloc[-1], lstm_delta=lstm_delta)

        return UnifiedSignal(
            symbol=symbol,
            primary_signal=result.signal,
            confidence=result.confidence,
            reasons=result.reasons,
        )


class AlphaAIEngine:
    """Broker portfolio analysis engine with optional Claude reporting."""

    def __init__(self, api_key: Optional[str] = None):
        self.broker = get_broker()
        self.broker.connect()
        self.claude = ClaudeAIIntegration(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        logger.info("AlphaAIEngine initialized - %s", type(self.broker).__name__)

    def analyze_and_decide(self, symbols: Optional[list[str]] = None) -> dict[str, Any]:
        """Main analysis cycle: portfolio -> Claude -> decisions."""
        if symbols is None:
            positions = self.broker.get_positions()
            symbols = [p["symbol"] for p in positions][:10]

        portfolio_details = self._build_portfolio_string()
        risk_report = self.claude.get_full_analysis(
            "bridgewater_risk",
            portfolio_details=portfolio_details,
        )
        logger.info("Bridgewater Risk report ready for %d symbols", len(symbols))

        try:
            dividend_analysis = self.broker.get_dividend_analysis()
            logger.info(
                "Dywidendy netto: %.2f PLN",
                dividend_analysis.get("net_dividends", 0),
            )
        except (AttributeError, RuntimeError, ValueError):
            dividend_analysis = {}

        return {
            "portfolio_value": self.broker.get_portfolio_value(),
            "positions_count": len(self.broker.get_positions()),
            "risk_report_summary": (
                risk_report[:500] + "..." if len(risk_report) > 500 else risk_report
            ),
            "dividend_info": dividend_analysis,
        }

    def _build_portfolio_string(self) -> str:
        """Format portfolio for Claude prompts."""
        positions = self.broker.get_positions()
        parts = [f"Wartość portfela: {self.broker.get_portfolio_value():.2f} PLN"]
        for position in positions[:15]:
            parts.append(
                f"{position['symbol']} {position['qty']:.2f} szt. "
                f"(avg {position.get('avg_cost', 0):.2f})"
            )
        return " | ".join(parts)

    def shutdown(self) -> None:
        self.broker.disconnect()
        logger.info("AlphaAIEngine shutdown")
