from __future__ import annotations

import pandas as pd

from signal_generator import generate_signal, signal_to_dict


def _row(**kwargs: float) -> pd.Series:
    defaults = dict(rsi=50.0, stoch_k=50.0, stoch_d=50.0, macd_hist=0.0, bb_pos=0.5)
    defaults.update(kwargs)
    return pd.Series(defaults)


def test_hold_neutral_inputs() -> None:
    result = generate_signal(_row(), lstm_delta=0.0)
    assert result.signal == "HOLD"


def test_buy_all_bullish() -> None:
    result = generate_signal(
        _row(rsi=28, stoch_k=18, stoch_d=15, macd_hist=0.001, bb_pos=0.1),
        lstm_delta=0.005,
    )
    assert result.signal == "BUY"
    assert result.score >= 2


def test_sell_all_bearish() -> None:
    result = generate_signal(
        _row(rsi=72, stoch_k=85, stoch_d=88, macd_hist=-0.001, bb_pos=0.92),
        lstm_delta=-0.005,
    )
    assert result.signal == "SELL"
    assert result.score <= -2


def test_lstm_delta_dominates_hold() -> None:
    # Neutral indicators but LSTM + MACD push score to ±2 → BUY/SELL
    buy = generate_signal(_row(macd_hist=0.001), lstm_delta=0.01)
    sell = generate_signal(_row(macd_hist=-0.001), lstm_delta=-0.01)
    assert buy.signal == "BUY"
    assert sell.signal == "SELL"


def test_confidence_clamped() -> None:
    for delta in (-0.1, 0.0, 0.1):
        result = generate_signal(_row(), lstm_delta=delta)
        assert 33 <= result.confidence <= 85


def test_signal_to_dict_keys() -> None:
    result = generate_signal(_row(), lstm_delta=0.0)
    d = signal_to_dict(result)
    assert set(d.keys()) == {"signal", "confidence", "score", "reasons", "regime"}
    assert isinstance(d["reasons"], list)
