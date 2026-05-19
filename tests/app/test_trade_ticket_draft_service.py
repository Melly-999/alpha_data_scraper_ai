"""PDS-002 — Tests for TradeTicketDraftService."""

from __future__ import annotations

from typing import Any

from app.services.trade_ticket_draft_service import (
    TradeTicketDraftInput,
    TradeTicketDraftResult,
    TradeTicketDraftService,
    create_trade_ticket_draft,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _long_input(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = dict(
        symbol="EURUSD",
        side="long",
        entry_type="market_simulated",
        timeframe="H1",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit_1=1.1100,
        take_profit_2=1.1200,
        risk_pct=0.5,
        confidence=80.0,
        reason="Strong H1 bullish momentum",
        source="scanner_preview",
    )
    base.update(overrides)
    return base


def _short_input(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = dict(
        symbol="GBPUSD",
        side="short",
        entry_type="breakout",
        timeframe="H4",
        entry_price=1.3000,
        stop_loss=1.3060,
        take_profit_1=1.2900,
        take_profit_2=1.2800,
        risk_pct=0.8,
        confidence=75.0,
        reason="Bearish breakout below support",
        source="scanner_preview",
    )
    base.update(overrides)
    return base


_svc = TradeTicketDraftService()


# ---------------------------------------------------------------------------
# Accepted cases
# ---------------------------------------------------------------------------

def test_creates_accepted_draft_from_valid_long_input():
    result = _svc.create(_long_input())
    assert result.accepted is True
    assert result.draft is not None
    assert result.validation is not None
    assert result.rejection_reasons == []


def test_creates_accepted_draft_from_valid_short_input():
    result = _svc.create(_short_input())
    assert result.accepted is True
    assert result.draft is not None
    assert result.rejection_reasons == []


# ---------------------------------------------------------------------------
# Symbol normalisation
# ---------------------------------------------------------------------------

def test_normalises_symbol_uppercase():
    result = _svc.create(_long_input(symbol="eurusd"))
    assert result.accepted is True
    assert result.draft is not None
    assert result.draft.symbol == "EURUSD"


def test_normalises_symbol_with_whitespace():
    result = _svc.create(_long_input(symbol="  eurjpy  "))
    assert result.accepted is True
    assert result.draft is not None
    assert result.draft.symbol == "EURJPY"


# ---------------------------------------------------------------------------
# Deterministic ticket_id
# ---------------------------------------------------------------------------

def test_deterministic_ticket_id_same_input():
    r1 = _svc.create(_long_input())
    r2 = _svc.create(_long_input())
    assert r1.draft is not None and r2.draft is not None
    assert r1.draft.ticket_id == r2.draft.ticket_id


def test_ticket_id_differs_for_different_symbol():
    r_eur = _svc.create(_long_input(symbol="EURUSD"))
    r_gbp = _svc.create(_long_input(symbol="GBPUSD"))
    assert r_eur.draft is not None and r_gbp.draft is not None
    assert r_eur.draft.ticket_id != r_gbp.draft.ticket_id


def test_ticket_id_differs_for_different_side():
    r_long = _svc.create(_long_input())
    r_short = _svc.create(
        _short_input(
            symbol="EURUSD", timeframe="H1", source="scanner_preview"
        )
    )
    assert r_long.draft is not None and r_short.draft is not None
    assert r_long.draft.ticket_id != r_short.draft.ticket_id


def test_ticket_id_has_expected_prefix():
    result = _svc.create(_long_input(source="scanner_preview"))
    assert result.draft is not None
    assert result.draft.ticket_id.startswith("paper-scanner_preview-EURUSD-H1-long-")


# ---------------------------------------------------------------------------
# Risk rejection
# ---------------------------------------------------------------------------

def test_rejects_risk_pct_above_1():
    result = _svc.create(_long_input(risk_pct=1.01))
    assert result.accepted is False
    assert result.draft is None
    assert any("risk_pct" in r or "le" in r.lower() for r in result.rejection_reasons)


def test_accepts_risk_pct_exactly_1():
    result = _svc.create(_long_input(risk_pct=1.0))
    assert result.accepted is True


def test_rejects_risk_pct_zero():
    result = _svc.create(_long_input(risk_pct=0.0))
    assert result.accepted is False


# ---------------------------------------------------------------------------
# Geometry rejection
# ---------------------------------------------------------------------------

def test_rejects_invalid_long_geometry_sl_above_entry():
    result = _svc.create(_long_input(stop_loss=1.1100))  # SL > entry
    assert result.accepted is False
    assert any("stop_loss" in r for r in result.rejection_reasons)


def test_rejects_invalid_long_geometry_tp_below_entry():
    result = _svc.create(_long_input(take_profit_1=1.0900))  # TP < entry
    assert result.accepted is False
    assert any("take_profit_1" in r or "above" in r for r in result.rejection_reasons)


def test_rejects_invalid_short_geometry_sl_below_entry():
    result = _svc.create(_short_input(stop_loss=1.2950))  # SL < entry
    assert result.accepted is False
    assert any("stop_loss" in r for r in result.rejection_reasons)


def test_rejects_invalid_short_geometry_tp_above_entry():
    result = _svc.create(_short_input(take_profit_1=1.3100))  # TP > entry
    assert result.accepted is False
    assert any("take_profit_1" in r or "below" in r for r in result.rejection_reasons)


# ---------------------------------------------------------------------------
# Missing SL / TP
# ---------------------------------------------------------------------------

def test_rejects_missing_stop_loss():
    data = _long_input()
    data.pop("stop_loss")
    result = _svc.create(data)
    assert result.accepted is False
    assert any("stop_loss" in r for r in result.rejection_reasons)


def test_rejects_missing_take_profit():
    data = _long_input()
    data.pop("take_profit_1")
    result = _svc.create(data)
    assert result.accepted is False
    assert any("take_profit_1" in r for r in result.rejection_reasons)


# ---------------------------------------------------------------------------
# Reason
# ---------------------------------------------------------------------------

def test_rejects_empty_reason():
    result = _svc.create(_long_input(reason=""))
    assert result.accepted is False
    assert any("reason" in r for r in result.rejection_reasons)


def test_rejects_blank_reason():
    result = _svc.create(_long_input(reason="   "))
    assert result.accepted is False


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------

def test_warning_when_confidence_below_70():
    result = _svc.create(_long_input(confidence=60.0))
    assert result.accepted is True
    assert any("confidence" in w for w in result.warnings)


def test_warning_when_take_profit_2_missing():
    data = _long_input()
    data.pop("take_profit_2")
    result = _svc.create(data)
    assert result.accepted is True
    assert any("take_profit_2" in w for w in result.warnings)


def test_no_confidence_warning_at_exactly_70():
    result = _svc.create(_long_input(confidence=70.0))
    assert not any("confidence" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# Forced safety fields
# ---------------------------------------------------------------------------

def test_always_forces_paper_only_true():
    result = _svc.create(_long_input())
    assert result.draft is not None
    assert result.draft.paper_only is True


def test_always_forces_dry_run_true():
    result = _svc.create(_long_input())
    assert result.draft is not None
    assert result.draft.dry_run is True


def test_always_forces_read_only_true():
    result = _svc.create(_long_input())
    assert result.draft is not None
    assert result.draft.read_only is True


def test_always_forces_live_orders_blocked_true():
    result = _svc.create(_long_input())
    assert result.draft is not None
    assert result.draft.live_orders_blocked is True


def test_always_forces_requires_human_review_true():
    result = _svc.create(_long_input())
    assert result.draft is not None
    assert result.draft.requires_human_review is True


def test_always_keeps_risk_allowed_false():
    result = _svc.create(_long_input())
    assert result.draft is not None
    assert result.draft.risk_allowed is False
    assert result.safety_contract["risk_allowed"] is False


def test_always_keeps_broker_execution_allowed_false():
    result = _svc.create(_long_input())
    assert result.draft is not None
    assert result.draft.broker_execution_allowed is False
    assert result.safety_contract["broker_execution_allowed"] is False


# ---------------------------------------------------------------------------
# Safety contract
# ---------------------------------------------------------------------------

def test_result_safety_contract_contains_max_risk_pct_1():
    result = _svc.create(_long_input())
    assert result.safety_contract["max_risk_pct"] == 1.0


def test_result_safety_contract_paper_and_dry_run():
    result = _svc.create(_long_input())
    sc = result.safety_contract
    assert sc["paper_only"] is True
    assert sc["dry_run"] is True
    assert sc["read_only"] is True
    assert sc["live_orders_blocked"] is True
    assert sc["execution_mode"] == "paper_only_draft"


def test_rejected_result_still_has_safety_contract():
    result = _svc.create(_long_input(risk_pct=2.0))
    assert result.accepted is False
    assert result.safety_contract["paper_only"] is True
    assert result.safety_contract["risk_allowed"] is False


# ---------------------------------------------------------------------------
# Malformed input
# ---------------------------------------------------------------------------

def test_malformed_dict_input_returns_accepted_false():
    result = _svc.create({"symbol": "EURUSD", "side": "long"})  # many fields missing
    assert result.accepted is False
    assert result.draft is None
    assert len(result.rejection_reasons) > 0


def test_malformed_input_no_internal_exception_leaked():
    result = _svc.create({"symbol": "!@#", "side": "long"})
    assert result.accepted is False
    # rejection reasons should be strings, not exception objects
    for r in result.rejection_reasons:
        assert isinstance(r, str)


def test_completely_empty_dict_returns_accepted_false():
    result = _svc.create({})
    assert result.accepted is False
    assert result.draft is None


# ---------------------------------------------------------------------------
# No live execution fields in result
# ---------------------------------------------------------------------------

def test_no_live_execution_fields_in_result():
    result = _svc.create(_long_input())
    result_dict = result.model_dump()
    forbidden = {
        "order_id", "fill_id", "execution_id", "broker_order_id",
        "account_id", "credential", "token", "secret",
    }
    for key in forbidden:
        assert key not in result_dict, f"Forbidden field found: {key}"


def test_no_live_execution_fields_in_draft():
    result = _svc.create(_long_input())
    assert result.draft is not None
    draft_dict = result.draft.model_dump()
    forbidden = {
        "order_id", "fill_id", "execution_id", "broker_order_id",
        "account_id", "credential", "token", "secret",
    }
    for key in forbidden:
        assert key not in draft_dict, f"Forbidden field found in draft: {key}"


# ---------------------------------------------------------------------------
# No broker/network side effects (module-level import check)
# ---------------------------------------------------------------------------

def test_service_has_no_broker_network_side_effects():
    import app.services.trade_ticket_draft_service as mod

    network_modules = {
        "requests", "httpx", "aiohttp", "urllib3",
        "MetaTrader5", "ibapi", "ib_insync",
        "supabase", "postgrest",
    }
    for net_mod in network_modules:
        assert net_mod not in dir(mod), (
            f"Unexpected network module reference in draft service: {net_mod}"
        )


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------

def test_create_trade_ticket_draft_function():
    result = create_trade_ticket_draft(_long_input())
    assert isinstance(result, TradeTicketDraftResult)
    assert result.accepted is True


def test_service_is_reusable():
    svc = TradeTicketDraftService()
    r1 = svc.create(_long_input())
    r2 = svc.create(_short_input())
    assert r1.accepted is True
    assert r2.accepted is True


# ---------------------------------------------------------------------------
# TradeTicketDraftInput model
# ---------------------------------------------------------------------------

def test_draft_input_accepts_valid_long():
    inp = TradeTicketDraftInput(**_long_input())
    assert inp.symbol == "EURUSD"
    assert inp.side.value == "long"


def test_draft_input_rejects_extra_fields():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        TradeTicketDraftInput(**_long_input(), unknown_field="bad")
