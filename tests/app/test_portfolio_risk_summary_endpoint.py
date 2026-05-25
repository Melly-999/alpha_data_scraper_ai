from __future__ import annotations

import pytest

from app.schemas.portfolio_risk import PortfolioRiskSummaryResponse

RISK_SUMMARY_PATH = "/api/portfolio/risk-summary"

FORBIDDEN_RESPONSE_KEYS = {
    "order_id",
    "account_id",
    "account_number",
    "execution_id",
    "trade_id",
    "place_order",
    "broker_execute",
    "api_key",
    "secret",
    "token",
    "password",
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

FORBIDDEN_RECOMMENDATION_PHRASES = (
    "you should buy",
    "you should sell",
    "recommend buying",
    "recommend selling",
)


# ---------------------------------------------------------------------------
# Basic contract
# ---------------------------------------------------------------------------


def test_portfolio_risk_summary_returns_200(client) -> None:
    response = client.get(RISK_SUMMARY_PATH)
    assert response.status_code == 200


def test_portfolio_risk_summary_returns_object(client) -> None:
    payload = client.get(RISK_SUMMARY_PATH).json()
    assert isinstance(payload, dict)


def test_portfolio_risk_summary_validates_schema(client) -> None:
    payload = client.get(RISK_SUMMARY_PATH).json()
    obj = PortfolioRiskSummaryResponse.model_validate(payload)
    # Safety Literal fields
    assert obj.read_only is True
    assert obj.dry_run is True
    assert obj.live_orders_blocked is True
    assert obj.risk_allowed is False
    assert obj.mode == "read_only"
    assert obj.execution_mode == "dry_run_only"
    assert obj.requires_human_review is True
    assert obj.source == "portfolio_risk_summary"


# ---------------------------------------------------------------------------
# Safety envelope — Literal fields
# ---------------------------------------------------------------------------


def test_portfolio_risk_summary_mode_is_read_only(client) -> None:
    assert client.get(RISK_SUMMARY_PATH).json()["mode"] == "read_only"


def test_portfolio_risk_summary_read_only_is_true(client) -> None:
    assert client.get(RISK_SUMMARY_PATH).json()["read_only"] is True


def test_portfolio_risk_summary_dry_run_is_true(client) -> None:
    assert client.get(RISK_SUMMARY_PATH).json()["dry_run"] is True


def test_portfolio_risk_summary_live_orders_blocked_is_true(client) -> None:
    assert client.get(RISK_SUMMARY_PATH).json()["live_orders_blocked"] is True


def test_portfolio_risk_summary_execution_mode_is_dry_run_only(client) -> None:
    assert client.get(RISK_SUMMARY_PATH).json()["execution_mode"] == "dry_run_only"


def test_portfolio_risk_summary_requires_human_review_is_true(client) -> None:
    assert client.get(RISK_SUMMARY_PATH).json()["requires_human_review"] is True


def test_portfolio_risk_summary_risk_allowed_is_false(client) -> None:
    assert client.get(RISK_SUMMARY_PATH).json()["risk_allowed"] is False


# ---------------------------------------------------------------------------
# Posture block
# ---------------------------------------------------------------------------


def test_portfolio_risk_posture_broker_execution_allowed_is_false(client) -> None:
    posture = client.get(RISK_SUMMARY_PATH).json()["posture"]
    assert posture["broker_execution_allowed"] is False


def test_portfolio_risk_posture_live_orders_blocked_is_true(client) -> None:
    posture = client.get(RISK_SUMMARY_PATH).json()["posture"]
    assert posture["live_orders_blocked"] is True


def test_portfolio_risk_posture_risk_allowed_is_false(client) -> None:
    posture = client.get(RISK_SUMMARY_PATH).json()["posture"]
    assert posture["risk_allowed"] is False


def test_portfolio_risk_posture_requires_human_review_is_true(client) -> None:
    posture = client.get(RISK_SUMMARY_PATH).json()["posture"]
    assert posture["requires_human_review"] is True


def test_portfolio_risk_posture_label_is_valid(client) -> None:
    label = client.get(RISK_SUMMARY_PATH).json()["posture"]["label"]
    assert label in {"safe_fallback", "read_only", "risk_blocked", "dry_run_only"}


# ---------------------------------------------------------------------------
# Risk limits
# ---------------------------------------------------------------------------


def test_portfolio_risk_max_risk_per_trade_within_cap(client) -> None:
    limits = client.get(RISK_SUMMARY_PATH).json()["limits"]
    assert limits["max_risk_per_trade_pct"] <= 1.0


def test_portfolio_risk_max_portfolio_risk_within_cap(client) -> None:
    limits = client.get(RISK_SUMMARY_PATH).json()["limits"]
    assert limits["max_portfolio_risk_pct"] <= 5.0


def test_portfolio_risk_used_within_max(client) -> None:
    limits = client.get(RISK_SUMMARY_PATH).json()["limits"]
    assert 0.0 <= limits["risk_used_pct"] <= limits["max_portfolio_risk_pct"]


def test_portfolio_risk_remaining_capacity_non_negative(client) -> None:
    limits = client.get(RISK_SUMMARY_PATH).json()["limits"]
    assert limits["remaining_risk_capacity_pct"] >= 0.0


# ---------------------------------------------------------------------------
# Exposure bounds
# ---------------------------------------------------------------------------


def test_portfolio_risk_exposure_values_non_negative(client) -> None:
    exposure = client.get(RISK_SUMMARY_PATH).json()["exposure"]
    assert exposure["total_positions"] >= 0
    assert exposure["open_positions"] >= 0
    assert exposure["total_notional"] >= 0.0
    assert 0.0 <= exposure["gross_exposure_pct"] <= 100.0
    assert 0.0 <= exposure["net_exposure_pct"] <= 100.0
    assert 0.0 <= exposure["cash_buffer_pct"] <= 100.0


# ---------------------------------------------------------------------------
# Forbidden fields / phrases
# ---------------------------------------------------------------------------


def test_portfolio_risk_summary_no_forbidden_keys(client) -> None:
    payload = client.get(RISK_SUMMARY_PATH).json()

    def _scan(obj: object) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                assert key not in FORBIDDEN_RESPONSE_KEYS, f"forbidden key: {key!r}"
                _scan(value)
        elif isinstance(obj, list):
            for item in obj:
                _scan(item)

    _scan(payload)


def test_portfolio_risk_summary_no_profit_guarantees(client) -> None:
    raw = client.get(RISK_SUMMARY_PATH).text.lower()
    for phrase in FORBIDDEN_PROFIT_PHRASES:
        assert phrase not in raw, f"forbidden phrase: {phrase!r}"


def test_portfolio_risk_summary_no_trade_recommendations(client) -> None:
    raw = client.get(RISK_SUMMARY_PATH).text.lower()
    for phrase in FORBIDDEN_RECOMMENDATION_PHRASES:
        assert phrase not in raw, f"forbidden phrase: {phrase!r}"


def test_portfolio_risk_summary_no_secrets_in_response(client) -> None:
    raw = client.get(RISK_SUMMARY_PATH).text.lower()
    for forbidden in ("api_key", "apikey", "secret", "password", "token"):
        assert f'"{forbidden}"' not in raw, f"potential secret field: {forbidden!r}"


# ---------------------------------------------------------------------------
# Non-GET rejection
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_portfolio_risk_summary_rejects_non_get_methods(
    client, method: str
) -> None:
    response = getattr(client, method)(RISK_SUMMARY_PATH)
    assert response.status_code == 405


# ---------------------------------------------------------------------------
# OpenAPI shape
# ---------------------------------------------------------------------------


def test_portfolio_risk_summary_openapi_is_get_only(client) -> None:
    path_item = client.app.openapi()["paths"][RISK_SUMMARY_PATH]
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


def test_portfolio_risk_summary_openapi_path_is_safe(client) -> None:
    assert RISK_SUMMARY_PATH == "/api/portfolio/risk-summary"
    for forbidden in ("execute", "broker_execute", "autotrade", "live", "place", "order"):
        assert forbidden not in RISK_SUMMARY_PATH


# ---------------------------------------------------------------------------
# Determinism / no broker calls
# ---------------------------------------------------------------------------


def test_portfolio_risk_summary_is_deterministic(client) -> None:
    r1 = client.get(RISK_SUMMARY_PATH).json()
    r2 = client.get(RISK_SUMMARY_PATH).json()
    for key in (
        "status",
        "mode",
        "read_only",
        "dry_run",
        "live_orders_blocked",
        "execution_mode",
        "requires_human_review",
        "risk_allowed",
        "source",
        "exposure",
        "limits",
        "posture",
    ):
        assert r1[key] == r2[key], f"non-deterministic field: {key}"


def test_portfolio_risk_summary_no_external_network_required(client) -> None:
    response = client.get(RISK_SUMMARY_PATH)
    assert response.status_code == 200
    assert response.json()


# ---------------------------------------------------------------------------
# Service import safety
# ---------------------------------------------------------------------------


def test_portfolio_risk_service_has_no_broker_imports() -> None:
    """Service must not import broker/execution/network modules."""
    import app.services.portfolio_risk_summary as svc_module

    forbidden_modules = {
        "ib_insync",
        "ibapi",
        "MetaTrader5",
        "requests",
        "httpx",
        "websockets",
        "alpaca",
        "ccxt",
        "supabase",
    }
    import sys

    for mod in forbidden_modules:
        assert mod not in sys.modules or not hasattr(
            svc_module, mod
        ), f"broker/network module {mod!r} must not be imported by service"
