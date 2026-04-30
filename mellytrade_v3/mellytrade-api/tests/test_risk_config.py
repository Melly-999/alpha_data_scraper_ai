from __future__ import annotations

HEADERS = {"X-API-Key": "test-key"}


def test_risk_config_requires_api_key(client):
    resp = client.get("/risk/config")
    assert resp.status_code == 401


def test_risk_config_reports_safety_posture(client):
    resp = client.get("/risk/config", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["dry_run"] is True
    assert body["autotrade_enabled"] is False
    assert body["read_only"] is True
    assert body["live_orders_blocked"] is True
    assert body["max_risk_percent"] <= 1.0
    assert body["min_confidence"] == 70.0
    assert body["cooldown_seconds"] == 60


def test_risk_config_lists_active_gates(client):
    body = client.get("/risk/config", headers=HEADERS).json()
    gate_names = {gate["name"] for gate in body["gates"]}
    assert {
        "min_confidence",
        "max_risk_percent",
        "cooldown_seconds",
        "sl_tp_required",
    }.issubset(gate_names)
    for gate in body["gates"]:
        assert gate["active"] is True
        assert gate["description"]


def test_risk_config_is_read_only_endpoint(client):
    """Direction B never exposes a write path for risk gates."""
    # POST/PUT/DELETE must not be defined on /risk/config.
    assert client.post("/risk/config", json={}, headers=HEADERS).status_code in (
        404,
        405,
    )
    assert client.put("/risk/config", json={}, headers=HEADERS).status_code in (
        404,
        405,
    )
    assert client.delete("/risk/config", headers=HEADERS).status_code in (
        404,
        405,
    )


def test_no_live_execution_routes_exposed(client):
    """No order placement / execution endpoints exist anywhere in the API."""
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
            # Must be a 404 (not implemented). Anything else means a route exists.
            assert (
                resp.status_code == 404
            ), f"unexpected route {method.upper()} {path}: {resp.status_code}"
