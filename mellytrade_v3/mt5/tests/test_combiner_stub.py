from ensemble_combiner import EnsembleCombiner, TechnicalSignal
from lstm_signal_adapter import LSTMSignal

def test_combiner_prefers_technical_when_lstm_unavailable():
    combiner = EnsembleCombiner()
    tech = TechnicalSignal(direction='BUY', confidence=80, sl=1.0, tp=1.2)
    lstm = LSTMSignal(direction='HOLD', confidence=0, available=False, reasons=['missing'])
    result = combiner.combine(tech, lstm)
    assert result.direction in ['BUY', 'SELL', 'HOLD']
    assert result.technical_weight >= result.lstm_weight
