from __future__ import annotations

"""Tests for SIG-UNIVERSE-002 endpoints.

Covers:
- GET /api/signals/scanner/universes — universe list endpoint
- GET /api/signals/scanner/preview?universe=<name> — universe param on preview
- Safety: no forbidden fields, GET-only, advisory posture enforced
"""

import pytest

from app.schemas.signal_scanner import SignalScannerBatch, SignalUniverseListResponse

UNIVERSES_PATH = "/api/signals/scanner/universes"
PREVIEW_PATH = "/api/signals/scanner/preview"

EXPECTED_UNIVERSE_NAMES = {
    "ai_mega_caps",
    "xtb_cfd_watchlist",
    "core_macro",
    "polish_eu_watchlist",
    "default_demo",
}

FORBIDDEN_RESPONSE_KEYS = {
    "account_id",
    "order_id",
    "execution_id",
    "api_key",
    "secret",
    "token",
    "credential",
    "password",
}


# ---------------------------------------------------------------------------
# GET /api/signals/scanner/universes — basic contract
# ---------------------------------------------------------------------------


def test_universes_returns_200(client) -> None:
    response = client.get(UNIVERSES_PATH)
    assert response.status_code == 200


def test_universes_response_is_read_only(client) -> None:
    payload = client.get(UNIVERSES_PATH).json()
    assert payload["read_only"] is True


def test_universes_response_execution_mode(client) -> None:
    payload = client.get(UNIVERSES_PATH).json()
    assert payload["execution_mode"] == "dry_run_only"


def test_universes_response_requires_human_review(client) -> None:
    payload = client.get(UNIVERSES_PATH).json()
    assert payload["requires_human_review"] is True


def test_universes_response_validates_against_schema(client) -> None:
    payload = client.get(UNIVERSES_PATH).json()
    response = SignalUniverseListResponse.model_validate(payload)
    assert response.read_only is True
    assert response.execution_mode == "dry_run_only"
    assert response.requires_human_review is True


# ---------------------------------------------------------------------------
# Universe names
# ---------------------------------------------------------------------------


def test_universes_contains_all_expected_names(client) -> None:
    payload = client.get(UNIVERSES_PATH).json()
    names = {u["name"] for u in payload["universes"]}
    assert EXPECTED_UNIVERSE_NAMES.issubset(names)


def test_universes_each_has_name_label_symbols(client) -> None:
    payload = client.get(UNIVERSES_PATH).json()
    for universe in payload["universes"]:
        assert isinstance(universe["name"], str) and universe["name"]
        assert isinstance(universe["label"], str) and universe["label"]
        assert isinstance(universe["symbols"], list)
        assert isinstance(universe["item_count"], int)
        assert universe["item_count"] == len(universe["symbols"])


def test_universes_ai_mega_caps_has_required_symbols(client) -> None:
    payload = client.get(UNIVERSES_PATH).json()
    ai_universe = next(u for u in payload["universes"] if u["name"] == "ai_mega_caps")
    symbols = set(ai_universe["symbols"])
    for expected in ("NVDA", "GOOGL", "AMZN", "MSFT", "AAPL", "META", "TSLA"):
        assert expected in symbols, f"Expected {expected!r} in ai_mega_caps universe"


def test_universes_xtb_cfd_has_required_symbols(client) -> None:
    payload = client.get(UNIVERSES_PATH).json()
    xtb = next(u for u in payload["universes"] if u["name"] == "xtb_cfd_watchlist")
    symbols = set(xtb["symbols"])
    for expected in ("US100", "US500", "XAUUSD", "NATGAS", "EURUSD"):
        assert expected in symbols, f"Expected {expected!r} in xtb_cfd_watchlist universe"


def test_universes_each_has_read_only_flags(client) -> None:
    payload = client.get(UNIVERSES_PATH).json()
    for universe in payload["universes"]:
        assert universe["read_only"] is True
        assert universe["execution_mode"] == "dry_run_only"
        assert universe["requires_human_review"] is True


# ---------------------------------------------------------------------------
# Forbidden fields not present in universe response
# ---------------------------------------------------------------------------


def test_universes_response_has_no_forbidden_keys(client) -> None:
    payload = client.get(UNIVERSES_PATH).json()

    def _collect_keys(value: object) -> set[str]:
        keys: set[str] = set()
        if isinstance(value, dict):
            for k, v in value.items():
                keys.add(k)
                keys.update(_collect_keys(v))
        elif isinstance(value, list):
            for item in value:
                keys.update(_collect_keys(item))
        return keys

    all_keys = _collect_keys(payload)
    for forbidden in FORBIDDEN_RESPONSE_KEYS:
        assert forbidden not in all_keys, (
            f"Forbidden key {forbidden!r} found in universes response"
        )


# ---------------------------------------------------------------------------
# GET /api/signals/scanner/universes — HTTP method safety
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_universes_endpoint_rejects_non_get_methods(client, method: str) -> None:
    response = getattr(client, method)(UNIVERSES_PATH)
    assert response.status_code == 405


def test_universes_openapi_is_get_only(client) -> None:
    schema = client.app.openapi()
    path_item = schema["paths"][UNIVERSES_PATH]
    operation_keys = {
        key
        for key in path_item
        if key in {"get", "put", "post", "patch", "delete", "head", "options", "trace"}
    }
    assert operation_keys == {"get"}


# ---------------------------------------------------------------------------
# GET /api/signals/scanner/preview?universe=<name>
# ---------------------------------------------------------------------------


def test_preview_with_universe_ai_mega_caps_returns_advisory_batch(client) -> None:
    response = client.get(PREVIEW_PATH, params={"universe": "ai_mega_caps"})
    assert response.status_code == 200
    batch = SignalScannerBatch.model_validate(response.json())
    assert batch.read_only is True
    assert batch.execution_mode == "dry_run_only"
    assert len(batch.results) > 0
    for result in batch.results:
        assert result.risk_allowed is False
        assert result.requires_human_review is True
        assert result.execution_mode == "dry_run_only"


def test_preview_with_universe_xtb_cfd_returns_advisory_batch(client) -> None:
    response = client.get(PREVIEW_PATH, params={"universe": "xtb_cfd_watchlist"})
    assert response.status_code == 200
    batch = SignalScannerBatch.model_validate(response.json())
    assert batch.read_only is True
    assert batch.execution_mode == "dry_run_only"
    assert len(batch.results) > 0
    # Should include at least one XTB-style symbol
    symbols = {r.symbol for r in batch.results}
    assert symbols & {"US100", "US500", "XAUUSD", "EURUSD", "BTCUSD"}


def test_preview_with_universe_core_macro_returns_advisory_batch(client) -> None:
    response = client.get(PREVIEW_PATH, params={"universe": "core_macro"})
    assert response.status_code == 200
    batch = SignalScannerBatch.model_validate(response.json())
    assert batch.read_only is True
    assert len(batch.results) > 0


def test_preview_with_universe_default_demo_returns_advisory_batch(client) -> None:
    response = client.get(PREVIEW_PATH, params={"universe": "default_demo"})
    assert response.status_code == 200
    batch = SignalScannerBatch.model_validate(response.json())
    assert batch.read_only is True
    assert len(batch.results) > 0


# ---------------------------------------------------------------------------
# Explicit symbols override universe param
# ---------------------------------------------------------------------------


def test_preview_explicit_symbols_override_universe(client) -> None:
    """Explicit symbols= query takes precedence over universe=."""
    response = client.get(
        PREVIEW_PATH,
        params={"symbols": "AAPL,NVDA", "universe": "xtb_cfd_watchlist"},
    )
    assert response.status_code == 200
    batch = SignalScannerBatch.model_validate(response.json())
    assert [r.symbol for r in batch.results] == ["AAPL", "NVDA"]


# ---------------------------------------------------------------------------
# Unknown universe safely falls back to default_demo
# ---------------------------------------------------------------------------


def test_preview_unknown_universe_falls_back_safely(client) -> None:
    response = client.get(
        PREVIEW_PATH, params={"universe": "completely_unknown_universe_xyz"}
    )
    assert response.status_code == 200
    batch = SignalScannerBatch.model_validate(response.json())
    assert batch.read_only is True
    assert len(batch.results) > 0
    for result in batch.results:
        assert result.risk_allowed is False
        assert result.requires_human_review is True


# ---------------------------------------------------------------------------
# OpenAPI — no forbidden paths introduced by SIG-UNIVERSE-002
# ---------------------------------------------------------------------------


def test_universes_openapi_path_has_no_forbidden_segments(client) -> None:
    for forbidden in ("order", "execute", "trade", "broker_execute", "autotrade", "live"):
        assert forbidden not in UNIVERSES_PATH


def test_openapi_still_has_no_execution_paths(client) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert UNIVERSES_PATH in paths
    assert not any("execute" in path for path in paths)
    assert not any("live-trade" in path or "live_trade" in path for path in paths)
    assert not any("place-order" in path or "place_order" in path for path in paths)
    assert not any("submit-trade" in path or "submit_trade" in path for path in paths)
