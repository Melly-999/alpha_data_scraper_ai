from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.position import PositionSummary

router = APIRouter(tags=["positions"])


@router.get("/positions/open", response_model=list[PositionSummary])
def open_positions(
    container: AppContainer = Depends(get_container),
) -> list[PositionSummary]:
    return container.account_service.get_open_positions()


@router.get("/positions/history", response_model=list[PositionSummary])
def position_history(
    container: AppContainer = Depends(get_container),
) -> list[PositionSummary]:
    return container.account_service.get_position_history()
