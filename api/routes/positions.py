"""GET /positions — open positions snapshot endpoint."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.account_service import AccountService

logger = logging.getLogger(__name__)
router = APIRouter()

_account_service = AccountService()


class PositionResponse(BaseModel):
    symbol: str
    direction: str
    lot: float
    entry_price: float
    sl: Optional[float]
    tp: Optional[float]
    profit: float
    timestamp: datetime


@router.get("/positions", response_model=list[PositionResponse])
def get_positions() -> list[PositionResponse]:
    """Return all currently open positions, or an empty list when MT5 is unavailable."""
    try:
        positions = _account_service.get_open_positions()
        logger.info("Positions endpoint served: %d positions", len(positions))
        return [
            PositionResponse(
                symbol=p.symbol,
                direction=p.direction,
                lot=p.lot,
                entry_price=p.entry_price,
                sl=p.sl,
                tp=p.tp,
                profit=p.profit,
                timestamp=p.timestamp,
            )
            for p in positions
        ]
    except Exception as exc:
        logger.error("Positions endpoint error: %s", exc)
        raise HTTPException(
            status_code=500, detail="Failed to retrieve positions"
        ) from exc
