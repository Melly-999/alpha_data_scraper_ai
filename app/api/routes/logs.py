from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.common import LogCategory, Severity
from app.schemas.log import LogEntry

router = APIRouter(tags=["logs"])


@router.get("/logs", response_model=list[LogEntry])
def logs(
    category: LogCategory | None = None,
    severity: Severity | None = None,
    search: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    container: AppContainer = Depends(get_container),
) -> list[LogEntry]:
    return container.log_service.list(
        category=category,
        severity=severity,
        search=search,
        limit=limit,
    )
