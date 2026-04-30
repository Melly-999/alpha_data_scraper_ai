from __future__ import annotations


def test_local_checklist_default_is_safe_without_tws(client) -> None:
    if hasattr(client.app.state, "broker_adapter"):
        del client.app.state.broker_adapter

    response = client.get("/api/local/checklist")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "MellyTrade Local Workstation"
    assert payload["summary"]["dry_run"] is True
    assert payload["summary"]["auto_trade"] is False
    assert payload["summary"]["supports_live_orders"] is False
    assert payload["summary"]["live_orders_blocked"] is True
    assert payload["summary"]["broker_connected"] is False

    checks = {item["id"]: item for item in payload["checks"]}
    assert {"backend", "dry_run", "auto_trade", "broker_live_orders"}.issubset(checks)
    assert checks["backend"]["status"] == "pass"
    assert checks["dry_run"]["status"] == "pass"
    assert checks["auto_trade"]["status"] == "pass"
    assert checks["broker_live_orders"]["status"] == "pass"


def test_local_checklist_marks_live_port_as_failed_but_blocked(client) -> None:
    from brokers.ibkr_paper import IBKRPaperAdapter, IBKRPaperConfig

    cached = IBKRPaperAdapter(
        config=IBKRPaperConfig(enabled=True, mode="paper", port=7496)
    )
    cached.connect()
    client.app.state.broker_adapter = cached

    response = client.get("/api/local/checklist")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["summary"]["supports_live_orders"] is False
    assert payload["summary"]["live_orders_blocked"] is True
    assert payload["summary"]["broker_status"] == "live_blocked"

    checks = {item["id"]: item for item in payload["checks"]}
    assert checks["broker_live_orders"]["status"] == "pass"
    assert checks["broker_mode"]["status"] == "fail"
