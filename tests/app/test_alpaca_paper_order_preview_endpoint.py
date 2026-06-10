"""ALPACA-PAPER-ORDER-PREVIEW-003 — Tests for GET /api/alpaca-paper/order-preview.

Verifies:
  1. Happy path — BUY and SELL allowed responses with correct structure.
  2. Blocked responses — invalid geometry, risk cap exceeded.
  3. Method restriction — POST/PUT/PATCH/DELETE return 405.
  4. Safety flags — always present in top-level response and nested order.
  5. Forbidden fields — absent from every level of the response.
  6. OpenAPI checks — path registered, GET-only, correct tag, operation_id.
  7. No broker/MT5/IBKR/Alpaca-SDK imports in route or service modules.
  8. submitted=False always present at top level and nested order.
  9. label="Preview only — not submitted" always present.
 10. broker="alpaca-paper-demo" always present.
 11. paper_order_id starts with "paper-alpaca-".
 12. run_id starts with "paper-alpaca-run-".
 13. Blocked responses are HTTP 200 (not 4xx/5xx).
 14. max_risk_pct > 1.0 returns allowed=false (HTTP 200).

Safety contract verified by every test group:
  paper_only             = True
  dry_run                = True
  read_only              = True
  live_orders_blocked    = True
  requires_human_review  = True
  execution_enabled      = False
  submitted              = False

Forbidden fields verified to be absent:
  account_id, broker_account_id, order_id, execution_id, trade_id,
  broker_order_id, live_account, live_trading, autotrade, api_key,
  secret, token, password.

No broker/MT5/IBKR/Alpaca-SDK modules may be imported in the route or
service module.
"""

from __future__ import annotations

import inspect
import re
from collections.abc import Iterable
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENDPOINT = "/api/alpaca-paper/order-preview"

_FORBIDDEN_FIELDS: tuple[str, ...] = (
    "account_id",
    "broker_account_id",
    "order_id",
    "execution_id",
    "trade_id",
    "broker_order_id",
    "live_account",
    "live_trading",
    "autotrade",
    "api_key",
    "secret",
    "token",
    "password",
)

# Patterns that match live broker SDK import statements only.
# Uses word-boundary regex so "alpaca-paper-demo" string literals
# in docstrings/comments are not flagged.
_FORBIDDEN_IMPORT_PATTERNS: tuple[str, ...] = (
    r"^\s*import\s+MetaTrader5",
    r"^\s*from\s+MetaTrader5",
    r"^\s*import\s+ibapi",
    r"^\s*from\s+ibapi",
    r"^\s*import\s+ib_insync",
    r"^\s*from\s+ib_insync",
    r"^\s*import\s+mt5_trader",
    r"^\s*from\s+mt5_trader",
    r"^\s*import\s+alpaca_trade_api",
    r"^\s*from\s+alpaca_trade_api",
    r"^\s*import\s+alpaca\b",
    r"^\s*from\s+alpaca\b",
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
        symbol="AAPL",
        side="BUY",
        quantity=10.0,
        entry_price=150.00,
        stop_loss=148.00,
        take_profit=155.00,
        max_risk_pct=0.5,
    )
    base.update(overrides)
    return base


def _sell_params(**overrides: Any) -> dict[str, Any]:
    """Return valid SELL query params (take_profit < entry_price < stop_loss)."""
    base: dict[str, Any] = dict(
        symbol="TSLA",
        side="SELL",
        quantity=5.0,
        entry_price=200.00,
        stop_loss=205.00,
        take_profit=192.00,
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


def _walk_keys(value: object) -> Iterable[str]:
    """Recursively yield all keys in a JSON-decoded structure."""
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _walk_keys(nested)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


# ---------------------------------------------------------------------------
# 1. Happy path — BUY (allowed)
# ---------------------------------------------------------------------------


def test_buy_allowed_returns_200(client) -> None:
    """Valid BUY geometry must return HTTP 200."""
    response = client.get(ENDPOINT, params=_buy_params())
    assert response.status_code == 200, response.text


def test_buy_allowed_response_is_json(client) -> None:
    """Response must be parseable JSON."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert isinstance(body, dict)


def test_buy_allowed_is_true(client) -> None:
    """Valid BUY must return allowed=true."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["allowed"] is True


def test_buy_allowed_reason_is_non_empty(client) -> None:
    """Allowed response must include a non-empty reason string."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert isinstance(body["reason"], str)
    assert len(body["reason"]) > 0


def test_buy_allowed_order_is_not_null(client) -> None:
    """When allowed=true, order must not be null."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["order"] is not None


def test_buy_order_direction_is_buy(client) -> None:
    """Order direction must match the requested side."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["order"]["direction"] == "BUY"


def test_buy_order_symbol_matches(client) -> None:
    """Order symbol must match the requested symbol."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["order"]["symbol"] == "AAPL"


def test_buy_order_status_is_preview(client) -> None:
    """Order status must be 'preview'."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["order"]["status"] == "preview"


def test_buy_order_fill_type_is_simulated(client) -> None:
    """Order fill_type must be 'simulated'."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["order"]["fill_type"] == "simulated"


def test_buy_order_broker_is_alpaca_paper_demo(client) -> None:
    """Order broker must be 'alpaca-paper-demo'."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["order"]["broker"] == "alpaca-paper-demo"


def test_buy_order_submitted_is_false(client) -> None:
    """Order submitted must be False."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["order"]["submitted"] is False


def test_buy_order_label_is_preview_only(client) -> None:
    """Order label must be 'Preview only — not submitted'."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["order"]["label"] == "Preview only — not submitted"


def test_buy_order_paper_order_id_prefix(client) -> None:
    """paper_order_id must start with 'paper-alpaca-'."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["order"]["paper_order_id"].startswith("paper-alpaca-")


def test_buy_order_run_id_prefix(client) -> None:
    """run_id must start with 'paper-alpaca-run-'."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["order"]["run_id"].startswith("paper-alpaca-run-")


def test_buy_order_paper_order_id_is_not_broker_format(client) -> None:
    """paper_order_id must not look like a live broker order ID."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    order_id = body["order"]["paper_order_id"]
    assert not order_id.startswith("ord_"), f"Looks like live order ID: {order_id}"
    assert not order_id.startswith("live-"), f"Looks like live order ID: {order_id}"


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


def test_sell_order_direction_is_sell(client) -> None:
    """Order direction must match the requested side."""
    body = client.get(ENDPOINT, params=_sell_params()).json()
    assert body["order"]["direction"] == "SELL"


def test_sell_order_not_null(client) -> None:
    """Valid SELL must return a non-null order."""
    body = client.get(ENDPOINT, params=_sell_params()).json()
    assert body["order"] is not None


# ---------------------------------------------------------------------------
# 3. Blocked — risk cap exceeded
# ---------------------------------------------------------------------------


def test_risk_cap_exceeded_returns_200(client) -> None:
    """max_risk_pct > 1.0 must return HTTP 200 (not 4xx)."""
    response = client.get(ENDPOINT, params=_buy_params(max_risk_pct=1.5))
    assert response.status_code == 200, response.text


def test_risk_cap_exceeded_allowed_is_false(client) -> None:
    """max_risk_pct > 1.0 must return allowed=false."""
    body = client.get(ENDPOINT, params=_buy_params(max_risk_pct=1.5)).json()
    assert body["allowed"] is False


def test_risk_cap_exceeded_order_is_null(client) -> None:
    """Blocked response must have order=null."""
    body = client.get(ENDPOINT, params=_buy_params(max_risk_pct=1.5)).json()
    assert body["order"] is None


def test_risk_cap_exceeded_reason_mentions_risk(client) -> None:
    """Blocked reason must mention max_risk_pct."""
    body = client.get(ENDPOINT, params=_buy_params(max_risk_pct=1.5)).json()
    assert "risk" in body["reason"].lower()


def test_risk_cap_exactly_one_is_allowed(client) -> None:
    """max_risk_pct=1.0 (exactly at cap) must return allowed=true."""
    body = client.get(ENDPOINT, params=_buy_params(max_risk_pct=1.0)).json()
    assert body["allowed"] is True


# ---------------------------------------------------------------------------
# 4. Blocked — BUY invalid geometry
# ---------------------------------------------------------------------------


def test_buy_bad_geometry_allowed_is_false(client) -> None:
    """BUY with stop_loss > entry_price must return allowed=false."""
    body = client.get(
        ENDPOINT,
        params=_buy_params(stop_loss=155.00, take_profit=160.00),
    ).json()
    assert body["allowed"] is False


def test_buy_bad_geometry_returns_200(client) -> None:
    """Invalid geometry must still return HTTP 200."""
    response = client.get(
        ENDPOINT,
        params=_buy_params(stop_loss=155.00, take_profit=160.00),
    )
    assert response.status_code == 200


def test_buy_bad_geometry_order_is_null(client) -> None:
    """Blocked BUY response must have order=null."""
    body = client.get(
        ENDPOINT,
        params=_buy_params(stop_loss=155.00, take_profit=160.00),
    ).json()
    assert body["order"] is None


# ---------------------------------------------------------------------------
# 5. Blocked — SELL invalid geometry
# ---------------------------------------------------------------------------


def test_sell_bad_geometry_allowed_is_false(client) -> None:
    """SELL with take_profit > entry_price must return allowed=false."""
    body = client.get(
        ENDPOINT,
        params=_sell_params(take_profit=210.00),
    ).json()
    assert body["allowed"] is False


def test_sell_bad_geometry_returns_200(client) -> None:
    """Invalid SELL geometry must still return HTTP 200."""
    response = client.get(ENDPOINT, params=_sell_params(take_profit=210.00))
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# 6. Method restriction
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_mutating_methods_return_405(client, method: str) -> None:
    """POST/PUT/PATCH/DELETE must return 405 Method Not Allowed."""
    response = getattr(client, method)(ENDPOINT)
    assert response.status_code == 405, (
        f"Expected 405 for {method.upper()} {ENDPOINT}, " f"got {response.status_code}"
    )


# ---------------------------------------------------------------------------
# 7. Safety flags — top-level response
# ---------------------------------------------------------------------------


def test_buy_response_has_all_safety_flags(client) -> None:
    """All six safety flags must be present in the top-level response."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    _assert_safety_flags(body, context="BUY top-level")


def test_sell_response_has_all_safety_flags(client) -> None:
    """All six safety flags must be present in the top-level response."""
    body = client.get(ENDPOINT, params=_sell_params()).json()
    _assert_safety_flags(body, context="SELL top-level")


def test_blocked_response_has_all_safety_flags(client) -> None:
    """Safety flags must be present even on a blocked response."""
    body = client.get(ENDPOINT, params=_buy_params(max_risk_pct=99.0)).json()
    _assert_safety_flags(body, context="blocked")


# ---------------------------------------------------------------------------
# 8. Safety flags — nested order
# ---------------------------------------------------------------------------


def test_buy_nested_order_has_all_safety_flags(client) -> None:
    """All six safety flags must be present in the nested order."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    _assert_safety_flags(body["order"], context="BUY order")


def test_sell_nested_order_has_all_safety_flags(client) -> None:
    """All six safety flags must be present in the nested order."""
    body = client.get(ENDPOINT, params=_sell_params()).json()
    _assert_safety_flags(body["order"], context="SELL order")


# ---------------------------------------------------------------------------
# 9. submitted / label / broker invariants
# ---------------------------------------------------------------------------


def test_buy_response_submitted_is_false(client) -> None:
    """Top-level submitted must be False."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["submitted"] is False


def test_sell_response_submitted_is_false(client) -> None:
    """Top-level submitted must be False."""
    body = client.get(ENDPOINT, params=_sell_params()).json()
    assert body["submitted"] is False


def test_blocked_response_submitted_is_false(client) -> None:
    """submitted must be False even on a blocked response."""
    body = client.get(ENDPOINT, params=_buy_params(max_risk_pct=99.0)).json()
    assert body["submitted"] is False


def test_buy_response_label(client) -> None:
    """Top-level label must be 'Preview only — not submitted'."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["label"] == "Preview only — not submitted"


def test_blocked_response_label(client) -> None:
    """label must be 'Preview only — not submitted' on blocked response."""
    body = client.get(ENDPOINT, params=_buy_params(max_risk_pct=99.0)).json()
    assert body["label"] == "Preview only — not submitted"


def test_buy_response_broker(client) -> None:
    """Top-level broker must be 'alpaca-paper-demo'."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    assert body["broker"] == "alpaca-paper-demo"


def test_blocked_response_broker(client) -> None:
    """broker must be 'alpaca-paper-demo' on blocked response."""
    body = client.get(ENDPOINT, params=_buy_params(max_risk_pct=99.0)).json()
    assert body["broker"] == "alpaca-paper-demo"


# ---------------------------------------------------------------------------
# 10. Forbidden fields
# ---------------------------------------------------------------------------


def test_buy_response_has_no_forbidden_fields(client) -> None:
    """No forbidden field must appear anywhere in the response."""
    body = client.get(ENDPOINT, params=_buy_params()).json()
    all_keys = set(_walk_keys(body))
    leaked = sorted(all_keys & set(_FORBIDDEN_FIELDS))
    assert not leaked, f"Forbidden fields found in BUY response: {leaked!r}"


def test_sell_response_has_no_forbidden_fields(client) -> None:
    """No forbidden field must appear anywhere in the response."""
    body = client.get(ENDPOINT, params=_sell_params()).json()
    all_keys = set(_walk_keys(body))
    leaked = sorted(all_keys & set(_FORBIDDEN_FIELDS))
    assert not leaked, f"Forbidden fields found in SELL response: {leaked!r}"


def test_blocked_response_has_no_forbidden_fields(client) -> None:
    """No forbidden field must appear in a blocked response."""
    body = client.get(ENDPOINT, params=_buy_params(max_risk_pct=99.0)).json()
    all_keys = set(_walk_keys(body))
    leaked = sorted(all_keys & set(_FORBIDDEN_FIELDS))
    assert not leaked, f"Forbidden fields found in blocked response: {leaked!r}"


# ---------------------------------------------------------------------------
# 11. OpenAPI checks
# ---------------------------------------------------------------------------


def test_endpoint_is_registered_in_openapi(client) -> None:
    """Endpoint must appear in the OpenAPI schema."""
    schema = client.app.openapi()
    assert (
        ENDPOINT in schema["paths"]
    ), f"{ENDPOINT} not found in OpenAPI paths: {list(schema['paths'].keys())}"


def test_endpoint_is_get_only_in_openapi(client) -> None:
    """Only GET method must be advertised in the OpenAPI schema."""
    schema = client.app.openapi()
    methods = set(schema["paths"][ENDPOINT].keys())
    assert methods == {"get"}, f"Expected only GET, got {methods}"


def test_endpoint_has_correct_operation_id(client) -> None:
    """operation_id must be 'get_alpaca_paper_order_preview'."""
    schema = client.app.openapi()
    op_id = schema["paths"][ENDPOINT]["get"].get("operationId")
    assert (
        op_id == "get_alpaca_paper_order_preview"
    ), f"Expected operation_id 'get_alpaca_paper_order_preview', got {op_id!r}"


def test_endpoint_has_alpaca_paper_tag(client) -> None:
    """Endpoint must be tagged 'alpaca-paper'."""
    schema = client.app.openapi()
    tags = schema["paths"][ENDPOINT]["get"].get("tags", [])
    assert "alpaca-paper" in tags, f"Expected 'alpaca-paper' tag, got {tags!r}"


def test_no_execution_shaped_path_in_openapi(client) -> None:
    """No execution-shaped paths must appear in the OpenAPI schema."""
    schema = client.app.openapi()
    forbidden_segments = {
        "execute",
        "place_order",
        "submit_order",
        "autotrade",
        "live",
        "place-order",
        "submit-order",
    }
    for path in schema.get("paths", {}):
        parts = {p for p in path.split("/") if p}
        leaked = sorted(parts & forbidden_segments)
        assert (
            not leaked
        ), f"Forbidden path segment(s) {leaked!r} found in path {path!r}"


# ---------------------------------------------------------------------------
# 12. No broker/Alpaca-SDK imports in source modules
# ---------------------------------------------------------------------------


def _assert_no_broker_imports(source: str, module_label: str) -> None:
    """Assert no live broker SDK import statement appears in source."""
    for pattern in _FORBIDDEN_IMPORT_PATTERNS:
        for line in source.splitlines():
            assert not re.match(pattern, line), (
                f"Forbidden broker import matched by pattern {pattern!r} "
                f"in {module_label}: {line!r}"
            )


def test_route_module_has_no_broker_imports() -> None:
    """Route module must not import any live broker SDK."""
    import app.api.routes.alpaca_paper as route_module

    _assert_no_broker_imports(inspect.getsource(route_module), "route module")


def test_service_module_has_no_broker_imports() -> None:
    """Service module must not import any live broker SDK."""
    import app.services.alpaca_paper_order_preview_service as svc_module

    _assert_no_broker_imports(inspect.getsource(svc_module), "service module")


# ---------------------------------------------------------------------------
# 13. Determinism — same inputs produce same paper_order_id
# ---------------------------------------------------------------------------


def test_buy_paper_order_id_is_deterministic(client) -> None:
    """Same inputs must produce the same paper_order_id."""
    params = _buy_params()
    body1 = client.get(ENDPOINT, params=params).json()
    body2 = client.get(ENDPOINT, params=params).json()
    assert body1["order"]["paper_order_id"] == body2["order"]["paper_order_id"]


def test_different_symbols_produce_different_ids(client) -> None:
    """Different symbols must produce different paper_order_id values."""
    body_aapl = client.get(ENDPOINT, params=_buy_params(symbol="AAPL")).json()
    body_msft = client.get(ENDPOINT, params=_buy_params(symbol="MSFT")).json()
    assert body_aapl["order"]["paper_order_id"] != body_msft["order"]["paper_order_id"]
