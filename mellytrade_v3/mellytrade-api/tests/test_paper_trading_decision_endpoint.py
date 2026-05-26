"""Tests for PAPER-M4-003 — GET /paper/decision/preview endpoint.

Covers:
  - Valid BUY/SELL previews return 200 with allowed=True
  - Blocked decisions: risk > 1%, missing SL/TP, invalid BUY/SELL geometry
  - All required safety flags present in every response
  - No broker_order_id / account_id / execution_id in any response
  - Route is GET-only (POST/PUT/PATCH/DELETE return 405)
  - Existing /health, /events, /watchlist routes are unaffected
"""

from __future__ import annotations

import pytest

_KEY = {"x-api-key": "test-key"}  # conftest sets FASTAPI_KEY=test-key
_URL = "/paper/decision/preview"

_BUY_VALID = dict(
    symbol="EURUSD",
    side="BUY",
    quantity=1.0,
    entry_price=1.1000,
    stop_loss=1.0950,
    take_profit=1.1100,
    confidence=80.0,
    max_risk_pct=0.01,
)

_SELL_VALID = dict(
    symbol="EURUSD",
    side="SELL",
    quantity=1.0,
    entry_price=1.1000,
    stop_loss=1.1050,
    take_profit=1.0900,
    confidence=80.0,
    max_risk_pct=0.01,
)

_FORBIDDEN_BROKER_FIELDS = {"broker_order_id", "account_id", "execution_id"}


def _get(client, params):
    return client.get(_URL, params=params, headers=_KEY)


# ---------------------------------------------------------------------------
# Tests 1–3: valid previews return 200 with allowed=True
# ---------------------------------------------------------------------------


class TestPaperPreviewValid:
    def test_valid_buy_returns_200(self, client):
        resp = _get(client, _BUY_VALID)
        assert resp.status_code == 200

    def test_valid_sell_returns_200(self, client):
        resp = _get(client, _SELL_VALID)
        assert resp.status_code == 200

    def test_valid_buy_preview_has_allowed_true(self, client):
        resp = _get(client, _BUY_VALID)
        assert resp.status_code == 200
        assert resp.json()["allowed"] is True

    def test_valid_sell_preview_has_allowed_true(self, client):
        resp = _get(client, _SELL_VALID)
        assert resp.status_code == 200
        assert resp.json()["allowed"] is True

    def test_valid_preview_includes_preview_order(self, client):
        resp = _get(client, _BUY_VALID)
        body = resp.json()
        assert body["preview_order"] is not None
        assert body["preview_order"]["symbol"] == "EURUSD"
        assert body["preview_order"]["direction"] == "BUY"

    def test_valid_sell_preview_order_direction(self, client):
        resp = _get(client, _SELL_VALID)
        body = resp.json()
        assert body["preview_order"] is not None
        assert body["preview_order"]["direction"] == "SELL"

    def test_valid_preview_has_reason(self, client):
        resp = _get(client, _BUY_VALID)
        body = resp.json()
        assert "reason" in body
        assert isinstance(body["reason"], str)


# ---------------------------------------------------------------------------
# Tests 4–8: blocked decisions
# ---------------------------------------------------------------------------


class TestPaperPreviewBlocked:
    def test_risk_above_1_never_executes(self, client):
        # max_risk_pct=1.5 — evaluate_paper_risk blocks it (200+allowed=False)
        # or FastAPI validates the param (422). Either way: no execution.
        params = {**_BUY_VALID, "max_risk_pct": 1.5}
        resp = _get(client, params)
        if resp.status_code == 200:
            body = resp.json()
            assert body["allowed"] is False
            assert body["execution_enabled"] is False
        else:
            assert resp.status_code == 422

    def test_missing_stop_loss_is_422(self, client):
        params = {k: v for k, v in _BUY_VALID.items() if k != "stop_loss"}
        resp = _get(client, params)
        assert resp.status_code == 422

    def test_missing_take_profit_is_422(self, client):
        params = {k: v for k, v in _BUY_VALID.items() if k != "take_profit"}
        resp = _get(client, params)
        assert resp.status_code == 422

    def test_invalid_buy_geometry_sl_above_entry(self, client):
        params = {**_BUY_VALID, "stop_loss": 1.1050}  # above entry → invalid
        resp = _get(client, params)
        assert resp.status_code == 200
        body = resp.json()
        assert body["allowed"] is False
        assert "BUY" in body["reason"]

    def test_invalid_buy_geometry_tp_below_entry(self, client):
        params = {**_BUY_VALID, "take_profit": 1.0900}  # below entry → invalid
        resp = _get(client, params)
        assert resp.status_code == 200
        body = resp.json()
        assert body["allowed"] is False
        assert "BUY" in body["reason"]

    def test_invalid_sell_geometry_sl_below_entry(self, client):
        params = {**_SELL_VALID, "stop_loss": 1.0950}  # below entry → invalid
        resp = _get(client, params)
        assert resp.status_code == 200
        body = resp.json()
        assert body["allowed"] is False
        assert "SELL" in body["reason"]

    def test_invalid_sell_geometry_tp_above_entry(self, client):
        params = {**_SELL_VALID, "take_profit": 1.1100}  # above entry → invalid
        resp = _get(client, params)
        assert resp.status_code == 200
        body = resp.json()
        assert body["allowed"] is False
        assert "SELL" in body["reason"]

    def test_blocked_decision_has_no_preview_order(self, client):
        params = {**_BUY_VALID, "stop_loss": 1.1050}
        resp = _get(client, params)
        assert resp.status_code == 200
        assert resp.json()["preview_order"] is None

    def test_blocked_decision_never_enables_execution(self, client):
        params = {**_BUY_VALID, "stop_loss": 1.1050}
        resp = _get(client, params)
        assert resp.status_code == 200
        assert resp.json()["execution_enabled"] is False


# ---------------------------------------------------------------------------
# Tests 9–13: safety flags and forbidden broker fields
# ---------------------------------------------------------------------------


class TestPaperPreviewSafetyFlags:
    def test_response_has_dry_run_true(self, client):
        body = _get(client, _BUY_VALID).json()
        assert body["dry_run"] is True

    def test_response_has_read_only_true(self, client):
        body = _get(client, _BUY_VALID).json()
        assert body["read_only"] is True

    def test_response_has_live_orders_blocked_true(self, client):
        body = _get(client, _BUY_VALID).json()
        assert body["live_orders_blocked"] is True

    def test_response_has_execution_enabled_false(self, client):
        body = _get(client, _BUY_VALID).json()
        assert body["execution_enabled"] is False

    def test_response_has_paper_only_true(self, client):
        body = _get(client, _BUY_VALID).json()
        assert body["paper_only"] is True

    def test_response_has_requires_human_review_true(self, client):
        body = _get(client, _BUY_VALID).json()
        assert body["requires_human_review"] is True

    def test_no_broker_order_id_in_response(self, client):
        body = _get(client, _BUY_VALID).json()
        assert "broker_order_id" not in body
        assert "broker_order_id" not in (body.get("preview_order") or {})

    def test_no_account_id_in_response(self, client):
        body = _get(client, _BUY_VALID).json()
        assert "account_id" not in body
        assert "account_id" not in (body.get("preview_order") or {})

    def test_no_execution_id_in_response(self, client):
        body = _get(client, _BUY_VALID).json()
        assert "execution_id" not in body
        assert "execution_id" not in (body.get("preview_order") or {})

    def test_preview_order_carries_safety_flags(self, client):
        order = _get(client, _BUY_VALID).json()["preview_order"]
        assert order["paper_only"] is True
        assert order["dry_run"] is True
        assert order["live_orders_blocked"] is True
        assert order["requires_human_review"] is True
        assert order["execution_enabled"] is False

    def test_safety_flags_stable_on_sell(self, client):
        body = _get(client, _SELL_VALID).json()
        assert body["paper_only"] is True
        assert body["dry_run"] is True
        assert body["read_only"] is True
        assert body["live_orders_blocked"] is True
        assert body["execution_enabled"] is False


# ---------------------------------------------------------------------------
# Tests 14–15: route is GET-only
# ---------------------------------------------------------------------------


class TestPaperPreviewRouteShape:
    def test_post_returns_405(self, client):
        resp = client.post(_URL, headers=_KEY, json={})
        assert resp.status_code == 405

    def test_put_returns_405(self, client):
        resp = client.put(_URL, headers=_KEY, json={})
        assert resp.status_code == 405

    def test_patch_returns_405(self, client):
        resp = client.patch(_URL, headers=_KEY, json={})
        assert resp.status_code == 405

    def test_delete_returns_405(self, client):
        resp = client.delete(_URL, headers=_KEY)
        assert resp.status_code == 405

    def test_route_appears_in_openapi_as_get_only(self, client):
        schema = client.get("/openapi.json").json()
        paths = schema.get("paths", {})
        paper_path = paths.get(_URL, {})
        assert "get" in paper_path
        for method in ("post", "put", "patch", "delete"):
            assert method not in paper_path


# ---------------------------------------------------------------------------
# Test 16: existing routes unaffected
# ---------------------------------------------------------------------------


class TestExistingRoutesUnchanged:
    def test_health_still_works(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_events_still_works(self, client):
        resp = client.get("/events")
        assert resp.status_code == 200
        assert "events" in resp.json()

    def test_watchlist_still_works(self, client):
        resp = client.get("/watchlist", headers=_KEY)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_health_safety_posture_unchanged(self, client):
        body = client.get("/health").json()
        assert body["dry_run"] is True
        assert body["autotrade_enabled"] is False
        assert body["read_only"] is True
        assert body["live_orders_blocked"] is True
        assert body["max_risk_percent"] <= 1.0
