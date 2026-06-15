"""TEST-ALPACA-PAPER-READONLY-ADAPTER — read-only adapter safety contract.

Verifies the Alpaca Paper read-only adapter (ALPACA-PAPER-READONLY-ADAPTER-001):

- Default (no credentials / not enabled) returns a safe degraded_demo preview.
- An injected read-only client yields sanitized positions only.
- read_only / dry_run / live_orders_blocked are always True; execution_enabled
  and order_placement_enabled are always False.
- No forbidden fields (account_id, broker_order_id, execution_id, api_key,
  secret, token) ever leak — even when the raw client objects carry them.
- Malformed / raising clients degrade safely (never raise, never place orders).
- Unsafe / disabled configuration never resolves a client (no Alpaca call).
- The GET-only /api/alpaca-paper/positions-preview route is GET-only and safe.

No test requires real Alpaca credentials or performs real network calls.
"""

from __future__ import annotations

from collections.abc import Iterable

import pytest

from app.services.alpaca_paper_readonly_adapter import AlpacaPaperReadOnlyAdapter

_FORBIDDEN_KEYS: frozenset[str] = frozenset(
    {
        "account_id",
        "broker_account_id",
        "asset_id",
        "broker_order_id",
        "order_id",
        "client_order_id",
        "execution_id",
        "api_key",
        "api_secret",
        "secret",
        "token",
        "password",
    }
)


def _walk_keys(value: object) -> Iterable[str]:
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _walk_keys(nested)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk_keys(item)


class _RawPosition:
    """Mimics an Alpaca SDK Position object, including fields that must NOT leak."""

    def __init__(
        self,
        symbol: str,
        qty: object,
        market_value: object,
        unrealized_pl: object,
        side: str,
    ) -> None:
        self.symbol = symbol
        self.qty = qty
        self.market_value = market_value
        self.unrealized_pl = unrealized_pl
        self.side = side
        # Sensitive / broker-internal fields that must never be exposed.
        self.asset_id = "b0b15f9e-secret-asset-id"
        self.account_id = "PA-LIVEACCT-0001"
        self.exchange = "NASDAQ"


class _FakeClient:
    def __init__(self, positions: object) -> None:
        self._positions = positions

    def get_all_positions(self) -> object:
        return self._positions


class _RaisingClient:
    def get_all_positions(self) -> object:
        raise RuntimeError("simulated client/network failure")


def _no_env(_name: str) -> None:
    return None


def _assert_safety_flags(payload: dict) -> None:
    assert payload["paper_only"] is True
    assert payload["dry_run"] is True
    assert payload["read_only"] is True
    assert payload["live_orders_blocked"] is True
    assert payload["execution_enabled"] is False
    assert payload["requires_human_review"] is True
    assert payload["order_placement_enabled"] is False
    assert payload["paper_simulated"] is True
    assert payload["redacted"] is True


def test_default_adapter_is_degraded_demo() -> None:
    adapter = AlpacaPaperReadOnlyAdapter(env_reader=_no_env)
    preview = adapter.get_positions_preview()
    payload = preview.model_dump()

    _assert_safety_flags(payload)
    assert payload["mode"] == "degraded_demo"
    assert payload["connected"] is False
    assert payload["source"] == "fallback"
    assert payload["count"] == 0
    assert payload["positions"] == []


def test_injected_client_returns_sanitized_positions() -> None:
    positions = [
        _RawPosition("aapl", "10", "1500.50", "12.25", "long"),
        _RawPosition("MSFT", 5, 2000.0, -8.0, "short"),
    ]
    adapter = AlpacaPaperReadOnlyAdapter(client=_FakeClient(positions))
    preview = adapter.get_positions_preview()
    payload = preview.model_dump()

    _assert_safety_flags(payload)
    assert payload["mode"] == "paper_readonly"
    assert payload["connected"] is True
    assert payload["source"] == "alpaca_paper_readonly"
    assert payload["count"] == 2

    first = payload["positions"][0]
    assert first["symbol"] == "AAPL"  # normalized upper-case
    assert first["qty"] == 10.0
    assert first["market_value"] == 1500.50
    assert first["unrealized_pl"] == 12.25
    assert first["side"] == "long"
    assert payload["positions"][1]["side"] == "short"


def test_no_forbidden_fields_leak_even_when_raw_carries_them() -> None:
    positions = [_RawPosition("TSLA", "3", "900.0", "1.5", "long")]
    adapter = AlpacaPaperReadOnlyAdapter(client=_FakeClient(positions))
    payload = adapter.get_positions_preview().model_dump()

    leaked = sorted(set(_walk_keys(payload)) & _FORBIDDEN_KEYS)
    assert not leaked, f"forbidden fields leaked: {leaked!r}"


def test_raising_client_degrades_safely() -> None:
    adapter = AlpacaPaperReadOnlyAdapter(client=_RaisingClient())
    payload = adapter.get_positions_preview().model_dump()

    _assert_safety_flags(payload)
    assert payload["mode"] == "degraded_demo"
    assert payload["connected"] is False
    assert payload["positions"] == []


def test_malformed_positions_degrade_safely() -> None:
    # Non-iterable payload -> empty; dict items missing symbol are skipped.
    adapter_bad = AlpacaPaperReadOnlyAdapter(client=_FakeClient(object()))
    assert adapter_bad.get_positions_preview().positions == []

    adapter_partial = AlpacaPaperReadOnlyAdapter(
        client=_FakeClient([{"qty": 1}, {"symbol": "NVDA", "qty": "2"}])
    )
    preview = adapter_partial.get_positions_preview()
    assert [p.symbol for p in preview.positions] == ["NVDA"]
    assert preview.positions[0].side == "unknown"


def test_unsafe_or_disabled_config_resolves_no_client() -> None:
    # Enabled + credentials present, but ALPACA_ENV is not "paper" -> no client.
    live_env = {
        "ALPACA_PAPER_READONLY_ENABLED": "true",
        "ALPACA_ENV": "live",
        "ALPACA_API_KEY": "present",
        "ALPACA_SECRET_KEY": "present",
    }
    adapter_live = AlpacaPaperReadOnlyAdapter(env_reader=live_env.get)
    assert adapter_live._resolve_client() is None
    assert adapter_live.get_positions_preview().mode == "degraded_demo"

    # Not enabled (default) -> no client even with credentials present.
    disabled_env = {
        "ALPACA_ENV": "paper",
        "ALPACA_API_KEY": "present",
        "ALPACA_SECRET_KEY": "present",
    }
    adapter_disabled = AlpacaPaperReadOnlyAdapter(env_reader=disabled_env.get)
    assert adapter_disabled._resolve_client() is None


# --- route tests -----------------------------------------------------------

_PATH = "/api/alpaca-paper/positions-preview"


def test_positions_preview_route_returns_200_and_safety_flags(client) -> None:
    response = client.get(_PATH)
    assert response.status_code == 200
    payload = response.json()
    _assert_safety_flags(payload)
    assert payload["provider"] == "alpaca_paper"
    # Default app process has no credentials -> degraded demo.
    assert payload["mode"] == "degraded_demo"


def test_positions_preview_route_has_no_forbidden_keys(client) -> None:
    payload = client.get(_PATH).json()
    leaked = sorted(set(_walk_keys(payload)) & _FORBIDDEN_KEYS)
    assert not leaked, f"forbidden response keys leaked: {leaked!r}"


@pytest.mark.parametrize("method", ("post", "put", "patch", "delete"))
def test_positions_preview_route_is_get_only(client, method: str) -> None:
    response = getattr(client, method)(_PATH)
    assert response.status_code == 405, f"{method.upper()} should be 405"


def test_positions_preview_openapi_is_get_only(client) -> None:
    schema = client.app.openapi()
    methods = set(schema["paths"][_PATH].keys())
    assert methods == {"get"}, f"expected only GET, got {methods}"
