"""Anthropic Claude client and trading-signal validation helpers."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import os
from typing import Any, Iterator, Optional

import requests

from prompts import get_prompt

logger = logging.getLogger(__name__)


@dataclass
class ClaudeSignal:
    """Structured Claude trading signal."""

    signal: str
    confidence: float
    risk: str
    reason: str

    def __iter__(self) -> Iterator[Any]:
        """Allow legacy tuple-unpacking as (signal, confidence, reason)."""
        yield self.signal
        yield self.confidence
        yield self.reason


class ClaudeAIClient:
    """Low-level Claude API client used by trading integrations."""

    base_url = "https://api.anthropic.com/v1/messages"
    model = "claude-3-5-sonnet-20241022"

    def __init__(self, api_key: Optional[str] = None, enabled: bool = True) -> None:
        self.api_key = (
            api_key or os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        )
        self.enabled = enabled
        if self.enabled and not self.api_key:
            raise ValueError("Claude API key is required when Claude is enabled")

    def _call_api(self, prompt_text: str, max_tokens: int = 1000) -> Optional[str]:
        """Call Claude and return raw text, or None on failure."""
        if not self.enabled:
            return None

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "messages": [{"role": "user", "content": prompt_text}],
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=body,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return str(data["content"][0].get("text", ""))
        except Exception as exc:
            logger.error("Claude API error: %s", exc)
            return None

    def get_trading_signal(self, context: dict[str, Any]) -> Optional[ClaudeSignal]:
        """Return a parsed Claude trading signal for the supplied context."""
        raw = self._call_api(self._build_signal_prompt(context))
        if raw is None:
            return None
        return self._parse_signal(raw)

    def get_signal(self, context: dict[str, Any]) -> Optional[ClaudeSignal]:
        """Backward-compatible alias for get_trading_signal()."""
        return self.get_trading_signal(context)

    def get_portfolio_signal(
        self, portfolio_context: dict[str, dict[str, Any]]
    ) -> dict[str, ClaudeSignal]:
        """Get one Claude signal per symbol in a portfolio context."""
        signals: dict[str, ClaudeSignal] = {}
        for symbol, context in portfolio_context.items():
            signal = self.get_trading_signal(context)
            if signal is not None:
                signals[symbol] = signal
        return signals

    @staticmethod
    def _build_signal_prompt(context: dict[str, Any]) -> str:
        return (
            "Return only JSON with keys signal, confidence, risk, reason for this "
            f"trading context: {json.dumps(context, default=str)}"
        )

    @staticmethod
    def _parse_signal(raw: str) -> ClaudeSignal:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            data = json.loads(text)
            signal = str(data.get("signal", "HOLD")).upper()
            if signal not in {"BUY", "SELL", "HOLD"}:
                signal = "HOLD"
            confidence = float(data.get("confidence", 50))
            confidence = max(0.0, min(100.0, confidence))
            risk = str(data.get("risk", "MEDIUM")).upper()
            reason = str(data.get("reason", "Claude returned a signal"))
            return ClaudeSignal(signal, confidence, risk, reason)
        except (TypeError, ValueError, json.JSONDecodeError):
            return ClaudeSignal(
                signal="HOLD",
                confidence=0.0,
                risk="HIGH",
                reason="Malformed Claude response",
            )


class ClaudeAIIntegration:
    """Trading-oriented Claude validation layer with safe fallbacks."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        enabled: bool = True,
        client: Optional[ClaudeAIClient] = None,
    ) -> None:
        self.client = client
        self.enabled = enabled

        if self.client is None:
            try:
                self.client = ClaudeAIClient(api_key=api_key, enabled=enabled)
            except ValueError:
                self.enabled = False
                self.client = None
                logger.warning("Claude AI integration disabled - no API key")
        elif not enabled:
            self.enabled = False

    def get_full_analysis(self, report_type: str, **kwargs: Any) -> str:
        """Generate a free-form analysis report using Claude."""
        if not self.enabled or self.client is None:
            return "Claude AI is disabled"

        prompt_text = get_prompt(report_type, **kwargs)
        result = self.client._call_api(prompt_text, max_tokens=4000)
        return result or "Claude AI analysis unavailable"

    def validate_signal(
        self,
        symbol: str,
        engine_signal: str,
        engine_confidence: float,
        market_data: dict[str, Any],
    ) -> ClaudeSignal:
        """Validate an engine signal without weakening local risk gates."""
        engine_signal = engine_signal.upper()
        if not self.enabled or self.client is None:
            return ClaudeSignal(
                engine_signal,
                float(engine_confidence),
                "UNKNOWN",
                "Claude disabled; using engine signal",
            )

        claude_signal = self.client.get_trading_signal(
            {
                "symbol": symbol,
                "engine_signal": engine_signal,
                "engine_confidence": engine_confidence,
                "market_data": market_data,
            }
        )
        if claude_signal is None:
            return ClaudeSignal(
                engine_signal,
                float(engine_confidence),
                "UNKNOWN",
                "Claude unavailable; using engine signal",
            )

        if claude_signal.signal == engine_signal:
            confidence = min(
                85.0, max(float(engine_confidence), claude_signal.confidence)
            )
            return ClaudeSignal(
                signal=engine_signal,
                confidence=confidence,
                risk=claude_signal.risk,
                reason=claude_signal.reason,
            )

        if claude_signal.signal == "HOLD":
            return ClaudeSignal(
                signal="HOLD",
                confidence=min(float(engine_confidence), claude_signal.confidence),
                risk=claude_signal.risk,
                reason=claude_signal.reason,
            )

        return ClaudeSignal(
            signal="HOLD",
            confidence=min(float(engine_confidence), claude_signal.confidence),
            risk="HIGH",
            reason=(
                f"Conflict between engine {engine_signal} and Claude "
                f"{claude_signal.signal}: {claude_signal.reason}"
            ),
        )

    def get_independent_signal(self, context: dict[str, Any]) -> Optional[ClaudeSignal]:
        """Ask Claude for an independent signal."""
        if not self.enabled or self.client is None:
            return None
        return self.client.get_trading_signal(context)

    def test_connection(self) -> bool:
        """Test if Claude can return a response."""
        if not self.enabled or self.client is None:
            return False
        return self.client._call_api("Say 'Hello'", max_tokens=100) is not None
