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


# --- New event types added in Task 2 ----------------------------------------

NEW_EVENT_TYPES = ("terminal_loaded", "risk_policy_loaded", "smoke_pending")


def test_terminal_events_terminal_loaded_present(client) -> None:
    payload = client.get("/api/terminal/events").json()
    types = [e["type"] for e in payload["events"]]
    assert "terminal_loaded" in types


def test_terminal_events_risk_policy_loaded_present(client) -> None:
    payload = client.get("/api/terminal/events").json()
    types = [e["type"] for e in payload["events"]]
    assert "risk_policy_loaded" in types


def test_terminal_events_default_smoke_is_pending_not_passed(client) -> None:
    """Default route output must not falsely advertise a passing smoke run."""
    payload = client.get("/api/terminal/events").json()
    types = [e["type"] for e in payload["events"]]
    assert "smoke_pending" in types
    assert "smoke_passed" not in types


def test_terminal_events_event_types_are_in_known_vocabulary(client) -> None:
    """Every emitted event type must come from the documented vocabulary."""
    from app.services.audit_event_service import KNOWN_EVENT_TYPES

    payload = client.get("/api/terminal/events").json()
    for event in payload["events"]:
        assert event["type"] in KNOWN_EVENT_TYPES, (
            f"Event type {event['type']!r} is not in KNOWN_EVENT_TYPES; "
            "add it deliberately to the tuple if it should be emitted."
        )


def test_terminal_events_safety_note_field_present_on_safety_severity(
    client,
) -> None:
    """Every safety-severity event ships a non-empty safety_note explanation."""
    payload = client.get("/api/terminal/events").json()
    safety_events = [e for e in payload["events"] if e["severity"] == "safety"]
    assert safety_events, "expected at least one safety-severity event"
    for event in safety_events:
        assert "safety_note" in event
        note = event["safety_note"]
        assert isinstance(note, str) and len(note) > 0, (
            f"safety event {event['id']} has empty safety_note"
        )


def test_terminal_events_safety_note_no_secret_leakage(client) -> None:
    """The safety_note copy must not include known secret patterns."""
    payload = client.get("/api/terminal/events").json()
    notes = " | ".join(
        e["safety_note"] for e in payload["events"] if e.get("safety_note")
    )
    for pattern in SECRET_PATTERNS:
        assert pattern not in notes, (
            f"Possible secret pattern {pattern!r} found in safety_note copy"
        )


def test_audit_service_smoke_passed_path_emits_success() -> None:
    """Direct service call with passed=True flips the smoke event to success."""
    from app.schemas.risk import RiskConfig
    from app.services.audit_event_service import AuditEventService

    config = RiskConfig(
        max_risk_per_trade=1.0,
        max_daily_loss=2.0,
        max_drawdown=5.0,
        min_confidence=70,
        min_rr=1.5,
        max_open_positions=3,
        max_lot_size=0.1,
        cooldown_seconds=120,
        allow_same_signal=False,
        dry_run=True,
        auto_trade=False,
        emergency_pause=False,
    )
    feed = AuditEventService().list_events(config, smoke_passed=True)

    types = [e.type for e in feed.events]
    assert "smoke_passed" in types
    assert "smoke_pending" not in types
    smoke_event = next(e for e in feed.events if e.type == "smoke_passed")
    assert smoke_event.severity == "success"
    assert smoke_event.read_only is True
    assert smoke_event.safety_note  # non-empty
