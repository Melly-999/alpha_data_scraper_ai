"""MOBILE-AI-008C — Tests for the real Claude analysis provider.

The Anthropic SDK call (``_call_model``) is always mocked — no network call is
made in CI. Confirms: key required, locked/safe response with provider_used,
the model can only fill descriptive fields (never risk or safety flags),
robust fallback on bad output, and safe degradation via provider selection.
"""

from __future__ import annotations

import inspect

import pytest

from app.services import mobile_ai_provider as provider_module
from app.services.mobile_ai_claude_provider import (
    ClaudeProvider,
    ClaudeProviderError,
)
from app.services.mobile_ai_provider import StubProvider

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32

VALID_JSON = (
    '{"market_bias": "Bullish", "trend": "Up short-term", '
    '"momentum": "Strong", "volatility": "High", "pattern": "Breakout retest", '
    '"key_levels": ["Support 1", "Resistance 2"], '
    '"confirmation_checklist": ["M15 close confirms"]}'
)


def _assert_locked(preview, provider_used: bool) -> None:
    assert preview.analysis_only is True
    assert preview.paper_only is True
    assert preview.live_orders_blocked is True
    assert preview.broker_execution is False
    assert preview.requires_human_review is True
    assert preview.stored is False
    assert preview.provider_used is provider_used
    assert preview.paper_game_plan.max_risk_per_trade_pct <= 1.0
    assert preview.risk_assessment.risk_per_trade_pct <= 1.0


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_requires_backend_api_key(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
    with pytest.raises(ClaudeProviderError):
        ClaudeProvider()


# ---------------------------------------------------------------------------
# analyze() — model output is descriptive only; safety is forced in code
# ---------------------------------------------------------------------------


def test_analyze_returns_locked_preview_with_provider_used(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    provider = ClaudeProvider()
    monkeypatch.setattr(provider, "_call_model", lambda image_bytes, mime: VALID_JSON)

    preview = provider.analyze(PNG, "image/png")

    _assert_locked(preview, provider_used=True)
    assert preview.chart_analysis.market_bias.value == "Bullish"
    assert preview.chart_analysis.pattern == "Breakout retest"


def test_analyze_falls_back_on_non_json(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    provider = ClaudeProvider()
    monkeypatch.setattr(provider, "_call_model", lambda image_bytes, mime: "not json")

    preview = provider.analyze(PNG, "image/png")

    _assert_locked(preview, provider_used=True)
    # Falls back to the deterministic scaffold chart content.
    assert preview.chart_analysis.instrument == "XAUUSD"


def test_model_cannot_set_risk_or_safety_flags(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    provider = ClaudeProvider()
    evil = (
        '{"market_bias": "Bullish", "broker_execution": true, '
        '"live_orders_blocked": false, "max_risk_per_trade_pct": 50, '
        '"risk_per_trade_pct": 99, "place_order": true, "stored": true}'
    )
    monkeypatch.setattr(provider, "_call_model", lambda image_bytes, mime: evil)

    preview = provider.analyze(PNG, "image/png")

    # Injected execution/risk keys are ignored; flags + risk stay locked.
    _assert_locked(preview, provider_used=True)
    assert preview.chart_analysis.market_bias.value == "Bullish"


def test_call_model_error_propagates(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    provider = ClaudeProvider()

    def boom(image_bytes: bytes, mime: str) -> str:
        raise ClaudeProviderError("network down")

    monkeypatch.setattr(provider, "_call_model", boom)
    with pytest.raises(ClaudeProviderError):
        provider.analyze(PNG, "image/png")


# ---------------------------------------------------------------------------
# Provider selection (default-disabled real provider)
# ---------------------------------------------------------------------------


def test_select_claude_when_enabled_with_key(monkeypatch) -> None:
    monkeypatch.setenv("MOBILE_AI_PROVIDER", "claude")
    monkeypatch.setenv("MOBILE_AI_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    assert isinstance(provider_module.select_provider(), ClaudeProvider)


def test_select_claude_enabled_without_key_degrades_to_stub(monkeypatch) -> None:
    monkeypatch.setenv("MOBILE_AI_PROVIDER", "claude")
    monkeypatch.setenv("MOBILE_AI_PROVIDER_ENABLED", "true")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
    assert isinstance(provider_module.select_provider(), StubProvider)


def test_select_claude_disabled_degrades_to_stub(monkeypatch) -> None:
    monkeypatch.setenv("MOBILE_AI_PROVIDER", "claude")
    monkeypatch.setenv("MOBILE_AI_PROVIDER_ENABLED", "false")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    assert isinstance(provider_module.select_provider(), StubProvider)


# ---------------------------------------------------------------------------
# Source-level safety (no execution / order / file-write surface)
# ---------------------------------------------------------------------------


def test_claude_module_defines_no_execution_functions() -> None:
    from app.services import mobile_ai_claude_provider as module

    names = {name for name, _ in inspect.getmembers(module, inspect.isfunction)}
    assert not (
        names
        & {
            "place_order",
            "cancel_order",
            "modify_order",
            "execute_trade",
            "submit_order",
            "broker_execute",
        }
    )


def test_claude_module_does_not_write_files() -> None:
    from app.services import mobile_ai_claude_provider as module

    src = inspect.getsource(module)
    assert "open(" not in src
    assert '"wb"' not in src and "'wb'" not in src
