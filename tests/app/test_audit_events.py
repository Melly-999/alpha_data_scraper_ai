from __future__ import annotations

VALID_SEVERITIES = {"info", "success", "warning", "error", "safety"}

# Exact unsafe execution path segments — must NOT appear in registered routes.
# Using complete path segments (split on "/") to avoid false positives from
# legitimate read-only routes like GET /api/orders (order history list).
UNSAFE_ROUTE_SEGMENTS = [
    "execute",
    "live-trade",
    "live_trade",
]

# Exact full paths that must not exist
UNSAFE_EXACT_PATHS = [
    "/api/order",
    "/api/trade/live",
    "/execute",
    "/api/execute",
]

SECRET_PATTERNS = [
    "API_KEY",
    "TOKEN",
    "PASSWORD",
    "SECRET",
    "MT5_PASSWORD",
    "CLAUDE_API_KEY",
    "GITHUB_TOKEN",
]


def test_terminal_events_returns_200(client) -> None:
    response = client.get("/api/terminal/events")
    assert response.status_code == 200


def test_terminal_events_safety_flags(client) -> None:
    payload = client.get("/api/terminal/events").json()
    assert payload["dry_run"] is True
    assert payload["auto_trade"] is False
    assert payload["read_only"] is True


def test_terminal_events_not_empty(client) -> None:
    payload = client.get("/api/terminal/events").json()
    assert len(payload["events"]) > 0


def test_terminal_events_dry_run_active_present(client) -> None:
    payload = client.get("/api/terminal/events").json()
    types = [e["type"] for e in payload["events"]]
    assert "dry_run_active" in types


def test_terminal_events_autotrade_disabled_present(client) -> None:
    payload = client.get("/api/terminal/events").json()
    types = [e["type"] for e in payload["events"]]
    assert "autotrade_disabled" in types


def test_terminal_events_live_orders_blocked_present(client) -> None:
    payload = client.get("/api/terminal/events").json()
    types = [e["type"] for e in payload["events"]]
    assert "live_orders_blocked" in types


def test_terminal_events_all_read_only(client) -> None:
    payload = client.get("/api/terminal/events").json()
    for event in payload["events"]:
        assert event["read_only"] is True


def test_terminal_events_no_secrets(client) -> None:
    payload = client.get("/api/terminal/events").json()
    raw = str(payload)
    for pattern in SECRET_PATTERNS:
        assert pattern not in raw, f"Possible secret pattern found: {pattern}"


def test_terminal_events_limit_1(client) -> None:
    response = client.get("/api/terminal/events?limit=1")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["events"]) <= 1


def test_terminal_events_high_limit_rejected(client) -> None:
    # FastAPI Query(le=200) rejects limit > 200 with 422
    response = client.get("/api/terminal/events?limit=500")
    assert response.status_code == 422


def test_terminal_events_zero_limit_rejected(client) -> None:
    # FastAPI Query(ge=1) rejects limit=0 with 422
    response = client.get("/api/terminal/events?limit=0")
    assert response.status_code == 422


def test_terminal_events_negative_limit_rejected(client) -> None:
    response = client.get("/api/terminal/events?limit=-1")
    assert response.status_code == 422


def test_no_unsafe_execution_routes(client) -> None:
    routes = {route.path for route in client.app.routes if hasattr(route, "path")}
    # Check for dangerous path segments in any registered route
    for segment in UNSAFE_ROUTE_SEGMENTS:
        matching = [path for path in routes if segment in path.split("/")]
        assert (
            not matching
        ), f"Unsafe route segment '{segment}' found in registered routes: {matching}"
    # Check that exact unsafe paths do not exist
    for exact in UNSAFE_EXACT_PATHS:
        assert exact not in routes, f"Unsafe exact route '{exact}' is registered"


def test_terminal_events_ids_non_empty(client) -> None:
    payload = client.get("/api/terminal/events").json()
    for event in payload["events"]:
        assert isinstance(event["id"], str)
        assert len(event["id"]) > 0


def test_terminal_events_timestamps_present(client) -> None:
    payload = client.get("/api/terminal/events").json()
    for event in payload["events"]:
        assert "timestamp" in event
        assert event["timestamp"] is not None
        assert len(event["timestamp"]) > 0


def test_terminal_events_severity_valid(client) -> None:
    payload = client.get("/api/terminal/events").json()
    for event in payload["events"]:
        assert (
            event["severity"] in VALID_SEVERITIES
        ), f"Event {event['id']} has invalid severity: {event['severity']}"


def test_terminal_events_source_and_message_non_empty(client) -> None:
    payload = client.get("/api/terminal/events").json()
    for event in payload["events"]:
        assert isinstance(event["source"], str) and len(event["source"]) > 0
        assert isinstance(event["message"], str) and len(event["message"]) > 0


def test_terminal_events_degraded_flag(client) -> None:
    payload = client.get("/api/terminal/events").json()
    assert "degraded" in payload
    assert isinstance(payload["degraded"], bool)


def test_terminal_events_generated_at_present(client) -> None:
    payload = client.get("/api/terminal/events").json()
    assert "generated_at" in payload
    assert payload["generated_at"] is not None
