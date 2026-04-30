from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.signal import SignalDetail, SignalReasoning, SignalSummary
from app.schemas.signal_decision import SignalDecisionHistoryResponse
from app.services.signal_decision_history_service import SignalDecisionHistoryService

router = APIRouter(tags=["signals"])

_decision_service = SignalDecisionHistoryService()


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
