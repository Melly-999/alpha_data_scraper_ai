from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AnalyticsMetric(BaseModel):
    label: str
    value: float
    formatted: str


class AnalyticsSummary(BaseModel):
    symbol: str
    timeframe: str
    total_trades: int
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float
    profit_factor: float
    total_return: float
    source: str
    fallback: bool
    generated_at: datetime
    cache_age_seconds: int
    highlights: list[AnalyticsMetric]
