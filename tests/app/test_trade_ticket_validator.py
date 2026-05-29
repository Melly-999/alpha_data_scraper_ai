"""PDS-001 — Tests for the TradeTicketValidator service."""

from __future__ import annotations

from typing import Any

from app.schemas.trade_ticket import (
    RiskValidationStatus,
    TradeTicketDraft,
)
from app.services.trade_ticket_validator import (
    TradeTicketValidator,
    TradeTicketValidationResult,
    validate_trade_ticket,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_long(**overrides: Any) -> TradeTicketDraft:
    base: dict[str, Any] = dict(
        ticket_id="TKT-LONG-001",
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
    )
    base.update(overrides)
    return TradeTicketDraft(**base)


def _make_short(**overrides: Any) -> TradeTicketDraft:
    base: dict[str, Any] = dict(
        ticket_id="TKT-SHORT-001",
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
    )
    base.update(overrides)
    return TradeTicketDraft(**base)


# ---------------------------------------------------------------------------
# Accepted cases
# ---------------------------------------------------------------------------


def test_accepted_true_for_valid_long():
    result = validate_trade_ticket(_make_long())
    assert result.accepted is True
    assert result.status == RiskValidationStatus.passed
    assert result.rejection_reasons == []


def test_accepted_true_for_valid_short():
    result = validate_trade_ticket(_make_short())
    assert result.accepted is True
    assert result.status == RiskValidationStatus.passed
    assert result.rejection_reasons == []


# ---------------------------------------------------------------------------
# Risk rejection
# ---------------------------------------------------------------------------


def test_rejected_when_risk_above_1_pct():
    # The schema itself enforces risk_pct <= 1.0, so we build a ticket with
    # exactly 1.0 and then temporarily bypass to test the validator layer
    # by calling the validator directly with a mock-like approach.
    # Since the schema blocks >1.0, we verify the validator also rejects it
    # by monkey-patching after construction.
    ticket = _make_long(risk_pct=1.0)
    # Directly manipulate the internal value to simulate a ticket that slipped
    # through (e.g. from an older schema version or direct dict injection).
    object.__setattr__(ticket, "risk_pct", 1.01)

    result = validate_trade_ticket(ticket)
    assert result.accepted is False
    assert any("risk_pct" in r for r in result.rejection_reasons)


def test_accepted_at_exactly_1_pct_risk():
    result = validate_trade_ticket(_make_long(risk_pct=1.0))
    assert result.accepted is True


# ---------------------------------------------------------------------------
# Geometry rejection
# ---------------------------------------------------------------------------


def test_rejected_when_long_geometry_invalid():
    ticket = _make_long()
    # Flip SL above entry to simulate bad geometry post-construction
    object.__setattr__(ticket, "stop_loss", ticket.entry_price + 0.01)

    result = validate_trade_ticket(ticket)
    assert result.accepted is False
    assert any("stop_loss" in r for r in result.rejection_reasons)


def test_rejected_when_short_geometry_invalid():
    ticket = _make_short()
    # Flip SL below entry
    object.__setattr__(ticket, "stop_loss", ticket.entry_price - 0.01)

    result = validate_trade_ticket(ticket)
    assert result.accepted is False
    assert any("stop_loss" in r for r in result.rejection_reasons)


# ---------------------------------------------------------------------------
# Safety flag rejection
# ---------------------------------------------------------------------------


def test_rejected_when_paper_only_false():
    ticket = _make_long()
    object.__setattr__(ticket, "paper_only", False)
    result = validate_trade_ticket(ticket)
    assert result.accepted is False
    assert any("paper_only" in r for r in result.rejection_reasons)


def test_rejected_when_dry_run_false():
    ticket = _make_long()
    object.__setattr__(ticket, "dry_run", False)
    result = validate_trade_ticket(ticket)
    assert result.accepted is False
    assert any("dry_run" in r for r in result.rejection_reasons)


def test_rejected_when_read_only_false():
    ticket = _make_long()
    object.__setattr__(ticket, "read_only", False)
    result = validate_trade_ticket(ticket)
    assert result.accepted is False
    assert any("read_only" in r for r in result.rejection_reasons)


def test_rejected_when_live_orders_blocked_false():
    ticket = _make_long()
    object.__setattr__(ticket, "live_orders_blocked", False)
    result = validate_trade_ticket(ticket)
    assert result.accepted is False
    assert any("live_orders_blocked" in r for r in result.rejection_reasons)


def test_rejected_when_requires_human_review_false():
    ticket = _make_long()
    object.__setattr__(ticket, "requires_human_review", False)
    result = validate_trade_ticket(ticket)
    assert result.accepted is False
    assert any("requires_human_review" in r for r in result.rejection_reasons)


def test_rejected_when_broker_execution_allowed_true():
    ticket = _make_long()
    object.__setattr__(ticket, "broker_execution_allowed", True)
    result = validate_trade_ticket(ticket)
    assert result.accepted is False
    assert any("broker_execution_allowed" in r for r in result.rejection_reasons)


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


def test_warning_when_confidence_below_70():
    ticket = _make_long(confidence=65.0, take_profit_2=1.1200)
    result = validate_trade_ticket(ticket)
    assert result.accepted is True
    assert any("confidence" in w for w in result.warnings)


def test_warning_when_tp2_missing():
    # Build without take_profit_2
    ticket = TradeTicketDraft(
        ticket_id="TKT-WARN",
        symbol="EURUSD",
        side="long",
        entry_type="manual",
        timeframe="H1",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit_1=1.1100,
        risk_pct=0.5,
        confidence=80.0,
        reason="Test warning on missing TP2",
    )
    result = validate_trade_ticket(ticket)
    assert result.accepted is True
    assert any("take_profit_2" in w for w in result.warnings)


def test_no_warning_when_confidence_exactly_70():
    ticket = _make_long(confidence=70.0)
    result = validate_trade_ticket(ticket)
    # No confidence warning at exactly 70
    assert not any("confidence" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# Safety invariants on accepted result
# ---------------------------------------------------------------------------


def test_accepted_result_never_flips_risk_allowed_to_true():
    result = validate_trade_ticket(_make_long())
    assert result.accepted is True
    assert result.normalized_ticket.risk_allowed is False
    assert result.safety_contract["risk_allowed"] is False


def test_accepted_result_never_enables_broker_execution():
    result = validate_trade_ticket(_make_long())
    assert result.accepted is True
    assert result.normalized_ticket.broker_execution_allowed is False
    assert result.safety_contract["broker_execution_allowed"] is False


def test_safety_contract_contains_required_fields():
    result = validate_trade_ticket(_make_long())
    sc = result.safety_contract
    assert sc["paper_only"] is True
    assert sc["dry_run"] is True
    assert sc["read_only"] is True
    assert sc["live_orders_blocked"] is True
    assert sc["max_risk_pct"] == 1.0


def test_safety_contract_execution_mode_is_paper_only_draft():
    result = validate_trade_ticket(_make_long())
    assert result.safety_contract["execution_mode"] == "paper_only_draft"


# ---------------------------------------------------------------------------
# Validator has no network/broker side effects (import check)
# ---------------------------------------------------------------------------


def test_validator_has_no_network_imports():
    import app.services.trade_ticket_validator as mod
    import sys

    network_modules = {
        "requests",
        "httpx",
        "aiohttp",
        "urllib3",
        "MetaTrader5",
        "mt5",
        "ibapi",
        "ib_insync",
        "supabase",
        "postgrest",
    }
    loaded = set(sys.modules.keys())
    # None of the network/broker modules should be imported as a side effect
    # of importing the validator
    for net_mod in network_modules:
        assert net_mod not in loaded or not any(
            net_mod in m for m in dir(mod)
        ), f"Unexpected network module reference: {net_mod}"


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------


def test_validate_trade_ticket_function_returns_result():
    result = validate_trade_ticket(_make_short())
    assert isinstance(result, TradeTicketValidationResult)
    assert result.accepted is True


# ---------------------------------------------------------------------------
# Validator instance is reusable
# ---------------------------------------------------------------------------


def test_validator_is_reusable():
    validator = TradeTicketValidator()
    r1 = validator.validate(_make_long())
    r2 = validator.validate(_make_short())
    assert r1.accepted is True
    assert r2.accepted is True
