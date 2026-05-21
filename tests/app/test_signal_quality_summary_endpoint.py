from __future__ import annotations

import pytest

from app.schemas.signal_quality import SignalQualitySummaryResponse

QUALITY_PATH = "/api/signals/quality/summary"

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


def test_signal_quality_summary_get_returns_200(client) -> None:
    response = client.get(QUALITY_PATH)
    assert response.status_code == 200


def test_signal_quality_summary_returns_object(client) -> None:
    response = client.get(QUALITY_PATH)
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)


def test_signal_quality_summary_validates_schema(client) -> None:
    response = client.get(QUALITY_PATH)
    assert response.status_code == 200
    obj = SignalQualitySummaryResponse.model_validate(response.json())
    assert obj.read_only is True
    assert obj.dry_run is True
    assert obj.live_orders_blocked is True
    assert obj.risk_allowed is False
    assert obj.mode == "read_only"
    assert obj.execution_mode == "dry_run_only"
    assert obj.requires_human_review is True
    assert obj.source == "signal_quality_summary"


# ---------------------------------------------------------------------------
# Safety envelope — Literal fields
# ---------------------------------------------------------------------------


def test_signal_quality_summary_read_only_is_true(client) -> None:
    payload = client.get(QUALITY_PATH).json()
    assert payload["read_only"] is True


def test_signal_quality_summary_dry_run_is_true(client) -> None:
    payload = client.get(QUALITY_PATH).json()
    assert payload["dry_run"] is True


def test_signal_quality_summary_live_orders_blocked_is_true(client) -> None:
    payload = client.get(QUALITY_PATH).json()
    assert payload["live_orders_blocked"] is True


def test_signal_quality_summary_risk_allowed_is_false(client) -> None:
    payload = client.get(QUALITY_PATH).json()
    assert payload["risk_allowed"] is False


def test_signal_quality_summary_execution_mode_is_dry_run_only(client) -> None:
    payload = client.get(QUALITY_PATH).json()
    assert payload["execution_mode"] == "dry_run_only"


def test_signal_quality_summary_requires_human_review_is_true(client) -> None:
    payload = client.get(QUALITY_PATH).json()
    assert payload["requires_human_review"] is True


# ---------------------------------------------------------------------------
# Counts and quality fields
# ---------------------------------------------------------------------------


def test_signal_quality_summary_counts_are_non_negative(client) -> None:
    payload = client.get(QUALITY_PATH).json()
    summary = payload["summary"]
    for key, value in summary.items():
        if key != "average_confidence":
            assert isinstance(value, int) and value >= 0, f"{key}={value!r}"
    assert 0.0 <= summary["average_confidence"] <= 100.0


def test_signal_quality_summary_score_in_bounds(client) -> None:
    payload = client.get(QUALITY_PATH).json()
    score = payload["quality"]["score"]
    assert 0.0 <= score <= 100.0


def test_signal_quality_summary_label_is_valid(client) -> None:
    payload = client.get(QUALITY_PATH).json()
    assert payload["quality"]["label"] in {"safe_fallback", "low", "moderate", "high"}


def test_signal_quality_summary_confidence_band_is_valid(client) -> None:
    payload = client.get(QUALITY_PATH).json()
    assert payload["quality"]["confidence_band"] in {"low", "medium", "high"}


def test_signal_quality_summary_freshness_is_valid(client) -> None:
    payload = client.get(QUALITY_PATH).json()
    assert payload["quality"]["freshness"] in {"fallback", "live", "stale"}


def test_signal_quality_summary_risk_posture_is_valid(client) -> None:
    payload = client.get(QUALITY_PATH).json()
    assert payload["quality"]["risk_posture"] in {
        "blocked",
        "watch_only",
        "dry_run_only",
    }


# ---------------------------------------------------------------------------
# Forbidden field check
# ---------------------------------------------------------------------------


def test_signal_quality_summary_has_no_forbidden_keys(client) -> None:
    payload = client.get(QUALITY_PATH).json()

    def _scan(obj: object) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                assert key not in FORBIDDEN_RESPONSE_KEYS, f"forbidden key: {key!r}"
                _scan(value)
        elif isinstance(obj, list):
            for item in obj:
                _scan(item)

    _scan(payload)


def test_signal_quality_summary_no_profit_guarantees(client) -> None:
    raw_json = client.get(QUALITY_PATH).text.lower()
    for phrase in FORBIDDEN_PROFIT_PHRASES:
        assert phrase not in raw_json, f"forbidden phrase found: {phrase!r}"


# ---------------------------------------------------------------------------
# Non-GET rejection
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_signal_quality_summary_rejects_non_get_methods(client, method: str) -> None:
    response = getattr(client, method)(QUALITY_PATH)
    assert response.status_code == 405


# ---------------------------------------------------------------------------
# OpenAPI shape
# ---------------------------------------------------------------------------


def test_signal_quality_summary_openapi_is_get_only(client) -> None:
    path_item = client.app.openapi()["paths"][QUALITY_PATH]
    operation_keys = {
        key
        for key in path_item
        if key in {"get", "put", "post", "patch", "delete", "head", "options", "trace"}
    }
    assert operation_keys == {"get"}


def test_signal_quality_summary_openapi_path_is_safe(client) -> None:
    assert QUALITY_PATH == "/api/signals/quality/summary"
    for forbidden in (
        "execute",
        "broker_execute",
        "autotrade",
        "live",
        "place",
        "order",
    ):
        assert forbidden not in QUALITY_PATH


# ---------------------------------------------------------------------------
# Determinism / no broker calls
# ---------------------------------------------------------------------------


def test_signal_quality_summary_is_deterministic(client) -> None:
    r1 = client.get(QUALITY_PATH).json()
    r2 = client.get(QUALITY_PATH).json()
    # updated_at may differ — compare everything except timestamp
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
        "summary",
        "quality",
    ):
        assert r1[key] == r2[key], f"non-deterministic field: {key}"


def test_signal_quality_summary_no_external_network_required(client) -> None:
    response = client.get(QUALITY_PATH)
    assert response.status_code == 200
    assert response.json()


def test_signal_quality_summary_no_secrets_in_response(client) -> None:
    raw = client.get(QUALITY_PATH).text.lower()
    for forbidden in ("api_key", "apikey", "secret", "password", "token"):
        assert (
            f'"{forbidden}"' not in raw
        ), f"potential secret field {forbidden!r} in response"
