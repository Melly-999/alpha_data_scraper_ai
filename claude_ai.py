"""
Claude AI Direct Integration — official Anthropic SDK.

Features
--------
* **Prompt caching** — the system prompt is marked with ``cache_control`` so
  Anthropic caches it after the first call (≈90 % token savings on repeats).
* **Streaming** — opt-in via ``use_streaming=True``; surfaces tokens
  progressively and avoids HTTP timeouts on long responses.
* **Adaptive thinking** — opt-in via ``use_thinking=True``; enables Claude's
  internal reasoning for deeper market analysis (Opus 4.6).
* **Structured outputs** — ``get_trading_signal_structured()`` uses
  ``client.messages.parse()`` + Pydantic so the API enforces the JSON schema
  and the SDK validates the object automatically; no manual parsing needed.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    import anthropic
    from pydantic import BaseModel as _BaseModel

    _SDK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SDK_AVAILABLE = False
    _BaseModel = object  # type: ignore[assignment,misc]

logger = logging.getLogger("ClaudeAI")


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclass
class ClaudeSignal:
    """Claude AI generated trading signal."""

    signal: str  # "BUY", "SELL", "HOLD"
    confidence: int  # 0-100
    risk: str  # "LOW", "MEDIUM", "HIGH"
    reason: str
    raw_response: Optional[str] = None


# ---------------------------------------------------------------------------
# Pydantic schema — used by get_trading_signal_structured()
# ---------------------------------------------------------------------------


class _SignalSchema(_BaseModel):
    """Strict JSON schema passed to client.messages.parse()."""

    signal: str
    confidence: int
    risk: str
    reason: str


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_MODEL = "claude-opus-4-6"
_MAX_TOKENS = 2048  # enough for thinking + compact JSON signal

# Stable system prompt — cached via cache_control to cut repeated token costs.
# Keep this text frozen; any change here resets the cache.
_SYSTEM = """\
You are a professional hedge fund trading system specialising in forex markets.
Analyse technical indicators and market conditions to produce actionable
trading signals.

Rules:
- If signals conflict, lean toward HOLD
- Raise confidence only when multiple indicators agree
- Risk reflects position size: HIGH=risky, MEDIUM=moderate, LOW=safe
- Confidence and risk must balance (high confidence + high risk = aggressive)"""

# User-turn template — volatile data goes here, after the cached system block.
_USER_TEMPLATE = """\
SYMBOL: {symbol}

MARKET DATA:
{data}

ANALYSIS TASK:
1. Analyse RSI, MACD, Bollinger Bands
2. Consider multi-timeframe confluence (M1/M5/H1)
3. Factor in news sentiment if available
4. Evaluate risk/reward ratio
5. Assess trend strength and momentum

Respond with VALID JSON ONLY (no markdown, no code blocks):
{{
  "signal": "BUY|SELL|HOLD",
  "confidence": <integer 0-100>,
  "risk": "LOW|MEDIUM|HIGH",
  "reason": "<2-3 sentence analysis>"
}}"""


def _system_block() -> List[Dict[str, Any]]:
    """Return the cached system content block."""
    return [
        {
            "type": "text",
            "text": _SYSTEM,
            "cache_control": {"type": "ephemeral"},
        }
    ]


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class ClaudeAIClient:
    """Anthropic SDK client for trading signal generation.

    Args:
        api_key: Anthropic API key. Falls back to ``CLAUDE_API_KEY`` env var.
        use_streaming: Stream responses (avoids timeout on long outputs).
        use_thinking: Enable adaptive thinking for deeper analysis.
    """

    MODEL = _MODEL
    MAX_TOKENS = _MAX_TOKENS

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        use_streaming: bool = False,
        use_thinking: bool = False,
    ) -> None:
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "CLAUDE_API_KEY not provided and "
                "CLAUDE_API_KEY environment variable not set"
            )
        self.use_streaming = use_streaming
        self.use_thinking = use_thinking
        self._sdk: Optional[Any] = (
            anthropic.Anthropic(api_key=self.api_key)
            if _SDK_AVAILABLE
            else None  # pragma: no cover
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_trading_signal(self, market_data: Dict[str, Any]) -> Optional[ClaudeSignal]:
        """Return a trading signal for *market_data*, or None on error."""
        prompt = self._build_prompt(market_data)
        try:
            text = self._call_api(prompt)
            if not text:
                return None
            sig = self._parse_response(text)
            sig.raw_response = text
            return sig
        except Exception as exc:
            logger.error("Claude AI request failed: %s", exc)
            return None

    def get_trading_signal_structured(
        self, market_data: Dict[str, Any]
    ) -> Optional[ClaudeSignal]:
        """Return a signal via the SDK's structured-output path.

        Uses ``client.messages.parse()`` with :class:`_SignalSchema` so the
        API enforces the JSON schema and the SDK validates the response object
        — no manual JSON parsing or markdown-stripping needed.

        Falls back to :meth:`get_trading_signal` if the SDK is unavailable.
        """
        if not _SDK_AVAILABLE or self._sdk is None:  # pragma: no cover
            return self.get_trading_signal(market_data)

        prompt = self._build_prompt(market_data)
        kwargs: Dict[str, Any] = {
            "model": self.MODEL,
            "max_tokens": self.MAX_TOKENS,
            "system": _system_block(),
            "messages": [{"role": "user", "content": prompt}],
        }
        if self.use_thinking:
            kwargs["thinking"] = {"type": "adaptive"}

        try:
            response = self._sdk.messages.parse(output_format=_SignalSchema, **kwargs)
            parsed: _SignalSchema = response.parsed_output
            sig = ClaudeSignal(
                signal=parsed.signal.upper(),
                confidence=int(parsed.confidence),
                risk=parsed.risk.upper(),
                reason=parsed.reason,
            )
            for block in response.content:
                if block.type == "text":
                    sig.raw_response = block.text
                    break
            return sig
        except anthropic.BadRequestError:
            # Refusal or schema enforcement failure — degrade gracefully
            logger.warning("Structured output failed; retrying via text path")
            return self.get_trading_signal(market_data)
        except Exception as exc:
            logger.error("Structured signal request failed: %s", exc)
            return None

    def get_portfolio_signal(
        self, portfolio_data: Dict[str, Dict]
    ) -> Optional[Dict[str, ClaudeSignal]]:
        """Return a signal for every symbol in *portfolio_data*."""
        signals: Dict[str, ClaudeSignal] = {}
        for symbol, data in portfolio_data.items():
            sig = self.get_trading_signal(data)
            if sig:
                signals[symbol] = sig
        return signals

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        """Format the user-turn prompt from *market_data*."""
        symbol = market_data.get("symbol", "UNKNOWN")
        data_str = json.dumps(market_data, indent=2, default=str)
        return _USER_TEMPLATE.format(symbol=symbol, data=data_str)

    def _call_api(self, prompt: str) -> Optional[str]:
        """Call the Claude API and return the text response.

        Applies:

        * **Prompt caching** — ``cache_control`` on the system block cuts
          repeated-call token costs by ≈90 % after the first cache write.
        * **Streaming** — when ``use_streaming=True`` the SDK streams tokens
          and assembles the final message via ``stream.get_final_message()``.
        * **Adaptive thinking** — when ``use_thinking=True`` Claude reasons
          internally before answering; thinking blocks are skipped when
          extracting the text reply.
        """
        if not _SDK_AVAILABLE or self._sdk is None:  # pragma: no cover
            logger.error("anthropic SDK not installed; cannot call API")
            return None

        kwargs: Dict[str, Any] = {
            "model": self.MODEL,
            "max_tokens": self.MAX_TOKENS,
            "system": _system_block(),
            "messages": [{"role": "user", "content": prompt}],
        }
        if self.use_thinking:
            kwargs["thinking"] = {"type": "adaptive"}

        try:
            if self.use_streaming:
                with self._sdk.messages.stream(**kwargs) as stream:
                    msg = stream.get_final_message()
            else:
                msg = self._sdk.messages.create(**kwargs)

            for block in msg.content:
                if block.type == "text":
                    return block.text

            logger.error("No text block in Claude response")
            return None

        except anthropic.AuthenticationError:
            logger.error("Invalid Claude API key")
        except anthropic.RateLimitError as exc:
            logger.error("Claude rate limited: %s", exc)
        except anthropic.APIStatusError as exc:
            logger.error("Claude API error %s: %s", exc.status_code, exc.message)
        except anthropic.APIConnectionError as exc:
            logger.error("Claude connection error: %s", exc)
        return None

    def _parse_response(self, response_text: str) -> ClaudeSignal:
        """Parse Claude's JSON reply into a :class:`ClaudeSignal`.

        Handles markdown code-fence wrapping defensively; used by
        :meth:`get_trading_signal` (the text-based path).
        """
        try:
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
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            logger.error(
                "Failed to parse Claude response: %s\nResponse: %s",
                exc,
                response_text,
            )
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
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Build a market-data dict ready for :meth:`get_trading_signal`."""
        data: Dict[str, Any] = {
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
        data.update(kwargs)
        return data


# ---------------------------------------------------------------------------
# Integration layer
# ---------------------------------------------------------------------------


class ClaudeAIIntegration:
    """Integration layer between Claude AI and the AI Engine."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        enabled: bool = True,
        use_streaming: bool = False,
        use_thinking: bool = False,
    ) -> None:
        self.enabled = enabled
        self.client: Optional[ClaudeAIClient] = (
            ClaudeAIClient(
                api_key,
                use_streaming=use_streaming,
                use_thinking=use_thinking,
            )
            if enabled
            else None
        )

    def validate_signal(
        self,
        symbol: str,
        engine_signal: str,
        engine_confidence: float,
        market_data: Dict[str, Any],
    ) -> tuple[str, float, str]:
        """Validate/refine an engine signal using Claude AI.

        Returns ``(signal, confidence, reason)``.
        """
        if not self.enabled or not self.client:
            return engine_signal, engine_confidence, "Claude validation disabled"

        try:
            ctx = {
                **market_data,
                "engine_signal": engine_signal,
                "engine_confidence": engine_confidence,
                "symbol": symbol,
            }
            claude_sig = self.client.get_trading_signal(ctx)
            if not claude_sig:
                return engine_signal, engine_confidence, "Claude analysis failed"

            if engine_signal == claude_sig.signal:
                refined_conf = min(
                    100.0,
                    (engine_confidence + claude_sig.confidence) / 2 * 1.1,
                )
                return (
                    engine_signal,
                    refined_conf,
                    f"Claude confirms ({claude_sig.reason})",
                )
            return (
                "HOLD",
                50.0,
                f"Conflict: Engine {engine_signal} vs Claude {claude_sig.signal}",
            )
        except Exception as exc:
            logger.error("Signal validation failed: %s", exc)
            return engine_signal, engine_confidence, "Validation error"

    def get_independent_signal(
        self, market_data: Dict[str, Any]
    ) -> Optional[ClaudeSignal]:
        """Get a completely independent signal from Claude."""
        if not self.enabled or not self.client:
            return None
        try:
            return self.client.get_trading_signal(market_data)
        except Exception as exc:
            logger.error("Failed to get independent signal: %s", exc)
            return None
