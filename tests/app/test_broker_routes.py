"""FastAPI broker route tests.

These run against the real ``app.main:app`` via ``TestClient`` and must
pass even without ``ib_insync`` installed.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def isolated_broker_state(client) -> None:
    """Reset any cached broker adapter between tests."""
    if hasattr(client.app.state, "broker_adapter"):
        del client.app.state.broker_adapter


def test_broker_health_default_is_safe_disabled(client, isolated_broker_state) -> None:
    response = client.get("/api/broker/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["connected"] is False
    assert payload["supports_live_orders"] is False
    assert payload["mode"] in {"disabled", "paper"}
    assert payload["status"] in {"disabled", "ok", "missing_dependency"}


def test_broker_account_default_is_safe_disconnected(
    client, isolated_broker_state
) -> None:
    response = client.get("/api/broker/account")
    assert response.status_code == 200
    payload = response.json()
    assert payload["connected"] is False
    assert payload["net_liquidation"] == 0.0
    assert payload["cash"] == 0.0
    assert payload["buying_power"] == 0.0


def test_broker_dry_run_report_returns_typed_payload(
    client, isolated_broker_state
) -> None:
    response = client.post(
        "/api/broker/dry-run-report",
        json={
            "decision_id": "demo-001",
            "signal_id": "sig-001",
            "symbol": "AAPL",
            "direction": "BUY",
            "confidence": 72.0,
            "reason": "unit-test",
            "metadata": {"source": "pytest"},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["dry_run"] is True
    assert payload["decision_id"] == "demo-001"
    assert payload["symbol"] == "AAPL"
    assert payload["direction"] == "BUY"
    # broker can be the safe disabled adapter or ibkr_paper depending on env;
    # either way, no live order may be placed.
    assert payload["broker"] in {"mt5_demo", "ibkr_paper"}


def test_broker_dry_run_report_rejects_invalid_direction(
    client, isolated_broker_state
) -> None:
    response = client.post(
        "/api/broker/dry-run-report",
        json={
            "decision_id": "demo-002",
            "symbol": "AAPL",
            "direction": "SHORT",
            "confidence": 50.0,
        },
    )
    assert response.status_code == 422


def test_broker_health_when_ibkr_paper_selected(
    client, isolated_broker_state, monkeypatch: pytest.MonkeyPatch
) -> None:
    from brokers.ibkr_paper import IBKRPaperAdapter, IBKRPaperConfig

    cached = IBKRPaperAdapter(
        config=IBKRPaperConfig(enabled=True, mode="paper", port=7497)
    )
    client.app.state.broker_adapter = cached

    response = client.get("/api/broker/health")
    payload = response.json()
    assert response.status_code == 200
    assert payload["adapter"] == "ibkr_paper"
    assert payload["mode"] == "paper"
    assert payload["port"] == 7497
    assert payload["supports_live_orders"] is False


def test_broker_health_when_live_port_selected_is_blocked(
    client, isolated_broker_state
) -> None:
    from brokers.ibkr_paper import IBKRPaperAdapter, IBKRPaperConfig

    cached = IBKRPaperAdapter(
        config=IBKRPaperConfig(enabled=True, mode="paper", port=7496)
    )
    cached.connect()
    client.app.state.broker_adapter = cached

    response = client.get("/api/broker/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["connected"] is False
    assert payload["status"] == "live_blocked"
    assert "live_port_blocked" in (payload["last_error"] or "")
