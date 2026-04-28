"""Broker adapter routes (paper-first, safety-first).

Endpoints:

* ``GET  /api/broker/health``           - typed adapter health snapshot
* ``GET  /api/broker/account``          - typed account snapshot
* ``POST /api/broker/dry-run-report``   - generate a dry-run execution report

Live order placement is **never** exposed here. The IBKR paper adapter
is the only non-default option in v1 and is itself paper-only.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Request

from app.schemas.broker import (
    BrokerAccountResponse,
    BrokerDryRunRequest,
    BrokerExecutionReportResponse,
    BrokerHealthResponse,
)
from app.schemas.common import LogCategory, Severity
from brokers.adapter_models import ExecutionDecision
from brokers.paper_factory import PaperBrokerAdapter, get_paper_broker_adapter

router = APIRouter(tags=["broker"])


def _adapter(request: Request) -> PaperBrokerAdapter:
    """Resolve the active paper broker adapter.

    Cached on ``app.state`` so a process-wide adapter is reused. Falls
    back to a typed disabled adapter if no broker is configured.
    """
    cached = getattr(request.app.state, "broker_adapter", None)
    if cached is not None:
        return cached
    adapter = get_paper_broker_adapter()
    request.app.state.broker_adapter = adapter
    return adapter


@router.get("/broker/health", response_model=BrokerHealthResponse)
def broker_health(request: Request) -> BrokerHealthResponse:
    adapter = _adapter(request)
    health = adapter.health()
    container = request.app.state.container
    container.log_service.add(
        category=LogCategory.SYSTEM,
        severity=Severity.DEBUG,
        message=(
            f"broker.health adapter={health.adapter} mode={health.mode} "
            f"connected={health.connected} status={health.status}"
        ),
    )
    return BrokerHealthResponse(**asdict(health))


@router.get("/broker/account", response_model=BrokerAccountResponse)
def broker_account(request: Request) -> BrokerAccountResponse:
    adapter = _adapter(request)
    snapshot = adapter.account_snapshot()
    container = request.app.state.container
    container.log_service.add(
        category=LogCategory.SYSTEM,
        severity=Severity.DEBUG,
        message=(
            f"broker.account adapter={snapshot.adapter} "
            f"connected={snapshot.connected}"
        ),
    )
    return BrokerAccountResponse(**asdict(snapshot))


@router.post(
    "/broker/dry-run-report",
    response_model=BrokerExecutionReportResponse,
)
def broker_dry_run_report(
    payload: BrokerDryRunRequest,
    request: Request,
) -> BrokerExecutionReportResponse:
    adapter = _adapter(request)
    decision = ExecutionDecision(
        decision_id=payload.decision_id,
        signal_id=payload.signal_id,
        symbol=payload.symbol,
        direction=payload.direction,
        confidence=payload.confidence,
        dry_run=True,
        quantity=payload.quantity,
        sl=payload.sl,
        tp=payload.tp,
        reason=payload.reason,
        metadata=dict(payload.metadata),
    )
    report = adapter.submit_dry_run_report(decision)

    container = request.app.state.container
    container.log_service.add(
        category=LogCategory.EXECUTION,
        severity=Severity.INFO,
        message=(
            f"broker.dry_run adapter={report.adapter} broker={report.broker} "
            f"decision_id={report.decision_id} symbol={report.symbol} "
            f"direction={report.direction} accepted={report.accepted} "
            f"reason={report.reason}"
        ),
    )

    body: dict[str, Any] = asdict(report)
    return BrokerExecutionReportResponse(**body)
