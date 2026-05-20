from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.terminal import (
    AuditEventFeedResponse,
    TradingPlanResponse,
    TerminalSummaryResponse,
)
from app.services.audit_event_service import AuditEventService
from app.services.terminal_summary import TerminalSummaryService
from app.services.trading_plan_service import TradingPlanService

router = APIRouter(tags=["terminal"])

_audit_service = AuditEventService()
_trading_plan_service = TradingPlanService()
_terminal_summary_service = TerminalSummaryService()


@router.get("/terminal/summary", response_model=TerminalSummaryResponse)
def terminal_summary() -> TerminalSummaryResponse:
    """Read-only terminal summary for the Terminal V1 dashboard.

    Returns a static advisory-only payload describing the current terminal
    mode, safety posture, and broker status. GET-only. Performs no mutation,
    no broker connection, and no order placement.
    """
    return _terminal_summary_service.get_summary()


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


@router.get("/terminal/trading-plan", response_model=TradingPlanResponse)
def terminal_trading_plan() -> TradingPlanResponse:
    """Read-only daily trading plan preview for Terminal V1.

    Returns a static, display-only planning context: instrument, bias,
    setup quality, risk tier, and no-trade conditions. GET-only. This is
    NOT a trade signal and NOT an order — the response schema deliberately
    omits any execution-shaped fields (quantity, lot size, sl, tp,
    order id). The endpoint performs no MT5, broker, or market-data calls.
    """
    return _trading_plan_service.get_plan()
