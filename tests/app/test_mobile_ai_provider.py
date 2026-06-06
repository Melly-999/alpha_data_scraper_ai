"""MOBILE-AI-008B — Tests for the backend AI provider abstraction.

Confirms the mock default, safe degradation to the stub for unknown / not-yet-
implemented providers, error fallback, locked response posture, and that the
provider module carries no execution / network / provider-key surface.
"""

from __future__ import annotations

import inspect

import pytest

from app.services import mobile_ai_provider as provider_module
from app.services.mobile_ai_provider import (
    MockProvider,
    StubProvider,
    run_analysis,
    select_provider,
)

FORBIDDEN_LIBRARIES = (
    "ib_insync",
    "ibapi",
    "MetaTrader5",
    "requests",
    "httpx",
    "websockets",
    "alpaca",
    "ccxt",
    "openai",
    "anthropic",
    "boto3",
)

FORBIDDEN_FUNCTION_NAMES = {
    "place_order",
    "cancel_order",
    "modify_order",
    "execute_trade",
    "submit_order",
    "broker_execute",
}

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


def _assert_locked(preview) -> None:
    assert preview.analysis_only is True
    assert preview.paper_only is True
    assert preview.live_orders_blocked is True
    assert preview.broker_execution is False
    assert preview.requires_human_review is True
    assert preview.stored is False
    assert preview.provider_used is False
    assert preview.paper_game_plan.max_risk_per_trade_pct <= 1.0
    assert preview.risk_assessment.risk_per_trade_pct <= 1.0


# ---------------------------------------------------------------------------
# Provider selection
# ---------------------------------------------------------------------------


def test_default_provider_is_mock(monkeypatch) -> None:
    monkeypatch.delenv("MOBILE_AI_PROVIDER", raising=False)
    assert isinstance(select_provider(), MockProvider)


def test_explicit_mock_provider(monkeypatch) -> None:
    monkeypatch.setenv("MOBILE_AI_PROVIDER", "mock")
    assert isinstance(select_provider(), MockProvider)


@pytest.mark.parametrize("name", ["claude", "openai", "anything-else"])
def test_unimplemented_or_unknown_provider_degrades_to_stub(
    monkeypatch, name: str
) -> None:
    monkeypatch.setenv("MOBILE_AI_PROVIDER", name)
    assert isinstance(select_provider(), StubProvider)


def test_empty_provider_env_defaults_to_mock(monkeypatch) -> None:
    # An empty value is treated as unset → safe deterministic mock default.
    monkeypatch.setenv("MOBILE_AI_PROVIDER", "")
    assert isinstance(select_provider(), MockProvider)


# ---------------------------------------------------------------------------
# Analysis output is locked and safe
# ---------------------------------------------------------------------------


def test_mock_provider_returns_locked_preview() -> None:
    _assert_locked(MockProvider().analyze(PNG, "image/png"))


def test_stub_provider_returns_locked_preview() -> None:
    _assert_locked(StubProvider().analyze(PNG, "image/png"))


def test_run_analysis_default_is_locked(monkeypatch) -> None:
    monkeypatch.delenv("MOBILE_AI_PROVIDER", raising=False)
    _assert_locked(run_analysis(PNG, "image/png"))


def test_run_analysis_degrades_on_provider_error(monkeypatch) -> None:
    class Boom:
        name = "boom"

        def analyze(self, image_bytes: bytes, mime: str):
            raise RuntimeError("provider exploded")

    monkeypatch.setattr(provider_module, "select_provider", lambda: Boom())
    # Must not raise; degrades to the safe stub preview.
    _assert_locked(run_analysis(PNG, "image/png"))


# ---------------------------------------------------------------------------
# Source-level safety
# ---------------------------------------------------------------------------


def test_provider_module_imports_no_forbidden_libraries() -> None:
    src = inspect.getsource(provider_module)
    for lib in FORBIDDEN_LIBRARIES:
        assert lib not in src, f"provider module references forbidden lib '{lib}'"


def test_provider_module_defines_no_execution_functions() -> None:
    names = {
        name for name, _ in inspect.getmembers(provider_module, inspect.isfunction)
    }
    assert not (names & FORBIDDEN_FUNCTION_NAMES)


def test_provider_module_does_not_write_files() -> None:
    src = inspect.getsource(provider_module)
    assert "open(" not in src
    assert '"wb"' not in src and "'wb'" not in src
