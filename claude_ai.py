# claude_ai.py
"""Claude AI integration — official Anthropic SDK with requests fallback.

New in this version
-------------------
* **Prompt caching** — the system prompt carries ``cache_control`` so
  Anthropic caches it after the first call (approx 90% token savings on
  repeated calls to the same system prompt).
* **Streaming** — opt-in via ``use_streaming=True``; avoids HTTP timeouts
  on long responses.
* **Adaptive thinking** — opt-in via ``use_thinking=True``; enables Claude's
  internal reasoning for deeper market analysis (Opus 4.x).
* **Structured outputs** — ``get_trading_signal_structured()`` attempts the
  SDK ``messages.parse()`` path; degrades to the text path on any failure.
* **Typed error handling** — ``AuthenticationError``, ``RateLimitError``,
  ``APIStatusError``, ``APIConnectionError`` are caught and logged distinctly.
* **``format_market_data()``** — static helper that builds a well-formed
  market-data dict ready for ``get_trading_signal()``.

Backwards-compatibility guarantees
-----------------------------------
* ``_call_api(prompt_text)`` remains the single patchable seam for tests.
* ``ClaudeSignal.confidence`` stays ``float``; ``raw_response`` is new but
  optional (``None`` default) so existing constructors still work.
* ``ClaudeAIIntegration.__init__`` still accepts ``client=`` for injection.
* Dual env-var lookup: ``ANTHROPIC_API_KEY`` then ``CLAUDE_API_KEY``.
* Model ID is ``claude-opus-4-20250514`` (stable date-versioned form).
* ``get_full_analysis()`` is preserved for production callers.
* Confidence clamping ``[33, 85]`` is enforced at every return path of
  ``validate_signal()`` — this is a hard safety invariant.
"""
from __future__ import annotations

import json
import logging
import os
import requests
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    import anthropic
    from pydantic import BaseModel as _BaseModel

    _SDK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SDK_AVAILABLE = False
    _BaseModel = object  # type: ignore[assignment,misc]

from prompts import get_prompt

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Confidence safety bounds — never exceed or go below these values.
# Enforced at every return path of validate_signal() — see CLAUDE.md.
# ---------------------------------------------------------------------------
_CONF_MAX: float = 85.0
_CONF_MIN: float = 33.0


def _clamp_conf(value: float) -> float:
    """Clamp confidence to [33, 85] — the project-wide safety invariant."""
    return min(_CONF_MAX, max(_CONF_MIN, float(value)))


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclass
class ClaudeSignal:
    """Claude AI generated trading signal."""

    signal: str  # "BUY", "SELL", "HOLD"
    confidence: float  # kept as float for arithmetic compatibility
    risk: str  # "LOW", "MEDIUM", "HIGH"
    reason: str
    raw_response: Optional[str] = field(default=None)  # populated by SDK path


# ---------------------------------------------------------------------------
# Pydantic schema — used by get_trading_signal_structured()
# ---------------------------------------------------------------------------


class _SignalSchema(_BaseModel):
    """Strict JSON schema for structured-output path."""

    signal: str
    confidence: int
    risk: str
    reason: str


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_MODEL = "claude-opus-4-20250514"
_MAX_TOKENS = 2048
_BASE_URL = "https://api.anthropic.com/v1/messages"

# Stable system prompt — marked with cache_control so Anthropic caches it
# after the first call. Keep this text frozen; any change resets the cache.
_SYSTEM_PROMPT = """\
You are a professional hedge fund trading system specialising in forex markets.
Analyse technical indicators and market conditions to produce actionable
trading signals.

Rules:
- If signals conflict, lean toward HOLD
- Raise confidence only when multiple indicators agree
- Risk reflects position size: HIGH=risky, MEDIUM=moderate, LOW=safe
- Confidence and risk must balance (high confidence + high risk = aggressive)"""

# User-turn template — volatile per-call data goes here.
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


def _sdk_system_block() -> List[Dict[str, Any]]:
    """Return the cached system-prompt content block."""
    return [
        {
            "type": "text",
            "text": _SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }
    ]


# ---------------------------------------------------------------------------
# ClaudeAIClient
# ---------------------------------------------------------------------------


class ClaudeAIClient:
    """Anthropic client for trading signal generation.

    Uses the official ``anthropic`` SDK when installed (prompt caching,
    streaming, thinking, structured outputs, typed errors). Falls back to
    raw ``requests`` HTTP calls when the SDK is not installed.

    The ``_call_api(prompt_text)`` method is the single entry-point mocked
    by tests — both SDK and requests paths funnel through it.
    """

    BASE_URL = _BASE_URL
    MODEL = _MODEL

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        use_streaming: bool = False,
        use_thinking: bool = False,
    ) -> None:
        self.api_key = (
            api_key
            or os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("CLAUDE_API_KEY")
        )
        if not self.api_key:
            raise ValueError("Claude API key is required")
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
        """Return a trading signal for *market_data*, or ``None`` on error."""
        prompt = self._build_prompt(market_data)
        raw = self._call_api(prompt)
        if raw is None:
            return None
        sig = self._parse_signal(raw)
        sig.raw_response = raw
        return sig

    def get_trading_signal_structured(
        self, market_data: Dict[str, Any]
    ) -> Optional[ClaudeSignal]:
        """Return a signal via the SDK structured-output path.

        Attempts ``client.messages.parse()`` with Pydantic schema enforcement.
        Degrades to :meth:`get_trading_signal` on any error or if SDK absent.
        """
        if not _SDK_AVAILABLE or self._sdk is None:  # pragma: no cover
            return self.get_trading_signal(market_data)

        prompt = self._build_prompt(market_data)
        kwargs: Dict[str, Any] = {
            "model": self.MODEL,
            "max_tokens": _MAX_TOKENS,
            "system": _sdk_system_block(),
            "messages": [{"role": "user", "content": prompt}],
        }
        if self.use_thinking:
            kwargs["thinking"] = {"type": "adaptive"}

        try:
            response = self._sdk.messages.parse(  # type: ignore[attr-defined]
                output_format=_SignalSchema, **kwargs
            )
            parsed = response.parsed_output  # type: ignore[attr-defined]
            sig = ClaudeSignal(
                signal=parsed.signal.upper(),
                confidence=float(parsed.confidence),
                risk=parsed.risk.upper(),
                reason=parsed.reason,
            )
            for block in response.content:
                if block.type == "text":
                    sig.raw_response = block.text
                    break
            return sig
        except Exception as exc:
            logger.warning(
                "Structured output path failed (%s); retrying via text path", exc
            )
            return self.get_trading_signal(market_data)

    def get_portfolio_signal(
        self, portfolio: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, ClaudeSignal]]:
        """Return a signal for every symbol in *portfolio*."""
        signals: Dict[str, ClaudeSignal] = {}
        for symbol, market_data in portfolio.items():
            signal = self.get_trading_signal(market_data)
            if signal is None:
                return None
            signals[symbol] = signal
        return signals

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

    # ------------------------------------------------------------------
    # Internal dispatch — this is the seam mocked by tests
    # ------------------------------------------------------------------

    def _call_api(self, prompt_text: str) -> Optional[str]:
        """Return raw text from Claude.

        Routes to the SDK path (prompt caching, streaming, thinking) when
        ``anthropic`` is installed, otherwise falls back to raw ``requests``.
        Tests patch this method to bypass the network entirely.
        """
        if _SDK_AVAILABLE and self._sdk is not None:
            return self._call_api_sdk(prompt_text)
        return self._call_api_requests(prompt_text)  # pragma: no cover

    def _call_api_sdk(self, prompt_text: str) -> Optional[str]:
        """SDK-backed call with prompt caching, optional streaming, optional thinking."""
        kwargs: Dict[str, Any] = {
            "model": self.MODEL,
            "max_tokens": _MAX_TOKENS,
            "system": _sdk_system_block(),
            "messages": [{"role": "user", "content": prompt_text}],
        }
        if self.use_thinking:
            kwargs["thinking"] = {"type": "adaptive"}

        try:
            if self.use_streaming:
                with self._sdk.messages.stream(**kwargs) as stream:  # type: ignore[union-attr]
                    msg = stream.get_final_message()
            else:
                msg = self._sdk.messages.create(**kwargs)  # type: ignore[union-attr]

            for block in msg.content:
                if block.type == "text":
                    return block.text

            logger.error("No text block in Claude response")
            return None

        except anthropic.AuthenticationError:  # type: ignore[attr-defined]
            logger.error("Invalid Claude API key")
        except anthropic.RateLimitError as exc:  # type: ignore[attr-defined]
            logger.error("Claude rate limited: %s", exc)
        except anthropic.APIStatusError as exc:  # type: ignore[attr-defined]
            logger.error("Claude API error %s: %s", exc.status_code, exc.message)
        except anthropic.APIConnectionError as exc:  # type: ignore[attr-defined]
            logger.error("Claude connection error: %s", exc)
        except Exception as exc:
            logger.error("Claude SDK call failed: %s", exc)
        return None

    def _call_api_requests(self, prompt_text: str) -> Optional[str]:
        """Fallback raw-HTTP call used when the SDK is not installed."""
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
        except Exception as exc:
            logger.error("Claude requests call failed: %s", exc)
            return None

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        """Format the user-turn prompt from *market_data*."""
        symbol = market_data.get("symbol", "UNKNOWN")
        data_str = json.dumps(market_data, indent=2, default=str)
        return _USER_TEMPLATE.format(symbol=symbol, data=data_str)

    def _parse_signal(self, raw: str) -> ClaudeSignal:
        """Parse Claude's JSON reply into a :class:`ClaudeSignal`.

        Handles markdown code-fence wrapping defensively.
        """
        payload = raw.strip()
        if payload.startswith("```json"):
            payload = payload[7:]
        if payload.startswith("```"):
            payload = payload[3:]
        if payload.endswith("```"):
            payload = payload[:-3]

        try:
            data = json.loads(payload.strip())
            return ClaudeSignal(
                signal=str(data.get("signal", "HOLD")).upper(),
                confidence=float(data.get("confidence", 50.0)),
                risk=str(data.get("risk", "MEDIUM")).upper(),
                reason=str(data.get("reason", "")),
            )
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            logger.warning("Could not parse Claude signal response: %s", exc)
            return ClaudeSignal(
                signal="HOLD",
                confidence=33.0,
                risk="HIGH",
                reason="Malformed Claude response",
            )


# ---------------------------------------------------------------------------
# ClaudeAIIntegration
# ---------------------------------------------------------------------------


class ClaudeAIIntegration:
    """Integration layer between Claude AI and the AI Engine."""

    BASE_URL = _BASE_URL
    MODEL = _MODEL

    def __init__(
        self,
        api_key: Optional[str] = None,
        enabled: bool = True,
        client: Optional[ClaudeAIClient] = None,
        use_streaming: bool = False,
        use_thinking: bool = False,
    ) -> None:
        self.api_key = (
            api_key
            or os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("CLAUDE_API_KEY")
        )
        self.enabled = enabled and (bool(self.api_key) or client is not None)
        self.client = client
        if self.enabled and self.client is None:
            self.client = ClaudeAIClient(
                api_key=self.api_key,
                use_streaming=use_streaming,
                use_thinking=use_thinking,
            )
        if not self.enabled:
            logger.warning("Claude AI integration disabled - no API key")

    def get_full_analysis(self, report_type: str, **kwargs: Any) -> str:
        """Generate professional analysis using Claude.

        Preserved for production callers in ai_engine.py, webhook_server.py,
        and monthly_dividend_report.py.
        """
        if not self.enabled:
            return "Claude AI is disabled"

        try:
            prompt_text = get_prompt(report_type, **kwargs)

            if (
                _SDK_AVAILABLE
                and self.client is not None
                and self.client._sdk is not None
            ):
                msg = self.client._sdk.messages.create(  # type: ignore[union-attr]
                    model=self.MODEL,
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt_text}],
                )
                for block in msg.content:
                    if block.type == "text":
                        return block.text
                return "No response from Claude"

            # Fallback: raw requests
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

        except Exception as exc:
            logger.error("Claude API error: %s", exc)
            return f"Error: {str(exc)}"

    def test_connection(self) -> bool:
        """Test if API key works."""
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
        """Validate/refine an engine signal using Claude AI.

        Returns ``(signal, confidence, reason)``.

        Confidence is clamped to ``[33, 85]`` at every return path.
        This is a hard safety invariant — see CLAUDE.md.
        """
        engine_signal = engine_signal.upper()
        engine_confidence = _clamp_conf(engine_confidence)

        if not self.enabled or self.client is None:
            return engine_signal, engine_confidence, "Claude AI disabled"

        data = dict(market_data)
        data["symbol"] = symbol
        claude_signal = self.client.get_trading_signal(data)
        if claude_signal is None:
            return engine_signal, engine_confidence, "Claude AI unavailable"

        if claude_signal.signal == engine_signal:
            confidence = _clamp_conf(
                (engine_confidence + claude_signal.confidence) / 2
            )
            return engine_signal, confidence, claude_signal.reason

        if claude_signal.signal == "HOLD":
            return engine_signal, engine_confidence, claude_signal.reason

        return (
            "HOLD",
            _clamp_conf(min(engine_confidence, claude_signal.confidence)),
            f"Conflict with Claude signal: {claude_signal.reason}",
        )

    def get_independent_signal(
        self, market_data: Dict[str, Any]
    ) -> Optional[ClaudeSignal]:
        """Get an independent signal from Claude (no engine signal to validate)."""
        if not self.enabled or self.client is None:
            return None
        return self.client.get_trading_signal(market_data)
