"""
Claude AI Direct Integration - Use Claude-3 Sonnet for trading signal generation.
Integrates with existing AI engine or works standalone.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any

import requests

logger = logging.getLogger("ClaudeAI")


@dataclass
class ClaudeSignal:
    """Claude AI generated trading signal."""

    signal: str  # "BUY", "SELL", "HOLD"
    confidence: int  # 0-100
    risk: str  # "LOW", "MEDIUM", "HIGH"
    reason: str
    raw_response: Optional[str] = None


class ClaudeAIClient:
    """Direct integration with Claude API for trading signal generation."""

    BASE_URL = "https://api.anthropic.com/v1/messages"
    MODEL = "claude-3-sonnet-20240229"
    MAX_TOKENS = 300

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude AI client.

        Args:
            api_key: Anthropic API key. If None, reads from CLAUDE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "CLAUDE_API_KEY not provided and CLAUDE_API_KEY environment variable not set"
            )

    def get_trading_signal(self, market_data: Dict[str, Any]) -> Optional[ClaudeSignal]:
        """
        Get trading signal from Claude AI based on market data.

        Args:
            market_data: Dict with keys like:
                - symbol: str
                - current_price: float
                - rsi: float
                - macd_hist: float
                - bb_position: float
                - news_sentiment: str
                - multiframe_signal: str
                - etc.

        Returns:
            ClaudeSignal or None on error.
        """
        prompt = self._build_prompt(market_data)

        try:
            response = self._call_api(prompt)
            if not response:
                return None

            signal = self._parse_response(response)
            signal.raw_response = response
            return signal

        except Exception as e:
            logger.error(f"Claude AI request failed: {e}")
            return None

    def get_portfolio_signal(
        self, portfolio_data: Dict[str, Dict]
    ) -> Optional[Dict[str, ClaudeSignal]]:
        """
        Get signals for entire portfolio.

        Args:
            portfolio_data: Dict keyed by symbol, each with market data.

        Returns:
            Dict[symbol -> ClaudeSignal] or None on error.
        """
        signals = {}
        for symbol, data in portfolio_data.items():
            sig = self.get_trading_signal(data)
            if sig:
                signals[symbol] = sig
        return signals

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        """Build trading analysis prompt for Claude."""
        symbol = market_data.get("symbol", "UNKNOWN")

        # Format market data for readability
        data_str = json.dumps(market_data, indent=2, default=str)

        prompt = f"""You are a professional hedge fund trading system analyzing forex markets.

SYMBOL: {symbol}

MARKET DATA:
{data_str}

ANALYSIS TASK:
1. Analyze technical indicators (RSI, MACD, Bollinger Bands)
2. Consider multi-timeframe confluence (M1/M5/H1)
3. Factor in news sentiment if available
4. Evaluate risk/reward ratio
5. Assess trend strength and momentum

RESPOND WITH VALID JSON ONLY (no markdown, no code blocks):
{{
  "signal": "BUY|SELL|HOLD",
  "confidence": <integer 0-100>,
  "risk": "LOW|MEDIUM|HIGH",
  "reason": "<2-3 sentence analysis>"
}}

IMPORTANT:
- If conflicting signals, lean toward HOLD
- Higher confidence only if multiple indicators align
- Risk should reflect position size: HIGH=risky, MEDIUM=moderate, LOW=safe
- confidence + risk must be balanced (high conf + high risk = aggressive)"""

        return prompt

    def _call_api(self, prompt: str) -> Optional[str]:
        """Call Claude API and return response text."""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        body = {
            "model": self.MODEL,
            "max_tokens": self.MAX_TOKENS,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        try:
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=body,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            # Extract text from response
            if "content" in data and len(data["content"]) > 0:
                return data["content"][0].get("text", "")

            logger.error(f"Unexpected API response structure: {data}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return None

    def _parse_response(self, response_text: str) -> ClaudeSignal:
        """Parse Claude's JSON response into ClaudeSignal."""
        try:
            # Clean response (remove markdown code blocks if present)
            text = response_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

            data = json.loads(text.strip())

            return ClaudeSignal(
                signal=str(data.get("signal", "HOLD")).upper(),
                confidence=int(data.get("confidence", 50)),
                risk=str(data.get("risk", "MEDIUM")).upper(),
                reason=str(data.get("reason", "No reason provided")),
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(
                f"Failed to parse Claude response: {e}\nResponse: {response_text}"
            )
            # Return neutral signal on parse error
            return ClaudeSignal(
                signal="HOLD",
                confidence=30,
                risk="HIGH",
                reason="Failed to parse AI response",
            )

    @staticmethod
    def format_market_data(
        symbol: str,
        current_price: float,
        rsi: float = 50.0,
        macd_hist: float = 0.0,
        bb_position: float = 50.0,
        slope: float = 0.0,
        multiframe_signal: Optional[str] = None,
        sentiment_score: Optional[float] = None,
        news_signal: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Format market data for Claude analysis.

        Returns:
            Dict ready for get_trading_signal()
        """
        data = {
            "symbol": symbol,
            "current_price": current_price,
            "rsi": round(rsi, 2),
            "macd_hist": round(macd_hist, 6),
            "bb_position": round(bb_position, 2),
            "slope": round(slope, 5),
        }

        if multiframe_signal:
            data["multiframe_signal"] = multiframe_signal
        if sentiment_score is not None:
            data["sentiment_score"] = round(sentiment_score, 2)
        if news_signal:
            data["news_signal"] = news_signal

        # Include any additional kwargs
        data.update(kwargs)

        return data


class ClaudeAIIntegration:
    """Integration layer between Claude AI and AI Engine."""

    def __init__(self, api_key: Optional[str] = None, enabled: bool = True):
        """
        Initialize Claude integration.

        Args:
            api_key: Anthropic API key.
            enabled: Whether to use Claude for secondary validation.
        """
        self.enabled = enabled
        self.client = ClaudeAIClient(api_key) if enabled else None

    def validate_signal(
        self,
        symbol: str,
        engine_signal: str,
        engine_confidence: float,
        market_data: Dict[str, Any],
    ) -> tuple[str, float, str]:
        """
        Validate/refine engine signal using Claude AI.

        Args:
            symbol: Currency pair
            engine_signal: Signal from AI Engine (BUY/SELL/HOLD)
            engine_confidence: Confidence from AI Engine (0-100)
            market_data: Market data dict

        Returns:
            (refined_signal, refined_confidence, reason)
        """
        if not self.enabled or not self.client:
            return engine_signal, engine_confidence, "Claude validation disabled"

        try:
            # Add engine signal to context
            market_data["engine_signal"] = engine_signal
            market_data["engine_confidence"] = engine_confidence
            market_data["symbol"] = symbol

            claude_sig = self.client.get_trading_signal(market_data)
            if not claude_sig:
                return engine_signal, engine_confidence, "Claude analysis failed"

            # Combine signals
            if engine_signal == claude_sig.signal:
                # Agreement: boost confidence
                refined_conf = min(
                    100, (engine_confidence + claude_sig.confidence) / 2 * 1.1
                )
                return (
                    engine_signal,
                    refined_conf,
                    f"Claude confirms ({claude_sig.reason})",
                )
            else:
                # Disagreement: reduce to HOLD
                return (
                    "HOLD",
                    50.0,
                    f"Conflict: Engine {engine_signal} vs Claude {claude_sig.signal}",
                )

        except Exception as e:
            logger.error(f"Signal validation failed: {e}")
            return engine_signal, engine_confidence, "Validation error"

    def get_independent_signal(
        self, market_data: Dict[str, Any]
    ) -> Optional[ClaudeSignal]:
        """Get completely independent signal from Claude."""
        if not self.enabled or not self.client:
            return None

        try:
            return self.client.get_trading_signal(market_data)
        except Exception as e:
            logger.error(f"Failed to get independent signal: {e}")
            return None
