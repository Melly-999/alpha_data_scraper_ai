# claude_ai.py
from __future__ import annotations

import requests
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from prompts import get_prompt

logger = logging.getLogger(__name__)


@dataclass
class ClaudeSignal:
    signal: str
    confidence: float
    risk: str
    reason: str


class ClaudeAIClient:
    """Small Claude trading-signal client used by integration tests and demos."""

    BASE_URL = "https://api.anthropic.com/v1/messages"
    MODEL = "claude-opus-4-20250514"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError("Claude API key is required")

    def _call_api(self, prompt_text: str) -> Optional[str]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": self.MODEL,
            "max_tokens": 1000,
            "temperature": 0.1,
            "messages": [{"role": "user", "content": prompt_text}],
        }

        try:
            response = requests.post(
                self.BASE_URL, headers=headers, json=body, timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0].get("text")
        except Exception as e:
            logger.error(f"Claude trading signal API error: {e}")
            return None

    def get_trading_signal(self, market_data: Dict[str, Any]) -> Optional[ClaudeSignal]:
        raw = self._call_api(json.dumps(market_data, default=str))
        if raw is None:
            return None
        return self._parse_signal(raw)

    def get_portfolio_signal(
        self, portfolio: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, ClaudeSignal]]:
        signals: Dict[str, ClaudeSignal] = {}
        for symbol, market_data in portfolio.items():
            signal = self.get_trading_signal(market_data)
            if signal is None:
                return None
            signals[symbol] = signal
        return signals

    def _parse_signal(self, raw: str) -> ClaudeSignal:
        payload = raw.strip()
        if payload.startswith("```"):
            lines = payload.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            payload = "\n".join(lines).strip()

        try:
            data = json.loads(payload)
            return ClaudeSignal(
                signal=str(data.get("signal", "HOLD")).upper(),
                confidence=float(data.get("confidence", 50.0)),
                risk=str(data.get("risk", "MEDIUM")).upper(),
                reason=str(data.get("reason", "")),
            )
        except (TypeError, ValueError, json.JSONDecodeError) as e:
            logger.warning(f"Could not parse Claude signal response: {e}")
            return ClaudeSignal(
                signal="HOLD",
                confidence=0.0,
                risk="HIGH",
                reason="Malformed Claude response",
            )


class ClaudeAIIntegration:
    """Integracja z Claude API (Anthropic)"""

    BASE_URL = "https://api.anthropic.com/v1/messages"
    MODEL = "claude-opus-4-20250514"  # lub claude-sonnet-4-20250514 dla szybszych

    def __init__(
        self,
        api_key: Optional[str] = None,
        enabled: bool = True,
        client: Optional[ClaudeAIClient] = None,
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.enabled = enabled and bool(self.api_key)
        self.client = client
        if self.enabled and self.client is None:
            self.client = ClaudeAIClient(api_key=self.api_key)
        if not self.enabled:
            logger.warning("Claude AI integration disabled - no API key")

    def get_full_analysis(self, report_type: str, **kwargs) -> str:
        """Generate professional analysis using Claude"""
        if not self.enabled:
            return "Claude AI is disabled"

        try:
            prompt_text = get_prompt(report_type, **kwargs)

            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            body = {
                "model": self.MODEL,
                "max_tokens": 4000,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt_text}],
            }

            response = requests.post(
                self.BASE_URL, headers=headers, json=body, timeout=60
            )
            response.raise_for_status()

            data = response.json()
            return data["content"][0].get("text", "No response from Claude")

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return f"Error: {str(e)}"

    def test_connection(self) -> bool:
        """Test if API key works"""
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            body = {
                "model": self.MODEL,
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Say 'Hello'"}],
            }
            response = requests.post(
                self.BASE_URL, headers=headers, json=body, timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

    def validate_signal(
        self,
        symbol: str,
        engine_signal: str,
        engine_confidence: float,
        market_data: Dict[str, Any],
    ) -> tuple[str, float, str]:
        if not self.enabled or self.client is None:
            return engine_signal, engine_confidence, "Claude AI disabled"

        data = dict(market_data)
        data["symbol"] = symbol
        claude_signal = self.client.get_trading_signal(data)
        if claude_signal is None:
            return engine_signal, engine_confidence, "Claude AI unavailable"

        if claude_signal.signal == engine_signal:
            confidence = min(100.0, (engine_confidence + claude_signal.confidence) / 2)
            return engine_signal, confidence, claude_signal.reason

        if claude_signal.signal == "HOLD":
            return engine_signal, engine_confidence, claude_signal.reason

        return (
            "HOLD",
            min(engine_confidence, claude_signal.confidence),
            f"Conflict with Claude signal: {claude_signal.reason}",
        )

    def get_independent_signal(
        self, market_data: Dict[str, Any]
    ) -> Optional[ClaudeSignal]:
        if not self.enabled or self.client is None:
            return None
        return self.client.get_trading_signal(market_data)
