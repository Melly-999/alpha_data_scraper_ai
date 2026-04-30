from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.local import (
    ChecklistStatus,
    LocalChecklistCheck,
    LocalChecklistResponse,
    LocalChecklistSummary,
)
from brokers.paper_factory import PaperBrokerAdapter, get_paper_broker_adapter

router = APIRouter(tags=["local"])


def _adapter(request: Request) -> PaperBrokerAdapter:
    cached = getattr(request.app.state, "broker_adapter", None)
    if cached is not None:
        return cached
    adapter = get_paper_broker_adapter()
    request.app.state.broker_adapter = adapter
    return adapter


def _check(
    check_id: str,
    label: str,
    status: ChecklistStatus,
    detail: str,
) -> LocalChecklistCheck:
    return LocalChecklistCheck(
        id=check_id,
        label=label,
        status=status,
        detail=detail,
    )


@router.get("/local/checklist", response_model=LocalChecklistResponse)
def local_checklist(
    request: Request,
    container: AppContainer = Depends(get_container),
) -> LocalChecklistResponse:
    """Read-only local workstation checklist.

    This endpoint aggregates existing in-process safety state only. It
    does not mutate config, connect to a broker, place orders, or call
    any execution path.
    """

    risk_config = container.risk_service.get_config()
    broker_health = _adapter(request).health()

    dry_run_pass = risk_config.dry_run is True
    auto_trade_pass = risk_config.auto_trade is False
    broker_live_orders_pass = broker_health.supports_live_orders is False
    live_orders_blocked = broker_live_orders_pass

    broker_mode_status: ChecklistStatus
    if broker_health.status == "live_blocked":
        broker_mode_status = "fail"
        broker_mode_detail = (
            f"status={broker_health.status}; live port or live mode is blocked"
        )
    elif broker_health.connected:
        broker_mode_status = "pass"
        broker_mode_detail = f"mode={broker_health.mode}; connected=true; read_only={broker_health.read_only}"
    elif broker_health.status in {
        "disabled",
        "missing_dependency",
        "connect_failed",
        "ok",
    }:
        broker_mode_status = "warn"
        broker_mode_detail = (
            f"mode={broker_health.mode}; status={broker_health.status}; "
            "disconnected/setup-pending is safe"
        )
    else:
        broker_mode_status = "warn"
        broker_mode_detail = (
            f"mode={broker_health.mode}; status={broker_health.status}; verify setup"
        )

    checks = [
        _check(
            "backend",
            "Backend API reachable",
            "pass",
            "FastAPI is responding",
        ),
        _check(
            "dry_run",
            "Dry-run mode",
            "pass" if dry_run_pass else "fail",
            f"dry_run={str(risk_config.dry_run).lower()}",
        ),
        _check(
            "auto_trade",
            "Auto-trade",
            "pass" if auto_trade_pass else "fail",
            f"auto_trade={str(risk_config.auto_trade).lower()}",
        ),
        _check(
            "broker_live_orders",
            "Broker live orders",
            "pass" if broker_live_orders_pass else "fail",
            f"supports_live_orders={str(broker_health.supports_live_orders).lower()}",
        ),
        _check(
            "broker_mode",
            "Broker mode/status",
            broker_mode_status,
            broker_mode_detail,
        ),
    ]

    overall_status: Literal["ok", "degraded"] = (
        "ok" if all(item.status == "pass" for item in checks) else "degraded"
    )

    return LocalChecklistResponse(
        status=overall_status,
        service="MellyTrade Local Workstation",
        checks=checks,
        summary=LocalChecklistSummary(
            dry_run=risk_config.dry_run,
            auto_trade=risk_config.auto_trade,
            supports_live_orders=broker_health.supports_live_orders,
            live_orders_blocked=live_orders_blocked,
            broker_status=broker_health.status,
            broker_mode=broker_health.mode,
            broker_connected=broker_health.connected,
            broker_read_only=broker_health.read_only,
        ),
    )
