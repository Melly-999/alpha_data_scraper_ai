"""Tests for PAPER-M4-002 — risk-gated paper trading service.

Covers:
  - evaluate_paper_risk: allow / block decisions (risk, geometry, missing fields)
  - create_paper_order: valid construction and safety flags
  - create_paper_fill: deterministic fill, no broker identifiers
  - open_paper_position: paper-only, no live execution
  - create_paper_run: collects objects, preserves safety flags
  - Module hygiene: no broker/MT5/IBKR imports, no route decorators
"""

from __future__ import annotations

import importlib
import inspect
import re

import pytest
from pydantic import ValidationError

from app.services.paper_trading_service import (
    create_paper_fill,
    create_paper_order,
    create_paper_run,
    evaluate_paper_risk,
    open_paper_position,
)

# ---------------------------------------------------------------------------
# Helpers — minimal valid parameters
# ---------------------------------------------------------------------------

_BUY_PARAMS = dict(
    symbol="EURUSD",
    side="BUY",
    quantity=1.0,
    entry_price=1.1000,
    stop_loss=1.0950,
    take_profit=1.1100,
    confidence=0.80,
    max_risk_pct=0.01,
)

_SELL_PARAMS = dict(
    symbol="EURUSD",
    side="SELL",
    quantity=1.0,
    entry_price=1.1000,
    stop_loss=1.1050,
    take_profit=1.0900,
    confidence=0.80,
    max_risk_pct=0.01,
)

_FORBIDDEN_BROKER_FIELDS = {"broker_order_id", "account_id", "execution_id"}


def _make_buy_order():
    return create_paper_order(**_BUY_PARAMS)


# ---------------------------------------------------------------------------
# evaluate_paper_risk — valid decision (allow)
# ---------------------------------------------------------------------------


class TestEvaluatePaperRiskAllow:
    def test_valid_buy_is_allowed(self):
        decision = evaluate_paper_risk(
            direction="BUY",
            entry_price=1.1000,
            stop_loss=1.0950,
            take_profit=1.1100,
            max_risk_pct=0.01,
        )
        assert decision.allowed is True
        assert decision.execution_enabled is False

    def test_valid_sell_is_allowed(self):
        decision = evaluate_paper_risk(
            direction="SELL",
            entry_price=1.1000,
            stop_loss=1.1050,
            take_profit=1.0900,
            max_risk_pct=0.01,
        )
        assert decision.allowed is True
        assert decision.execution_enabled is False

    def test_risk_at_boundary_is_allowed(self):
        decision = evaluate_paper_risk(
            direction="BUY",
            entry_price=1.1000,
            stop_loss=1.0950,
            take_profit=1.1100,
            max_risk_pct=1.0,
        )
        assert decision.allowed is True
        assert decision.execution_enabled is False


# ---------------------------------------------------------------------------
# evaluate_paper_risk — block decisions
# ---------------------------------------------------------------------------


class TestEvaluatePaperRiskBlock:
    def test_blocks_risk_above_1(self):
        decision = evaluate_paper_risk(
            direction="BUY",
            entry_price=1.1000,
            stop_loss=1.0950,
            take_profit=1.1100,
            max_risk_pct=1.01,
        )
        assert decision.allowed is False
        assert "1.0" in decision.reason
        assert decision.execution_enabled is False

    def test_blocks_missing_stop_loss(self):
        decision = evaluate_paper_risk(
            direction="BUY",
            entry_price=1.1000,
            stop_loss=None,
            take_profit=1.1100,
            max_risk_pct=0.01,
        )
        assert decision.allowed is False
        assert "stop_loss" in decision.reason
        assert decision.execution_enabled is False

    def test_blocks_missing_take_profit(self):
        decision = evaluate_paper_risk(
            direction="BUY",
            entry_price=1.1000,
            stop_loss=1.0950,
            take_profit=None,
            max_risk_pct=0.01,
        )
        assert decision.allowed is False
        assert "take_profit" in decision.reason
        assert decision.execution_enabled is False

    def test_blocks_invalid_buy_geometry_sl_above_entry(self):
        decision = evaluate_paper_risk(
            direction="BUY",
            entry_price=1.1000,
            stop_loss=1.1050,
            take_profit=1.1100,
            max_risk_pct=0.01,
        )
        assert decision.allowed is False
        assert "BUY" in decision.reason
        assert decision.execution_enabled is False

    def test_blocks_invalid_buy_geometry_tp_below_entry(self):
        decision = evaluate_paper_risk(
            direction="BUY",
            entry_price=1.1000,
            stop_loss=1.0950,
            take_profit=1.0900,
            max_risk_pct=0.01,
        )
        assert decision.allowed is False
        assert "BUY" in decision.reason
        assert decision.execution_enabled is False

    def test_blocks_invalid_sell_geometry_sl_below_entry(self):
        decision = evaluate_paper_risk(
            direction="SELL",
            entry_price=1.1000,
            stop_loss=1.0950,
            take_profit=1.0900,
            max_risk_pct=0.01,
        )
        assert decision.allowed is False
        assert "SELL" in decision.reason
        assert decision.execution_enabled is False

    def test_blocks_invalid_sell_geometry_tp_above_entry(self):
        decision = evaluate_paper_risk(
            direction="SELL",
            entry_price=1.1000,
            stop_loss=1.1050,
            take_profit=1.1100,
            max_risk_pct=0.01,
        )
        assert decision.allowed is False
        assert "SELL" in decision.reason
        assert decision.execution_enabled is False

    def test_execution_enabled_always_false_on_block(self):
        decision = evaluate_paper_risk(
            direction="BUY",
            entry_price=1.1000,
            stop_loss=1.0950,
            take_profit=1.1100,
            max_risk_pct=5.0,
        )
        assert decision.execution_enabled is False


# ---------------------------------------------------------------------------
# create_paper_order
# ---------------------------------------------------------------------------


class TestCreatePaperOrder:
    def test_valid_buy_order_created(self):
        order = _make_buy_order()
        assert order.symbol == "EURUSD"
        assert order.direction == "BUY"
        assert order.status == "pending"

    def test_valid_sell_order_created(self):
        order = create_paper_order(**_SELL_PARAMS)
        assert order.direction == "SELL"

    def test_safety_flags_enforced(self):
        order = _make_buy_order()
        assert order.paper_only is True
        assert order.dry_run is True
        assert order.live_orders_blocked is True
        assert order.requires_human_review is True
        assert order.execution_enabled is False

    def test_max_risk_pct_above_1_rejected(self):
        with pytest.raises(ValidationError):
            create_paper_order(**{**_BUY_PARAMS, "max_risk_pct": 1.5})

    def test_paper_order_id_has_po_prefix(self):
        order = _make_buy_order()
        assert order.paper_order_id.startswith("po_")


# ---------------------------------------------------------------------------
# create_paper_fill — deterministic, no broker identifiers
# ---------------------------------------------------------------------------


class TestCreatePaperFill:
    def test_fill_created_from_order(self):
        order = _make_buy_order()
        fill = create_paper_fill(order)
        assert fill.symbol == order.symbol
        assert fill.direction == order.direction
        assert fill.fill_price == order.entry_price
        assert fill.quantity == order.quantity

    def test_fill_references_order(self):
        order = _make_buy_order()
        fill = create_paper_fill(order)
        assert fill.paper_order_ref == order.paper_order_id

    def test_fill_has_no_broker_order_id(self):
        order = _make_buy_order()
        fill = create_paper_fill(order)
        assert not hasattr(fill, "broker_order_id")

    def test_fill_has_no_account_id(self):
        order = _make_buy_order()
        fill = create_paper_fill(order)
        assert not hasattr(fill, "account_id")

    def test_fill_has_no_execution_id(self):
        order = _make_buy_order()
        fill = create_paper_fill(order)
        assert not hasattr(fill, "execution_id")

    def test_fill_forbidden_fields_absent_from_schema(self):
        from app.schemas_paper_trading import PaperFill as _PaperFill

        for field_name in _FORBIDDEN_BROKER_FIELDS:
            assert field_name not in _PaperFill.model_fields

    def test_fill_safety_flags(self):
        order = _make_buy_order()
        fill = create_paper_fill(order)
        assert fill.paper_only is True
        assert fill.dry_run is True
        assert fill.execution_enabled is False

    def test_fill_price_is_deterministic(self):
        order = _make_buy_order()
        fill_a = create_paper_fill(order)
        fill_b = create_paper_fill(order)
        assert fill_a.fill_price == fill_b.fill_price
        assert fill_a.paper_order_ref == fill_b.paper_order_ref


# ---------------------------------------------------------------------------
# open_paper_position — paper-only, no live execution
# ---------------------------------------------------------------------------


class TestOpenPaperPosition:
    def _make_trio(self):
        order = _make_buy_order()
        fill = create_paper_fill(order)
        pos = open_paper_position(order, fill)
        return order, fill, pos

    def test_position_created(self):
        order, fill, pos = self._make_trio()
        assert pos.symbol == order.symbol
        assert pos.direction == order.direction
        assert pos.entry_price == order.entry_price
        assert pos.current_price == fill.fill_price
        assert pos.stop_loss == order.stop_loss
        assert pos.take_profit == order.take_profit
        assert pos.status == "open"

    def test_position_is_paper_only(self):
        _, _, pos = self._make_trio()
        assert pos.paper_only is True
        assert pos.dry_run is True
        assert pos.live_orders_blocked is True
        assert pos.requires_human_review is True
        assert pos.execution_enabled is False

    def test_position_forbidden_fields_absent_from_schema(self):
        from app.schemas_paper_trading import PaperPosition as _PaperPosition

        for field_name in _FORBIDDEN_BROKER_FIELDS:
            assert field_name not in _PaperPosition.model_fields

    def test_position_references_order(self):
        order, _, pos = self._make_trio()
        assert pos.paper_order_ref == order.paper_order_id

    def test_unrealized_pnl_zero_at_open(self):
        _, _, pos = self._make_trio()
        assert pos.unrealized_pnl == 0.0


# ---------------------------------------------------------------------------
# create_paper_run — groups objects, preserves safety flags
# ---------------------------------------------------------------------------


class TestCreatePaperRun:
    def _make_run_objects(self):
        order = _make_buy_order()
        fill = create_paper_fill(order)
        pos = open_paper_position(order, fill)
        return order, fill, pos

    def test_run_collects_all_objects(self):
        order, fill, pos = self._make_run_objects()
        run = create_paper_run([order], [fill], [pos])
        assert len(run.orders) == 1
        assert len(run.fills) == 1
        assert len(run.positions) == 1

    def test_run_preserves_all_safety_flags(self):
        order, fill, pos = self._make_run_objects()
        run = create_paper_run([order], [fill], [pos])
        assert run.paper_only is True
        assert run.dry_run is True
        assert run.live_orders_blocked is True
        assert run.requires_human_review is True
        assert run.execution_enabled is False

    def test_run_counts_open_positions(self):
        order, fill, pos = self._make_run_objects()
        run = create_paper_run([order], [fill], [pos])
        assert run.open_positions_count == 1
        assert run.closed_positions_count == 0

    def test_run_counts_accepted_signals(self):
        order, fill, pos = self._make_run_objects()
        run = create_paper_run([order], [fill], [pos])
        assert run.total_signals == 1
        assert run.accepted_signals == 1
        assert run.rejected_signals == 0

    def test_run_max_risk_pct_propagated(self):
        order, fill, pos = self._make_run_objects()
        run = create_paper_run([order], [fill], [pos], max_risk_pct=0.5)
        assert run.max_risk_pct == 0.5

    def test_empty_run_accepted(self):
        run = create_paper_run([], [], [])
        assert run.total_signals == 0
        assert run.execution_enabled is False

    def test_run_id_has_run_prefix(self):
        run = create_paper_run([], [], [])
        assert run.run_id.startswith("run_")


# ---------------------------------------------------------------------------
# Module hygiene — no broker imports, no route decorators
# ---------------------------------------------------------------------------


class TestModuleHygiene:
    def _service_source(self) -> str:
        import app.services.paper_trading_service as svc_mod

        return inspect.getsource(svc_mod)

    def test_no_mt5_import(self):
        src = self._service_source()
        assert "import MetaTrader5" not in src
        assert "import mt5" not in src.lower()

    def test_no_ibkr_import(self):
        src = self._service_source()
        assert "import ib_insync" not in src
        assert "import ibkr" not in src.lower()

    def test_no_broker_execution_symbols(self):
        src = self._service_source()
        assert "place_order" not in src
        assert "execute_order" not in src

    def test_no_route_decorators(self):
        src = self._service_source()
        assert "@app.get" not in src
        assert "@app.post" not in src
        assert "@router.get" not in src
        assert "@router.post" not in src

    def test_no_execution_enabled_true_literal(self):
        src = self._service_source()
        assert "execution_enabled=True" not in src
        assert "execution_enabled = True" not in src

    def test_no_dry_run_false_literal(self):
        src = self._service_source()
        assert "dry_run=False" not in src
        assert "dry_run = False" not in src

    def test_service_importable_without_broker_deps(self):
        mod = importlib.import_module("app.services.paper_trading_service")
        assert hasattr(mod, "evaluate_paper_risk")
        assert hasattr(mod, "create_paper_order")
        assert hasattr(mod, "create_paper_fill")
        assert hasattr(mod, "open_paper_position")
        assert hasattr(mod, "create_paper_run")

    def test_no_mutating_route_decorators_in_service(self):
        src = self._service_source()
        mutating_pattern = re.compile(
            r"@(?:app|router)\.(?:post|put|patch|delete)\s*\("
        )
        assert not mutating_pattern.search(src)
