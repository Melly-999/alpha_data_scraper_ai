from __future__ import annotations

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
    "/api/signals/execute",
    "/api/signals/order",
    "/api/signals/live-trade",
]

EXPECTED_STEP_KEYS = [
    "signal_received",
    "confidence_checked",
    "risk_checked",
    "broker_safety_checked",
    "dry_run_decision",
    "blocked_or_allowed_reason",
    "audit_event_reference",
]


def test_signal_lifecycle_returns_200(client) -> None:
    response = client.get("/api/signals/lifecycle")
    assert response.status_code == 200


def test_signal_lifecycle_safety_flags(client) -> None:
    payload = client.get("/api/signals/lifecycle").json()
    assert payload["dry_run"] is True
    assert payload["auto_trade"] is False
    assert payload["read_only"] is True
    assert payload["supports_live_orders"] is False


def test_signal_lifecycle_records_are_safe(client) -> None:
    payload = client.get("/api/signals/lifecycle").json()
    assert payload["lifecycle"]
    for record in payload["lifecycle"]:
        assert record["dry_run"] is True
        assert record["auto_trade"] is False
        assert record["read_only"] is True
        assert record["supports_live_orders"] is False
        assert record["order_placed"] is False
        assert record["max_risk_per_trade"] <= 0.01


def test_signal_lifecycle_dry_run_allowed_is_not_order_placed(client) -> None:
    payload = client.get("/api/signals/lifecycle").json()
    dry_run_allowed = [
        record for record in payload["lifecycle"] if record["dry_run_allowed"] is True
    ]
    assert dry_run_allowed
    for record in dry_run_allowed:
        assert record["decision"] == "dry_run_allowed"
        assert record["order_placed"] is False
        dry_run_step = [
            step for step in record["steps"] if step["key"] == "dry_run_decision"
        ][0]
        assert "no order was placed" in dry_run_step["detail"].lower()


def test_signal_lifecycle_contains_expected_steps(client) -> None:
    payload = client.get("/api/signals/lifecycle?limit=1").json()
    record = payload["lifecycle"][0]
    assert [step["key"] for step in record["steps"]] == EXPECTED_STEP_KEYS


def test_signal_lifecycle_has_blocked_reason_and_audit_reference(client) -> None:
    payload = client.get("/api/signals/lifecycle").json()
    assert any(record["blocked_reason"] for record in payload["lifecycle"])
    for record in payload["lifecycle"]:
        assert record["audit_event_id"]
        audit_steps = [
            step for step in record["steps"] if step["key"] == "audit_event_reference"
        ]
        assert audit_steps
        assert audit_steps[0]["audit_event_id"] == record["audit_event_id"]


def test_signal_lifecycle_limit_and_symbol_filter(client) -> None:
    response = client.get("/api/signals/lifecycle?limit=1&symbol=AAPL")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] <= 1
    for record in payload["lifecycle"]:
        assert record["symbol"] == "AAPL"


def test_signal_lifecycle_high_limit_rejected(client) -> None:
    response = client.get("/api/signals/lifecycle?limit=500")
    assert response.status_code == 422


def test_signal_lifecycle_is_get_only(client) -> None:
    routes = [
        route
        for route in client.app.routes
        if getattr(route, "path", None) == "/api/signals/lifecycle"
    ]
    assert routes
    assert all(getattr(route, "methods", set()) == {"GET"} for route in routes)


def test_signal_lifecycle_route_precedes_signal_id_route(client) -> None:
    paths = [route.path for route in client.app.routes if hasattr(route, "path")]
    lifecycle_index = paths.index("/api/signals/lifecycle")
    signal_id_index = paths.index("/api/signals/{signal_id}")
    assert lifecycle_index < signal_id_index


def test_signal_lifecycle_no_secrets(client) -> None:
    payload = client.get("/api/signals/lifecycle").json()
    raw = str(payload)
    for pattern in SECRET_PATTERNS:
        assert pattern not in raw, f"Possible secret pattern found: {pattern}"


def test_no_unsafe_signal_lifecycle_execution_routes(client) -> None:
    routes = {route.path for route in client.app.routes if hasattr(route, "path")}
    for segment in UNSAFE_ROUTE_SEGMENTS:
        matching = [path for path in routes if segment in path.split("/")]
        assert not matching, f"Unsafe route segment '{segment}' found: {matching}"
    for exact in UNSAFE_EXACT_PATHS:
        assert exact not in routes, f"Unsafe exact route '{exact}' is registered"
