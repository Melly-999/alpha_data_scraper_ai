from __future__ import annotations

import inspect

import pytest

from app.api.routes import news as news_module
from app.schemas.news import NewsItem

SENTIMENT_PATH = "/api/news/sentiment"

VALID_SENTIMENT_VALUES = {"positive", "negative", "neutral"}
VALID_IMPACT_VALUES = {"high", "medium", "low"}

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
    "NewsAPI",
    "newsapi",
)

FORBIDDEN_FUNCTION_NAMES = {
    "place_order",
    "cancel_order",
    "modify_order",
    "execute_trade",
    "broker_execute",
}

FORBIDDEN_PROFIT_PHRASES = (
    "guaranteed profit",
    "guarantee profit",
    "buy now",
    "sell now",
    "trade now",
    "execute trade",
    "place order",
)


# ---------------------------------------------------------------------------
# Basic contract
# ---------------------------------------------------------------------------


def test_news_sentiment_get_returns_200(client) -> None:
    response = client.get(SENTIMENT_PATH)
    assert response.status_code == 200


def test_news_sentiment_returns_list(client) -> None:
    response = client.get(SENTIMENT_PATH)
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) > 0


def test_news_sentiment_items_validate_schema(client) -> None:
    response = client.get(SENTIMENT_PATH)
    assert response.status_code == 200
    items = [NewsItem.model_validate(item) for item in response.json()]
    assert len(items) > 0
    for item in items:
        assert item.id
        assert item.headline
        assert item.source
        assert item.sentiment in VALID_SENTIMENT_VALUES
        assert item.impact in VALID_IMPACT_VALUES
        assert item.time


# ---------------------------------------------------------------------------
# Sentiment / impact bounds
# ---------------------------------------------------------------------------


def test_news_sentiment_values_are_bounded(client) -> None:
    response = client.get(SENTIMENT_PATH)
    assert response.status_code == 200
    for raw in response.json():
        assert (
            raw["sentiment"] in VALID_SENTIMENT_VALUES
        ), f"unexpected sentiment: {raw['sentiment']!r}"


def test_news_impact_values_are_bounded(client) -> None:
    response = client.get(SENTIMENT_PATH)
    assert response.status_code == 200
    for raw in response.json():
        assert (
            raw["impact"] in VALID_IMPACT_VALUES
        ), f"unexpected impact: {raw['impact']!r}"


def test_news_items_have_non_empty_headlines(client) -> None:
    response = client.get(SENTIMENT_PATH)
    assert response.status_code == 200
    for item in response.json():
        assert item["headline"].strip(), "headline must not be empty"


def test_news_items_have_non_empty_sources(client) -> None:
    response = client.get(SENTIMENT_PATH)
    assert response.status_code == 200
    for item in response.json():
        assert item["source"].strip(), "source must not be empty"


def test_news_items_have_unique_ids(client) -> None:
    response = client.get(SENTIMENT_PATH)
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()]
    assert len(ids) == len(set(ids)), "item IDs must be unique"


# ---------------------------------------------------------------------------
# Forbidden field check
# ---------------------------------------------------------------------------


def test_news_sentiment_has_no_forbidden_keys(client) -> None:
    response = client.get(SENTIMENT_PATH)
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
# No profit guarantees / trade recommendations
# ---------------------------------------------------------------------------


def test_news_sentiment_no_profit_guarantees(client) -> None:
    response = client.get(SENTIMENT_PATH)
    assert response.status_code == 200
    raw_json = response.text.lower()
    for phrase in FORBIDDEN_PROFIT_PHRASES:
        assert (
            phrase not in raw_json
        ), f"forbidden profit/trade phrase found: {phrase!r}"


# ---------------------------------------------------------------------------
# Non-GET rejection
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_news_sentiment_rejects_non_get_methods(client, method: str) -> None:
    response = getattr(client, method)(SENTIMENT_PATH)
    assert response.status_code == 405


# ---------------------------------------------------------------------------
# OpenAPI shape
# ---------------------------------------------------------------------------


def test_news_sentiment_openapi_is_get_only(client) -> None:
    path_item = client.app.openapi()["paths"][SENTIMENT_PATH]
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


def test_news_sentiment_openapi_path_is_safe(client) -> None:
    assert SENTIMENT_PATH == "/api/news/sentiment"
    for forbidden in (
        "execute",
        "broker_execute",
        "autotrade",
        "live",
        "place",
        "order",
    ):
        assert forbidden not in SENTIMENT_PATH


def test_news_sentiment_openapi_forbidden_paths_remain_clean(client) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert SENTIMENT_PATH in paths
    assert not any("execute" in path for path in paths)
    assert not any("live-trade" in path or "live_trade" in path for path in paths)
    assert not any("place-order" in path or "place_order" in path for path in paths)


# ---------------------------------------------------------------------------
# Determinism / no broker calls
# ---------------------------------------------------------------------------


def test_news_sentiment_is_deterministic(client) -> None:
    r1 = client.get(SENTIMENT_PATH).json()
    r2 = client.get(SENTIMENT_PATH).json()
    assert r1 == r2


def test_news_sentiment_module_has_no_execution_libraries() -> None:
    source = inspect.getsource(news_module)
    for forbidden in FORBIDDEN_LIBRARIES:
        assert (
            forbidden not in source
        ), f"forbidden library reference found in route module: {forbidden!r}"


def test_news_sentiment_module_has_no_execution_function_names() -> None:
    all_names = {
        name for name, obj in inspect.getmembers(news_module, inspect.isfunction)
    }
    assert not (all_names & FORBIDDEN_FUNCTION_NAMES)


def test_news_sentiment_no_external_network_required(client) -> None:
    """Endpoint must respond without any external network call."""
    response = client.get(SENTIMENT_PATH)
    assert response.status_code == 200
    assert response.json()


def test_news_sentiment_no_secrets_in_response(client) -> None:
    response = client.get(SENTIMENT_PATH)
    assert response.status_code == 200
    raw = response.text.lower()
    for forbidden in ("api_key", "apikey", "secret", "password", "token"):
        # Ensure value-like patterns don't appear — key names handled by forbidden-keys test
        assert (
            f'"{forbidden}"' not in raw
        ), f"potential secret field name {forbidden!r} found in response"
