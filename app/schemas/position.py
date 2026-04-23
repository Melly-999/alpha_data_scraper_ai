from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import Direction


class PositionSummary(BaseModel):
    id: str
    ticket: int
    symbol: str
    direction: Direction
    lots: float
    open_price: float
    current_price: float | None = None
    close_price: float | None = None
    sl: float | None = None
    tp: float | None = None
    unrealized_pnl: float | None = None
    realized_pnl: float | None = None
    duration_seconds: int
    signal_id: str | None = None
    mt5_synced: bool
    open_time: datetime
    close_time: datetime | None = None
