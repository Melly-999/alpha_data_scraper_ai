from __future__ import annotations

from typing import Any, Dict

import httpx
import pandas as pd

from mt5 import mt5_bridge
from mt5.lstm_signal_adapter import AdapterSignal, predict_signal


def test_adapter_fallback_without_ohlcv():
    sig = predict_signal(None)
    assert sig.action == "HOLD"
    assert sig.is_fallback
    assert sig.confidence == 33.0


def test_adapter_uses_injected_model(ohlcv):
    # Custom predict_fn produces a deterministic BUY bias.
    def up_model(frame: pd.DataFrame) -> float:
        return 0.005  # delta ~ 0.45% on ~1.10 close

    sig = predict_signal(ohlcv, threshold=1e-4, predict_fn=up_model)
    assert sig.action == "BUY"
    assert 33.0 <= sig.confidence <= 85.0


def test_bridge_run_once_posts_signal_to_api(ohlcv, monkeypatch):
    """End-to-end-ish: fetch via injected fetcher, predict, POST via mock transport."""
    captured: Dict[str, Any] = {}

    def transport_handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["json"] = request.read().decode()
        return httpx.Response(200, json={"id": 1, "status": "accepted"})

    transport = httpx.MockTransport(transport_handler)
    client = httpx.Client(transport=transport, timeout=5.0)

    def fetcher(symbol: str, timeframe: str, bars: int) -> pd.DataFrame:
        assert symbol == "EURUSD"
        return ohlcv

    def predict_fn(frame: pd.DataFrame) -> float:
        return 0.004  # force BUY

    # Patch the adapter used inside run_once so we exercise the full
    # bridge path (fetch → adapt → HTTP) deterministically.
    def fake_predict(frame, threshold=1e-4, predict_fn=None):
        from mt5.lstm_signal_adapter import AdapterSignal

        return AdapterSignal("BUY", 75.0, predict_fn(frame) if predict_fn else 0.004)

    monkeypatch.setattr(
        mt5_bridge, "predict_signal", lambda f: fake_predict(f, predict_fn=predict_fn)
    )

    cfg = mt5_bridge.BridgeConfig(
        api_url="http://test",
        api_key="test-key",
        symbol="EURUSD",
        timeframe="M5",
        bars=120,
        sl_pips=20,
        tp_pips=40,
        risk_percent=0.5,
    )
    result = mt5_bridge.run_once(config=cfg, fetcher=fetcher, http_client=client)

    assert result["status"] == "sent"
    assert result["http"] == 200
    assert "/signal" in captured["url"]
    assert captured["headers"].get("x-api-key") == "test-key"
    assert '"symbol":"EURUSD"' in captured["json"] or '"symbol": "EURUSD"' in captured["json"]
