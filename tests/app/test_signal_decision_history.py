from __future__ import annotations

VALID_DIRECTIONS = {"BUY", "SELL", "HOLD", "UNKNOWN"}
VALID_RISK_STATUSES = {"pass", "warn", "blocked", "unknown"}
VALID_DECISIONS = {"dry_run_allowed", "blocked", "watch_only", "no_action"}

SECRET_PATTERNS = [
    "API_KEY",
    "TOKEN",
    "PASSWORD",
    "SECRET",
    "MT5_PASSWORD",
    "CLAUDE_API_KEY",
    "GITHUB_TOKEN",
]

UNSAFE_ROUTE_SEGMENTS = ["execute", "live-trade", "live_trade"]
UNSAFE_EXACT_PATHS = [
    "/api/order",
    "/api/trade/live",
    "/execute",
    "/api/execute",
]


def test_signal_decisions_returns_200(client) -> None:
    response = client.get("/api/signals/decisions")
    assert response.status_code == 200


def test_signal_decisions_safety_flags(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    assert payload["dry_run"] is True
    assert payload["auto_trade"] is False
    assert payload["read_only"] is True


def test_signal_decisions_not_empty(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    assert len(payload["decisions"]) > 0


def test_signal_decisions_all_records_safe(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert rec["dry_run"] is True
        assert rec["auto_trade"] is False
        assert rec["read_only"] is True
        assert rec["stop_loss_required"] is True
        assert rec["take_profit_required"] is True
        assert rec["max_risk_per_trade"] <= 0.01


def test_signal_decisions_at_least_one_blocked(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    decisions = [r["decision"] for r in payload["decisions"]]
    assert "blocked" in decisions


def test_signal_decisions_at_least_one_dry_run_allowed(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    decisions = [r["decision"] for r in payload["decisions"]]
    assert "dry_run_allowed" in decisions


def test_signal_decisions_risk_statuses(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    statuses = {r["risk_status"] for r in payload["decisions"]}
    assert statuses & {"blocked", "pass"}


def test_signal_decisions_limit_1(client) -> None:
    response = client.get("/api/signals/decisions?limit=1")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["decisions"]) <= 1


def test_signal_decisions_limit_200(client) -> None:
    response = client.get("/api/signals/decisions?limit=200")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["decisions"]) <= 200


def test_signal_decisions_high_limit_rejected(client) -> None:
    response = client.get("/api/signals/decisions?limit=500")
    assert response.status_code == 422


def test_signal_decisions_zero_limit_rejected(client) -> None:
    response = client.get("/api/signals/decisions?limit=0")
    assert response.status_code == 422


def test_signal_decisions_negative_limit_rejected(client) -> None:
    response = client.get("/api/signals/decisions?limit=-5")
    assert response.status_code == 422


def test_signal_decisions_symbol_filter_known(client) -> None:
    response = client.get("/api/signals/decisions?symbol=AAPL")
    assert response.status_code == 200
    payload = response.json()
    for rec in payload["decisions"]:
        assert rec["symbol"].upper() == "AAPL"


def test_signal_decisions_symbol_filter_unknown(client) -> None:
    response = client.get("/api/signals/decisions?symbol=ZZZZZZ")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 0
    assert payload["decisions"] == []


def test_signal_decisions_no_secrets(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    raw = str(payload)
    for pattern in SECRET_PATTERNS:
        assert pattern not in raw, f"Possible secret pattern found: {pattern}"


def test_no_unsafe_execution_routes(client) -> None:
    routes = {route.path for route in client.app.routes if hasattr(route, "path")}
    for segment in UNSAFE_ROUTE_SEGMENTS:
        matching = [path for path in routes if segment in path.split("/")]
        assert not matching, f"Unsafe route segment '{segment}' found: {matching}"
    for exact in UNSAFE_EXACT_PATHS:
        assert exact not in routes, f"Unsafe exact route '{exact}' is registered"


def test_signal_decisions_ids_non_empty(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert isinstance(rec["id"], str) and len(rec["id"]) > 0


def test_signal_decisions_timestamps_present(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert "timestamp" in rec
        assert rec["timestamp"] is not None


def test_signal_decisions_symbols_non_empty(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert isinstance(rec["symbol"], str) and len(rec["symbol"]) > 0


def test_signal_decisions_confidence_in_range(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert (
            0.0 <= rec["confidence"] <= 1.0
        ), f"Confidence {rec['confidence']} out of range for {rec['id']}"


def test_signal_decisions_direction_valid(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert rec["direction"] in VALID_DIRECTIONS


def test_signal_decisions_decision_valid(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert rec["decision"] in VALID_DECISIONS


def test_signal_decisions_source_strategy_non_empty(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    for rec in payload["decisions"]:
        assert isinstance(rec["source"], str) and len(rec["source"]) > 0
        assert isinstance(rec["strategy"], str) and len(rec["strategy"]) > 0


def test_signal_decisions_total_matches_decisions(client) -> None:
    payload = client.get("/api/signals/decisions").json()
    assert payload["total"] == len(payload["decisions"])


def test_signal_decisions_existing_signals_unaffected(client) -> None:
    response = client.get("/api/signals")
    assert response.status_code == 200
