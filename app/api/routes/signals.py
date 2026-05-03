from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.signal import SignalDetail, SignalReasoning, SignalSummary
from app.schemas.signal_decision import SignalDecisionHistoryResponse
from app.schemas.signal_lifecycle import (
    LifecycleDecision,
    LifecycleRiskStatus,
    SignalLifecycleResponse,
)
from app.services.signal_decision_history_service import SignalDecisionHistoryService
from app.services.signal_lifecycle_service import SignalLifecycleService

router = APIRouter(tags=["signals"])

_decision_service = SignalDecisionHistoryService()
_lifecycle_service = SignalLifecycleService(_decision_service)


@router.get("/signals", response_model=list[SignalSummary])
def list_signals(
    container: AppContainer = Depends(get_container),
) -> list[SignalSummary]:
    return container.signal_service.list_signals()


@router.get("/signals/decisions", response_model=SignalDecisionHistoryResponse)
def signal_decisions(
    limit: int = Query(default=50, ge=1, le=200),
    symbol: str | None = Query(default=None),
) -> SignalDecisionHistoryResponse:
    """Read-only signal decision history.

    Returns a log of dry-run signal decisions showing what happened to each
    signal: blocked, watch-only, or dry-run-allowed. GET-only. No mutation,
    no order placement, no broker connection.
    """
    return _decision_service.list_decisions(limit=limit, symbol=symbol)


@router.get("/signals/lifecycle", response_model=SignalLifecycleResponse)
def signal_lifecycle(
    limit: int = Query(default=50, ge=1, le=200),
    symbol: str | None = Query(default=None),
    decision: LifecycleDecision | None = Query(default=None),
    risk_status: LifecycleRiskStatus | None = Query(default=None),
) -> SignalLifecycleResponse:
    """Read-only signal lifecycle view.

    Explains the path from signal receipt through confidence, risk, broker
    safety, dry-run decision, and audit correlation. GET-only. No mutation,
    no broker connection, no MT5 execution, and no order placement.
    """
    return _lifecycle_service.list_lifecycle(
        limit=limit,
        symbol=symbol,
        decision=decision,
        risk_status=risk_status,
    )


@router.get("/signals/{signal_id}", response_model=SignalDetail)
def signal_detail(
    signal_id: str,
    container: AppContainer = Depends(get_container),
) -> SignalDetail:
    try:
        return container.signal_service.get_signal_detail(signal_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Signal not found") from exc


@router.get("/signals/{signal_id}/reasoning", response_model=SignalReasoning)
def signal_reasoning(
    signal_id: str,
    container: AppContainer = Depends(get_container),
) -> SignalReasoning:
    try:
        return container.signal_service.get_reasoning(signal_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Signal not found") from exc
