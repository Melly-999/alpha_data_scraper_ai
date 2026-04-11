from __future__ import annotations

from indicators import add_indicators
from lstm_model import LSTMPipeline
from mt5_fetcher import MT5Fetcher
from signal_generator import generate_signal


def test_pipeline_end_to_end() -> None:
    fetcher = MT5Fetcher(symbol="EURUSD", timeframe="M5")
    raw = fetcher.get_latest_rates(bars=320)
    data = add_indicators(raw)

    feature_cols = [
        "close",
        "rsi",
        "stoch_k",
        "stoch_d",
        "macd_hist",
        "bb_pos",
        "volume",
    ]
    features = data[feature_cols]

    model = LSTMPipeline(lookback=20, epochs=1, batch_size=8)
    model.fit(features)
    delta = model.predict_next_delta(features)

    result = generate_signal(data.iloc[-1], delta)

    assert result.signal in {"BUY", "SELL", "HOLD"}
    assert 33 <= result.confidence <= 85
