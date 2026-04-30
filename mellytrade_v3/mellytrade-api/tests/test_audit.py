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


def _backdate_latest():
    db_mod = importlib.import_module("app.database")
    model_mod = importlib.import_module("app.models")
    with db_mod.SessionLocal() as session:
        row = (
            session.query(model_mod.SignalRecord)
            .order_by(model_mod.SignalRecord.id.desc())
            .first()
        )
        if row is None:
            return
        row.created_at = datetime.now(timezone.utc) - timedelta(seconds=120)
        session.commit()


def test_audit_requires_api_key(client):
    resp = client.get("/audit")
    assert resp.status_code == 401


def test_audit_returns_safety_state_when_empty(client):
    resp = client.get("/audit", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["dry_run"] is True
    assert body["read_only"] is True
    assert body["live_orders_blocked"] is True

    types = {e["type"] for e in body["events"]}
    assert "dry_run_active" in types
    assert "read_only_mode_active" in types
    assert "live_orders_blocked" in types


def test_audit_records_signal_accepted(client):
    client.post("/signal", json=_buy(), headers=HEADERS)
    _backdate_latest()

    body = client.get("/audit", headers=HEADERS).json()
    accepted = [e for e in body["events"] if e["type"] == "signal_accepted"]
    assert len(accepted) == 1
    assert accepted[0]["severity"] == "info"
    assert accepted[0]["signal_id"] is not None
    assert accepted[0]["detail"]["symbol"] == "EURUSD"


def test_audit_records_risk_gate_failure(client):
    client.post("/signal", json=_buy(confidence=50), headers=HEADERS)
    body = client.get("/audit", headers=HEADERS).json()
    failures = [e for e in body["events"] if e["type"] == "risk_gate_failed"]
    assert len(failures) >= 1
    assert failures[0]["severity"] == "warning"
    assert failures[0]["detail"]["reason"] == "confidence_below_min"


def test_audit_records_cooldown(client):
    client.post("/signal", json=_buy(), headers=HEADERS)
    blocked = client.post("/signal", json=_buy(), headers=HEADERS)
    assert blocked.status_code == 400

    body = client.get("/audit", headers=HEADERS).json()
    cooldowns = [e for e in body["events"] if e["type"] == "cooldown_active"]
    # First entry is the safety-state cooldown banner is NOT created here;
    # only signal-derived cooldown_active events are surfaced.
    assert any(e.get("signal_id") for e in cooldowns)


def test_audit_filter_by_event_type(client):
    client.post("/signal", json=_buy(), headers=HEADERS)
    _backdate_latest()
    client.post("/signal", json=_buy(confidence=50), headers=HEADERS)

    only_accepted = client.get(
        "/audit?event_type=signal_accepted", headers=HEADERS
    ).json()
    assert all(e["type"] == "signal_accepted" for e in only_accepted["events"])
    assert len(only_accepted["events"]) >= 1


def test_audit_no_execution_events_present(client):
    """The audit feed must never carry trade-execution events.

    `live_orders_blocked` is allowed (and required) — that is a *negative*
    safety-state event. What must be absent are positive execution events
    such as order placement, order fills, or trade closures.
    """
    forbidden_substrings = (
        "order_placed",
        "order_filled",
        "order_executed",
        "trade_executed",
        "position_opened",
        "position_closed",
        "trade_filled",
    )

    body = client.get("/audit", headers=HEADERS).json()
    for event in body["events"]:
        for needle in forbidden_substrings:
            assert needle not in event["type"], event
