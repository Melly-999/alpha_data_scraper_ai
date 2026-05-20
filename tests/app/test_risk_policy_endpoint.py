from __future__ import annotations

import inspect

import pytest

from app.api.routes import risk as risk_module
from app.schemas.risk import RiskPolicyResponse

POLICY_PATH = "/api/risk/policy"

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


def test_risk_policy_get_returns_200(client) -> None:
    response = client.get(POLICY_PATH)
    assert response.status_code == 200


def test_risk_policy_response_validates_schema(client) -> None:
    response = client.get(POLICY_PATH)
    assert response.status_code == 200
    result = RiskPolicyResponse.model_validate(response.json())
    assert result.execution_enabled is False
    assert result.min_confidence > 0
    assert result.daily_loss_cap_pct > 0
    assert result.open_position_cap > 0


# ---------------------------------------------------------------------------
# Safety flags
# ---------------------------------------------------------------------------


def test_risk_policy_safety_flags(client) -> None:
    response = client.get(POLICY_PATH)
    assert response.status_code == 200
    result = RiskPolicyResponse.model_validate(response.json())
    assert result.read_only is True
    assert result.dry_run is True
    assert result.auto_trade is False
    assert result.live_orders_blocked is True


def test_risk_policy_execution_mode_is_dry_run_only(client) -> None:
    response = client.get(POLICY_PATH)
    assert response.status_code == 200
    result = RiskPolicyResponse.model_validate(response.json())
    assert result.execution_mode == "dry_run_only"


def test_risk_policy_broker_execution_disabled(client) -> None:
    response = client.get(POLICY_PATH)
    assert response.status_code == 200
    result = RiskPolicyResponse.model_validate(response.json())
    assert result.broker_execution_enabled is False
    assert result.execution_enabled is False


def test_risk_policy_requires_human_review(client) -> None:
    response = client.get(POLICY_PATH)
    assert response.status_code == 200
    result = RiskPolicyResponse.model_validate(response.json())
    assert result.requires_human_review is True


# ---------------------------------------------------------------------------
# Risk invariants
# ---------------------------------------------------------------------------


def test_risk_policy_max_risk_within_ceiling(client) -> None:
    response = client.get(POLICY_PATH)
    assert response.status_code == 200
    result = RiskPolicyResponse.model_validate(response.json())
    assert (
        result.max_risk_per_trade_pct <= 1.0
    ), f"max_risk_per_trade_pct {result.max_risk_per_trade_pct} exceeds 1.0"


def test_risk_policy_stop_loss_required(client) -> None:
    response = client.get(POLICY_PATH)
    assert response.status_code == 200
    result = RiskPolicyResponse.model_validate(response.json())
    assert result.stop_loss_required is True


def test_risk_policy_take_profit_required(client) -> None:
    response = client.get(POLICY_PATH)
    assert response.status_code == 200
    result = RiskPolicyResponse.model_validate(response.json())
    assert result.take_profit_required is True


# ---------------------------------------------------------------------------
# Forbidden field check
# ---------------------------------------------------------------------------


def test_risk_policy_has_no_forbidden_keys(client) -> None:
    response = client.get(POLICY_PATH)
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
def test_risk_policy_rejects_non_get_methods(client, method: str) -> None:
    response = getattr(client, method)(POLICY_PATH)
    assert response.status_code == 405


# ---------------------------------------------------------------------------
# OpenAPI shape
# ---------------------------------------------------------------------------


def test_risk_policy_openapi_is_get_only(client) -> None:
    path_item = client.app.openapi()["paths"][POLICY_PATH]
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


def test_risk_policy_openapi_path_is_safe(client) -> None:
    assert POLICY_PATH == "/api/risk/policy"
    for forbidden in (
        "execute",
        "broker_execute",
        "autotrade",
        "live",
        "place",
    ):
        assert forbidden not in POLICY_PATH


def test_risk_policy_openapi_forbidden_paths_remain_clean(client) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert POLICY_PATH in paths
    assert not any("execute" in path for path in paths)
    assert not any("live-trade" in path or "live_trade" in path for path in paths)
    assert not any("place-order" in path or "place_order" in path for path in paths)


# ---------------------------------------------------------------------------
# Determinism / no broker calls
# ---------------------------------------------------------------------------


def test_risk_policy_is_deterministic(client) -> None:
    r1 = client.get(POLICY_PATH).json()
    r2 = client.get(POLICY_PATH).json()
    assert r1 == r2


def test_risk_policy_module_has_no_execution_libraries() -> None:
    source = inspect.getsource(risk_module)
    for forbidden in FORBIDDEN_LIBRARIES:
        assert forbidden not in source


def test_risk_policy_module_has_no_execution_function_names() -> None:
    all_names = {
        name for name, obj in inspect.getmembers(risk_module, inspect.isfunction)
    }
    assert not (all_names & FORBIDDEN_FUNCTION_NAMES)
