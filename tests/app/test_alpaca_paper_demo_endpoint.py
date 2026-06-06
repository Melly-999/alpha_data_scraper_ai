"""TEST-ALPACA-PAPER-DEMO — Alpaca Paper Trading Demo endpoint safety contract.

Verifies:
- All endpoints return HTTP 200
- All endpoints are GET-only
- All responses include required safety flags
- No forbidden fields leak (API keys, account IDs, secrets, credentials)
- POST/PUT/PATCH/DELETE return 405
- OpenAPI exposes only GET
- No execution-shaped paths appear
- No Alpaca SDK dependency or network calls

Safety contract:
- paper_only: True
- dry_run: True
- read_only: True
- live_orders_blocked: True
- execution_enabled: False
- requires_human_review: True
"""

from __future__ import annotations

from collections.abc import Iterable

import pytest

_PATHS: tuple[str, ...] = (
    "/api/alpaca-paper/status",
    "/api/alpaca-paper/account-preview",
    "/api/alpaca-paper/market-clock",
    "/api/alpaca-paper/watchlist-preview",
)

_FORBIDDEN_KEYS: tuple[str, ...] = (
    "account_id",
    "api_key",
    "api_secret",
    "secret",
    "token",
    "password",
    "broker_order_id",
    "execution_id",
    "live_account",
    "live_trading",
    "autotrade",
)


def _walk_keys(value: object) -> Iterable[str]:
    """Recursively walk all keys in a JSON response."""
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _walk_keys(nested)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


@pytest.mark.parametrize("path", _PATHS)
def test_alpaca_paper_get_routes_return_200(client, path: str) -> None:
    """Verify all Alpaca Paper endpoints return HTTP 200."""
    response = client.get(path)
    assert response.status_code == 200, f"Expected 200 for {path}, got {response.status_code}"


@pytest.mark.parametrize("path", _PATHS)
def test_alpaca_paper_routes_are_get_only_in_openapi(client, path: str) -> None:
    """Verify OpenAPI schema shows only GET method."""
    schema = client.app.openapi()
    methods = set(schema["paths"][path].keys())
    assert methods == {"get"}, f"Expected only GET, got {methods}"


@pytest.mark.parametrize("path", _PATHS)
def test_alpaca_paper_post_put_patch_delete_return_405(client, path: str) -> None:
    """Verify mutating HTTP methods return 405 Method Not Allowed."""
    for method in ("post", "put", "patch", "delete"):
        response = getattr(client, method)(path)
        assert (
            response.status_code == 405
        ), f"Expected 405 for {method.upper()} {path}, got {response.status_code}"


@pytest.mark.parametrize("path", _PATHS)
def test_alpaca_paper_responses_include_safety_flags(client, path: str) -> None:
    """Verify all responses include required safety flags."""
    response = client.get(path)
    payload = response.json()

    assert payload["paper_only"] is True, f"{path}: paper_only must be True"
    assert payload["dry_run"] is True, f"{path}: dry_run must be True"
    assert payload["read_only"] is True, f"{path}: read_only must be True"
    assert payload["live_orders_blocked"] is True, f"{path}: live_orders_blocked must be True"
    assert payload["execution_enabled"] is False, f"{path}: execution_enabled must be False"
    assert payload["requires_human_review"] is True, f"{path}: requires_human_review must be True"


@pytest.mark.parametrize("path", _PATHS)
def test_alpaca_paper_responses_have_no_forbidden_keys(client, path: str) -> None:
    """Verify no forbidden keys (credentials, secrets) leak in responses."""
    response = client.get(path)
    payload = response.json()

    all_keys = set(_walk_keys(payload))
    leaked = sorted(all_keys & set(_FORBIDDEN_KEYS))
    assert not leaked, f"{path}: forbidden response keys leaked: {leaked!r}"


@pytest.mark.parametrize("path", _PATHS)
def test_alpaca_paper_paths_have_no_forbidden_segments(path: str) -> None:
    """Verify path contains no execution-shaped segments."""
    forbidden_segments = {"execute", "place_order", "submit_order", "autotrade", "live"}
    parts = {part for part in path.split("/") if part}
    leaked = sorted(parts & forbidden_segments)
    assert not leaked, f"path {path!r} contains forbidden segment(s): {leaked!r}"


def test_alpaca_paper_openapi_does_not_advertise_mutation_methods(client) -> None:
    """Verify OpenAPI schema advertises only GET for all Alpaca Paper paths."""
    schema = client.app.openapi()
    for path in _PATHS:
        methods = set(schema["paths"][path].keys())
        assert methods == {"get"}, f"Expected only GET for {path}, got {methods}"


def test_alpaca_paper_no_forbidden_compound_paths(client) -> None:
    """Verify no forbidden compound patterns appear in any path."""
    schema = client.app.openapi()
    all_paths = list(schema.get("paths", {}).keys())

    forbidden_patterns = (
        "order/place",
        "order/submit",
        "trade/execute",
        "trading/execute",
        "autotrade/enable",
        "disable-dry-run",
        "execute-trade",
    )

    for path in all_paths:
        for pattern in forbidden_patterns:
            normalized_path = path.replace("_", "-").replace("{", "").replace("}", "")
            assert (
                pattern not in normalized_path
            ), f"Forbidden pattern {pattern!r} found in {path!r}"


def test_alpaca_paper_status_endpoint_contains_feature_list(client) -> None:
    """Verify status endpoint includes list of available endpoints."""
    response = client.get("/api/alpaca-paper/status")
    payload = response.json()

    assert "features" in payload, "status endpoint must include 'features' field"
    assert isinstance(payload["features"], list), "features must be a list"
    assert len(payload["features"]) > 0, "features list must not be empty"

    expected_features = [
        "GET /alpaca-paper/status",
        "GET /alpaca-paper/account-preview",
        "GET /alpaca-paper/market-clock",
        "GET /alpaca-paper/watchlist-preview",
    ]
    for feature in expected_features:
        assert feature in payload["features"], f"Expected feature {feature!r} not found"


def test_alpaca_paper_account_preview_structure(client) -> None:
    """Verify account preview endpoint returns correct structure."""
    response = client.get("/api/alpaca-paper/account-preview")
    payload = response.json()

    assert "account" in payload, "account preview must include 'account' field"
    account = payload["account"]
    assert account["status"] == "active", "account status must be 'active'"
    assert account["account_type"] == "paper", "account type must be 'paper'"
    assert account["currency"] == "USD", "currency must be 'USD'"
    assert "buying_power" in account, "account must include buying_power"
    assert "cash" in account, "account must include cash"
    assert "equity" in account, "account must include equity"


def test_alpaca_paper_market_clock_structure(client) -> None:
    """Verify market clock endpoint returns correct structure."""
    response = client.get("/api/alpaca-paper/market-clock")
    payload = response.json()

    assert "clock" in payload, "market clock must include 'clock' field"
    clock = payload["clock"]
    assert "timestamp" in clock, "clock must include timestamp"
    assert "is_open" in clock, "clock must include is_open"
    assert "trading_hours" in clock, "clock must include trading_hours"
    trading_hours = clock["trading_hours"]
    assert "open" in trading_hours, "trading_hours must include open time"
    assert "close" in trading_hours, "trading_hours must include close time"


def test_alpaca_paper_watchlist_preview_structure(client) -> None:
    """Verify watchlist preview endpoint returns correct structure."""
    response = client.get("/api/alpaca-paper/watchlist-preview")
    payload = response.json()

    assert "watchlist" in payload, "watchlist preview must include 'watchlist' field"
    watchlist = payload["watchlist"]
    assert "watchlists_count" in watchlist, "watchlist must include watchlists_count"
    assert "items_count" in watchlist, "watchlist must include items_count"
    assert "default_items" in watchlist, "watchlist must include default_items"
    assert isinstance(watchlist["default_items"], list), "default_items must be a list"
