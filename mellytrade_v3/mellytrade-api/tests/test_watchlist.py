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


def test_watchlist_requires_api_key(client):
    resp = client.get("/watchlist")
    assert resp.status_code == 401


def test_watchlist_returns_expected_fields(client):
    resp = client.get("/watchlist", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert body

    item = body[0]
    expected = {
        "symbol",
        "name",
        "asset_class",
        "last_price",
        "change_pct",
        "signal_status",
        "signal_confidence",
        "alert_count",
        "risk_state",
        "source",
        "generated_at",
        "read_only",
    }
    assert expected.issubset(item)
    assert item["read_only"] is True


def test_watchlist_enriches_signal_status_and_alert_counts(client):
    rejected = client.post(
        "/signal",
        json=_buy(symbol="GBPUSD", confidence=50.0),
        headers=HEADERS,
    )
    assert rejected.status_code == 400

    resp = client.get("/watchlist", headers=HEADERS)
    assert resp.status_code == 200
    rows = {row["symbol"]: row for row in resp.json()}

    assert rows["GBPUSD"]["signal_status"] == "rejected"
    assert rows["GBPUSD"]["signal_confidence"] == 50.0
    assert rows["GBPUSD"]["alert_count"] >= 1
    assert rows["GBPUSD"]["risk_state"] == "blocked"
    assert rows["GBPUSD"]["read_only"] is True


def test_watchlist_endpoint_is_get_only(client):
    for method in ("post", "put", "delete", "patch"):
        resp = client.request(method.upper(), "/watchlist", json={}, headers=HEADERS)
        assert resp.status_code in (404, 405)


def test_no_live_execution_routes_exposed_after_watchlist(client):
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
