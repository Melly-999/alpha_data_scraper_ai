"""MOBILE-AI-008B — Backend AI provider abstraction (mock default).

Selects the analysis implementation behind the screenshot preview endpoint.
This module is the pluggable provider layer described in
``docs/mobile/mobile_ai_provider_integration_contract.md``.

Safety (008B scope):
  * default provider is the deterministic ``mock`` — no network, no AI provider
    call, no key required,
  * any other selection degrades to the safe ``stub`` (also deterministic),
  * no image storage / persistence / logging,
  * the response is always the Literal-locked ``ScreenshotAnalysisPreview``
    (analysis-only, paper-only); ``provider_used`` stays ``False`` because no
    real provider runs in this slice.

A real backend provider (Claude) is introduced only in MOBILE-AI-008C, behind
an explicit env flag and key — never in the frontend.
"""

from __future__ import annotations

import os
from typing import Protocol

from app.schemas.mobile_ai import (
    ChartAnalysisResult,
    MarketBias,
    PaperGamePlan,
    RiskAssessment,
    RiskLevel,
    ScreenshotAnalysisPreview,
)

# Default provider when ``MOBILE_AI_PROVIDER`` is unset.
DEFAULT_PROVIDER = "mock"


def build_preview() -> ScreenshotAnalysisPreview:
    """Return the deterministic analysis-only preview.

    Content is static and advisory only — no AI provider, no OCR, and no
    dependence on image contents beyond successful validation. Mirrors the
    safe ``/mobile`` mock copy. ``provider_used`` stays ``False``.
    """
    chart = ChartAnalysisResult(
        instrument="XAUUSD",
        timeframe="M15",
        trading_style="Intraday / paper only",
        market_bias=MarketBias.NEUTRAL_BULLISH,
        trend="Bullish short-term",
        key_levels=["Support 2,318-2,322", "Resistance 2,341-2,346"],
        momentum="Improving",
        volatility=RiskLevel.HIGH,
        pattern="Retest continuation candidate",
        confirmation_checklist=[
            "M15 close confirms",
            "Retest holds",
            "Momentum confirms",
            "Risk <= 1%",
        ],
    )
    plan = PaperGamePlan(
        scenario="Long only if confirmed",
        entry_zone="2,322 - 2,326 (example)",
        invalidation="M15 candle close below 2,316 (example)",
        take_profit_1="2,341 (example)",
        take_profit_2="2,352 (example)",
        max_risk_per_trade_pct=1.0,
    )
    risk = RiskAssessment(
        safety_score=82,
        risk_per_trade_pct=1.0,
        stop_loss_present=True,
        take_profit_present=True,
        overtrading_risk=RiskLevel.MEDIUM,
        news_risk=RiskLevel.HIGH,
    )
    return ScreenshotAnalysisPreview(
        chart_analysis=chart,
        paper_game_plan=plan,
        risk_assessment=risk,
    )


class AnalysisProvider(Protocol):
    """A backend analysis provider. Implementations must not store the image."""

    name: str

    def analyze(self, image_bytes: bytes, mime: str) -> ScreenshotAnalysisPreview: ...


class MockProvider:
    """Deterministic default provider — no network, no key, no real call."""

    name = "mock"

    def analyze(self, image_bytes: bytes, mime: str) -> ScreenshotAnalysisPreview:
        return build_preview()


class StubProvider:
    """Safe fallback used when a provider is unavailable, unknown, or errors."""

    name = "stub"

    def analyze(self, image_bytes: bytes, mime: str) -> ScreenshotAnalysisPreview:
        return build_preview()


def _provider_name() -> str:
    """Return the configured provider name (backend env only), lowercased."""
    return (os.getenv("MOBILE_AI_PROVIDER") or DEFAULT_PROVIDER).strip().lower()


def select_provider() -> AnalysisProvider:
    """Pick the analysis provider from backend config.

    008B only ships ``mock`` (default) and ``stub`` (fallback). Any other
    selection — including ``claude``, whose real implementation arrives in
    008C — safely degrades to the deterministic stub.
    """
    name = _provider_name()
    if name == "mock":
        return MockProvider()
    # Unknown / not-yet-implemented provider (e.g. "claude" before 008C):
    # degrade to the safe deterministic stub. No network, no key, no error.
    return StubProvider()


def run_analysis(image_bytes: bytes, mime: str) -> ScreenshotAnalysisPreview:
    """Run the selected provider, degrading to the stub on any error.

    The image bytes are passed through for analysis only and are never stored
    or logged here.
    """
    provider = select_provider()
    try:
        return provider.analyze(image_bytes, mime)
    except Exception:
        # Degraded fallback — never surface a provider error to the caller.
        return StubProvider().analyze(image_bytes, mime)
