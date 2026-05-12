from __future__ import annotations

import inspect

import pytest

from app.api.routes import signals as signals_module
from app.schemas.signal_scanner import SignalScannerBatch


SCANNER_PATH = "/api/signals/scanner/preview"
FORBIDDEN_RESPONSE_KEYS = {
    "order_id",
    "account_id",
    "execution_id",
    "trade_id",
    "credential",
    "secret",
    "token",
    "api_key",
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


def _path_item(client) -> dict:
    schema = client.app.openapi()
    return schema["paths"][SCANNER_PATH]


def test_scanner_preview_get_returns_batch(client) -> None:
    response = client.get(SCANNER_PATH)
    assert response.status_code == 200

    payload = response.json()
    batch = SignalScannerBatch.model_validate(payload)

    assert batch.read_only is True
    assert batch.execution_mode == "dry_run_only"
    assert batch.results
    assert len(batch.results) == 6
    assert [result.symbol for result in batch.results] == [
        "AAPL",
        "NVDA",
        "MSFT",
        "TSLA",
        "EURUSD",
        "XAUUSD",
    ]
    for result in batch.results:
        assert result.risk_allowed is False
        assert result.requires_human_review is True
        assert result.source == "scanner"
        assert result.execution_mode == "dry_run_only"
        assert "order_id" not in result.model_dump()
        assert "account_id" not in result.model_dump()
        assert "execution_id" not in result.model_dump()
        assert "trade_id" not in result.model_dump()
        assert "credential" not in result.model_dump()
        assert "secret" not in result.model_dump()
        assert "token" not in result.model_dump()
        assert "api_key" not in result.model_dump()


@pytest.mark.parametrize(
    "query, expected",
    [
        ("AAPL,NVDA,EURUSD,XAUUSD", ["AAPL", "NVDA", "EURUSD", "XAUUSD"]),
        (" aapl , nvda , , msft ", ["AAPL", "NVDA", "MSFT"]),
    ],
)
def test_scanner_preview_parses_and_normalizes_symbols(
    client, query: str, expected: list[str]
) -> None:
    response = client.get(SCANNER_PATH, params={"symbols": query})
    assert response.status_code == 200

    batch = SignalScannerBatch.model_validate(response.json())
    assert [result.symbol for result in batch.results] == expected


def test_scanner_preview_ignores_blank_symbols(client) -> None:
    response = client.get(SCANNER_PATH, params={"symbols": " , , AAPL, , "})
    assert response.status_code == 200

    batch = SignalScannerBatch.model_validate(response.json())
    assert [result.symbol for result in batch.results] == ["AAPL"]


def test_scanner_preview_caps_large_symbol_lists(client) -> None:
    symbols = ",".join(f"SYM{i}" for i in range(30))
    response = client.get(SCANNER_PATH, params={"symbols": symbols})
    assert response.status_code == 200

    batch = SignalScannerBatch.model_validate(response.json())
    assert len(batch.results) == 25
    assert batch.results[0].symbol == "SYM0"
    assert batch.results[-1].symbol == "SYM24"


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_scanner_preview_rejects_non_get_methods(client, method: str) -> None:
    response = getattr(client, method)(SCANNER_PATH)
    assert response.status_code == 405


def test_scanner_preview_openapi_is_get_only(client) -> None:
    path_item = _path_item(client)
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


def test_scanner_preview_openapi_path_is_safe(client) -> None:
    assert SCANNER_PATH == "/api/signals/scanner/preview"
    for forbidden in (
        "order",
        "trade",
        "execute",
        "broker_execute",
        "autotrade",
        "live",
    ):
        assert forbidden not in SCANNER_PATH


def test_scanner_preview_openapi_forbidden_scan_remains_clean(client) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert SCANNER_PATH in paths
    assert not any("execute" in path for path in paths)
    assert not any("live-trade" in path or "live_trade" in path for path in paths)
    assert not any("place-order" in path or "place_order" in path for path in paths)
    assert not any("submit-trade" in path or "submit_trade" in path for path in paths)


def test_scanner_preview_module_has_no_execution_libraries() -> None:
    source = inspect.getsource(signals_module)
    for forbidden in FORBIDDEN_LIBRARIES:
        assert forbidden not in source


def test_scanner_preview_module_has_no_execution_function_names() -> None:
    function_names = {
        name
        for name, obj in inspect.getmembers(signals_module, inspect.isfunction)
    }
    assert not (function_names & FORBIDDEN_FUNCTION_NAMES)
