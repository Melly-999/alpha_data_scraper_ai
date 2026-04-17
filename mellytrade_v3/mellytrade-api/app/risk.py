from __future__ import annotations

import time
from dataclasses import dataclass

from app.schemas import SignalIn


@dataclass(frozen=True)
class Decision:
    accepted: bool
    reason: str = ""


class RiskManager:
    def __init__(
        self,
        max_risk_percent: float = 1.0,
        min_confidence: float = 70.0,
        cooldown_seconds: int = 120,
    ) -> None:
        self.max_risk_percent = max_risk_percent
        self.min_confidence = min_confidence
        self.cooldown_seconds = cooldown_seconds
        self.last_seen: dict[str, float] = {}

    def validate(self, signal: SignalIn) -> Decision:
        if signal.riskPercent > self.max_risk_percent:
            return Decision(False, "Risk percent above max")
        if signal.confidence < self.min_confidence:
            return Decision(False, "Confidence below minimum")
        if signal.stopLoss is None or signal.takeProfit is None:
            return Decision(False, "SL/TP required")

        key = f"{signal.symbol}:{signal.direction}"
        now = time.time()
        last = self.last_seen.get(key, 0.0)
        if now - last < self.cooldown_seconds:
            return Decision(False, "Cooldown active")

        self.last_seen[key] = now
        return Decision(True)
