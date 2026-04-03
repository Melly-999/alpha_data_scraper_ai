from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from lstm_model import LSTMPipeline, NaiveSequenceModel, build_sequences


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


# ---------------------------------------------------------------------------
# NaiveSequenceModel
# ---------------------------------------------------------------------------

def test_naive_model_returns_last_timestep_value() -> None:
    """predict(x) should return x[:, -1, 0:1] — the last time-step, first feature."""
    model = NaiveSequenceModel()
    x = np.array([[[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]])  # shape (1, 3, 2)
    result = model.predict(x)
    # Last timestep = [5.0, 6.0], first feature slice = [[5.0]]
    assert result.shape == (1, 1)
    assert result[0, 0] == pytest.approx(5.0)


def test_naive_model_batch_of_samples() -> None:
    model = NaiveSequenceModel()
    # shape (3 samples, 4 timesteps, 2 features)
    x = np.zeros((3, 4, 2))
    x[:, -1, 0] = [10.0, 20.0, 30.0]  # last timestep, first feature
    result = model.predict(x)
    assert result.shape == (3, 1)
    assert list(result[:, 0]) == pytest.approx([10.0, 20.0, 30.0])


# ---------------------------------------------------------------------------
# LSTMPipeline fallback: too-few sequences
# ---------------------------------------------------------------------------

def test_fit_falls_back_to_naive_when_too_few_rows() -> None:
    """When build_sequences produces <10 sequences, NaiveSequenceModel is used."""
    # With lookback=30 and only 35 rows we get 5 sequences (<10)
    rng = np.random.default_rng(42)
    n = 35
    close = 1.0 + np.cumsum(rng.normal(0, 0.001, n))
    df = pd.DataFrame({"close": close, "open": close, "high": close, "low": close})

    pipeline = LSTMPipeline(lookback=30, epochs=1)
    pipeline.fit(df, target_col="close")

    assert isinstance(pipeline.model, NaiveSequenceModel)


# ---------------------------------------------------------------------------
# LSTMPipeline fallback: TensorFlow absent
# ---------------------------------------------------------------------------

def test_fit_falls_back_to_naive_when_tf_is_none(sample_ohlcv: pd.DataFrame) -> None:
    """When tf is patched to None the pipeline uses NaiveSequenceModel."""
    import lstm_model as _mod

    original_tf = _mod.tf
    try:
        _mod.tf = None
        features = sample_ohlcv[["close", "open", "high", "low"]].copy()
        pipeline = LSTMPipeline(lookback=20, epochs=1)
        pipeline.fit(features, target_col="close")
        assert isinstance(pipeline.model, NaiveSequenceModel)
    finally:
        _mod.tf = original_tf


# ---------------------------------------------------------------------------
# LSTMPipeline.predict_next_delta — guard conditions
# ---------------------------------------------------------------------------

def test_predict_returns_zero_when_model_not_fitted() -> None:
    """predict_next_delta must return 0.0 when model/scaler are None."""
    pipeline = LSTMPipeline(lookback=20)
    df = pd.DataFrame({"close": [1.0] * 25, "open": [1.0] * 25})
    result = pipeline.predict_next_delta(df, close_col_index=0)
    assert result == 0.0


def test_predict_returns_zero_when_data_shorter_than_lookback(
    sample_ohlcv: pd.DataFrame,
) -> None:
    """predict_next_delta returns 0.0 if len(values) < lookback + 1."""
    features = sample_ohlcv[["close", "open", "high", "low", "volume"]].copy()
    pipeline = LSTMPipeline(lookback=20, epochs=1)
    pipeline.fit(features)

    # Pass only 15 rows — less than lookback(20) + 1
    short_df = features.iloc[:15].copy()
    result = pipeline.predict_next_delta(short_df, close_col_index=0)
    assert result == 0.0
