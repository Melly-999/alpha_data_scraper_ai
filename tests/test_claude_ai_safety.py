"""Safety invariant tests for claude_ai.py — SDK migration (CLAUDE-SDK-001).

Five targeted tests that verify the hard safety requirements from CLAUDE.md:
confidence stays in [33, 85], get_full_analysis() survives, client injection
works, and both env-var lookup paths are honoured.
"""

from __future__ import annotations

import json
import os
from unittest.mock import MagicMock, patch

from claude_ai import (
    ClaudeAIClient,
    ClaudeAIIntegration,
    ClaudeSignal,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MARKET_DATA: dict = {
    "symbol": "EURUSD",
    "current_price": 1.1050,
    "rsi": 60.0,
    "macd_hist": 0.001,
}


def _raw(signal: str = "BUY", confidence: int = 85, risk: str = "MEDIUM") -> str:
    return json.dumps(
        {"signal": signal, "confidence": confidence, "risk": risk, "reason": "test"}
    )


def _make_client(api_key: str = "sk-test") -> ClaudeAIClient:
    return ClaudeAIClient(api_key=api_key)


# ---------------------------------------------------------------------------
# 1. Agreement path caps at 85
# ---------------------------------------------------------------------------


def test_validate_signal_agreement_caps_at_85():
    """When engine=BUY@85 and Claude=BUY@85, averaged result must be ≤85.0."""
    client = _make_client()
    with patch.object(client, "_call_api", return_value=_raw("BUY", 85)):
        integration = ClaudeAIIntegration(client=client)
        sig, conf, reason = integration.validate_signal(
            "EURUSD", "BUY", 85.0, _MARKET_DATA
        )

    assert sig == "BUY"
    assert conf <= 85.0, f"Confidence {conf} exceeds 85 — clamping invariant broken"
    assert conf >= 33.0
    assert isinstance(conf, float)


# ---------------------------------------------------------------------------
# 2. Agreement path floors at 33
# ---------------------------------------------------------------------------


def test_validate_signal_agreement_floors_at_33():
    """When engine=SELL@10 and Claude=SELL@10 (below floor), result must be ≥33.0."""
    client = _make_client()
    with patch.object(client, "_call_api", return_value=_raw("SELL", 10)):
        integration = ClaudeAIIntegration(client=client)
        sig, conf, reason = integration.validate_signal(
            "EURUSD", "SELL", 10.0, _MARKET_DATA
        )

    assert sig == "SELL"
    assert conf >= 33.0, f"Confidence {conf} below 33 — floor invariant broken"
    assert conf <= 85.0
    assert isinstance(conf, float)


# ---------------------------------------------------------------------------
# 3. get_full_analysis() exists and returns str (or safe fallback)
# ---------------------------------------------------------------------------


def test_get_full_analysis_method_exists_and_returns_string_or_safe_fallback():
    """Disabled integration must return a plain string, not raise or return None."""
    integration = ClaudeAIIntegration(api_key=None, enabled=False)
    result = integration.get_full_analysis("market_summary", symbol="EURUSD")

    assert isinstance(result, str), "get_full_analysis must always return str"
    assert result  # non-empty


# ---------------------------------------------------------------------------
# 4. client= injection works without an API key
# ---------------------------------------------------------------------------


def test_claude_ai_integration_accepts_client_injection():
    """ClaudeAIIntegration(client=<injected>) must work even if no api_key env var."""
    mock_client = MagicMock(spec=ClaudeAIClient)
    mock_client.get_trading_signal.return_value = ClaudeSignal(
        signal="HOLD", confidence=50.0, risk="MEDIUM", reason="injected"
    )

    env_patch = {"ANTHROPIC_API_KEY": "", "CLAUDE_API_KEY": ""}
    with patch.dict(os.environ, env_patch, clear=False):
        # Remove vars if present so no key leaks through
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ.pop("CLAUDE_API_KEY", None)
        integration = ClaudeAIIntegration(api_key=None, client=mock_client)

    assert (
        integration.enabled is True
    ), "Integration must be enabled when client is injected"
    assert integration.client is mock_client


# ---------------------------------------------------------------------------
# 5. Dual env-var lookup: ANTHROPIC_API_KEY then CLAUDE_API_KEY
# ---------------------------------------------------------------------------


def test_dual_env_lookup_prefers_api_key_then_anthropic_then_claude():
    """Client picks up ANTHROPIC_API_KEY first; CLAUDE_API_KEY is the fallback."""
    # Case A: only ANTHROPIC_API_KEY is set
    with patch.dict(
        os.environ,
        {"ANTHROPIC_API_KEY": "sk-anthro", "CLAUDE_API_KEY": ""},
        clear=False,
    ):
        os.environ.pop("CLAUDE_API_KEY", None)
        client_a = ClaudeAIClient()
    assert client_a.api_key == "sk-anthro", "Should pick up ANTHROPIC_API_KEY"

    # Case B: only CLAUDE_API_KEY is set (legacy name)
    with patch.dict(
        os.environ,
        {"CLAUDE_API_KEY": "sk-claude-legacy", "ANTHROPIC_API_KEY": ""},
        clear=False,
    ):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        client_b = ClaudeAIClient()
    assert client_b.api_key == "sk-claude-legacy", "Should fall back to CLAUDE_API_KEY"

    # Case C: explicit api_key param overrides env vars
    with patch.dict(
        os.environ,
        {"ANTHROPIC_API_KEY": "sk-env", "CLAUDE_API_KEY": "sk-env2"},
        clear=False,
    ):
        client_c = ClaudeAIClient(api_key="sk-explicit")
    assert client_c.api_key == "sk-explicit", "Explicit param must take priority"
