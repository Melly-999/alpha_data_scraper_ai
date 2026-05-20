from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class MarketItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str
    price: float
    change_pct: float
    signal: Literal["BUY", "SELL", "HOLD", "WATCH"]
    confidence: int

    @field_validator("confidence")
    @classmethod
    def _confidence_range(cls, v: int) -> int:
        if not (0 <= v <= 100):
            raise ValueError("confidence must be 0–100")
        return v

    @field_validator("price")
    @classmethod
    def _positive_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be positive")
        return v
