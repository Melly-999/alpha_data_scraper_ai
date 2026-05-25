from __future__ import annotations

from app.schemas.portfolio_risk import (
    PortfolioRiskExposure,
    PortfolioRiskLimits,
    PortfolioRiskPosture,
    PortfolioRiskSummaryResponse,
)

# ---------------------------------------------------------------------------
# Deterministic safe-fallback constants
# No broker calls, no external API calls, no writes, no secrets.
# ---------------------------------------------------------------------------

_MAX_RISK_PER_TRADE_PCT: float = 1.0
_MAX_PORTFOLIO_RISK_PCT: float = 5.0


class PortfolioRiskSummaryService:
    """
    Produces a deterministic, read-only portfolio risk summary.

    This service performs zero broker calls, zero external API calls, and zero
    writes.  It does not import or reference MT5, IBKR, Alpaca, ccxt, requests,
    httpx, websockets, Supabase client, or any broker SDK.  It does not read
    secrets, account IDs, or environment credentials.
    """

    def get_summary(self) -> PortfolioRiskSummaryResponse:
        """Return a deterministic advisory portfolio risk snapshot."""
        exposure = PortfolioRiskExposure(
            total_positions=1,
            open_positions=0,
            total_notional=0.0,
            gross_exposure_pct=0.0,
            net_exposure_pct=0.0,
            cash_buffer_pct=100.0,
        )
        limits = PortfolioRiskLimits(
            max_risk_per_trade_pct=_MAX_RISK_PER_TRADE_PCT,
            max_portfolio_risk_pct=_MAX_PORTFOLIO_RISK_PCT,
            risk_used_pct=0.0,
            remaining_risk_capacity_pct=_MAX_PORTFOLIO_RISK_PCT,
            max_open_positions=5,
        )
        posture = PortfolioRiskPosture(
            label="dry_run_only",
            status="ok",
            broker_execution_allowed=False,
            live_orders_blocked=True,
            risk_allowed=False,
            requires_human_review=True,
        )
        return PortfolioRiskSummaryResponse(
            status="ok",
            exposure=exposure,
            limits=limits,
            posture=posture,
        )
