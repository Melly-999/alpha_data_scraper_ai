from pathlib import Path

import pandas as pd

from lstm_signal_adapter import LSTMSignalAdapter


def test_adapter_returns_fallback_without_config(monkeypatch):
    monkeypatch.delenv('ALPHA_REPO_PATH', raising=False)
    monkeypatch.delenv('ALPHA_LSTM_CLASS', raising=False)
    monkeypatch.delenv('ALPHA_LSTM_FUNCTION', raising=False)

    adapter = LSTMSignalAdapter('EURUSD')
    result = adapter.predict(None)
    assert result.available is False
    assert result.direction == 'HOLD'


def test_adapter_loads_alpha_lstm_pipeline(monkeypatch):
    repo_root = Path(__file__).resolve().parents[3]
    monkeypatch.setenv('ALPHA_REPO_PATH', str(repo_root))
    monkeypatch.setenv('ALPHA_LSTM_CLASS', 'lstm_model.LSTMPipeline')
    monkeypatch.delenv('ALPHA_LSTM_FUNCTION', raising=False)

    close = [1.10 + idx * 0.0001 for idx in range(80)]
    frame = pd.DataFrame(
        {
            'close': close,
            'open': [value - 0.00005 for value in close],
            'high': [value + 0.0002 for value in close],
            'low': [value - 0.0002 for value in close],
            'volume': [1000 + idx for idx in range(80)],
        }
    )

    result = LSTMSignalAdapter('EURUSD').predict(frame)

    assert result.available is True
    assert result.direction in {'BUY', 'SELL', 'HOLD'}
    assert result.reasons
