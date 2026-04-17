from __future__ import annotations

import json
from typing import Any, Dict, Optional

from pydantic import BaseModel


class SignalIn(BaseModel):
    symbol: str
    direction: str
    confidence: float
    price: float
    stopLoss: Optional[float] = None
    takeProfit: Optional[float] = None
    riskPercent: float
    timestamp: Optional[str] = None
    source: str = "mt5"
    meta: Optional[Dict[str, Any]] = None

    def meta_json(self) -> str:
        return json.dumps(self.meta or {}, separators=(",", ":"), sort_keys=True)


class HealthResponse(BaseModel):
    status: str = "ok"
