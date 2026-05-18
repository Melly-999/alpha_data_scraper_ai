from __future__ import annotations

from collections.abc import Iterable

import pytest


_PATHS: tuple[str, ...] = (
    "/api/backtest/summary",
    "/api/investment",
    "/api/signals/feed",
)

_FORBIDDEN_KEYS: tuple[str, ...] = (
    "order_id",
    "trade_id",
    "execution_id",
    "account_id",
    "api_key",
    "secret",
    "token",
    "password",
    "broker_execute",
    "place_order",
    "execute_order",
    "cancel_order",
)

_FORBIDDEN_PATH_SEGMENTS: tuple[str, ...] = (
    "order",
    "execute",
    "trade",
    "broker_execute",
    "autotrade",
    "live",
)


def _walk_keys(value: object) -> Iterable[str]:
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _walk_keys(nested)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


@pytest.mark.parametrize("path", _PATHS)
def test_local_demo_get_routes_return_200(client, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.parametrize("path", _PATHS)
def test_local_demo_routes_are_get_only_in_openapi(client, path: str) -> None:
    schema = client.app.openapi()
    methods = set(schema["paths"][path].keys())
    assert methods == {"get"}


@pytest.mark.parametrize("path", _PATHS)
def test_local_demo_post_put_patch_delete_return_405(client, path: str) -> None:
    for method in ("post", "put", "patch", "delete"):
        response = getattr(client, method)(path)
        assert response.status_code == 405


@pytest.mark.parametrize("path", _PATHS)
def test_local_demo_responses_are_safe_and_degraded(client, path: str) -> None:
    response = client.get(path)
    payload = response.json()

    assert payload["read_only"] is True
    assert payload["execution_mode"] == "dry_run_only"
    assert payload["requires_human_review"] is True
    assert payload["degraded"] is True
    assert payload["source"] == "local_demo"
    assert payload["live_orders_blocked"] is True

    if path == "/api/signals/feed":
        assert payload["risk_allowed"] is False
        assert payload["signals"] == []
        assert "investment advice" not in payload["message"].lower()
        assert "guaranteed profit" not in payload["message"].lower()
    elif path == "/api/backtest/summary":
        assert payload["summary"]["status"] == "not_available"
        assert payload["summary"]["runs"] == 0
        assert payload["summary"]["last_run_at"] is None
        assert "investment advice" not in payload["summary"]["message"].lower()
        assert "guaranteed profit" not in payload["summary"]["message"].lower()
    elif path == "/api/investment":
        assert payload["portfolio"]["positions_count"] == 0
        assert payload["portfolio"]["status"] == "not_connected"
        assert "investment advice" not in payload["message"].lower()
        assert "guaranteed profit" not in payload["message"].lower()

    all_keys = set(_walk_keys(payload))
    leaked = sorted(all_keys & set(_FORBIDDEN_KEYS))
    assert not leaked, f"forbidden response keys leaked: {leaked!r}"


@pytest.mark.parametrize("path", _PATHS)
def test_local_demo_paths_have_no_forbidden_segments(path: str) -> None:
    parts = {part for part in path.split("/") if part}
    leaked = sorted(parts & set(_FORBIDDEN_PATH_SEGMENTS))
    assert not leaked, f"path {path!r} contains forbidden segment(s): {leaked!r}"


def test_local_demo_openapi_does_not_advertise_mutation_methods(client) -> None:
    schema = client.app.openapi()
    for path in _PATHS:
        methods = set(schema["paths"][path].keys())
        assert methods == {"get"}
