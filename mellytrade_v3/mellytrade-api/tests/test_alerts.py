from __future__ import annotations

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


def test_alerts_requires_api_key(client):
    resp = client.get("/alerts")
    assert resp.status_code == 401


def test_alerts_returns_safety_alerts(client):
    resp = client.get("/alerts", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert body
    assert all(alert["read_only"] is True for alert in body)

    categories = {alert["category"] for alert in body}
    assert "safety" in categories
    assert "high_impact_news_placeholder" in categories
    assert any(alert["id"] == "safety-dry-run-active" for alert in body)
    assert any(alert["id"] == "safety-read-only-mode-active" for alert in body)
    assert any(alert["id"] == "safety-live-orders-blocked" for alert in body)


def test_alerts_include_risk_gate_failures(client):
    rejected = client.post(
        "/signal",
        json=_buy(confidence=50.0),
        headers=HEADERS,
    )
    assert rejected.status_code == 400

    resp = client.get("/alerts", headers=HEADERS)
    assert resp.status_code == 200
    alerts = resp.json()
    risk_alerts = [alert for alert in alerts if alert["category"] == "risk_gate_failed"]
    assert risk_alerts
    assert risk_alerts[0]["symbol"] == "EURUSD"
    assert risk_alerts[0]["signal_id"] is not None
    assert risk_alerts[0]["metadata"]["reason"] == "confidence_below_min"


def test_alerts_endpoint_is_get_only(client):
    for method in ("post", "put", "delete"):
        resp = client.request(method.upper(), "/alerts", json={}, headers=HEADERS)
        assert resp.status_code in (404, 405)


def test_no_live_execution_routes_exposed_after_alerts(client):
    forbidden_paths = [
        "/order",
        "/orders",
        "/execute",
        "/execute_signal",
        "/place_order",
        "/buy",
        "/sell",
        "/close",
        "/flatten",
    ]
    for path in forbidden_paths:
        for method in ("get", "post", "put", "delete"):
            resp = getattr(client, method)(path)
            assert (
                resp.status_code == 404
            ), f"unexpected route {method.upper()} {path}: {resp.status_code}"
