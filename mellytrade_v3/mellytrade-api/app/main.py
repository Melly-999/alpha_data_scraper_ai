from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import cf_hub
from .auth import require_api_key
from .config import Settings, get_settings
from .database import SessionLocal, init_db
from .models import SignalRecord
from .risk import evaluate
from .schemas import HealthOut, RejectedOut, SignalIn, SignalOut

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


def get_db() -> Session:  # pragma: no cover - trivial
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health", response_model=HealthOut)
def health(settings: Settings = Depends(get_settings)) -> HealthOut:
    return HealthOut(
        cooldown_seconds=settings.cooldown_seconds,
        min_confidence=settings.min_confidence,
        max_risk_percent=settings.max_risk_percent,
        database=settings.database_url.split("://", 1)[0],
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


@app.get("/signals", response_model=List[SignalOut])
def list_signals(
    limit: int = 50,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
) -> List[SignalOut]:
    limit = max(1, min(limit, 500))
    rows = (
        db.execute(
            select(SignalRecord).order_by(SignalRecord.created_at.desc()).limit(limit)
        )
        .scalars()
        .all()
    )
    return [SignalOut.model_validate(r) for r in rows]


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
