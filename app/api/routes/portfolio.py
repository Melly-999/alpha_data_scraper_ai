from __future__ import annotations

from fastapi import APIRouter

from app.schemas.portfolio_risk import PortfolioRiskSummaryResponse
from app.services.portfolio_risk_summary import PortfolioRiskSummaryService

router = APIRouter(tags=["portfolio"])

_portfolio_risk_service = PortfolioRiskSummaryService()


@router.get("/portfolio/risk-summary", response_model=PortfolioRiskSummaryResponse)
def portfolio_risk_summary() -> PortfolioRiskSummaryResponse:
    """Read-only advisory portfolio risk summary.

    No execution, no broker call, no mutation, no persistence.
    Returns a deterministic snapshot of the paper/read-only portfolio posture.
    """
    return _portfolio_risk_service.get_summary()
