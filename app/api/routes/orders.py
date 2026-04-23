from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.order import OrderRow

router = APIRouter(tags=["orders"])


@router.get("/orders", response_model=list[OrderRow])
def orders(container: AppContainer = Depends(get_container)) -> list[OrderRow]:
    return container.account_service.get_orders()
