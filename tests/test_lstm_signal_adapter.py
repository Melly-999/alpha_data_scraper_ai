from __future__ import annotations

import pytest

import lstm_signal_adapter
from lstm_signal_adapter import LSTMSignalAdapter


def test_lstm_adapter_returns_fallback_when_not_enough_bars(sample_ohlcv) -> None:
    adapter = LSTMSignalAdapter("EURUSD")

    signal = adapter.predict(sample_ohlcv.head(20))

    assert signal.available is False
    assert signal.direction == "HOLD"
    assert "Insufficient bars" in signal.reasons[0]


def test_lstm_adapter_uses_predict_next_delta(monkeypatch, sample_ohlcv) -> None:
    created: list[FakePipeline] = []

    class FakePipeline:
        def __init__(self, lookback: int, epochs: int, batch_size: int) -> None:
            self.lookback = lookback
            self.epochs = epochs
            self.batch_size = batch_size
            created.append(self)

        def fit(self, features, target_col: str = "close") -> None:
            assert target_col == "close"
            assert len(features) >= LSTMSignalAdapter.MIN_BARS_TO_FIT

        def predict_next_delta(self, features, close_col_index: int = 0) -> float:
            assert close_col_index == 0
            assert "close" in features.columns
            return 0.002

    monkeypatch.setattr(lstm_signal_adapter, "LSTMPipeline", FakePipeline)

    adapter = LSTMSignalAdapter("EURUSD", ensemble_size=5)
    signal = adapter.predict(sample_ohlcv)

    assert created
    assert created[0].lookback == LSTMSignalAdapter.LOOKBACK
    assert signal.available is True
    assert signal.lstm_delta == pytest.approx(0.002)
    assert signal.lstm_uncertainty == 1.0
    assert signal.regime in {"TRENDING", "RANGING", "UNKNOWN"}


def test_lstm_adapter_falls_back_when_pipeline_fit_raises(
    monkeypatch, sample_ohlcv
) -> None:
    class FailingPipeline:
        def __init__(self, lookback: int, epochs: int, batch_size: int) -> None:
            pass

        def fit(self, features, target_col: str = "close") -> None:
            raise RuntimeError("fit failed")

    monkeypatch.setattr(lstm_signal_adapter, "LSTMPipeline", FailingPipeline)

    adapter = LSTMSignalAdapter("EURUSD")
    signal = adapter.predict(sample_ohlcv)

    assert signal.available is False
    assert signal.direction == "HOLD"
    assert "LSTM not fitted" in signal.reasons[0]
