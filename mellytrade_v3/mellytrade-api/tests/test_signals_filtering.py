from __future__ import annotations

import importlib
from datetime import datetime, timedelta, timezone

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


def _seed_records(client, *, accept_eurusd: int, reject_low_conf: int) -> None:
    """Seed accepted EURUSD signals and rejected low-confidence GBPUSD signals."""
    db_mod = importlib.import_module("app.database")
    model_mod = importlib.import_module("app.models")

    for _ in range(accept_eurusd):
        resp = client.post("/signal", json=_buy(), headers=HEADERS)
        assert resp.status_code == 200, resp.text
        # Backdate so the cooldown does not trip the next insert.
        with db_mod.SessionLocal() as session:
            row = (
                session.query(model_mod.SignalRecord)
                .order_by(model_mod.SignalRecord.id.desc())
                .first()
            )
            assert row is not None
            row.created_at = datetime.now(timezone.utc) - timedelta(seconds=120)
            session.commit()

    for _ in range(reject_low_conf):
        resp = client.post(
            "/signal",
            json=_buy(symbol="GBPUSD", confidence=50.0),
            headers=HEADERS,
        )
        assert resp.status_code == 400


def test_signals_returns_dashboard_summary_fields(client):
    resp = client.post("/signal", json=_buy(), headers=HEADERS)
    assert resp.status_code == 200

    rows = client.get("/signals", headers=HEADERS).json()
    assert len(rows) == 1
    row = rows[0]
    # Dashboard contract fields.
    assert row["symbol"] == "EURUSD"
    assert row["action"] == "BUY"
    assert row["confidence"] == 75.0
    assert row["confidence_clamped"] == 75.0
    assert row["risk_pct"] == 0.5
    assert row["status"] == "accepted"
    assert row["dry_run"] is True
    assert row["read_only"] is True


def test_signals_confidence_clamped_to_range(client):
    """Pipeline clamps confidence to [33, 85] for dashboard display."""
    db_mod = importlib.import_module("app.database")
    model_mod = importlib.import_module("app.models")

    client.post("/signal", json=_buy(), headers=HEADERS)
    with db_mod.SessionLocal() as session:
        row = session.query(model_mod.SignalRecord).first()
        assert row is not None
        row.confidence = 99.0  # Simulate raw upstream score outside clamp.
        row.created_at = datetime.now(timezone.utc) - timedelta(seconds=120)
        session.commit()

    rows = client.get("/signals", headers=HEADERS).json()
    assert rows[0]["confidence"] == 99.0
    assert rows[0]["confidence_clamped"] == 85.0


def test_signals_filter_by_symbol(client):
    _seed_records(client, accept_eurusd=2, reject_low_conf=1)
    rows = client.get("/signals?symbol=EURUSD", headers=HEADERS).json()
    assert len(rows) == 2
    assert all(r["symbol"] == "EURUSD" for r in rows)


def test_signals_filter_by_status(client):
    _seed_records(client, accept_eurusd=2, reject_low_conf=1)
    accepted = client.get("/signals?status=accepted", headers=HEADERS).json()
    rejected = client.get("/signals?status=rejected", headers=HEADERS).json()
    assert all(r["status"] == "accepted" for r in accepted)
    assert all(r["status"] == "rejected" for r in rejected)
    assert len(accepted) == 2
    assert len(rejected) == 1
    assert rejected[0]["rejection_reason"]
    assert "confidence_below_min" in rejected[0]["reason"]


def test_signals_invalid_status_rejected(client):
    resp = client.get("/signals?status=somethingelse", headers=HEADERS)
    assert resp.status_code == 400
    assert resp.json()["reason"] == "invalid_status"


def test_signals_limit_clamped(client):
    resp = client.get("/signals?limit=0", headers=HEADERS)
    assert resp.status_code == 422  # FastAPI Query ge=1 enforcement
    resp = client.get("/signals?limit=10000", headers=HEADERS)
    assert resp.status_code == 422  # FastAPI Query le=500 enforcement


def test_signals_requires_api_key(client):
    resp = client.get("/signals")
    assert resp.status_code == 401
