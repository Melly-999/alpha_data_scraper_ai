"""PAPER-RUN-API-001 — Tests for GET /api/paper/run/preview.

Verifies:
  1. Happy path — BUY and SELL allowed responses with correct structure.
  2. Blocked responses — invalid geometry, risk cap exceeded.
  3. Method restriction — POST/PUT/PATCH/DELETE return 405.
  4. Safety flags — always present in top-level response and all nested objects.
  5. Forbidden fields — absent from every level of the response.
  6. OpenAPI checks — path registered, GET-only, correct tag, operation_id.
  7. No broker/MT5/IBKR imports in route or service modules.
  8. config.json not mutated by GET calls.
  9. Blocked responses are HTTP 200 (not 4xx/5xx).
 10. Response shape matches the frontend TypeScript contract.

Safety contract verified by every test group:
  paper_only             = True
  dry_run                = True
  read_only              = True
  live_orders_blocked    = True
  requires_human_review  = True
  execution_enabled      = False

Forbidden fields verified to be absent:
  account_id, broker_account_id, order_id, execution_id, trade_id,
  broker_order_id, ibkr_order_id, mt5_ticket, secret, token, api_key,
  password.

No broker/MT5/IBKR modules may be imported in the route or service module.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENDPOINT = "/api/paper/run/preview"

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

_SAFETY_FLAGS: dict[str, Any] = {
    "paper_only": True,
    "dry_run": True,
    "read_only": True,
    "live_orders_blocked": True,
    "requires_human_review": True,
    "execution_enabled": False,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _buy_params(**overrides: Any) -> dict[str, Any]:
    """Return valid BUY query params (stop_loss < entry_price < take_profit)."""
    base: dict[str, Any] = dict(
        symbol="EURUSD",
        side="BUY",
        quantity=1.0,
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
        confidence=80.0,
        max_risk_pct=0.5,
    )
    base.update(overrides)
    return base


def _sell_params(**overrides: Any) -> dict[str, Any]:
    """Return valid SELL query params (take_profit < entry_price < stop_loss)."""
    base: dict[str, Any] = dict(
        symbol="GBPUSD",
        side="SELL",
        quantity=1.0,
        entry_price=1.3000,
        stop_loss=1.3060,
        take_profit=1.2900,
        confidence=75.0,
        max_risk_pct=0.5,
    )
    base.update(overrides)
    return base


def _assert_safety_flags(obj: dict[str, Any], context: str = "") -> None:
    """Assert all six safety flags are present and correct in obj."""
    label = f" [{context}]" if context else ""
    for flag, expected in _SAFETY_FLAGS.items():
        assert flag in obj, f"Safety flag '{flag}' missing{label}"
        assert obj[flag] == expected, (
            f"Safety flag '{flag}' expected {expected!r}, " f"got {obj[flag]!r}{label}"
        )


def _assert_no_forbidden_fields(obj: dict[str, Any], context: str = "") -> None:
    """Assert no forbidden field is present in obj (flat check)."""
    label = f" [{context}]" if context else ""
    for field in _FORBIDDEN_FIELDS:
        assert (
            field not in obj
        ), f"Forbidden field '{field}' found in response{label}: {obj}"


# ---------------------------------------------------------------------------
# 1. Happy path — BUY (allowed)
# ---------------------------------------------------------------------------


def test_buy_allowed_returns_200(client) -> None:
    """Valid BUY geometry must return HTTP 200."""
    response = client.get(ENDPOINT, params=_buy_params())
    assert response.status_code == 200, response.text


def test_buy_allowed_response_is_json(client) -> None:
    """Response must be parseable JSON."""
    response = client.get(ENDPOINT, params=_buy_params())
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)


def test_buy_allowed_is_true(client) -> None:
    """Valid BUY must return allowed=true."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["allowed"] is True


def test_buy_allowed_reason_is_non_empty(client) -> None:
    """allowed response must include a non-empty reason string."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert isinstance(body["reason"], str)
    assert len(body["reason"]) > 0


def test_buy_allowed_paper_run_is_not_null(client) -> None:
    """When allowed=true, paper_run must not be null."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["paper_run"] is not None


def test_buy_paper_run_has_exactly_one_order(client) -> None:
    """Paper run must contain exactly one order for a single-signal preview."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert len(body["paper_run"]["orders"]) == 1


def test_buy_paper_run_has_exactly_one_fill(client) -> None:
    """Paper run must contain exactly one fill."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert len(body["paper_run"]["fills"]) == 1


def test_buy_paper_run_has_exactly_one_position(client) -> None:
    """Paper run must contain exactly one position."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert len(body["paper_run"]["positions"]) == 1


def test_buy_order_direction_is_buy(client) -> None:
    """Order direction must match the requested side."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["paper_run"]["orders"][0]["direction"] == "BUY"


def test_buy_fill_direction_is_buy(client) -> None:
    """Fill direction must match the requested side."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["paper_run"]["fills"][0]["direction"] == "BUY"


def test_buy_position_direction_is_buy(client) -> None:
    """Position direction must match the requested side."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["paper_run"]["positions"][0]["direction"] == "BUY"


def test_buy_paper_ids_use_paper_prefix(client) -> None:
    """All IDs must use paper-scoped prefixes (no broker/execution IDs)."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    run = body["paper_run"]
    assert run["run_id"].startswith("paper-run-preview-")
    assert run["orders"][0]["paper_order_id"].startswith("paper-order-")
    assert run["fills"][0]["paper_fill_id"].startswith("paper-fill-")
    assert run["positions"][0]["paper_position_id"].startswith("paper-pos-")


def test_buy_fill_refs_order_id(client) -> None:
    """Fill's paper_order_ref must match the order's paper_order_id."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    run = body["paper_run"]
    assert run["fills"][0]["paper_order_ref"] == run["orders"][0]["paper_order_id"]


def test_buy_position_refs_order_id(client) -> None:
    """Position's paper_order_ref must match the order's paper_order_id."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    run = body["paper_run"]
    assert run["positions"][0]["paper_order_ref"] == run["orders"][0]["paper_order_id"]


def test_buy_symbol_echoed_in_order(client) -> None:
    """Order symbol must match the requested symbol."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["paper_run"]["orders"][0]["symbol"] == "EURUSD"


def test_buy_run_accepted_signals_is_one(client) -> None:
    """Paper run accepted_signals must be 1 for a single accepted preview."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["paper_run"]["accepted_signals"] == 1


def test_buy_run_rejected_signals_is_zero(client) -> None:
    """Paper run rejected_signals must be 0 when the preview is allowed."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["paper_run"]["rejected_signals"] == 0


def test_buy_position_status_is_open(client) -> None:
    """Position status must be 'open' in the preview."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["paper_run"]["positions"][0]["status"] == "open"


# ---------------------------------------------------------------------------
# 2. Happy path — SELL (allowed)
# ---------------------------------------------------------------------------


def test_sell_allowed_returns_200(client) -> None:
    """Valid SELL geometry must return HTTP 200."""
    response = client.get(ENDPOINT, params=_sell_params())
    assert response.status_code == 200, response.text


def test_sell_allowed_is_true(client) -> None:
    """Valid SELL must return allowed=true."""
    body = client.get(ENDPOINT, params=_sell_params()).json()
    assert body["allowed"] is True


def test_sell_paper_run_is_not_null(client) -> None:
    """When SELL is allowed, paper_run must not be null."""
    body = client.get(ENDPOINT, params=_sell_params()).json()
    assert body["paper_run"] is not None


def test_sell_order_direction_is_sell(client) -> None:
    """Order direction must be SELL for a sell preview."""
    body = client.get(ENDPOINT, params=_sell_params()).json()
    assert body["paper_run"]["orders"][0]["direction"] == "SELL"


def test_sell_position_direction_is_sell(client) -> None:
    """Position direction must be SELL for a sell preview."""
    body = client.get(ENDPOINT, params=_sell_params()).json()
    assert body["paper_run"]["positions"][0]["direction"] == "SELL"


# ---------------------------------------------------------------------------
# 3. Blocked — BUY invalid geometry (stop_loss >= entry_price)
# ---------------------------------------------------------------------------


def test_buy_invalid_geometry_stop_above_entry_returns_200(client) -> None:
    """Invalid BUY geometry must return HTTP 200 (not 4xx/5xx)."""
    params = _buy_params(stop_loss=1.1050, entry_price=1.1000, take_profit=1.1100)
    response = client.get(ENDPOINT, params=params)
    assert response.status_code == 200, response.text


def test_buy_invalid_geometry_stop_above_entry_is_blocked(client) -> None:
    """stop_loss >= entry_price on BUY must return allowed=false."""
    params = _buy_params(stop_loss=1.1050, entry_price=1.1000, take_profit=1.1100)
    body = client.get(ENDPOINT, params=params).json()
    assert body["allowed"] is False


def test_buy_invalid_geometry_paper_run_is_null(client) -> None:
    """Blocked BUY must return paper_run=null."""
    params = _buy_params(stop_loss=1.1050, entry_price=1.1000, take_profit=1.1100)
    body = client.get(ENDPOINT, params=params).json()
    assert body["paper_run"] is None


def test_buy_invalid_geometry_take_below_entry_is_blocked(client) -> None:
    """take_profit <= entry_price on BUY must also return allowed=false."""
    params = _buy_params(stop_loss=1.0950, entry_price=1.1000, take_profit=1.0980)
    body = client.get(ENDPOINT, params=params).json()
    assert body["allowed"] is False


def test_buy_blocked_reason_is_non_empty(client) -> None:
    """Blocked response must include a non-empty reason."""
    params = _buy_params(stop_loss=1.1050, entry_price=1.1000, take_profit=1.1100)
    body = client.get(ENDPOINT, params=params).json()
    assert isinstance(body["reason"], str)
    assert len(body["reason"]) > 0


# ---------------------------------------------------------------------------
# 4. Blocked — SELL invalid geometry (stop_loss <= entry_price)
# ---------------------------------------------------------------------------


def test_sell_invalid_geometry_returns_200(client) -> None:
    """Invalid SELL geometry must return HTTP 200 (not 4xx/5xx)."""
    # stop_loss below entry_price is wrong for a short
    params = _sell_params(stop_loss=1.2950, entry_price=1.3000, take_profit=1.2900)
    response = client.get(ENDPOINT, params=params)
    assert response.status_code == 200, response.text


def test_sell_invalid_geometry_is_blocked(client) -> None:
    """stop_loss <= entry_price on SELL must return allowed=false."""
    params = _sell_params(stop_loss=1.2950, entry_price=1.3000, take_profit=1.2900)
    body = client.get(ENDPOINT, params=params).json()
    assert body["allowed"] is False


def test_sell_invalid_geometry_paper_run_is_null(client) -> None:
    """Blocked SELL must return paper_run=null."""
    params = _sell_params(stop_loss=1.2950, entry_price=1.3000, take_profit=1.2900)
    body = client.get(ENDPOINT, params=params).json()
    assert body["paper_run"] is None


# ---------------------------------------------------------------------------
# 5. Blocked — max_risk_pct exceeds 1.0
# ---------------------------------------------------------------------------


def test_risk_cap_exceeded_returns_200(client) -> None:
    """max_risk_pct > 1.0 must return HTTP 200 (blocked, not 4xx/5xx)."""
    params = _buy_params(max_risk_pct=1.5)
    response = client.get(ENDPOINT, params=params)
    assert response.status_code == 200, response.text


def test_risk_cap_exceeded_is_blocked(client) -> None:
    """max_risk_pct > 1.0 must return allowed=false."""
    params = _buy_params(max_risk_pct=1.5)
    body = client.get(ENDPOINT, params=params).json()
    assert body["allowed"] is False


def test_risk_cap_exceeded_paper_run_is_null(client) -> None:
    """Blocked risk response must have paper_run=null."""
    params = _buy_params(max_risk_pct=1.5)
    body = client.get(ENDPOINT, params=params).json()
    assert body["paper_run"] is None


def test_risk_cap_exactly_one_is_allowed(client) -> None:
    """max_risk_pct == 1.0 must be allowed (boundary: <= 1.0)."""
    params = _buy_params(max_risk_pct=1.0)
    body = client.get(ENDPOINT, params=params).json()
    assert body["allowed"] is True


# ---------------------------------------------------------------------------
# 6. Safety flags — always present in top-level and nested objects
# ---------------------------------------------------------------------------


def test_top_level_safety_flags_present_allowed(client) -> None:
    """All six safety flags must be present and correct on allowed response."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    _assert_safety_flags(body, "top-level allowed")


def test_top_level_safety_flags_present_blocked(client) -> None:
    """All six safety flags must be present and correct on blocked response."""
    params = _buy_params(stop_loss=1.1050, entry_price=1.1000, take_profit=1.1100)
    body = client.get(ENDPOINT, params=params).json()
    _assert_safety_flags(body, "top-level blocked")


def test_paper_run_safety_flags_present(client) -> None:
    """Safety flags must be present on the paper_run object."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    _assert_safety_flags(body["paper_run"], "paper_run")


def test_order_safety_flags_present(client) -> None:
    """Safety flags must be present on each order object."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    _assert_safety_flags(body["paper_run"]["orders"][0], "order")


def test_fill_safety_flags_present(client) -> None:
    """Safety flags must be present on each fill object."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    _assert_safety_flags(body["paper_run"]["fills"][0], "fill")


def test_position_safety_flags_present(client) -> None:
    """Safety flags must be present on each position object."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    _assert_safety_flags(body["paper_run"]["positions"][0], "position")


@pytest.mark.parametrize("flag", list(_SAFETY_FLAGS.keys()))
def test_each_safety_flag_individually_on_top_level(client, flag: str) -> None:
    """Each safety flag is verified individually at the top level."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert (
        body[flag] == _SAFETY_FLAGS[flag]
    ), f"Flag '{flag}': expected {_SAFETY_FLAGS[flag]!r}, got {body[flag]!r}"


# ---------------------------------------------------------------------------
# 7. Forbidden fields — absent from every response level
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("field", _FORBIDDEN_FIELDS)
def test_top_level_has_no_forbidden_field(client, field: str) -> None:
    """No forbidden field may appear at the top level of the response."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert (
        field not in body
    ), f"Forbidden field '{field}' found at top level of preview response"


def test_paper_run_has_no_forbidden_fields(client) -> None:
    """No forbidden field may appear in the paper_run object."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    _assert_no_forbidden_fields(body["paper_run"], "paper_run")


def test_order_has_no_forbidden_fields(client) -> None:
    """No forbidden field may appear in any order object."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    for order in body["paper_run"]["orders"]:
        _assert_no_forbidden_fields(order, "order")


def test_fill_has_no_forbidden_fields(client) -> None:
    """No forbidden field may appear in any fill object."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    for fill in body["paper_run"]["fills"]:
        _assert_no_forbidden_fields(fill, "fill")


def test_position_has_no_forbidden_fields(client) -> None:
    """No forbidden field may appear in any position object."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    for position in body["paper_run"]["positions"]:
        _assert_no_forbidden_fields(position, "position")


def test_blocked_response_has_no_forbidden_fields(client) -> None:
    """No forbidden field may appear in a blocked response."""
    params = _buy_params(stop_loss=1.1050, entry_price=1.1000, take_profit=1.1100)
    body = client.get(ENDPOINT, params=params).json()
    _assert_no_forbidden_fields(body, "blocked top-level")


# ---------------------------------------------------------------------------
# 8. Method restriction — only GET is registered
# ---------------------------------------------------------------------------


def test_post_returns_405(client) -> None:
    """POST must return 405 Method Not Allowed."""
    response = client.post(ENDPOINT, json={})
    assert (
        response.status_code == 405
    ), f"Expected 405 for POST, got {response.status_code}"


def test_put_returns_405(client) -> None:
    """PUT must return 405 Method Not Allowed."""
    response = client.put(ENDPOINT, json={})
    assert (
        response.status_code == 405
    ), f"Expected 405 for PUT, got {response.status_code}"


def test_patch_returns_405(client) -> None:
    """PATCH must return 405 Method Not Allowed."""
    response = client.patch(ENDPOINT, json={})
    assert (
        response.status_code == 405
    ), f"Expected 405 for PATCH, got {response.status_code}"


def test_delete_returns_405(client) -> None:
    """DELETE must return 405 Method Not Allowed."""
    response = client.delete(ENDPOINT)
    assert (
        response.status_code == 405
    ), f"Expected 405 for DELETE, got {response.status_code}"


# ---------------------------------------------------------------------------
# 9. OpenAPI schema checks
# ---------------------------------------------------------------------------


def test_openapi_schema_includes_preview_path(client) -> None:
    """The OpenAPI schema must list GET /api/paper/run/preview."""
    paths = client.app.openapi().get("paths", {})
    assert ENDPOINT in paths, (
        f"Expected {ENDPOINT!r} in OpenAPI paths; " f"first few: {sorted(paths)[:5]}"
    )


def test_preview_openapi_path_has_only_get_method(client) -> None:
    """The preview path must register only GET — no mutating methods."""
    path_item = client.app.openapi().get("paths", {}).get(ENDPOINT, {})
    assert "get" in path_item, "GET method missing from OpenAPI for preview path"
    for method in ("post", "put", "patch", "delete"):
        assert (
            method not in path_item
        ), f"Unexpected method '{method}' registered on /api/paper/run/preview"


def test_preview_openapi_tags_include_paper_run_preview(client) -> None:
    """The preview endpoint must be tagged 'paper-run-preview'."""
    path_item = client.app.openapi().get("paths", {}).get(ENDPOINT, {})
    tags = path_item.get("get", {}).get("tags", [])
    assert "paper-run-preview" in tags, f"Expected 'paper-run-preview' tag, got {tags}"


def test_preview_openapi_operation_id(client) -> None:
    """The preview endpoint must use operation_id='get_paper_run_preview'."""
    path_item = client.app.openapi().get("paths", {}).get(ENDPOINT, {})
    op_id = path_item.get("get", {}).get("operationId", "")
    assert op_id == "get_paper_run_preview", f"Unexpected operationId: {op_id!r}"


def test_openapi_summary_has_no_execution_language(client) -> None:
    """OpenAPI summary for the preview endpoint must not imply live execution."""
    path_item = client.app.openapi().get("paths", {}).get(ENDPOINT, {})
    summary: str = path_item.get("get", {}).get("summary", "").lower()
    forbidden_words = ("live broker", "live order", "execute trade", "place order")
    for word in forbidden_words:
        assert word not in summary, (
            f"Execution-implying phrase '{word}' found in preview summary: "
            f"{summary!r}"
        )


# ---------------------------------------------------------------------------
# 10. No broker/MT5/IBKR imports in route or service modules
# ---------------------------------------------------------------------------


def test_route_module_imports_no_broker_modules() -> None:
    """The route module must not import any broker adapters."""
    import app.api.routes.paper_run_preview as mod

    src = inspect.getsource(mod)
    for forbidden in _FORBIDDEN_BROKER_MODULES:
        assert (
            forbidden not in src
        ), f"Forbidden module reference '{forbidden}' found in route source"


def test_route_module_imports_no_mt5() -> None:
    """The route module must have no MetaTrader5 references."""
    import app.api.routes.paper_run_preview as mod

    src = inspect.getsource(mod)
    assert "MetaTrader5" not in src
    assert "mt5." not in src


def test_service_module_imports_no_broker_modules() -> None:
    """The service module must not import any broker adapters."""
    import app.services.paper_run_preview_service as mod

    src = inspect.getsource(mod)
    for forbidden in _FORBIDDEN_BROKER_MODULES:
        assert (
            forbidden not in src
        ), f"Forbidden module reference '{forbidden}' found in service source"


def test_service_module_imports_no_mt5() -> None:
    """The service module must have no MetaTrader5 references."""
    import app.services.paper_run_preview_service as mod

    src = inspect.getsource(mod)
    assert "MetaTrader5" not in src
    assert "mt5." not in src


# ---------------------------------------------------------------------------
# 11. config.json not mutated
# ---------------------------------------------------------------------------


def test_allowed_response_does_not_mutate_config_json(client) -> None:
    """Calling the preview endpoint (allowed) must not change config.json."""
    config_path = Path("config.json")
    config_before = json.loads(config_path.read_text())

    client.get(ENDPOINT, params=_buy_params())

    config_after = json.loads(config_path.read_text())
    assert (
        config_before == config_after
    ), "config.json was mutated by a GET to the preview endpoint"


def test_blocked_response_does_not_mutate_config_json(client) -> None:
    """Calling the preview endpoint (blocked) must not change config.json."""
    config_path = Path("config.json")
    config_before = json.loads(config_path.read_text())

    params = _buy_params(stop_loss=1.1050, entry_price=1.1000, take_profit=1.1100)
    client.get(ENDPOINT, params=params)

    config_after = json.loads(config_path.read_text())
    assert (
        config_before == config_after
    ), "config.json was mutated by a blocked GET to the preview endpoint"


def test_config_autotrade_still_disabled_after_preview(client) -> None:
    """autotrade.enabled must remain false after calling the preview endpoint."""
    client.get(ENDPOINT, params=_buy_params())
    config = json.loads(Path("config.json").read_text())
    assert config["autotrade"]["enabled"] is False
    assert config["autotrade"]["dry_run"] is True


# ---------------------------------------------------------------------------
# 12. Response serialisation (suitable for frontend consumption)
# ---------------------------------------------------------------------------


def test_allowed_response_serializable(client) -> None:
    """Allowed response must round-trip through JSON without loss."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body == json.loads(json.dumps(body))


def test_blocked_response_serializable(client) -> None:
    """Blocked response must round-trip through JSON without loss."""
    params = _buy_params(stop_loss=1.1050, entry_price=1.1000, take_profit=1.1100)
    body = client.get(ENDPOINT, params=params).json()
    assert body == json.loads(json.dumps(body))


def test_order_status_is_valid_literal(client) -> None:
    """Order status must be one of the valid literal values."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    valid_statuses = {"pending", "open", "closed", "cancelled", "rejected"}
    for order in body["paper_run"]["orders"]:
        assert (
            order["status"] in valid_statuses
        ), f"Invalid order status: {order['status']!r}"


def test_position_status_is_valid_literal(client) -> None:
    """Position status must be one of the valid literal values."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    valid_statuses = {"open", "closed"}
    for pos in body["paper_run"]["positions"]:
        assert (
            pos["status"] in valid_statuses
        ), f"Invalid position status: {pos['status']!r}"


def test_max_risk_pct_echoed_correctly_in_order(client) -> None:
    """max_risk_pct in the response must match the requested value."""
    body = client.get(ENDPOINT, params=_buy_params(max_risk_pct=0.5)).json()
    assert body["paper_run"]["orders"][0]["max_risk_pct"] == pytest.approx(0.5)


def test_max_risk_pct_echoed_correctly_in_position(client) -> None:
    """max_risk_pct in the position must match the requested value."""
    body = client.get(ENDPOINT, params=_buy_params(max_risk_pct=0.5)).json()
    assert body["paper_run"]["positions"][0]["max_risk_pct"] == pytest.approx(0.5)


def test_run_max_risk_pct_matches_request(client) -> None:
    """Paper run max_risk_pct must match the requested value."""
    body = client.get(ENDPOINT, params=_buy_params(max_risk_pct=0.5)).json()
    assert body["paper_run"]["max_risk_pct"] == pytest.approx(0.5)
