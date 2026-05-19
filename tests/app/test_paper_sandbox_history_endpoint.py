"""PAPER-002B — Tests for the GET-only paper sandbox history endpoint.

GET /api/paper/sandbox/history

All tests are paper-only decision-support assertions.  No broker execution,
no MT5/IBKR calls, no network I/O.  Every test uses the
TestClient fixture from conftest.py.

Safety contract verified by every test group:
  paper_only             = True
  dry_run                = True
  read_only              = True
  live_orders_blocked    = True
  requires_human_review  = True
  broker_execution_allowed = False
  risk_allowed           = False
  execution_mode         = "dry_run_only"

Forbidden fields verified to be absent:
  account_id, broker_account_id, order_id, execution_id, trade_id,
  broker_order_id, ibkr_order_id, mt5_ticket, secret, token, api_key,
  password.

No broker/MT5/IBKR modules may be imported in the route module.
"""

from __future__ import annotations

import inspect
from collections.abc import Generator

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ENDPOINT = "/api/paper/sandbox/history"

_FORBIDDEN_FIELDS: tuple[str, ...] = (
    "account_id",
    "broker_account_id",
    "order_id",
    "execution_id",
    "trade_id",
    "broker_order_id",
    "ibkr_order_id",
    "mt5_ticket",
    "secret",
    "token",
    "api_key",
    "password",
)

_FORBIDDEN_BROKER_MODULES: tuple[str, ...] = (
    "MetaTrader5",
    "ibapi",
    "ib_insync",
    "ibkr",
    "mt5_trader",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_history() -> Generator[None, None, None]:
    """Reset the module-level history singleton before and after each test.

    Prevents cross-test state pollution from the in-memory store.
    """
    from app.services.paper_sandbox_history import get_paper_sandbox_history

    svc = get_paper_sandbox_history()
    svc.reset()
    yield
    svc.reset()


# ---------------------------------------------------------------------------
# 1. Basic behaviour — GET returns 200
# ---------------------------------------------------------------------------


def test_history_get_returns_200(client) -> None:
    """GET /api/paper/sandbox/history must return HTTP 200."""
    response = client.get(ENDPOINT)
    assert response.status_code == 200, response.text


def test_history_response_is_json(client) -> None:
    """Response body must be parseable JSON."""
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)


# ---------------------------------------------------------------------------
# 2. Empty state — explicit and safe
# ---------------------------------------------------------------------------


def test_empty_state_count_is_zero(client) -> None:
    """When no events exist, count must be 0."""
    assert client.get(ENDPOINT).json()["count"] == 0


def test_empty_state_events_is_empty_list(client) -> None:
    """When no events exist, events must be an empty list."""
    assert client.get(ENDPOINT).json()["events"] == []


def test_empty_state_still_has_all_safety_flags(client) -> None:
    """Safety flags must be present even when the history is empty."""
    body = client.get(ENDPOINT).json()
    assert body["paper_only"] is True
    assert body["dry_run"] is True
    assert body["read_only"] is True
    assert body["live_orders_blocked"] is True
    assert body["execution_mode"] == "dry_run_only"
    assert body["broker_execution_allowed"] is False
    assert body["risk_allowed"] is False
    assert body["requires_human_review"] is True


# ---------------------------------------------------------------------------
# 3. Canonical safety flags — checked individually
# ---------------------------------------------------------------------------


def test_response_paper_only_is_true(client) -> None:
    assert client.get(ENDPOINT).json()["paper_only"] is True


def test_response_dry_run_is_true(client) -> None:
    assert client.get(ENDPOINT).json()["dry_run"] is True


def test_response_read_only_is_true(client) -> None:
    assert client.get(ENDPOINT).json()["read_only"] is True


def test_response_live_orders_blocked_is_true(client) -> None:
    assert client.get(ENDPOINT).json()["live_orders_blocked"] is True


def test_response_execution_mode_is_dry_run_only(client) -> None:
    assert client.get(ENDPOINT).json()["execution_mode"] == "dry_run_only"


def test_response_broker_execution_allowed_is_false(client) -> None:
    assert client.get(ENDPOINT).json()["broker_execution_allowed"] is False


def test_response_risk_allowed_is_false(client) -> None:
    assert client.get(ENDPOINT).json()["risk_allowed"] is False


def test_response_requires_human_review_is_true(client) -> None:
    assert client.get(ENDPOINT).json()["requires_human_review"] is True


# ---------------------------------------------------------------------------
# 4. Forbidden fields — not present in top-level response or nested events
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("field", _FORBIDDEN_FIELDS)
def test_top_level_response_has_no_forbidden_field(client, field: str) -> None:
    """No forbidden field may appear at the top level of the response."""
    body = client.get(ENDPOINT).json()
    assert field not in body, (
        f"Forbidden field '{field}' found at top level of history response"
    )


def test_events_contain_no_forbidden_fields_when_populated(client) -> None:
    """No forbidden field may appear in any audit event in the response."""
    from app.services.paper_sandbox_history import get_paper_sandbox_history

    svc = get_paper_sandbox_history()
    svc.append(
        event_type="sandbox_preview_requested",
        message="Forbidden field check fixture",
        source="test",
        metadata={"symbol": "EURUSD", "timeframe": "H1"},
    )

    body = client.get(ENDPOINT).json()
    assert body["count"] == 1

    for event in body["events"]:
        for field in _FORBIDDEN_FIELDS:
            assert field not in event, (
                f"Forbidden field '{field}' found in audit event: {event}"
            )


# ---------------------------------------------------------------------------
# 5. Events surfaced via service appear in endpoint response
# ---------------------------------------------------------------------------


def test_event_appended_via_service_appears_in_response(client) -> None:
    """An event appended to the singleton must appear in the endpoint response."""
    from app.services.paper_sandbox_history import get_paper_sandbox_history

    svc = get_paper_sandbox_history()
    appended = svc.append(
        event_type="sandbox_state_created",
        message="Test event for endpoint response check",
        source="test_suite",
    )

    body = client.get(ENDPOINT).json()
    assert body["count"] == 1
    assert len(body["events"]) == 1
    event = body["events"][0]
    assert event["event_id"] == appended.event_id
    assert event["event_type"] == "sandbox_state_created"
    assert event["message"] == "Test event for endpoint response check"
    assert event["source"] == "test_suite"


def test_multiple_events_appear_in_order(client) -> None:
    """Multiple appended events appear in FIFO order (most-recent last)."""
    from app.services.paper_sandbox_history import get_paper_sandbox_history

    svc = get_paper_sandbox_history()
    for i in range(3):
        svc.append(
            event_type="safety_flags_checked",
            message=f"Event {i}",
            source="test",
        )

    body = client.get(ENDPOINT).json()
    assert body["count"] == 3
    assert len(body["events"]) == 3
    messages = [e["message"] for e in body["events"]]
    assert messages == ["Event 0", "Event 1", "Event 2"]


def test_count_matches_events_length(client) -> None:
    """'count' must always equal len('events')."""
    from app.services.paper_sandbox_history import get_paper_sandbox_history

    svc = get_paper_sandbox_history()
    for i in range(5):
        svc.append(
            event_type="human_review_required",
            message=f"Count check {i}",
            source="test",
        )

    body = client.get(ENDPOINT).json()
    assert body["count"] == len(body["events"])


# ---------------------------------------------------------------------------
# 6. Event safety flags locked in response events
# ---------------------------------------------------------------------------


def test_event_safety_flags_locked_in_response(client) -> None:
    """Each event in the response must carry the full safety contract."""
    from app.services.paper_sandbox_history import get_paper_sandbox_history

    svc = get_paper_sandbox_history()
    svc.append(
        event_type="ticket_draft_observed",
        message="Safety flags check fixture",
        source="test",
    )

    body = client.get(ENDPOINT).json()
    event = body["events"][0]

    assert event["paper_only"] is True
    assert event["dry_run"] is True
    assert event["read_only"] is True
    assert event["live_orders_blocked"] is True
    assert event["execution_mode"] == "dry_run_only"
    assert event["requires_human_review"] is True
    assert event["broker_execution_allowed"] is False
    assert event["risk_allowed"] is False


def test_top_level_safety_flags_unchanged_with_events(client) -> None:
    """Top-level history safety flags must not change when events are present."""
    from app.services.paper_sandbox_history import get_paper_sandbox_history

    svc = get_paper_sandbox_history()
    svc.append(
        event_type="sandbox_state_reset",
        message="Top-level flag check fixture",
        source="test",
    )

    body = client.get(ENDPOINT).json()
    assert body["paper_only"] is True
    assert body["dry_run"] is True
    assert body["read_only"] is True
    assert body["live_orders_blocked"] is True
    assert body["execution_mode"] == "dry_run_only"
    assert body["broker_execution_allowed"] is False
    assert body["risk_allowed"] is False
    assert body["requires_human_review"] is True


# ---------------------------------------------------------------------------
# 7. Event metadata remains sanitized in endpoint response
# ---------------------------------------------------------------------------


def test_forbidden_metadata_key_sanitized_in_response(client) -> None:
    """Forbidden metadata keys must be absent from event metadata in response."""
    from app.services.paper_sandbox_history import get_paper_sandbox_history

    svc = get_paper_sandbox_history()
    svc.append(
        event_type="sandbox_preview_requested",
        message="Metadata sanitization check",
        source="test",
        metadata={
            "symbol": "EURUSD",
            "account_id": "SHOULD_BE_DROPPED",
            "order_id": "SHOULD_BE_DROPPED",
            "secret": "SHOULD_BE_DROPPED",
            "token": "SHOULD_BE_DROPPED",
            "api_key": "SHOULD_BE_DROPPED",
        },
    )

    body = client.get(ENDPOINT).json()
    event = body["events"][0]
    meta = event.get("metadata", {})

    assert "account_id" not in meta
    assert "order_id" not in meta
    assert "secret" not in meta
    assert "token" not in meta
    assert "api_key" not in meta
    assert meta.get("symbol") == "EURUSD"


def test_non_finite_metadata_values_absent_in_response(client) -> None:
    """Non-finite float metadata values must be absent from event in response."""
    import math
    from app.services.paper_sandbox_history import get_paper_sandbox_history

    svc = get_paper_sandbox_history()
    svc.append(
        event_type="safety_flags_checked",
        message="Non-finite float check",
        source="test",
        metadata={
            "valid_value": 1.5,
            "nan_value": float("nan"),
            "inf_value": float("inf"),
        },
    )

    body = client.get(ENDPOINT).json()
    meta = body["events"][0].get("metadata", {})

    assert meta.get("valid_value") == pytest.approx(1.5)
    assert "nan_value" not in meta
    assert "inf_value" not in meta


# ---------------------------------------------------------------------------
# 8. Method restriction — POST/PUT/PATCH/DELETE must not succeed
# ---------------------------------------------------------------------------


def test_post_to_history_returns_405(client) -> None:
    """POST to the history endpoint must return 405 Method Not Allowed."""
    response = client.post(ENDPOINT, json={})
    assert response.status_code == 405, (
        f"Expected 405 for POST, got {response.status_code}"
    )


def test_put_to_history_returns_405(client) -> None:
    """PUT to the history endpoint must return 405 Method Not Allowed."""
    response = client.put(ENDPOINT, json={})
    assert response.status_code == 405, (
        f"Expected 405 for PUT, got {response.status_code}"
    )


def test_patch_to_history_returns_405(client) -> None:
    """PATCH to the history endpoint must return 405 Method Not Allowed."""
    response = client.patch(ENDPOINT, json={})
    assert response.status_code == 405, (
        f"Expected PATCH to return 405, got {response.status_code}"
    )


def test_delete_to_history_returns_405(client) -> None:
    """DELETE to the history endpoint must return 405 Method Not Allowed."""
    response = client.delete(ENDPOINT)
    assert response.status_code == 405, (
        f"Expected DELETE to return 405, got {response.status_code}"
    )


# ---------------------------------------------------------------------------
# 9. OpenAPI schema checks
# ---------------------------------------------------------------------------


def test_openapi_schema_includes_history_path(client) -> None:
    """The OpenAPI schema must list GET /api/paper/sandbox/history."""
    paths = client.app.openapi().get("paths", {})
    assert ENDPOINT in paths, (
        f"Expected {ENDPOINT} in OpenAPI paths; found: {sorted(paths)[:10]}"
    )


def test_history_openapi_path_has_only_get_method(client) -> None:
    """The history path must register only GET — no mutating methods."""
    path_item = client.app.openapi().get("paths", {}).get(ENDPOINT, {})
    assert "get" in path_item, "GET method missing from OpenAPI for history path"
    for method in ("post", "put", "patch", "delete"):
        assert method not in path_item, (
            f"Unexpected method '{method}' registered on history path"
        )


def test_history_openapi_tags_include_paper_sandbox(client) -> None:
    """The history endpoint must be tagged 'paper-sandbox'."""
    path_item = client.app.openapi().get("paths", {}).get(ENDPOINT, {})
    get_op = path_item.get("get", {})
    tags = get_op.get("tags", [])
    assert "paper-sandbox" in tags, (
        f"Expected 'paper-sandbox' tag on history endpoint, got {tags}"
    )


def test_history_openapi_operation_id(client) -> None:
    """The history endpoint must use operation_id='get_paper_sandbox_history'."""
    path_item = client.app.openapi().get("paths", {}).get(ENDPOINT, {})
    op_id = path_item.get("get", {}).get("operationId", "")
    assert op_id == "get_paper_sandbox_history", (
        f"Unexpected operationId: {op_id!r}"
    )


def test_history_openapi_summary_no_execution_language(client) -> None:
    """OpenAPI summary for the history endpoint must not imply execution."""
    path_item = client.app.openapi().get("paths", {}).get(ENDPOINT, {})
    summary: str = path_item.get("get", {}).get("summary", "").lower()
    forbidden_words = ("execut", "order", "buy", "sell", "live", "broker")
    for word in forbidden_words:
        assert word not in summary, (
            f"Execution-implying word '{word}' found in history summary: "
            f"{summary!r}"
        )


# ---------------------------------------------------------------------------
# 10. No broker/MT5/IBKR imports in route module
# ---------------------------------------------------------------------------


def test_route_module_imports_no_broker_modules() -> None:
    """The paper_sandbox route module must not import any broker adapters."""
    import app.api.routes.paper_sandbox as mod

    src = inspect.getsource(mod)
    for forbidden in _FORBIDDEN_BROKER_MODULES:
        assert forbidden not in src, (
            f"Forbidden module reference '{forbidden}' found in route source"
        )


def test_route_module_no_metatrader5() -> None:
    """The route module must have no MetaTrader5 references."""
    import app.api.routes.paper_sandbox as mod

    src = inspect.getsource(mod)
    assert "MetaTrader5" not in src
    assert "mt5." not in src


# ---------------------------------------------------------------------------
# 11. Policy invariance — endpoint must not mutate safety config
# ---------------------------------------------------------------------------


def test_history_does_not_mutate_config_json(client) -> None:
    """Calling the history endpoint must not change config.json."""
    import json
    from pathlib import Path

    config_path = Path("config.json")
    config_before = json.loads(config_path.read_text())

    client.get(ENDPOINT)

    config_after = json.loads(config_path.read_text())
    assert config_before == config_after, (
        "config.json was mutated by a GET to the history endpoint"
    )


def test_config_autotrade_still_disabled_after_history_call(client) -> None:
    """autotrade.enabled must remain false after calling the history endpoint."""
    import json
    from pathlib import Path

    client.get(ENDPOINT)

    config = json.loads(Path("config.json").read_text())
    assert config["autotrade"]["enabled"] is False
    assert config["autotrade"]["dry_run"] is True


# ---------------------------------------------------------------------------
# 12. Response suitable for PAPER-002C frontend read-only panel
# ---------------------------------------------------------------------------


def test_history_response_has_events_key(client) -> None:
    """Response must contain an 'events' key for the frontend panel."""
    assert "events" in client.get(ENDPOINT).json()


def test_history_response_has_count_key(client) -> None:
    """Response must contain a 'count' key for the frontend panel."""
    assert "count" in client.get(ENDPOINT).json()


def test_history_response_serializable_for_frontend(client) -> None:
    """Response must be a plain JSON dict — suitable for frontend consumption."""
    import json

    from app.services.paper_sandbox_history import get_paper_sandbox_history

    svc = get_paper_sandbox_history()
    svc.append(
        event_type="degraded_fallback_used",
        message="Serialization check",
        source="test",
        metadata={"note": "round-trip test"},
    )

    response = client.get(ENDPOINT)
    assert response.status_code == 200
    body = response.json()
    re_serialised = json.loads(json.dumps(body))
    assert body == re_serialised


def test_history_response_event_has_expected_keys(client) -> None:
    """Each event in the response must carry all expected display fields."""
    from app.services.paper_sandbox_history import get_paper_sandbox_history

    svc = get_paper_sandbox_history()
    svc.append(
        event_type="human_review_required",
        message="Field key check",
        source="test_panel",
        severity="warning",
    )

    body = client.get(ENDPOINT).json()
    event = body["events"][0]

    for key in ("event_id", "timestamp", "event_type", "source", "severity", "message"):
        assert key in event, f"Expected field '{key}' missing from event"


# ---------------------------------------------------------------------------
# 13. Preview endpoint still works (regression guard)
# ---------------------------------------------------------------------------


def test_preview_endpoint_still_returns_200_after_history_wiring(client) -> None:
    """The preview endpoint must not be broken by adding the history endpoint."""
    response = client.get("/api/paper/sandbox/preview")
    assert response.status_code == 200, (
        f"Preview endpoint broke after history wiring: {response.status_code}"
    )


def test_preview_safety_flags_unchanged_after_history_wiring(client) -> None:
    """Preview endpoint safety flags must remain correct after history wiring."""
    body = client.get("/api/paper/sandbox/preview").json()
    assert body["paper_only"] is True
    assert body["dry_run"] is True
    assert body["read_only"] is True
    assert body["live_orders_blocked"] is True
    assert body["execution_mode"] == "dry_run_only"
    assert body["broker_execution_allowed"] is False
    assert body["risk_allowed"] is False
    assert body["requires_human_review"] is True
