from __future__ import annotations

import numpy as np
import pandas as pd

from lstm_model import LSTMPipeline, build_sequences


def test_build_sequences_shapes() -> None:
    arr = np.arange(120).reshape(40, 3)
    x, y = build_sequences(arr, lookback=5)
    assert x.shape == (35, 5, 3)
    assert y.shape == (35,)


def test_lstm_pipeline_predict_delta(sample_ohlcv: pd.DataFrame) -> None:
    features = sample_ohlcv[["close", "open", "high", "low", "volume"]].copy()
    model = LSTMPipeline(lookback=20, epochs=1, batch_size=8)
    model.fit(features)
    delta = model.predict_next_delta(features, close_col_index=0)
    assert isinstance(delta, float)
    assert np.isfinite(delta)
