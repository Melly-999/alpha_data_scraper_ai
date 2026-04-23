from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.signal import SignalDetail, SignalReasoning, SignalSummary

router = APIRouter(tags=["signals"])


@router.get("/signals", response_model=list[SignalSummary])
def list_signals(
    container: AppContainer = Depends(get_container),
) -> list[SignalSummary]:
    return container.signal_service.list_signals()


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
