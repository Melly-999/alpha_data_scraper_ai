from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse, Response
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from . import alerts, audit, cf_hub, reports
from .auth import require_api_key
from .config import Settings, get_settings
from .database import SessionLocal, init_db
from .models import SignalRecord
from .risk import evaluate
from .schemas import (
    AlertOut,
    AuditOut,
    HealthOut,
    RejectedOut,
    ReportOut,
    RiskConfigOut,
    RiskGateStatus,
    SignalIn,
    SignalOut,
    SignalSummaryOut,
)

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="MellyTrade API",
    version="0.1.0",
    description=(
        "Signal intake for the MellyTrade v3 pipeline. Enforces strict risk "
        "gates (max 1% risk, min 70 confidence, SL/TP required, cooldown)."
    ),
    lifespan=lifespan,
)


@app.exception_handler(HTTPException)
async def rejected_http_exception_handler(
    request: Request, exc: HTTPException
) -> Response:
    if exc.status_code in (
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_401_UNAUTHORIZED,
    ):
        detail = exc.detail
        if isinstance(detail, dict):
            reason = str(detail.get("reason", "rejected"))
            message = detail.get("detail")
        else:
            reason = "rejected"
            message = str(detail) if detail is not None else None
        body = RejectedOut(reason=reason, detail=message)
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    return await http_exception_handler(request, exc)


def get_db() -> Session:  # pragma: no cover - trivial
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _live_orders_blocked(settings: Settings) -> bool:
    """Live orders are blocked unless every safety toggle is explicitly off."""
    return settings.dry_run or settings.read_only or not settings.autotrade_enabled


def _clamp_confidence(value: float) -> float:
    """Mirror the alpha pipeline clamping ([33, 85]) for dashboard display."""
    return max(33.0, min(85.0, value))


@app.get("/health", response_model=HealthOut)
def health(settings: Settings = Depends(get_settings)) -> HealthOut:
    return HealthOut(
        cooldown_seconds=settings.cooldown_seconds,
        min_confidence=settings.min_confidence,
        max_risk_percent=settings.max_risk_percent,
        database=settings.database_url.split("://", 1)[0],
        dry_run=settings.dry_run,
        autotrade_enabled=settings.autotrade_enabled,
        read_only=settings.read_only,
        live_orders_blocked=_live_orders_blocked(settings),
    )


@app.post(
    "/signal",
    response_model=SignalOut,
    responses={400: {"model": RejectedOut}, 401: {"model": RejectedOut}},
)
async def create_signal(
    payload: SignalIn,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> SignalOut:
    decision = evaluate(payload, settings, db)
    if not decision.accepted:
        rejected = SignalRecord(
            symbol=payload.symbol,
            action=payload.action,
            confidence=payload.confidence,
            risk_percent=payload.risk_percent,
            entry_price=payload.entry_price,
            stop_loss=payload.stop_loss,
            take_profit=payload.take_profit,
            source=payload.source,
            status="rejected",
            reason=f"{decision.reason}: {decision.detail}".strip(": "),
        )
        db.add(rejected)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"reason": decision.reason, "detail": decision.detail},
        )

    record = SignalRecord(
        symbol=payload.symbol,
        action=payload.action,
        confidence=payload.confidence,
        risk_percent=payload.risk_percent,
        entry_price=payload.entry_price,
        stop_loss=payload.stop_loss,
        take_profit=payload.take_profit,
        source=payload.source,
        status="accepted",
        reason="",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    forwarded = await cf_hub.publish(_signal_payload(record), settings)
    if not forwarded:
        log.info("CF hub not configured or unreachable; signal stored locally")

    return SignalOut.model_validate(record)


def _record_to_summary(record: SignalRecord, settings: Settings) -> SignalSummaryOut:
    rejection_reason = record.reason or None if record.status != "accepted" else None
    return SignalSummaryOut(
        id=record.id,
        created_at=record.created_at,
        symbol=record.symbol,
        action=record.action,  # type: ignore[arg-type]
        confidence=record.confidence,
        confidence_clamped=_clamp_confidence(record.confidence),
        risk_pct=record.risk_percent,
        entry_price=record.entry_price,
        stop_loss=record.stop_loss,
        take_profit=record.take_profit,
        source=record.source,
        status=record.status,
        reason=record.reason,
        rejection_reason=rejection_reason,
        dry_run=settings.dry_run,
        read_only=settings.read_only,
    )


@app.get("/signals", response_model=List[SignalSummaryOut])
def list_signals(
    limit: int = Query(50, ge=1, le=500),
    symbol: Optional[str] = Query(default=None, max_length=16),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    since: Optional[datetime] = Query(default=None),
    until: Optional[datetime] = Query(default=None),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> List[SignalSummaryOut]:
    """Read-only list of signals enriched with safety context.

    Filters are optional; SL/TP, gating and audit metadata are preserved.
    """
    stmt: Select[Any] = select(SignalRecord)
    if symbol:
        stmt = stmt.where(SignalRecord.symbol == symbol.strip())
    if status_filter:
        if status_filter not in ("accepted", "rejected"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "reason": "invalid_status",
                    "detail": "status must be 'accepted' or 'rejected'",
                },
            )
        stmt = stmt.where(SignalRecord.status == status_filter)
    if since is not None:
        stmt = stmt.where(SignalRecord.created_at >= since)
    if until is not None:
        stmt = stmt.where(SignalRecord.created_at <= until)

    stmt = stmt.order_by(SignalRecord.created_at.desc()).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return [_record_to_summary(r, settings) for r in rows]


@app.get("/audit", response_model=AuditOut)
def list_audit_events(
    limit: int = Query(100, ge=1, le=500),
    event_type: Optional[str] = Query(default=None),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> AuditOut:
    """Read-only audit feed for the trader dashboard.

    Combines persisted signal decisions with the static safety posture so
    the operator can verify dry_run/read_only/live_orders_blocked at a glance.
    """
    events = audit.collect_events(
        db=db,
        settings=settings,
        limit=limit,
        event_type=event_type,
    )
    return AuditOut(
        events=events,
        dry_run=settings.dry_run,
        read_only=settings.read_only,
        live_orders_blocked=_live_orders_blocked(settings),
    )


@app.get("/alerts", response_model=List[AlertOut])
def list_alerts(
    limit: int = Query(100, ge=1, le=500),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> List[AlertOut]:
    """Read-only alert center feed derived from existing safety state."""
    return alerts.collect_alerts(db=db, settings=settings, limit=limit)


@app.get("/reports/daily", response_model=ReportOut)
def read_daily_report(
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> ReportOut:
    """Read-only daily report for Direction B dashboard review."""
    return reports.build_report(db=db, settings=settings, period="daily")


@app.get("/reports/weekly", response_model=ReportOut)
def read_weekly_report(
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> ReportOut:
    """Read-only weekly report for Direction B dashboard review."""
    return reports.build_report(db=db, settings=settings, period="weekly")


@app.get("/risk/config", response_model=RiskConfigOut)
def read_risk_config(
    settings: Settings = Depends(get_settings),
    _: str = Depends(require_api_key),
) -> RiskConfigOut:
    """Read-only snapshot of risk gates and the current safety posture.

    The dashboard renders this without exposing any mutation path; live
    execution remains blocked while `dry_run` or `read_only` is on.
    """
    gates = [
        RiskGateStatus(
            name="min_confidence",
            active=True,
            description=(
                f"Reject signals with confidence < {settings.min_confidence:g}"
            ),
        ),
        RiskGateStatus(
            name="max_risk_percent",
            active=True,
            description=(
                f"Reject signals with risk_percent > {settings.max_risk_percent:g}"
            ),
        ),
        RiskGateStatus(
            name="cooldown_seconds",
            active=True,
            description=(
                f"Reject same-symbol BUY/SELL within " f"{settings.cooldown_seconds}s"
            ),
        ),
        RiskGateStatus(
            name="sl_tp_required",
            active=True,
            description="BUY/SELL must include valid stop_loss and take_profit",
        ),
    ]
    return RiskConfigOut(
        min_confidence=settings.min_confidence,
        max_risk_percent=settings.max_risk_percent,
        cooldown_seconds=settings.cooldown_seconds,
        dry_run=settings.dry_run,
        autotrade_enabled=settings.autotrade_enabled,
        read_only=settings.read_only,
        live_orders_blocked=_live_orders_blocked(settings),
        gates=gates,
    )


def _signal_payload(record: SignalRecord) -> Dict[str, Any]:
    return {
        "id": record.id,
        "created_at": record.created_at.isoformat(),
        "symbol": record.symbol,
        "action": record.action,
        "confidence": record.confidence,
        "risk_percent": record.risk_percent,
        "entry_price": record.entry_price,
        "stop_loss": record.stop_loss,
        "take_profit": record.take_profit,
        "source": record.source,
        "status": record.status,
    }
