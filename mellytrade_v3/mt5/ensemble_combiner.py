from __future__ import annotations

from dataclasses import dataclass
from lstm_signal_adapter import LSTMSignal

@dataclass
class TechnicalSignal:
    direction: str
    confidence: float
    sl: float
    tp: float

@dataclass
class CombinedSignal:
    direction: str
    confidence: float
    sl: float
    tp: float
    lstm_weight: float
    technical_weight: float
    regime: str
    reasons: list[str]
    blocked: bool = False
    block_reason: str = ''

class EnsembleCombiner:
    def combine(self, tech: TechnicalSignal, lstm: LSTMSignal) -> CombinedSignal:
        reasons = []
        if not lstm.available:
            lstm_weight = 0.0
            reasons.append('LSTM unavailable -> 100% technical')
        else:
            lstm_weight = 0.5
            if lstm.lstm_uncertainty > 0.3:
                penalty = (lstm.lstm_uncertainty - 0.3) * 2
                lstm_weight = max(0.1, lstm_weight - penalty)
                reasons.append(f'LSTM uncertainty {lstm.lstm_uncertainty:.2f} reduced weight to {lstm_weight:.2f}')
        tech_weight = 1.0 - lstm_weight

        scores = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        scores[str(tech.direction)] += float(tech.confidence) * tech_weight
        if lstm.available and lstm.direction != 'HOLD':
            scores[str(lstm.direction)] += float(lstm.confidence) * lstm_weight
        else:
            scores['HOLD'] += 30.0 * lstm_weight

        direction = max(scores, key=scores.get)
        if direction == 'HOLD':
            return CombinedSignal(direction='HOLD', confidence=0.0, sl=tech.sl, tp=tech.tp, lstm_weight=lstm_weight, technical_weight=tech_weight, regime=lstm.regime, reasons=['No consensus'], blocked=True, block_reason='HOLD signal')

        raw_conf = float(tech.confidence) * tech_weight + float(lstm.confidence if lstm.available else 0.0) * lstm_weight
        regime_penalty = {'TRENDING': 1.0, 'RANGING': 0.9, 'VOLATILE': 0.8, 'UNKNOWN': 0.9}.get(lstm.regime, 0.9)
        confidence = round(raw_conf * regime_penalty, 1)
        reasons.append(f'Combined confidence {confidence:.1f}')
        if lstm.reasons:
            reasons.extend(lstm.reasons[:3])

        blocked = confidence < 70.0
        reason = '' if not blocked else f'Confidence {confidence:.1f}% < 70%'
        return CombinedSignal(direction=direction, confidence=confidence, sl=tech.sl, tp=tech.tp, lstm_weight=lstm_weight, technical_weight=tech_weight, regime=lstm.regime, reasons=reasons, blocked=blocked, block_reason=reason)
