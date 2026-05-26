"""Tests for PAPER-M4-004 — GET /paper/run/preview endpoint.

Covers:
  - Valid BUY/SELL previews return 200 with allowed=True and a populated paper_run
  - Blocked decisions: risk > 1%, missing SL/TP, invalid BUY/SELL geometry
  - Full pipeline output: order, fill, position inside paper_run
  - All required safety flags present in every response
  - No broker_order_id / account_id / execution_id in any response
  - Route is GET-only (POST/PUT/PATCH/DELETE return 405)
  - Existing /health, /events, /watchlist, /paper/decision/preview unaffected
"""

from __future__ import annotations

import pytest

_KEY = {"x-api-key": "test-key"}  # conftest sets FASTAPI_KEY=test-key
_URL = "/paper/run/preview"

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
# Tests 1–4: valid previews return 200 with allowed=True and a paper_run
# ---------------------------------------------------------------------------


class TestPaperRunPreviewValid:
    def test_valid_buy_returns_200(self, client):
        resp = _get(client, _BUY_VALID)
        assert resp.status_code == 200

    def test_valid_sell_returns_200(self, client):
        resp = _get(client, _SELL_VALID)
        assert resp.status_code == 200

    def test_valid_buy_has_allowed_true(self, client):
        body = _get(client, _BUY_VALID).json()
        assert body["allowed"] is True

    def test_valid_sell_has_allowed_true(self, client):
        body = _get(client, _SELL_VALID).json()
        assert body["allowed"] is True

    def test_valid_buy_has_paper_run(self, client):
        body = _get(client, _BUY_VALID).json()
        assert body["paper_run"] is not None

    def test_valid_sell_has_paper_run(self, client):
        body = _get(client, _SELL_VALID).json()
        assert body["paper_run"] is not None

    def test_valid_preview_has_reason(self, client):
        body = _get(client, _BUY_VALID).json()
        assert "reason" in body
        assert isinstance(body["reason"], str)


# ---------------------------------------------------------------------------
# Tests 5–8: paper_run contains full pipeline output
# ---------------------------------------------------------------------------


class TestPaperRunPreviewPipelineOutput:
    def test_paper_run_has_one_order(self, client):
        run = _get(client, _BUY_VALID).json()["paper_run"]
        assert len(run["orders"]) == 1

    def test_paper_run_has_one_fill(self, client):
        run = _get(client, _BUY_VALID).json()["paper_run"]
        assert len(run["fills"]) == 1

    def test_paper_run_has_one_position(self, client):
        run = _get(client, _BUY_VALID).json()["paper_run"]
        assert len(run["positions"]) == 1

    def test_paper_run_order_symbol_and_direction(self, client):
        run = _get(client, _BUY_VALID).json()["paper_run"]
        order = run["orders"][0]
        assert order["symbol"] == "EURUSD"
        assert order["direction"] == "BUY"

    def test_paper_run_sell_order_direction(self, client):
        run = _get(client, _SELL_VALID).json()["paper_run"]
        assert run["orders"][0]["direction"] == "SELL"

    def test_paper_run_fill_references_order(self, client):
        run = _get(client, _BUY_VALID).json()["paper_run"]
        order_id = run["orders"][0]["paper_order_id"]
        fill_ref = run["fills"][0]["paper_order_ref"]
        assert fill_ref == order_id

    def test_paper_run_position_references_order(self, client):
        run = _get(client, _BUY_VALID).json()["paper_run"]
        order_id = run["orders"][0]["paper_order_id"]
        pos_ref = run["positions"][0]["paper_order_ref"]
        assert pos_ref == order_id

    def test_paper_run_accepted_signals_count(self, client):
        run = _get(client, _BUY_VALID).json()["paper_run"]
        assert run["total_signals"] == 1
        assert run["accepted_signals"] == 1
        assert run["rejected_signals"] == 0

    def test_paper_run_open_positions_count(self, client):
        run = _get(client, _BUY_VALID).json()["paper_run"]
        assert run["open_positions_count"] == 1
        assert run["closed_positions_count"] == 0


# ---------------------------------------------------------------------------
# Tests 9–12: blocked decisions
# ---------------------------------------------------------------------------


class TestPaperRunPreviewBlocked:
    def test_risk_above_1_never_executes(self, client):
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
        params = {**_BUY_VALID, "stop_loss": 1.1050}
        resp = _get(client, params)
        assert resp.status_code == 200
        body = resp.json()
        assert body["allowed"] is False
        assert "BUY" in body["reason"]

    def test_invalid_sell_geometry_sl_below_entry(self, client):
        params = {**_SELL_VALID, "stop_loss": 1.0950}
        resp = _get(client, params)
        assert resp.status_code == 200
        body = resp.json()
        assert body["allowed"] is False
        assert "SELL" in body["reason"]

    def test_blocked_decision_has_no_paper_run(self, client):
        params = {**_BUY_VALID, "stop_loss": 1.1050}
        resp = _get(client, params)
        assert resp.status_code == 200
        assert resp.json()["paper_run"] is None

    def test_blocked_decision_never_enables_execution(self, client):
        params = {**_BUY_VALID, "stop_loss": 1.1050}
        resp = _get(client, params)
        assert resp.status_code == 200
        assert resp.json()["execution_enabled"] is False


# ---------------------------------------------------------------------------
# Tests 13–17: safety flags and forbidden broker fields
# ---------------------------------------------------------------------------


class TestPaperRunPreviewSafetyFlags:
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

    def test_safety_flags_stable_on_sell(self, client):
        body = _get(client, _SELL_VALID).json()
        assert body["paper_only"] is True
        assert body["dry_run"] is True
        assert body["read_only"] is True
        assert body["live_orders_blocked"] is True
        assert body["execution_enabled"] is False

    def test_no_broker_order_id_in_response(self, client):
        body = _get(client, _BUY_VALID).json()
        assert "broker_order_id" not in body
        run = body.get("paper_run") or {}
        for order in run.get("orders", []):
            assert "broker_order_id" not in order
        for fill in run.get("fills", []):
            assert "broker_order_id" not in fill
        for pos in run.get("positions", []):
            assert "broker_order_id" not in pos

    def test_no_account_id_in_response(self, client):
        body = _get(client, _BUY_VALID).json()
        assert "account_id" not in body
        run = body.get("paper_run") or {}
        for order in run.get("orders", []):
            assert "account_id" not in order

    def test_no_execution_id_in_response(self, client):
        body = _get(client, _BUY_VALID).json()
        assert "execution_id" not in body
        run = body.get("paper_run") or {}
        for order in run.get("orders", []):
            assert "execution_id" not in order

    def test_paper_run_carries_safety_flags(self, client):
        run = _get(client, _BUY_VALID).json()["paper_run"]
        assert run["paper_only"] is True
        assert run["dry_run"] is True
        assert run["live_orders_blocked"] is True
        assert run["requires_human_review"] is True
        assert run["execution_enabled"] is False


# ---------------------------------------------------------------------------
# Tests 18–19: route is GET-only
# ---------------------------------------------------------------------------


class TestPaperRunPreviewRouteShape:
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
# Test 20: existing routes unaffected
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

    def test_decision_preview_still_works(self, client):
        resp = client.get("/paper/decision/preview", params=_BUY_VALID, headers=_KEY)
        assert resp.status_code == 200
        assert resp.json()["allowed"] is True

    def test_health_safety_posture_unchanged(self, client):
        body = client.get("/health").json()
        assert body["dry_run"] is True
        assert body["autotrade_enabled"] is False
        assert body["read_only"] is True
        assert body["live_orders_blocked"] is True
        assert body["max_risk_percent"] <= 1.0
