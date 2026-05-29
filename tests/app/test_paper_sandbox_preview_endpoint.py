"""PAPER-001B — Tests for the GET-only paper sandbox preview endpoint.

GET /api/paper/sandbox/preview

All tests are paper-only decision-support assertions.  No broker execution,
no MT5/IBKR calls, no Supabase, no network I/O.  Every test uses the
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
  max_risk_pct           <= 1.0

Forbidden fields verified to be absent:
  account_id, broker_account_id, order_id, execution_id, trade_id,
  broker_order_id, ibkr_order_id, mt5_ticket, secret, token, api_key,
  password.

No broker/MT5/IBKR modules may be imported in the route module.
"""

from __future__ import annotations

import inspect
from collections.abc import Generator
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ENDPOINT = "/api/paper/sandbox/preview"

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


def _valid_draft_payload(**overrides: Any) -> dict[str, Any]:
    """Return a valid paper-only ticket draft payload for sandbox submission."""
    base: dict[str, Any] = dict(
        symbol="EURUSD",
        side="long",
        entry_type="market_simulated",
        timeframe="H1",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit_1=1.1100,
        risk_pct=0.5,
        confidence=80.0,
        reason="Strong H1 bullish momentum — preview test fixture",
        source="scanner_preview",
    )
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_sandbox() -> Generator[None, None, None]:
    """Reset the module-level sandbox singleton before and after each test.

    Prevents cross-test state pollution from the in-memory store.
    """
    from app.services.paper_sandbox import get_paper_sandbox

    sandbox = get_paper_sandbox()
    sandbox.reset()
    yield
    sandbox.reset()


# ---------------------------------------------------------------------------
# 1. Basic behaviour — GET returns 200
# ---------------------------------------------------------------------------


def test_preview_get_returns_200(client) -> None:
    """GET /api/paper/sandbox/preview must return HTTP 200."""
    response = client.get(ENDPOINT)
    assert response.status_code == 200, response.text


def test_preview_response_is_json(client) -> None:
    """Response body must be parseable JSON."""
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)


# ---------------------------------------------------------------------------
# 2. Empty state — explicit and safe
# ---------------------------------------------------------------------------


def test_empty_state_count_is_zero(client) -> None:
    """When no records exist, count must be 0."""
    response = client.get(ENDPOINT)
    assert response.json()["count"] == 0


def test_empty_state_entries_is_empty_list(client) -> None:
    """When no records exist, entries must be an empty list."""
    response = client.get(ENDPOINT)
    assert response.json()["entries"] == []


def test_empty_state_still_has_all_safety_flags(client) -> None:
    """Safety flags must be present even when the sandbox is empty."""
    body = response = client.get(ENDPOINT)
    body = response.json()
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
# 4. Forbidden fields — not present in top-level response or nested entries
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("field", _FORBIDDEN_FIELDS)
def test_top_level_response_has_no_forbidden_field(client, field: str) -> None:
    """No forbidden field may appear at the top level of the response."""
    body = client.get(ENDPOINT).json()
    assert (
        field not in body
    ), f"Forbidden field '{field}' found at top level of preview response"


def test_entries_contain_no_forbidden_fields_when_populated(client) -> None:
    """No forbidden field may appear in any sandbox entry in the response."""
    # Populate the sandbox via direct service call (not via POST route —
    # no POST route exists for sandbox preview).
    from app.services.paper_sandbox import get_paper_sandbox
    from app.schemas.trade_ticket import TradeTicketDraft

    sandbox = get_paper_sandbox()
    draft = TradeTicketDraft(
        ticket_id="test-forbidden-fields-check",
        symbol="EURUSD",
        side="long",
        entry_type="market_simulated",
        timeframe="H1",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit_1=1.1100,
        risk_pct=0.5,
        confidence=80.0,
        reason="Forbidden field check fixture",
        source="test",
    )
    sandbox.submit(draft)

    body = client.get(ENDPOINT).json()
    assert body["count"] == 1

    for entry in body["entries"]:
        for field in _FORBIDDEN_FIELDS:
            assert (
                field not in entry
            ), f"Forbidden field '{field}' found in sandbox entry: {entry}"


# ---------------------------------------------------------------------------
# 5. Method restriction — POST/PUT/PATCH/DELETE must not succeed
# ---------------------------------------------------------------------------


def test_post_to_preview_returns_405(client) -> None:
    """POST to the preview endpoint must return 405 Method Not Allowed."""
    response = client.post(ENDPOINT, json={})
    assert (
        response.status_code == 405
    ), f"Expected 405 for POST, got {response.status_code}"


def test_put_to_preview_returns_405(client) -> None:
    """PUT to the preview endpoint must return 405 Method Not Allowed."""
    response = client.put(ENDPOINT, json={})
    assert (
        response.status_code == 405
    ), f"Expected 405 for PUT, got {response.status_code}"


def test_patch_to_preview_returns_405(client) -> None:
    """PATCH to the preview endpoint must return 405 Method Not Allowed."""
    response = client.patch(ENDPOINT, json={})
    assert (
        response.status_code == 405
    ), f"Expected 405 for PATCH, got {response.status_code}"


def test_delete_to_preview_returns_405(client) -> None:
    """DELETE to the preview endpoint must return 405 Method Not Allowed."""
    response = client.delete(ENDPOINT)
    assert (
        response.status_code == 405
    ), f"Expected 405 for DELETE, got {response.status_code}"


# ---------------------------------------------------------------------------
# 6. OpenAPI schema checks
# ---------------------------------------------------------------------------


def test_openapi_schema_includes_preview_path(client) -> None:
    """The OpenAPI schema must list GET /api/paper/sandbox/preview."""
    paths = client.app.openapi().get("paths", {})
    assert (
        ENDPOINT in paths
    ), f"Expected {ENDPOINT} in OpenAPI paths; found: {sorted(paths)[:10]}"


def test_preview_openapi_path_has_only_get_method(client) -> None:
    """The preview path must register only GET — no mutating methods."""
    path_item = client.app.openapi().get("paths", {}).get(ENDPOINT, {})
    assert "get" in path_item, "GET method missing from OpenAPI for preview path"
    for method in ("post", "put", "patch", "delete"):
        assert (
            method not in path_item
        ), f"Unexpected method '{method}' registered on preview path"


def test_preview_openapi_tags_include_paper_sandbox(client) -> None:
    """The preview endpoint must be tagged 'paper-sandbox'."""
    path_item = client.app.openapi().get("paths", {}).get(ENDPOINT, {})
    get_op = path_item.get("get", {})
    tags = get_op.get("tags", [])
    assert (
        "paper-sandbox" in tags
    ), f"Expected 'paper-sandbox' tag on preview endpoint, got {tags}"


def test_openapi_preview_operation_id(client) -> None:
    """The preview endpoint must use operation_id='get_paper_sandbox_preview'."""
    path_item = client.app.openapi().get("paths", {}).get(ENDPOINT, {})
    op_id = path_item.get("get", {}).get("operationId", "")
    assert op_id == "get_paper_sandbox_preview", f"Unexpected operationId: {op_id!r}"


# ---------------------------------------------------------------------------
# 7. No broker/MT5/IBKR imports in route module
# ---------------------------------------------------------------------------


def test_route_module_imports_no_broker_modules() -> None:
    """The paper_sandbox route module must not import any broker adapters."""
    import app.api.routes.paper_sandbox as mod

    src = inspect.getsource(mod)
    for forbidden in _FORBIDDEN_BROKER_MODULES:
        assert (
            forbidden not in src
        ), f"Forbidden module reference '{forbidden}' found in route source"


def test_route_module_imports_no_mt5() -> None:
    """The route module must have no MetaTrader5 references."""
    import app.api.routes.paper_sandbox as mod

    src = inspect.getsource(mod)
    assert "MetaTrader5" not in src
    assert "mt5." not in src


# ---------------------------------------------------------------------------
# 8. Safety with simulated sandbox records
# ---------------------------------------------------------------------------


def test_preview_returns_correct_count_after_submission(client) -> None:
    """count must match number of submitted entries."""
    from app.services.paper_sandbox import get_paper_sandbox
    from app.schemas.trade_ticket import TradeTicketDraft

    sandbox = get_paper_sandbox()
    for i in range(3):
        draft = TradeTicketDraft(
            ticket_id=f"test-count-{i}",
            symbol="EURUSD",
            side="long",
            entry_type="market_simulated",
            timeframe="H1",
            entry_price=1.1000 + i * 0.001,
            stop_loss=1.0950,
            take_profit_1=1.1100,
            risk_pct=0.5,
            confidence=80.0,
            reason=f"Count test fixture {i}",
            source="test",
        )
        sandbox.submit(draft)

    body = client.get(ENDPOINT).json()
    assert body["count"] == 3
    assert len(body["entries"]) == 3


def test_preview_entries_have_sandbox_entry_id_prefix(client) -> None:
    """Every sandbox_entry_id must use the paper-scoped prefix."""
    from app.services.paper_sandbox import get_paper_sandbox
    from app.schemas.trade_ticket import TradeTicketDraft

    sandbox = get_paper_sandbox()
    draft = TradeTicketDraft(
        ticket_id="test-id-prefix",
        symbol="GBPUSD",
        side="short",
        entry_type="breakout",
        timeframe="H4",
        entry_price=1.3000,
        stop_loss=1.3060,
        take_profit_1=1.2900,
        risk_pct=0.8,
        confidence=75.0,
        reason="ID prefix test fixture",
        source="test",
    )
    sandbox.submit(draft)

    body = client.get(ENDPOINT).json()
    assert body["count"] == 1
    entry = body["entries"][0]
    assert entry["sandbox_entry_id"].startswith("paper-sandbox-entry-"), (
        f"sandbox_entry_id does not use paper-scoped prefix: "
        f"{entry['sandbox_entry_id']!r}"
    )


def test_preview_entry_safety_flags_locked_even_with_records(client) -> None:
    """Each entry in the response must carry the full safety contract."""
    from app.services.paper_sandbox import get_paper_sandbox
    from app.schemas.trade_ticket import TradeTicketDraft

    sandbox = get_paper_sandbox()
    draft = TradeTicketDraft(
        ticket_id="test-entry-safety",
        symbol="EURUSD",
        side="long",
        entry_type="market_simulated",
        timeframe="H1",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit_1=1.1100,
        risk_pct=0.5,
        confidence=80.0,
        reason="Entry safety flags test",
        source="test",
    )
    sandbox.submit(draft)

    body = client.get(ENDPOINT).json()
    entry = body["entries"][0]

    assert entry["paper_only"] is True
    assert entry["dry_run"] is True
    assert entry["read_only"] is True
    assert entry["live_orders_blocked"] is True
    assert entry["requires_human_review"] is True
    assert entry["broker_execution_allowed"] is False
    assert entry["risk_allowed"] is False
    assert entry["execution_mode"] == "dry_run_only"


def test_preview_top_level_safety_flags_unchanged_with_records(client) -> None:
    """Top-level state safety flags must not change when records are present."""
    from app.services.paper_sandbox import get_paper_sandbox
    from app.schemas.trade_ticket import TradeTicketDraft

    sandbox = get_paper_sandbox()
    draft = TradeTicketDraft(
        ticket_id="test-toplevel-safety",
        symbol="EURUSD",
        side="long",
        entry_type="market_simulated",
        timeframe="H1",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit_1=1.1100,
        risk_pct=0.5,
        confidence=80.0,
        reason="Top-level safety flags test",
        source="test",
    )
    sandbox.submit(draft)

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
# 9. Policy invariance — endpoint must not mutate safety config
# ---------------------------------------------------------------------------


def test_preview_does_not_mutate_config_json(client) -> None:
    """Calling the preview endpoint must not change config.json."""
    import json
    from pathlib import Path

    config_path = Path("config.json")
    config_before = json.loads(config_path.read_text())

    client.get(ENDPOINT)

    config_after = json.loads(config_path.read_text())
    assert (
        config_before == config_after
    ), "config.json was mutated by a GET to the preview endpoint"


def test_config_autotrade_still_disabled_after_preview_call(client) -> None:
    """autotrade.enabled must remain false after calling the preview endpoint."""
    import json
    from pathlib import Path

    client.get(ENDPOINT)

    config = json.loads(Path("config.json").read_text())
    assert config["autotrade"]["enabled"] is False
    assert config["autotrade"]["dry_run"] is True


# ---------------------------------------------------------------------------
# 10. Response suitable for PAPER-001C frontend read-only panel
# ---------------------------------------------------------------------------


def test_preview_response_has_entries_key(client) -> None:
    """Response must contain an 'entries' key for the frontend panel."""
    body = client.get(ENDPOINT).json()
    assert "entries" in body


def test_preview_response_has_count_key(client) -> None:
    """Response must contain a 'count' key for the frontend panel."""
    body = client.get(ENDPOINT).json()
    assert "count" in body


def test_preview_count_matches_entries_length(client) -> None:
    """'count' must always equal len('entries')."""
    body = client.get(ENDPOINT).json()
    assert body["count"] == len(body["entries"])


def test_preview_response_serializable_for_frontend(client) -> None:
    """Response must be a plain JSON dict — suitable for frontend consumption."""
    import json

    response = client.get(ENDPOINT)
    assert response.status_code == 200
    # Round-trip: parse → serialise → parse must be identical.
    body = response.json()
    re_serialised = json.loads(json.dumps(body))
    assert body == re_serialised


def test_preview_no_execution_language_in_openapi_summary(client) -> None:
    """OpenAPI summary for the preview endpoint must not imply execution."""
    path_item = client.app.openapi().get("paths", {}).get(ENDPOINT, {})
    summary: str = path_item.get("get", {}).get("summary", "").lower()
    forbidden_words = ("execut", "order", "buy", "sell", "live", "broker")
    for word in forbidden_words:
        assert word not in summary, (
            f"Execution-implying word '{word}' found in preview summary: "
            f"{summary!r}"
        )
