# ai_engine.py
from __future__ import annotations

import logging
import os
from typing import Optional

from brokers.broker_factory import get_broker
from claude_ai import ClaudeAIIntegration

logger = logging.getLogger(__name__)


class AlphaAIEngine:
    """Główny silnik Alpha AI - broker + Claude analysis"""

    def __init__(self, api_key: Optional[str] = None):
        self.broker = get_broker()
        self.broker.connect()
        self.claude = ClaudeAIIntegration(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        logger.info(f"✅ AlphaAIEngine initialized - {type(self.broker).__name__}")

    def analyze_and_decide(self, symbols: Optional[list] = None) -> dict:
        """Main analysis cycle: portfolio → Claude → decisions"""

        if symbols is None:
            positions = self.broker.get_positions()
            symbols = [p["symbol"] for p in positions][:10]  # max 10 dla testów

        portfolio_details = self._build_portfolio_string()

        # Bridgewater Risk
        risk_report = self.claude.get_full_analysis(
            "bridgewater_risk", portfolio_details=portfolio_details
        )

        logger.info("✅ Bridgewater Risk report ready")

        # Dividend analysis (if using XTB)
        try:
            dividend_analysis = self.broker.get_dividend_analysis()
            logger.info(
                f"Dywidendy netto: {dividend_analysis.get('net_dividends', 0):.2f} PLN"
            )
        except Exception as exc:
            logger.debug("Dividend analysis unavailable: %s", exc)
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
        """Format portfolio for Claude prompts"""
        positions = self.broker.get_positions()
        parts = [f"Wartość portfela: {self.broker.get_portfolio_value():.2f} PLN"]
        for p in positions[:15]:
            parts.append(
                f"{p['symbol']} {p['qty']:.2f} szt. (avg {p.get('avg_cost', 0):.2f})"
            )
        return " | ".join(parts)

    def shutdown(self):
        self.broker.disconnect()
        logger.info("✅ AlphaAIEngine shutdown")
