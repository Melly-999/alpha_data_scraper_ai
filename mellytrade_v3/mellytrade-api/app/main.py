from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import Base, engine, get_db
from app.models import SignalLog
from app.publisher import publish_signal
from app.risk import RiskManager
from app.schemas import HealthResponse, SignalIn

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="MellyTrade API", version="0.3.0", lifespan=lifespan)
risk_manager = RiskManager(
    max_risk_percent=settings.max_risk_percent,
    min_confidence=settings.min_confidence,
    cooldown_seconds=settings.cooldown_seconds,
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.post("/signal")
async def signal_ingest(
    signal: SignalIn,
    db: Session = Depends(get_db),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
) -> dict[str, object]:
    if x_api_key != settings.fastapi_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    decision = risk_manager.validate(signal)
    status = "accepted" if decision.accepted else "blocked"

    row = SignalLog(
        symbol=signal.symbol,
        direction=signal.direction,
        confidence=signal.confidence,
        price=signal.price,
        stop_loss=signal.stopLoss,
        take_profit=signal.takeProfit,
        risk_percent=signal.riskPercent,
        status=status,
        reason=decision.reason,
        source=signal.source,
        meta_json=signal.meta_json(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    if not decision.accepted:
        logger.info("Blocked signal %s %s: %s", signal.symbol, signal.direction, decision.reason)
        raise HTTPException(status_code=400, detail=decision.reason)

    try:
        cf_result = await publish_signal(signal)
    except Exception as exc:
        logger.exception("Accepted signal %s failed to publish", row.id)
        raise HTTPException(status_code=502, detail="Signal accepted but publish failed") from exc

    return {"status": "accepted", "signal_id": row.id, "cf_result": cf_result}
