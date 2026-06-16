"""TEST-ALPACA-PAPER-ORDER-DRAFT — local-only paper order draft safety contract.

Verifies ALPACA-PAPER-ORDER-DRAFT-001:

- A valid request builds a draft (valid=true) with a local paper-draft-* id.
- Invalid side / order_type / time_in_force, missing stop-loss/take-profit,
  invalid quantity/notional, bad geometry, and max_risk_pct > 1% are blocked
  (valid=false, draft=null) — HTTP 200, not an error.
- draft_only=true, order_submission_enabled=false, execution_enabled=false,
  live_orders_blocked=true, dry_run=true, read_only=true,
  requires_human_review=true on every response.
- No forbidden fields (account_id, broker_order_id, execution_id, api_key,
  secret, token) ever appear.
- The service never calls Alpaca and never performs network I/O.
- The POST route is named ``order-draft`` (not execute/submit) and is allowed.

No test requires real Alpaca credentials or performs real network calls.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pytest

from app.schemas.alpaca_paper_order_draft import AlpacaPaperOrderDraftRequest
from app.services import alpaca_paper_order_draft_service as draft_service
from app.services.alpaca_paper_order_draft_service import (
    build_alpaca_paper_order_draft,
)

_FORBIDDEN_KEYS: frozenset[str] = frozenset(
    {
        "account_id",
        "broker_account_id",
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


def _valid_buy(**overrides: object) -> AlpacaPaperOrderDraftRequest:
    base: dict[str, object] = {
        "symbol": "AAPL",
        "side": "BUY",
        "order_type": "market",
        "time_in_force": "day",
        "quantity": 10,
        "entry_price": 100.0,
        "stop_loss": 95.0,
        "take_profit": 110.0,
        "max_risk_pct": 0.5,
    }
    base.update(overrides)
    return AlpacaPaperOrderDraftRequest(**base)  # type: ignore[arg-type]


def _assert_safety_flags(payload: dict) -> None:
    assert payload["paper_only"] is True
    assert payload["dry_run"] is True
    assert payload["read_only"] is True
    assert payload["live_orders_blocked"] is True
    assert payload["execution_enabled"] is False
    assert payload["requires_human_review"] is True
    assert payload["draft_only"] is True
    assert payload["order_submission_enabled"] is False
    assert payload["message"] == "Draft only — not submitted to Alpaca."


def test_valid_buy_draft_is_built() -> None:
    resp = build_alpaca_paper_order_draft(_valid_buy())
    payload = resp.model_dump()

    _assert_safety_flags(payload)
    assert payload["valid"] is True
    draft = payload["draft"]
    assert draft is not None
    assert draft["draft_id"].startswith("paper-draft-")
    assert draft["status"] == "draft"
    assert draft["symbol"] == "AAPL"
    assert draft["side"] == "BUY"


def test_valid_sell_draft_is_built() -> None:
    resp = build_alpaca_paper_order_draft(
        _valid_buy(side="SELL", stop_loss=110.0, take_profit=95.0)
    )
    assert resp.valid is True
    assert resp.draft is not None
    assert resp.draft.side == "SELL"


def test_notional_instead_of_quantity_is_accepted() -> None:
    resp = build_alpaca_paper_order_draft(_valid_buy(quantity=None, notional=1500.0))
    assert resp.valid is True
    assert resp.draft is not None
    assert resp.draft.notional == 1500.0


def test_invalid_side_is_blocked() -> None:
    resp = build_alpaca_paper_order_draft(_valid_buy(side="HOLD"))
    assert resp.valid is False
    assert resp.draft is None
    assert "side" in resp.reason.lower()


def test_invalid_order_type_is_blocked() -> None:
    resp = build_alpaca_paper_order_draft(_valid_buy(order_type="iceberg"))
    assert resp.valid is False
    assert resp.draft is None


def test_invalid_time_in_force_is_blocked() -> None:
    resp = build_alpaca_paper_order_draft(_valid_buy(time_in_force="forever"))
    assert resp.valid is False
    assert resp.draft is None


def test_both_quantity_and_notional_blocked() -> None:
    resp = build_alpaca_paper_order_draft(_valid_buy(quantity=10, notional=1500.0))
    assert resp.valid is False
    assert resp.draft is None


def test_neither_quantity_nor_notional_blocked() -> None:
    resp = build_alpaca_paper_order_draft(_valid_buy(quantity=None, notional=None))
    assert resp.valid is False


def test_non_positive_quantity_blocked() -> None:
    resp = build_alpaca_paper_order_draft(_valid_buy(quantity=0))
    assert resp.valid is False


def test_missing_stop_loss_blocked() -> None:
    resp = build_alpaca_paper_order_draft(_valid_buy(stop_loss=None))
    assert resp.valid is False
    assert "stop_loss" in resp.reason


def test_missing_take_profit_blocked() -> None:
    resp = build_alpaca_paper_order_draft(_valid_buy(take_profit=None))
    assert resp.valid is False
    assert "take_profit" in resp.reason


def test_max_risk_over_one_percent_blocked() -> None:
    resp = build_alpaca_paper_order_draft(_valid_buy(max_risk_pct=1.5))
    assert resp.valid is False
    assert resp.draft is None
    assert "risk" in resp.reason.lower()


def test_bad_buy_geometry_blocked() -> None:
    # stop_loss above entry violates BUY geometry.
    resp = build_alpaca_paper_order_draft(_valid_buy(stop_loss=105.0))
    assert resp.valid is False
    assert "geometry" in resp.reason.lower()


def test_no_forbidden_fields_in_response() -> None:
    payload = build_alpaca_paper_order_draft(_valid_buy()).model_dump()
    leaked = sorted(set(_walk_keys(payload)) & _FORBIDDEN_KEYS)
    assert not leaked, f"forbidden fields leaked: {leaked!r}"


def test_service_does_not_call_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Building a draft must not open any socket (no Alpaca/network call)."""
    import socket

    def _boom(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("network access attempted during draft build")

    monkeypatch.setattr(socket, "socket", _boom)
    resp = build_alpaca_paper_order_draft(_valid_buy())
    assert resp.valid is True  # built purely locally, no socket opened


def test_service_source_has_no_alpaca_or_submit() -> None:
    """The draft service must not import Alpaca or reference order submission."""
    source = Path(draft_service.__file__).read_text(encoding="utf-8").lower()
    for needle in ("import alpaca", "tradingclient", "submit_order", "place_order"):
        assert needle not in source, f"unexpected {needle!r} in draft service"


# --- route tests -----------------------------------------------------------

_PATH = "/api/alpaca-paper/order-draft"

_VALID_BODY = {
    "symbol": "AAPL",
    "side": "BUY",
    "order_type": "market",
    "time_in_force": "day",
    "quantity": 10,
    "entry_price": 100.0,
    "stop_loss": 95.0,
    "take_profit": 110.0,
    "max_risk_pct": 0.5,
}


def test_route_valid_draft_returns_200(client) -> None:
    response = client.post(_PATH, json=_VALID_BODY)
    assert response.status_code == 200
    payload = response.json()
    _assert_safety_flags(payload)
    assert payload["valid"] is True
    assert payload["draft"]["draft_id"].startswith("paper-draft-")


def test_route_blocked_draft_returns_200(client) -> None:
    body = dict(_VALID_BODY, max_risk_pct=2.0)
    response = client.post(_PATH, json=body)
    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is False
    assert payload["draft"] is None


def test_route_no_forbidden_keys(client) -> None:
    payload = client.post(_PATH, json=_VALID_BODY).json()
    leaked = sorted(set(_walk_keys(payload)) & _FORBIDDEN_KEYS)
    assert not leaked, f"forbidden response keys leaked: {leaked!r}"


def test_route_get_not_allowed(client) -> None:
    # The draft route is POST-only; GET must not be allowed.
    assert client.get(_PATH).status_code == 405


def test_openapi_route_is_named_draft_and_post_only(client) -> None:
    schema = client.app.openapi()
    assert _PATH in schema["paths"], f"{_PATH} missing from OpenAPI"
    methods = set(schema["paths"][_PATH].keys())
    assert methods == {"post"}, f"expected only POST, got {methods}"
    # Path must not resemble execution/submission.
    parts = set(_PATH.split("/"))
    for forbidden in ("execute", "submit-order", "place-order", "order-submit"):
        assert forbidden not in parts
