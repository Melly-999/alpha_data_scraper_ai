from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.terminal import AuditEventFeedResponse
from app.services.audit_event_service import AuditEventService

router = APIRouter(tags=["terminal"])

_audit_service = AuditEventService()


@router.get("/terminal/events", response_model=AuditEventFeedResponse)
def terminal_events(
    limit: int = Query(default=50, ge=1, le=200),
    container: AppContainer = Depends(get_container),
) -> AuditEventFeedResponse:
    """Read-only audit/event feed for MellyTrade Terminal V1.

    Returns a structured list of system audit events showing backend state,
    safety posture, and service degradation status. GET-only. Performs no
    mutation, broker connection attempt, or order placement.
    """
    risk_config = container.risk_service.get_config()
    return _audit_service.list_events(risk_config, limit=limit)
