from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

Action = Literal["BUY", "SELL", "HOLD"]


class SignalIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str = Field(..., min_length=3, max_length=16)
    action: Action
    confidence: float = Field(..., ge=0, le=100)
    risk_percent: float = Field(..., gt=0, le=100)
    entry_price: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    take_profit: float = Field(..., gt=0)
    source: str = Field(default="api", max_length=32)

    @model_validator(mode="after")
    def _validate_sl_tp(self) -> "SignalIn":
        if self.action == "BUY":
            if self.stop_loss >= self.entry_price:
                raise ValueError("BUY stop_loss must be below entry_price")
            if self.take_profit <= self.entry_price:
                raise ValueError("BUY take_profit must be above entry_price")
        elif self.action == "SELL":
            if self.stop_loss <= self.entry_price:
                raise ValueError("SELL stop_loss must be above entry_price")
            if self.take_profit >= self.entry_price:
                raise ValueError("SELL take_profit must be below entry_price")
        return self


class SignalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    symbol: str
    action: Action
    confidence: float
    risk_percent: float
    entry_price: float
    stop_loss: float
    take_profit: float
    source: str
    status: str
    reason: str


class HealthOut(BaseModel):
    status: str = "ok"
    service: str = "mellytrade-api"
    version: str = "0.1.0"
    cooldown_seconds: int
    min_confidence: float
    max_risk_percent: float
    database: str


class RejectedOut(BaseModel):
    status: Literal["rejected"] = "rejected"
    reason: str
    detail: Optional[str] = None
