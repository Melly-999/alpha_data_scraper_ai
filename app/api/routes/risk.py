from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.risk import (
    EmergencyStopResponse,
    RiskConfig,
    RiskConfigUpdate,
    RiskStatus,
    RiskViolation,
)

router = APIRouter(tags=["risk"])


@router.get("/risk/config", response_model=RiskConfig)
def risk_config(container: AppContainer = Depends(get_container)) -> RiskConfig:
    return container.risk_service.get_config()


@router.put("/risk/config", response_model=RiskConfig)
def update_risk_config(
    payload: RiskConfigUpdate,
    container: AppContainer = Depends(get_container),
) -> RiskConfig:
    return container.risk_service.update_config(payload)


@router.get("/risk/status", response_model=RiskStatus)
def risk_status(container: AppContainer = Depends(get_container)) -> RiskStatus:
    account = container.account_service.get_account_overview()
    return container.risk_service.get_status(
        open_positions=account.open_positions,
        drawdown=account.drawdown,
        daily_loss_used=abs(account.daily_pnl_pct),
    )


@router.get("/risk/violations", response_model=list[RiskViolation])
def risk_violations(
    container: AppContainer = Depends(get_container),
) -> list[RiskViolation]:
    return container.risk_service.list_violations()


@router.post("/risk/emergency-stop", response_model=EmergencyStopResponse)
def emergency_stop(
    container: AppContainer = Depends(get_container),
) -> EmergencyStopResponse:
    return container.risk_service.trigger_emergency_stop()
