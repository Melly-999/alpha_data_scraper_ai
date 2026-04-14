from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import get_db
from app.models import SignalLog
from app.publisher import publish_signal
from app.risk import RiskManager
from app.schemas import SignalIn

settings = get_settings()
router = APIRouter()
risk_manager = RiskManager(
    max_risk_percent=settings.max_risk_percent,
    min_confidence=settings.min_confidence,
    cooldown_seconds=settings.cooldown_seconds,
)

@router.post('/signal')
async def signal_ingest(
    signal: SignalIn,
    db: Session = Depends(get_db),
    x_api_key: str | None = Header(default=None, alias='X-API-Key'),
):
    if x_api_key != settings.fastapi_key:
        raise HTTPException(status_code=401, detail='Unauthorized')

    decision = risk_manager.validate(signal)
    status = 'accepted' if decision.accepted else 'blocked'

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
        meta_json=str(signal.meta or {}),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    if not decision.accepted:
        raise HTTPException(status_code=400, detail=decision.reason)

    cf_result = await publish_signal(signal)
    return {'status': 'accepted', 'signal_id': row.id, 'cf_result': cf_result}
