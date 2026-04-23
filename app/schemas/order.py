from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import Direction, OrderSource, OrderStatus, OrderType


class OrderRow(BaseModel):
    id: str
    ticket: int
    symbol: str
    direction: Direction
    type: OrderType
    lots: float
    price: float
    sl: float | None = None
    tp: float | None = None
    status: OrderStatus
    source: OrderSource
    confidence: int | None = None
    slippage_pips: float | None = None
    submitted_at: datetime
    filled_at: datetime | None = None
    notes: str
