"""Tests for PAPER-M4-001 — paper trading domain model schemas.

Covers:
  - Valid construction of all four models
  - Safety flag enforcement (Literal constants cannot be overridden)
  - Geometry validation for PaperOrder (BUY and SELL)
  - max_risk_pct <= 1.0 enforcement
  - extra="forbid" on every model
  - Forbidden field names never appear in any model schema
  - Serialization round-trip
  - ID prefix conventions
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas_paper_trading import (
    PaperFill,
    PaperOrder,
    PaperPosition,
    PaperRun,
)

# ---------------------------------------------------------------------------
# Helpers — minimal valid payloads
# ---------------------------------------------------------------------------

_BUY_ORDER = dict(
    symbol="EURUSD",
    direction="BUY",
    quantity=1.0,
    entry_price=1.1000,
    stop_loss=1.0950,
    take_profit=1.1100,
    max_risk_pct=0.01,
)

_SELL_ORDER = dict(
    symbol="EURUSD",
    direction="SELL",
    quantity=1.0,
    entry_price=1.1000,
    stop_loss=1.1050,
    take_profit=1.0900,
    max_risk_pct=0.01,
)

_FILL = dict(
    paper_order_ref="po_abc123",
    symbol="EURUSD",
    direction="BUY",
    fill_price=1.1000,
    quantity=1.0,
)

_POSITION = dict(
    paper_order_ref="po_abc123",
    symbol="EURUSD",
    direction="BUY",
    quantity=1.0,
    entry_price=1.1000,
    current_price=1.1020,
    stop_loss=1.0950,
    take_profit=1.1100,
    max_risk_pct=0.01,
)

_FORBIDDEN_FIELD_NAMES = {
    "order_id",
    "fill_id",
    "execution_id",
    "broker_order_id",
    "ibkr_order_id",
    "mt5_ticket",
    "account_id",
    "broker_account_id",
    "credential",
    "secret",
    "token",
    "api_key",
    "password",
}


# ---------------------------------------------------------------------------
# PaperOrder — valid construction
# ---------------------------------------------------------------------------


class TestPaperOrderValid:
    def test_buy_order_accepted(self):
        order = PaperOrder(**_BUY_ORDER)
        assert order.symbol == "EURUSD"
        assert order.direction == "BUY"
        assert order.status == "pending"

    def test_sell_order_accepted(self):
        order = PaperOrder(**_SELL_ORDER)
        assert order.direction == "SELL"

    def test_id_has_po_prefix(self):
        order = PaperOrder(**_BUY_ORDER)
        assert order.paper_order_id.startswith("po_")

    def test_created_at_is_set(self):
        order = PaperOrder(**_BUY_ORDER)
        assert order.created_at is not None

    def test_rejection_reason_defaults_none(self):
        order = PaperOrder(**_BUY_ORDER)
        assert order.rejection_reason is None


# ---------------------------------------------------------------------------
# PaperOrder — safety flags
# ---------------------------------------------------------------------------


class TestPaperOrderSafetyFlags:
    def test_paper_only_is_true(self):
        assert PaperOrder(**_BUY_ORDER).paper_only is True

    def test_dry_run_is_true(self):
        assert PaperOrder(**_BUY_ORDER).dry_run is True

    def test_live_orders_blocked_is_true(self):
        assert PaperOrder(**_BUY_ORDER).live_orders_blocked is True

    def test_requires_human_review_is_true(self):
        assert PaperOrder(**_BUY_ORDER).requires_human_review is True

    def test_execution_enabled_is_false(self):
        assert PaperOrder(**_BUY_ORDER).execution_enabled is False

    def test_cannot_override_paper_only(self):
        with pytest.raises(ValidationError):
            PaperOrder(**_BUY_ORDER, paper_only=False)

    def test_cannot_override_dry_run(self):
        with pytest.raises(ValidationError):
            PaperOrder(**_BUY_ORDER, dry_run=False)

    def test_cannot_override_execution_enabled(self):
        with pytest.raises(ValidationError):
            PaperOrder(**_BUY_ORDER, execution_enabled=True)

    def test_cannot_override_live_orders_blocked(self):
        with pytest.raises(ValidationError):
            PaperOrder(**_BUY_ORDER, live_orders_blocked=False)

    def test_cannot_override_requires_human_review(self):
        with pytest.raises(ValidationError):
            PaperOrder(**_BUY_ORDER, requires_human_review=False)


# ---------------------------------------------------------------------------
# PaperOrder — risk constraint
# ---------------------------------------------------------------------------


class TestPaperOrderRisk:
    def test_max_risk_pct_at_boundary_accepted(self):
        order = PaperOrder(**{**_BUY_ORDER, "max_risk_pct": 1.0})
        assert order.max_risk_pct == 1.0

    def test_max_risk_pct_above_1_rejected(self):
        with pytest.raises(ValidationError):
            PaperOrder(**{**_BUY_ORDER, "max_risk_pct": 1.01})

    def test_max_risk_pct_zero_rejected(self):
        with pytest.raises(ValidationError):
            PaperOrder(**{**_BUY_ORDER, "max_risk_pct": 0.0})


# ---------------------------------------------------------------------------
# PaperOrder — geometry validation (BUY)
# ---------------------------------------------------------------------------


class TestPaperOrderGeometryBuy:
    def test_buy_sl_equal_entry_rejected(self):
        with pytest.raises(ValidationError, match="stop_loss must be strictly below"):
            PaperOrder(**{**_BUY_ORDER, "stop_loss": 1.1000})

    def test_buy_sl_above_entry_rejected(self):
        with pytest.raises(ValidationError, match="stop_loss must be strictly below"):
            PaperOrder(**{**_BUY_ORDER, "stop_loss": 1.1050})

    def test_buy_tp_equal_entry_rejected(self):
        with pytest.raises(ValidationError, match="take_profit must be strictly above"):
            PaperOrder(**{**_BUY_ORDER, "take_profit": 1.1000})

    def test_buy_tp_below_entry_rejected(self):
        with pytest.raises(ValidationError, match="take_profit must be strictly above"):
            PaperOrder(**{**_BUY_ORDER, "take_profit": 1.0950})


# ---------------------------------------------------------------------------
# PaperOrder — geometry validation (SELL)
# ---------------------------------------------------------------------------


class TestPaperOrderGeometrySell:
    def test_sell_sl_equal_entry_rejected(self):
        with pytest.raises(ValidationError, match="stop_loss must be strictly above"):
            PaperOrder(**{**_SELL_ORDER, "stop_loss": 1.1000})

    def test_sell_sl_below_entry_rejected(self):
        with pytest.raises(ValidationError, match="stop_loss must be strictly above"):
            PaperOrder(**{**_SELL_ORDER, "stop_loss": 1.0950})

    def test_sell_tp_equal_entry_rejected(self):
        with pytest.raises(ValidationError, match="take_profit must be strictly below"):
            PaperOrder(**{**_SELL_ORDER, "take_profit": 1.1000})

    def test_sell_tp_above_entry_rejected(self):
        with pytest.raises(ValidationError, match="take_profit must be strictly below"):
            PaperOrder(**{**_SELL_ORDER, "take_profit": 1.1050})


# ---------------------------------------------------------------------------
# PaperOrder — extra fields forbidden
# ---------------------------------------------------------------------------


class TestPaperOrderExtraForbidden:
    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            PaperOrder(**_BUY_ORDER, unexpected_field="x")

    @pytest.mark.parametrize("field", sorted(_FORBIDDEN_FIELD_NAMES))
    def test_forbidden_field_rejected(self, field: str):
        with pytest.raises(ValidationError):
            PaperOrder(**_BUY_ORDER, **{field: "x"})


# ---------------------------------------------------------------------------
# PaperOrder — forbidden field names not in schema
# ---------------------------------------------------------------------------


class TestPaperOrderForbiddenFieldsAbsent:
    @pytest.mark.parametrize("field", sorted(_FORBIDDEN_FIELD_NAMES))
    def test_forbidden_field_not_in_model_fields(self, field: str):
        assert field not in PaperOrder.model_fields


# ---------------------------------------------------------------------------
# PaperOrder — serialization round-trip
# ---------------------------------------------------------------------------


class TestPaperOrderRoundTrip:
    def test_round_trip(self):
        original = PaperOrder(**_BUY_ORDER)
        data = original.model_dump()
        restored = PaperOrder.model_validate(data)
        assert restored.paper_order_id == original.paper_order_id
        assert restored.execution_enabled is False
        assert restored.paper_only is True


# ---------------------------------------------------------------------------
# PaperFill — valid construction and safety flags
# ---------------------------------------------------------------------------


class TestPaperFillValid:
    def test_fill_accepted(self):
        fill = PaperFill(**_FILL)
        assert fill.symbol == "EURUSD"
        assert fill.fill_price == 1.1000

    def test_id_has_pf_prefix(self):
        fill = PaperFill(**_FILL)
        assert fill.paper_fill_id.startswith("pf_")

    def test_paper_order_ref_stored(self):
        fill = PaperFill(**_FILL)
        assert fill.paper_order_ref == "po_abc123"

    def test_safety_flags(self):
        fill = PaperFill(**_FILL)
        assert fill.paper_only is True
        assert fill.dry_run is True
        assert fill.live_orders_blocked is True
        assert fill.requires_human_review is True
        assert fill.execution_enabled is False

    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            PaperFill(**_FILL, unexpected="x")

    @pytest.mark.parametrize("field", sorted(_FORBIDDEN_FIELD_NAMES))
    def test_forbidden_field_not_in_schema(self, field: str):
        assert field not in PaperFill.model_fields

    def test_cannot_override_execution_enabled(self):
        with pytest.raises(ValidationError):
            PaperFill(**_FILL, execution_enabled=True)

    def test_round_trip(self):
        original = PaperFill(**_FILL)
        restored = PaperFill.model_validate(original.model_dump())
        assert restored.paper_fill_id == original.paper_fill_id
        assert restored.execution_enabled is False


# ---------------------------------------------------------------------------
# PaperPosition — valid construction and safety flags
# ---------------------------------------------------------------------------


class TestPaperPositionValid:
    def test_position_accepted(self):
        pos = PaperPosition(**_POSITION)
        assert pos.symbol == "EURUSD"
        assert pos.status == "open"

    def test_id_has_pp_prefix(self):
        pos = PaperPosition(**_POSITION)
        assert pos.paper_position_id.startswith("pp_")

    def test_unrealized_pnl_defaults_zero(self):
        pos = PaperPosition(**_POSITION)
        assert pos.unrealized_pnl == 0.0

    def test_closed_at_defaults_none(self):
        pos = PaperPosition(**_POSITION)
        assert pos.closed_at is None

    def test_safety_flags(self):
        pos = PaperPosition(**_POSITION)
        assert pos.paper_only is True
        assert pos.dry_run is True
        assert pos.live_orders_blocked is True
        assert pos.requires_human_review is True
        assert pos.execution_enabled is False

    def test_max_risk_pct_above_1_rejected(self):
        with pytest.raises(ValidationError):
            PaperPosition(**{**_POSITION, "max_risk_pct": 1.5})

    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            PaperPosition(**_POSITION, unexpected="x")

    @pytest.mark.parametrize("field", sorted(_FORBIDDEN_FIELD_NAMES))
    def test_forbidden_field_not_in_schema(self, field: str):
        assert field not in PaperPosition.model_fields

    def test_cannot_override_execution_enabled(self):
        with pytest.raises(ValidationError):
            PaperPosition(**_POSITION, execution_enabled=True)

    def test_round_trip(self):
        original = PaperPosition(**_POSITION)
        restored = PaperPosition.model_validate(original.model_dump())
        assert restored.paper_position_id == original.paper_position_id
        assert restored.execution_enabled is False


# ---------------------------------------------------------------------------
# PaperRun — valid construction and collections
# ---------------------------------------------------------------------------


class TestPaperRunValid:
    def test_empty_run_accepted(self):
        run = PaperRun()
        assert run.total_signals == 0
        assert run.orders == []
        assert run.positions == []
        assert run.fills == []

    def test_id_has_run_prefix(self):
        run = PaperRun()
        assert run.run_id.startswith("run_")

    def test_ended_at_defaults_none(self):
        run = PaperRun()
        assert run.ended_at is None

    def test_safety_flags(self):
        run = PaperRun()
        assert run.paper_only is True
        assert run.dry_run is True
        assert run.live_orders_blocked is True
        assert run.requires_human_review is True
        assert run.execution_enabled is False

    def test_max_risk_pct_defaults_to_1(self):
        run = PaperRun()
        assert run.max_risk_pct == 1.0

    def test_max_risk_pct_above_1_rejected(self):
        with pytest.raises(ValidationError):
            PaperRun(max_risk_pct=1.01)

    def test_run_collects_order(self):
        order = PaperOrder(**_BUY_ORDER)
        run = PaperRun(orders=[order])
        assert len(run.orders) == 1
        assert run.orders[0].paper_order_id == order.paper_order_id

    def test_run_collects_position(self):
        pos = PaperPosition(**_POSITION)
        run = PaperRun(positions=[pos])
        assert len(run.positions) == 1

    def test_run_collects_fill(self):
        fill = PaperFill(**_FILL)
        run = PaperRun(fills=[fill])
        assert len(run.fills) == 1

    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            PaperRun(unexpected="x")

    @pytest.mark.parametrize("field", sorted(_FORBIDDEN_FIELD_NAMES))
    def test_forbidden_field_not_in_schema(self, field: str):
        assert field not in PaperRun.model_fields

    def test_cannot_override_execution_enabled(self):
        with pytest.raises(ValidationError):
            PaperRun(execution_enabled=True)

    def test_round_trip(self):
        order = PaperOrder(**_BUY_ORDER)
        run = PaperRun(orders=[order], total_signals=1, accepted_signals=1)
        restored = PaperRun.model_validate(run.model_dump())
        assert restored.run_id == run.run_id
        assert len(restored.orders) == 1
        assert restored.execution_enabled is False
