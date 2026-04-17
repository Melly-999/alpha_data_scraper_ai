from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_db
from app.main import app, risk_manager


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "signals.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=engine)
    risk_manager.last_seen.clear()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def fake_publish_signal(_payload):
        return {"published": True}

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr("app.main.publish_signal", fake_publish_signal)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def valid_payload():
    return {
        "symbol": "EURUSD",
        "direction": "BUY",
        "confidence": 80,
        "price": 1.1,
        "stopLoss": 1.09,
        "takeProfit": 1.12,
        "riskPercent": 0.5,
    }


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_signal_unauthorized(client, valid_payload):
    response = client.post("/signal", json=valid_payload)
    assert response.status_code == 401


def test_signal_success(client, valid_payload):
    response = client.post(
        "/signal",
        json=valid_payload,
        headers={"X-API-Key": "change-me-fastapi-key"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


@pytest.mark.parametrize(
    ("patch", "detail"),
    [
        ({"riskPercent": 1.1}, "Risk percent above max"),
        ({"confidence": 69.9}, "Confidence below minimum"),
        ({"stopLoss": None}, "SL/TP required"),
    ],
)
def test_signal_blocked_by_risk_rules(client, valid_payload, patch, detail):
    payload = {**valid_payload, **patch}
    response = client.post(
        "/signal",
        json=payload,
        headers={"X-API-Key": "change-me-fastapi-key"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == detail


def test_signal_blocked_by_cooldown(client, valid_payload):
    headers = {"X-API-Key": "change-me-fastapi-key"}
    accepted = client.post("/signal", json=valid_payload, headers=headers)
    assert accepted.status_code == 200

    blocked = client.post("/signal", json=valid_payload, headers=headers)
    assert blocked.status_code == 400
    assert blocked.json()["detail"] == "Cooldown active"
