import numpy as np
import pytest

from lstm_model import LSTMModel


def test_predict_returns_none_when_untrained():
    model = LSTMModel()
    price = np.linspace(100, 101, 60)
    rsi = np.linspace(40, 60, 60)

    pred = model.predict(price, rsi)

    assert pred is None


def test_predict_returns_none_for_nan_input():
    model = LSTMModel()
    if not model.torch_available:
        pytest.skip("Torch not available - model inference path disabled by design.")

    model.trained = True
    price = np.linspace(100, 101, 60)
    rsi = np.linspace(40, 60, 60)
    price[0] = np.nan

    pred = model.predict(price, rsi)

    assert pred is None
