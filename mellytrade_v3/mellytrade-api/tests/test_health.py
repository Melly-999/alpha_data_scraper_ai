from __future__ import annotations


def test_health_reports_risk_settings(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "mellytrade-api"
    assert body["cooldown_seconds"] == 60
    assert body["min_confidence"] == 70.0
    assert body["max_risk_percent"] == 1.0
    assert body["database"] == "sqlite"
