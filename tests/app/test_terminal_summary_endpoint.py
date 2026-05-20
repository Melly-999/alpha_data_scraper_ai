from __future__ import annotations

import inspect

import pytest

from app.api.routes import terminal as terminal_module
from app.schemas.terminal import TerminalSummaryResponse

SUMMARY_PATH = "/api/terminal/summary"

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


# ---------------------------------------------------------------------------
# Basic contract
# ---------------------------------------------------------------------------


def test_terminal_summary_get_returns_200(client) -> None:
    response = client.get(SUMMARY_PATH)
    assert response.status_code == 200


def test_terminal_summary_response_validates_schema(client) -> None:
    response = client.get(SUMMARY_PATH)
    assert response.status_code == 200

    result = TerminalSummaryResponse.model_validate(response.json())
    assert result.mode == "read-only"
    assert result.backend in ("online", "fallback")


# ---------------------------------------------------------------------------
# Safety flags
# ---------------------------------------------------------------------------


def test_terminal_summary_safety_flags(client) -> None:
    response = client.get(SUMMARY_PATH)
    assert response.status_code == 200

    result = TerminalSummaryResponse.model_validate(response.json())
    assert result.safety.read_only is True
    assert result.safety.dry_run is True
    assert result.safety.auto_trade is False
    assert result.safety.live_orders_blocked is True


def test_terminal_summary_broker_is_read_only(client) -> None:
    response = client.get(SUMMARY_PATH)
    assert response.status_code == 200

    result = TerminalSummaryResponse.model_validate(response.json())
    assert result.broker.read_only is True
    assert result.broker.execution_enabled is False
    assert result.broker.name == "IBKR Paper"


def test_terminal_summary_broker_permissions_block_execution(client) -> None:
    response = client.get(SUMMARY_PATH)
    assert response.status_code == 200

    result = TerminalSummaryResponse.model_validate(response.json())
    perms = result.broker.permissions
    assert perms.orders == "denied"
    assert perms.live_execution == "denied"
    assert perms.market_data == "allowed"
    assert perms.account_read == "allowed"
    assert perms.positions_read == "allowed"


# ---------------------------------------------------------------------------
# Forbidden field check
# ---------------------------------------------------------------------------


def test_terminal_summary_has_no_forbidden_keys(client) -> None:
    response = client.get(SUMMARY_PATH)
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
def test_terminal_summary_rejects_non_get_methods(client, method: str) -> None:
    response = getattr(client, method)(SUMMARY_PATH)
    assert response.status_code == 405


# ---------------------------------------------------------------------------
# OpenAPI shape
# ---------------------------------------------------------------------------


def test_terminal_summary_openapi_is_get_only(client) -> None:
    path_item = client.app.openapi()["paths"][SUMMARY_PATH]
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


def test_terminal_summary_openapi_path_is_safe(client) -> None:
    assert SUMMARY_PATH == "/api/terminal/summary"
    for forbidden in (
        "order",
        "trade",
        "execute",
        "broker_execute",
        "autotrade",
        "live",
    ):
        assert forbidden not in SUMMARY_PATH


def test_terminal_summary_openapi_forbidden_paths_remain_clean(client) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert SUMMARY_PATH in paths
    assert not any("execute" in path for path in paths)
    assert not any("live-trade" in path or "live_trade" in path for path in paths)
    assert not any("place-order" in path or "place_order" in path for path in paths)


# ---------------------------------------------------------------------------
# Determinism / no broker calls
# ---------------------------------------------------------------------------


def test_terminal_summary_is_deterministic(client) -> None:
    r1 = client.get(SUMMARY_PATH).json()
    r2 = client.get(SUMMARY_PATH).json()
    # All fields except updated_at must be identical.
    r1.pop("updated_at", None)
    r2.pop("updated_at", None)
    assert r1 == r2


def test_terminal_summary_module_has_no_execution_libraries() -> None:
    source = inspect.getsource(terminal_module)
    for forbidden in FORBIDDEN_LIBRARIES:
        assert forbidden not in source


def test_terminal_summary_module_has_no_execution_function_names() -> None:
    function_names = {
        name for name, obj in inspect.getmembers(terminal_module, inspect.isfunction)
    }
    assert not (function_names & FORBIDDEN_FUNCTION_NAMES)
