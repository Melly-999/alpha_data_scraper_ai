from lstm_signal_adapter import LSTMSignalAdapter

def test_adapter_returns_fallback_without_config():
    adapter = LSTMSignalAdapter('EURUSD')
    result = adapter.predict(None)
    assert result.available is False
    assert result.direction == 'HOLD'
