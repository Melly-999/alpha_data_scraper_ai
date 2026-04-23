from __future__ import annotations


def test_health_endpoint_reports_dependencies(client) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "dependencies" in payload
    assert payload["safety"]["auto_trade"] is False
    assert payload["safety"]["dry_run"] is True


def test_signals_contract_and_confidence_bounds(client) -> None:
    response = client.get("/api/signals")

    assert response.status_code == 200
    payload = response.json()
    assert payload
    for item in payload:
        assert {
            "id",
            "symbol",
            "direction",
            "confidence",
            "eligible",
            "blocked",
        }.issubset(item)
        assert 33 <= item["confidence"] <= 85


def test_signal_reasoning_contract(client) -> None:
    response = client.get("/api/signals/sig-001/reasoning")

    assert response.status_code == 200
    payload = response.json()
    assert payload["signal_id"] == "sig-001"
    assert isinstance(payload["risk_gate_results"], list)
    assert payload["risk_gate_results"]


def test_risk_config_update_is_sanitized(client) -> None:
    response = client.put(
        "/api/risk/config",
        json={
            "max_risk_per_trade": 4.0,
            "min_confidence": 20,
            "auto_trade": True,
            "dry_run": False,
            "allow_same_signal": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["max_risk_per_trade"] == 1.0
    assert payload["min_confidence"] >= 70
    assert payload["auto_trade"] is False
    assert payload["dry_run"] is True
    assert payload["allow_same_signal"] is False


def test_emergency_stop_is_idempotent_and_blocks_execution_paths(client) -> None:
    first = client.post("/api/risk/emergency-stop")
    second = client.post("/api/risk/emergency-stop")
    signals = client.get("/api/signals")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["stopped"] is True
    assert second.json()["config"]["emergency_pause"] is True
    blocked = [
        item for item in signals.json() if item["blocked_reason"] == "EMERGENCY_STOP"
    ]
    assert blocked
