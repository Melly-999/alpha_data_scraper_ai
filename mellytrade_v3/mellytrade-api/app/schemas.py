from pydantic import BaseModel

class SignalIn(BaseModel):
    symbol: str
    direction: str
    confidence: float
    price: float
    stopLoss: float
    takeProfit: float
    riskPercent: float
    timestamp: str | None = None
    source: str = 'mt5'
    meta: dict | None = None
