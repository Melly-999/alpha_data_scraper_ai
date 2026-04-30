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


def test_daily_report_requires_api_key(client):
    resp = client.get("/reports/daily")
    assert resp.status_code == 401


def test_daily_report_returns_read_only_summary(client):
    accepted = client.post("/signal", json=_buy(), headers=HEADERS)
    assert accepted.status_code == 200

    rejected = client.post(
        "/signal",
        json=_buy(symbol="GBPUSD", confidence=50.0),
        headers=HEADERS,
    )
    assert rejected.status_code == 400

    resp = client.get("/reports/daily", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()

    assert body["period"] == "daily"
    assert body["read_only"] is True
    assert body["safety_posture"]["dry_run"] is True
    assert body["safety_posture"]["read_only"] is True
    assert body["safety_posture"]["live_orders_blocked"] is True
    assert body["risk_config_snapshot"]["max_risk_percent"] == 1.0
    assert body["signal_counts"]["total"] == 2
    assert body["signal_counts"]["accepted"] == 1
    assert body["signal_counts"]["rejected"] == 1
    assert body["alert_counts_by_category"]["safety"] >= 1
    assert body["alert_counts_by_severity"]["success"] >= 1
    assert body["latest_audit_events"]
    assert "read-only" in body["markdown_summary"]


def test_weekly_report_returns_same_contract(client):
    resp = client.get("/reports/weekly", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()

    assert body["period"] == "weekly"
    assert body["read_only"] is True
    assert body["signal_counts"] == {
        "total": 0,
        "accepted": 0,
        "rejected": 0,
    }
    assert "markdown_summary" in body
    assert body["risk_config_snapshot"]["live_orders_blocked"] is True


def test_reports_are_get_only(client):
    for path in ("/reports/daily", "/reports/weekly"):
        for method in ("post", "put", "delete", "patch"):
            resp = client.request(method.upper(), path, json={}, headers=HEADERS)
            assert resp.status_code in (404, 405)


def test_no_live_execution_routes_exposed_after_reports(client):
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
