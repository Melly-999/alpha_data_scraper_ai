from __future__ import annotations

SECRET_PATTERNS = [
    "API_KEY",
    "TOKEN",
    "PASSWORD",
    "SECRET",
    "MT5_PASSWORD",
    "CLAUDE_API_KEY",
    "GITHUB_TOKEN",
    "FASTAPI_KEY",
    "CF_API_SECRET",
]

UNSAFE_ROUTES = [
    "/execute",
    "/order",
    "/live-trade",
    "/trade/live",
    "/api/execute",
    "/api/order",
    "/api/live-trade",
]

REQUIRED_EVENT_TYPES = {
    "dry_run_active",
    "autotrade_disabled",
    "read_only_mode_confirmed",
    "live_orders_blocked",
}


def test_events_returns_200(client) -> None:
    resp = client.get("/events")
    assert resp.status_code == 200


def test_events_safety_flags(client) -> None:
    body = client.get("/events").json()
    assert body["dry_run"] is True
    assert body["auto_trade"] is False
    assert body["read_only"] is True


def test_events_not_empty(client) -> None:
    body = client.get("/events").json()
    assert len(body["events"]) > 0


def test_events_has_dry_run_active(client) -> None:
    body = client.get("/events").json()
    types = {e["type"] for e in body["events"]}
    assert "dry_run_active" in types


def test_events_has_autotrade_disabled(client) -> None:
    body = client.get("/events").json()
    types = {e["type"] for e in body["events"]}
    assert "autotrade_disabled" in types


def test_events_has_read_only_mode_confirmed(client) -> None:
    body = client.get("/events").json()
    types = {e["type"] for e in body["events"]}
    assert "read_only_mode_confirmed" in types


def test_events_has_live_orders_blocked(client) -> None:
    body = client.get("/events").json()
    types = {e["type"] for e in body["events"]}
    assert "live_orders_blocked" in types


def test_all_required_event_types_present(client) -> None:
    body = client.get("/events").json()
    types = {e["type"] for e in body["events"]}
    missing = REQUIRED_EVENT_TYPES - types
    assert not missing, f"Missing required event types: {missing}"


def test_all_events_read_only(client) -> None:
    body = client.get("/events").json()
    for event in body["events"]:
        assert (
            event["read_only"] is True
        ), f"Event {event['id']} has read_only={event['read_only']}"


def test_events_limit_reduces_count(client) -> None:
    full = client.get("/events").json()
    limited = client.get("/events?limit=2").json()
    assert len(limited["events"]) <= 2
    assert len(limited["events"]) <= len(full["events"])


def test_events_limit_200_accepted(client) -> None:
    resp = client.get("/events?limit=200")
    assert resp.status_code == 200
    assert len(resp.json()["events"]) <= 200


def test_events_limit_above_200_rejected(client) -> None:
    resp = client.get("/events?limit=201")
    assert resp.status_code == 422


def test_events_limit_zero_rejected(client) -> None:
    resp = client.get("/events?limit=0")
    assert resp.status_code == 422


def test_events_limit_negative_rejected(client) -> None:
    resp = client.get("/events?limit=-1")
    assert resp.status_code == 422


def test_events_no_secret_leakage(client) -> None:
    body = client.get("/events").json()
    raw = str(body)
    for pattern in SECRET_PATTERNS:
        assert (
            pattern not in raw
        ), f"Possible secret pattern found in response: {pattern}"


def test_no_unsafe_execution_routes(client) -> None:
    routes = {route.path for route in client.app.routes if hasattr(route, "path")}
    for unsafe in UNSAFE_ROUTES:
        assert unsafe not in routes, f"Unsafe route '{unsafe}' is registered"


def test_events_have_required_fields(client) -> None:
    body = client.get("/events").json()
    for event in body["events"]:
        assert "id" in event and event["id"]
        assert "timestamp" in event and event["timestamp"]
        assert "type" in event and event["type"]
        assert "severity" in event and event["severity"]
        assert "source" in event and event["source"]
        assert "message" in event and event["message"]


def test_events_severity_values_valid(client) -> None:
    valid = {"info", "success", "warning", "error", "safety"}
    body = client.get("/events").json()
    for event in body["events"]:
        assert (
            event["severity"] in valid
        ), f"Unexpected severity {event['severity']!r} on event {event['id']}"


def test_events_degraded_flag_present(client) -> None:
    body = client.get("/events").json()
    assert "degraded" in body
    assert isinstance(body["degraded"], bool)


def test_events_fallback_flag_present(client) -> None:
    body = client.get("/events").json()
    assert "fallback" in body
    assert isinstance(body["fallback"], bool)


def test_events_generated_at_present(client) -> None:
    body = client.get("/events").json()
    assert "generated_at" in body
    assert body["generated_at"] is not None


def test_existing_health_unaffected(client) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
