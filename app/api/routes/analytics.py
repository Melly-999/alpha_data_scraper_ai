from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.analytics import AnalyticsSummary

router = APIRouter(tags=["analytics"])


@router.get("/analytics/summary", response_model=AnalyticsSummary)
def analytics_summary(
    container: AppContainer = Depends(get_container),
) -> AnalyticsSummary:
    return container.analytics_service.get_summary()
