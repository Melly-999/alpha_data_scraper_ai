from __future__ import annotations

from typing import Any, Dict

import httpx
import pandas as pd

from mt5 import mt5_bridge
from mt5.lstm_signal_adapter import predict_signal, reset_cache


def test_adapter_fallback_without_ohlcv():
    sig = predict_signal(None)
    assert sig.action == "HOLD"
    assert sig.is_fallback
    assert sig.confidence == 33.0


def test_adapter_fits_and_predicts_with_real_lstm(ohlcv, monkeypatch, tmp_path):
    """Exercises the full fit → predict_next_delta path on the bundled
    ``lstm_model.LSTMPipeline``. Without a real OHLCV frame the adapter
    would fall back to HOLD — this test proves the bridge now hands one
    over and the pipeline accepts it.
    """
    import pathlib

    # The alpha repo lives two levels above mellytrade_v3/mt5/tests/.
    repo_root = pathlib.Path(__file__).resolve().parents[3]
    assert (repo_root / "lstm_model.py").exists(), repo_root

    reset_cache()
    monkeypatch.setenv("ALPHA_REPO_PATH", str(repo_root))
    monkeypatch.setenv("ALPHA_LSTM_CLASS", "lstm_model.LSTMPipeline")
    monkeypatch.delenv("ALPHA_LSTM_FUNCTION", raising=False)

    sig = predict_signal(ohlcv)

    # The naive/TF-free fallback inside LSTMPipeline may return ~0 delta
    # → HOLD. What matters is that the model ran (no fallback:* reason)
    # and confidence stays within the clamp.
    assert sig.action in ("BUY", "SELL", "HOLD")
    assert 33.0 <= sig.confidence <= 85.0
    assert not sig.reason.startswith("fallback:"), sig.reason


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
        assert {"open", "high", "low", "close"}.issubset(set(ohlcv.columns))
        return ohlcv

    # Replace the adapter with a deterministic BUY so we can assert on
    # the exact payload shape the bridge hands off to the API.
    def fake_predict(frame):
        from mt5.lstm_signal_adapter import AdapterSignal

        assert {"open", "high", "low", "close"}.issubset(set(frame.columns))
        return AdapterSignal("BUY", 75.0, 0.004)

    monkeypatch.setattr(mt5_bridge, "predict_signal", fake_predict)

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
    assert (
        '"symbol":"EURUSD"' in captured["json"]
        or '"symbol": "EURUSD"' in captured["json"]
    )


def test_bridge_run_once_reports_api_rejection_as_failure(ohlcv, monkeypatch):
    def transport_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "status": "rejected",
                "reason": "risk_above_max",
                "detail": "2.0 > 1.0",
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(transport_handler), timeout=5.0)

    def fetcher(symbol: str, timeframe: str, bars: int) -> pd.DataFrame:
        return ohlcv

    def fake_predict(frame):
        from mt5.lstm_signal_adapter import AdapterSignal

        return AdapterSignal("BUY", 75.0, 0.004)

    monkeypatch.setattr(mt5_bridge, "predict_signal", fake_predict)

    cfg = mt5_bridge.BridgeConfig(
        api_url="http://test",
        api_key="test-key",
        symbol="EURUSD",
        timeframe="M5",
        bars=120,
        sl_pips=20,
        tp_pips=40,
        risk_percent=2.0,
    )
    result = mt5_bridge.run_once(config=cfg, fetcher=fetcher, http_client=client)

    assert result["status"] == "failed"
    assert result["http"] == 400
    assert result["body"]["reason"] == "risk_above_max"
