from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.dashboard import AccountOverview

router = APIRouter(tags=["account"])


@router.get("/account/overview", response_model=AccountOverview)
def account_overview(
    container: AppContainer = Depends(get_container),
) -> AccountOverview:
    return container.account_service.get_account_overview()
