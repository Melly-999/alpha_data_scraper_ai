from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.dashboard import DashboardSummary

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(
    container: AppContainer = Depends(get_container),
) -> DashboardSummary:
    return container.dashboard_service.get_summary()
