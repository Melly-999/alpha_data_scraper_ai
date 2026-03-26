from __future__ import annotations

from indicators import add_indicators
from lstm_model import LSTMPipeline
from mt5_fetcher import MT5Fetcher
from signal_generator import generate_signal


def test_stress_pipeline_multiple_runs() -> None:
    fetcher = MT5Fetcher(symbol="EURUSD", timeframe="M5")

    for _ in range(12):
        raw = fetcher.get_latest_rates(bars=260)
        data = add_indicators(raw)
        features = data[
            ["close", "rsi", "stoch_k", "stoch_d", "macd_hist", "bb_pos", "volume"]
        ]

        model = LSTMPipeline(lookback=20, epochs=1, batch_size=8)
        model.fit(features)
        delta = model.predict_next_delta(features)

        result = generate_signal(data.iloc[-1], delta)
        assert result.signal in {"BUY", "SELL", "HOLD"}
        assert 33 <= result.confidence <= 85
