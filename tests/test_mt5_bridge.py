from __future__ import annotations

import asyncio
from typing import cast

import pandas as pd

from lstm_signal_adapter import LSTMSignal
from mt5_bridge import LSTMSignalAdapter, MT5Bridge


class FakeAdapter:
    def predict(self, df: pd.DataFrame) -> LSTMSignal:
        return LSTMSignal(
            direction="HOLD",
            confidence=0.0,
            lstm_delta=0.0,
            lstm_uncertainty=1.0,
            regime="UNKNOWN",
            score=0,
            reasons=["forced fallback"],
            available=False,
        )


def test_mt5_bridge_uses_technical_only_when_lstm_unavailable(monkeypatch) -> None:
    monkeypatch.setenv("FASTAPI_KEY", "test-key")
    monkeypatch.setenv("MT5_LOGIN", "123")
    monkeypatch.setenv("MT5_PASSWORD", "password")
    monkeypatch.setenv("MT5_SERVER", "server")
    monkeypatch.setattr("mt5_bridge.SYMBOLS", ["EURUSD"])

    bridge = MT5Bridge()
    bridge._lstm = {"EURUSD": cast(LSTMSignalAdapter, FakeAdapter())}

    df = pd.DataFrame(
        {
            "close": [1.1000, 1.1005, 1.1010],
            "high": [1.1010, 1.1015, 1.1020],
            "low": [1.0990, 1.0995, 1.1000],
            "ema_fast": [1.0995, 1.1000, 1.1012],
            "ema_slow": [1.1000, 1.1000, 1.1005],
            "rsi": [52.0, 54.0, 55.0],
            "atr": [0.0008, 0.0008, 0.0008],
        }
    )
    monkeypatch.setattr(bridge, "_get_df", lambda symbol: df)

    payload = asyncio.run(bridge._analyse("EURUSD", "2026-04-16T00:00:00+00:00"))

    assert payload is not None
    assert payload["direction"] == "BUY"
    assert payload["meta"]["lstm_weight"] == 0.0
    assert payload["meta"]["technical_weight"] == 1.0
    assert "LSTM unavailable" in payload["meta"]["reasons"][0]
