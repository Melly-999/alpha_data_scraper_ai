from __future__ import annotations

import inspect

import pytest

from app.api.routes import market as market_module
from app.schemas.market import MarketItem

OVERVIEW_PATH = "/api/market/overview"

FORBIDDEN_RESPONSE_KEYS = {
    "order_id",
    "account_id",
    "execution_id",
    "trade_id",
    "place_order",
    "broker_execute",
    "api_key",
    "secret",
    "token",
    "password",
}

FORBIDDEN_LIBRARIES = (
    "ib_insync",
    "ibapi",
    "MetaTrader5",
    "requests",
    "httpx",
    "websockets",
    "alpaca",
    "ccxt",
)

FORBIDDEN_FUNCTION_NAMES = {
    "place_order",
    "cancel_order",
    "modify_order",
    "execute_trade",
    "broker_execute",
}

ADVISORY_SIGNALS = {"BUY", "SELL", "HOLD", "WATCH"}


# ---------------------------------------------------------------------------
# Basic contract
# ---------------------------------------------------------------------------


def test_market_overview_get_returns_200(client) -> None:
    response = client.get(OVERVIEW_PATH)
    assert response.status_code == 200


def test_market_overview_response_is_list(client) -> None:
    response = client.get(OVERVIEW_PATH)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_market_overview_response_validates_schema(client) -> None:
    response = client.get(OVERVIEW_PATH)
    assert response.status_code == 200

    items = response.json()
    assert len(items) > 0
    for raw in items:
        item = MarketItem.model_validate(raw)
        assert item.symbol
        assert item.price > 0
        assert 0 <= item.confidence <= 100
        assert item.signal in ADVISORY_SIGNALS


# ---------------------------------------------------------------------------
# Advisory-only signal labels
# ---------------------------------------------------------------------------


def test_market_overview_signals_are_advisory_labels(client) -> None:
    response = client.get(OVERVIEW_PATH)
    assert response.status_code == 200

    for raw in response.json():
        item = MarketItem.model_validate(raw)
        assert item.signal in ADVISORY_SIGNALS, f"unexpected signal: {item.signal!r}"


def test_market_overview_confidence_within_bounds(client) -> None:
    response = client.get(OVERVIEW_PATH)
    assert response.status_code == 200

    for raw in response.json():
        item = MarketItem.model_validate(raw)
        assert (
            0 <= item.confidence <= 100
        ), f"{item.symbol} confidence {item.confidence} out of range"


def test_market_overview_prices_are_positive(client) -> None:
    response = client.get(OVERVIEW_PATH)
    assert response.status_code == 200

    for raw in response.json():
        item = MarketItem.model_validate(raw)
        assert item.price > 0, f"{item.symbol} price must be positive"


# ---------------------------------------------------------------------------
# Forbidden field check
# ---------------------------------------------------------------------------


def test_market_overview_has_no_forbidden_keys(client) -> None:
    response = client.get(OVERVIEW_PATH)
    assert response.status_code == 200

    payload = response.json()

    def _scan(obj: object) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                assert key not in FORBIDDEN_RESPONSE_KEYS, f"forbidden key: {key!r}"
                _scan(value)
        elif isinstance(obj, list):
            for item in obj:
                _scan(item)

    _scan(payload)


# ---------------------------------------------------------------------------
# Non-GET rejection
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_market_overview_rejects_non_get_methods(client, method: str) -> None:
    response = getattr(client, method)(OVERVIEW_PATH)
    assert response.status_code == 405


# ---------------------------------------------------------------------------
# OpenAPI shape
# ---------------------------------------------------------------------------


def test_market_overview_openapi_is_get_only(client) -> None:
    path_item = client.app.openapi()["paths"][OVERVIEW_PATH]
    operation_keys = {
        key
        for key in path_item
        if key
        in {
            "get",
            "put",
            "post",
            "patch",
            "delete",
            "head",
            "options",
            "trace",
        }
    }
    assert operation_keys == {"get"}


def test_market_overview_openapi_path_is_safe(client) -> None:
    assert OVERVIEW_PATH == "/api/market/overview"
    for forbidden in (
        "order",
        "trade",
        "execute",
        "broker_execute",
        "autotrade",
        "live",
    ):
        assert forbidden not in OVERVIEW_PATH


def test_market_overview_openapi_forbidden_paths_remain_clean(client) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert OVERVIEW_PATH in paths
    assert not any("execute" in path for path in paths)
    assert not any("live-trade" in path or "live_trade" in path for path in paths)
    assert not any("place-order" in path or "place_order" in path for path in paths)


# ---------------------------------------------------------------------------
# Determinism / no broker calls
# ---------------------------------------------------------------------------


def test_market_overview_is_deterministic(client) -> None:
    r1 = client.get(OVERVIEW_PATH).json()
    r2 = client.get(OVERVIEW_PATH).json()
    assert r1 == r2


def test_market_overview_module_has_no_execution_libraries() -> None:
    source = inspect.getsource(market_module)
    for forbidden in FORBIDDEN_LIBRARIES:
        assert forbidden not in source


def test_market_overview_module_has_no_execution_function_names() -> None:
    function_names = {
        name for name, obj in inspect.getmembers(market_module, inspect.isfunction)
    }
    assert not (function_names & FORBIDDEN_FUNCTION_NAMES)
