from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

HEADERS = {"X-API-Key": "test-key"}


def _buy(**overrides) -> dict:
    base = {
        "symbol": "EURUSD",
        "action": "BUY",
        "confidence": 75.0,
        "risk_percent": 0.5,
        "entry_price": 1.1000,
        "stop_loss": 1.0980,
        "take_profit": 1.1040,
        "source": "unit-test",
    }
    base.update(overrides)
    return base


def test_signal_requires_api_key(client):
    resp = client.post("/signal", json=_buy())
    assert resp.status_code == 401


def test_signal_accepts_valid_buy(client):
    resp = client.post("/signal", json=_buy(), headers=HEADERS)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "accepted"
    assert body["symbol"] == "EURUSD"
    assert body["reason"] == ""
    assert body["id"] > 0


def test_signal_rejects_low_confidence(client):
    resp = client.post("/signal", json=_buy(confidence=60), headers=HEADERS)
    assert resp.status_code == 400
    assert resp.json()["detail"]["reason"] == "confidence_below_min"


def test_signal_rejects_excessive_risk(client):
    resp = client.post("/signal", json=_buy(risk_percent=2.0), headers=HEADERS)
    assert resp.status_code == 400
    assert resp.json()["detail"]["reason"] == "risk_above_max"


def test_signal_rejects_invalid_sl_tp(client):
    # BUY but SL above entry — schema-level rejection (422).
    resp = client.post(
        "/signal", json=_buy(stop_loss=1.1100), headers=HEADERS
    )
    assert resp.status_code == 422


def test_signal_cooldown_blocks_then_clears(client):
    """Back-to-back signals are gated; after the cooldown window they pass."""
    import importlib

    first = client.post("/signal", json=_buy(), headers=HEADERS)
    assert first.status_code == 200

    blocked = client.post("/signal", json=_buy(), headers=HEADERS)
    assert blocked.status_code == 400
    assert blocked.json()["detail"]["reason"] == "cooldown_active"

    db_mod = importlib.import_module("app.database")
    model_mod = importlib.import_module("app.models")
    with db_mod.SessionLocal() as session:
        rec = session.query(model_mod.SignalRecord).first()
        assert rec is not None
        rec.created_at = datetime.now(timezone.utc) - timedelta(seconds=120)
        session.commit()

    cleared = client.post("/signal", json=_buy(), headers=HEADERS)
    assert cleared.status_code == 200, cleared.text
    rows = client.get("/signals", headers=HEADERS).json()
    assert len(rows) >= 3  # accepted, rejected, accepted
