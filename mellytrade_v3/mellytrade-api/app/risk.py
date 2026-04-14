import time

class Decision:
    def __init__(self, accepted, reason=''):
        self.accepted = accepted
        self.reason = reason

class RiskManager:
    def __init__(self, max_risk_percent=1.0, min_confidence=70.0, cooldown_seconds=120):
        self.max_risk_percent = max_risk_percent
        self.min_confidence = min_confidence
        self.cooldown_seconds = cooldown_seconds
        self.last_seen = {}

    def validate(self, signal):
        if signal.riskPercent > self.max_risk_percent:
            return Decision(False, 'Risk percent above max')
        if signal.confidence < self.min_confidence:
            return Decision(False, 'Confidence below minimum')
        if signal.stopLoss is None or signal.takeProfit is None:
            return Decision(False, 'SL/TP required')
        key = str(signal.symbol) + ':' + str(signal.direction)
        now = time.time()
        last = self.last_seen.get(key, 0)
        if now - last < self.cooldown_seconds:
            return Decision(False, 'Cooldown active')
        self.last_seen[key] = now
        return Decision(True, '')
