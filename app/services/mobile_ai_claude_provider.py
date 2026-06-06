"""MOBILE-AI-008C — Real Claude (Anthropic) analysis provider.

Backend-only, **default-disabled** provider for the screenshot preview
endpoint. It is selected only when ``MOBILE_AI_PROVIDER=claude`` AND
``MOBILE_AI_PROVIDER_ENABLED=true`` AND an ``ANTHROPIC_API_KEY`` is present
(see ``app/services/mobile_ai_provider.py``).

Hard safety rules enforced here, regardless of model output:

  * the image is sent to Anthropic for analysis only and is never stored or
    logged (only its size/MIME are used locally),
  * the model may only fill **descriptive** chart-review text fields; it can
    never set risk numbers, the paper plan, or any safety flag,
  * the returned ``ScreenshotAnalysisPreview`` keeps every execution-safety
    flag locked (paper-only, live-orders-blocked, broker-execution false,
    human-review required) and the risk ceiling (≤ 1%) from the deterministic
    scaffold; only ``provider_used`` flips to ``True``,
  * no broker, order, wallet, or execution surface exists in this module.

``anthropic`` is imported lazily so importing this module never requires the
SDK or a key, and the default (disabled) path never touches it.

Enabling this provider sends uploaded screenshots to Anthropic; review the
provider's data-use policy and the image privacy/retention policy first
(``docs/mobile/mobile_ai_image_privacy_retention_policy.md``).
"""

from __future__ import annotations

import base64
import json
import os
from typing import Any

from app.schemas.mobile_ai import ChartAnalysisResult, ScreenshotAnalysisPreview
from app.services.mobile_ai_provider import build_preview

DEFAULT_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 1024

# Descriptive-only extraction. The model never sets risk, plan, or safety flags.
_SYSTEM_PROMPT = (
    "You are a read-only chart screenshot analyst for a paper-trading study "
    "tool. Return ONLY a compact JSON object with these string/array fields: "
    "market_bias, trend, momentum, volatility, pattern, key_levels (array of "
    "strings), confirmation_checklist (array of strings). Describe the chart "
    "for educational review only. Do NOT give financial advice, do NOT provide "
    "entry/exit prices, position sizes, or any instruction to buy, sell, or "
    "execute. Analysis only."
)
_USER_PROMPT = "Describe this chart screenshot as JSON for paper-only review."


class ClaudeProviderError(RuntimeError):
    """Raised when the Claude provider cannot produce a result."""


class ClaudeProvider:
    """Real backend Claude provider (analysis-only). Default-disabled."""

    name = "claude"

    def __init__(self) -> None:
        self._api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        if not self._api_key:
            raise ClaudeProviderError("No backend API key configured.")
        self._model = os.getenv("CLAUDE_MOBILE_AI_MODEL") or DEFAULT_MODEL

    def analyze(self, image_bytes: bytes, mime: str) -> ScreenshotAnalysisPreview:
        """Send the image to Claude for descriptive analysis (analysis only).

        Any failure raises ``ClaudeProviderError`` so the caller degrades to
        the safe deterministic stub. Safety flags and risk are always taken
        from the locked scaffold, never from the model.
        """
        raw = self._call_model(image_bytes, mime)
        chart = self._chart_from_model(raw)

        # Start from the deterministic, safety-locked scaffold and override only
        # the descriptive chart-review block + the informational provider flag.
        # Risk, paper plan, and all execution-safety flags stay as scaffolded.
        scaffold = build_preview()
        return scaffold.model_copy(
            update={"chart_analysis": chart, "provider_used": True}
        )

    def _call_model(self, image_bytes: bytes, mime: str) -> str:
        """Return the raw text from Claude. Lazy-imports the SDK."""
        try:
            import anthropic  # lazy: never imported on the default disabled path
        except Exception as exc:  # pragma: no cover - import guard
            raise ClaudeProviderError("anthropic SDK unavailable") from exc

        try:
            client = anthropic.Anthropic(api_key=self._api_key)
            encoded = base64.standard_b64encode(image_bytes).decode("ascii")
            # Typed as Any: a plain dict payload that is valid at runtime but
            # does not need to match the SDK's strict TypedDict param shapes.
            messages: Any = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime,
                                "data": encoded,
                            },
                        },
                        {"type": "text", "text": _USER_PROMPT},
                    ],
                }
            ]
            message = client.messages.create(
                model=self._model,
                max_tokens=_MAX_TOKENS,
                system=_SYSTEM_PROMPT,
                messages=messages,
            )
            parts = [
                getattr(block, "text", "") for block in getattr(message, "content", [])
            ]
            return "".join(parts).strip()
        except ClaudeProviderError:
            raise
        except Exception as exc:
            # Never leak provider/network/key details to the caller.
            raise ClaudeProviderError("Claude analysis failed") from exc

    def _chart_from_model(self, raw: str) -> ChartAnalysisResult:
        """Build a descriptive ChartAnalysisResult from the model JSON.

        Falls back to the deterministic scaffold's chart block if the response
        is missing, not JSON, or fails schema validation. Only descriptive
        fields are taken from the model; safety flags stay schema-locked.
        """
        fallback = build_preview().chart_analysis
        if not raw:
            return fallback

        text = raw.strip()
        if text.startswith("```"):
            # Strip a ``` / ```json fence if present.
            text = text.split("```", 2)[1] if "```" in text[3:] else text.strip("`")
            if text.lstrip().lower().startswith("json"):
                text = text.lstrip()[4:]

        try:
            data = json.loads(text)
        except (ValueError, TypeError):
            return fallback
        if not isinstance(data, dict):
            return fallback

        allowed = {
            "instrument",
            "timeframe",
            "trading_style",
            "market_bias",
            "trend",
            "key_levels",
            "momentum",
            "volatility",
            "pattern",
            "confirmation_checklist",
        }
        payload = {k: v for k, v in data.items() if k in allowed}
        merged = fallback.model_dump()
        merged.update(payload)
        try:
            # Pydantic re-validates: bad enums/lengths fall back to scaffold.
            # Safety flags are defaults on the model and cannot be set here.
            return ChartAnalysisResult(**merged)
        except Exception:
            return fallback
