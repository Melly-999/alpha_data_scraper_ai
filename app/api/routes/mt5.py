from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.mt5 import MT5Status

router = APIRouter(tags=["mt5"])


@router.get("/mt5/status", response_model=MT5Status)
def mt5_status(container: AppContainer = Depends(get_container)) -> MT5Status:
    return container.mt5_service.get_status()
