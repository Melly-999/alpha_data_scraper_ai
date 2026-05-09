"""Read-only central safety status endpoint.

``GET /api/safety/status`` returns a single, structured snapshot of the
Terminal V1 safety posture. The endpoint is GET-only by construction;
``test_safety_status.py`` asserts that every other HTTP method against
this path returns 405.

This route deliberately reads the live ``RiskConfig`` from the existing
risk service rather than hard-coding values, so the response always
reflects the actual running configuration. The repo-wide ceiling
(``max_risk_per_trade_pct <= 1.0``) is enforced both at the schema level
(``Field(..., le=1.0)``) and by ``tests/app/test_safety_invariants.py``.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.core.container import AppContainer
from app.schemas.safety import SafetyPillar, SafetyStatusResponse

router = APIRouter(tags=["safety"])

# Closed, ordered list of pillars the Terminal V1 backend asserts. The
# enum membership is checked by the schema's Literal; the ordering is
# preserved here for UI display so reviewers see a stable layout.
_DEFAULT_PILLARS: tuple[SafetyPillar, ...] = (
    "DRY_RUN_ACTIVE",
    "READ_ONLY_ACTIVE",
    "AUTO_TRADE_DISABLED",
    "LIVE_ORDERS_BLOCKED",
    "MAX_RISK_CAPPED",
)

_SAFETY_NOTE = (
    "Terminal V1 is in read-only / dry-run mode. Live orders are blocked, "
    "autotrade is disabled, and per-trade risk is capped at 1%. No code "
    "path on this surface can submit an order to a real broker."
)


@router.get("/safety/status", response_model=SafetyStatusResponse)
def safety_status(
    container: AppContainer = Depends(get_container),
) -> SafetyStatusResponse:
    """Return the central safety posture snapshot.

    GET-only. Performs no mutation, no broker call, no order placement.
    Pulls the per-trade risk ceiling from the live ``RiskConfig`` so the
    response tracks the operator's actual configuration, but the schema
    itself caps the value at 1.0.
    """
    risk_config = container.risk_service.get_config()
    return SafetyStatusResponse(
        dry_run=True,
        auto_trade=False,
        read_only=True,
        live_orders_blocked=True,
        max_risk_per_trade_pct=float(risk_config.max_risk_per_trade),
        pillars=list(_DEFAULT_PILLARS),
        safety_note=_SAFETY_NOTE,
        generated_at=datetime.now(timezone.utc),
    )
