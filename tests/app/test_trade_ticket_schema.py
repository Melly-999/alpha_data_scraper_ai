"""PDS-001 — Tests for the TradeTicketDraft schema."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.trade_ticket import (
    RiskValidationStatus,
    TicketStatus,
    TradeSide,
    TradeTicketDraft,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _long_ticket(**overrides) -> dict:
    base = dict(
        ticket_id="TKT-001",
        symbol="EURUSD",
        side="long",
        entry_type="market_simulated",
        timeframe="H1",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit_1=1.1100,
        risk_pct=0.5,
        confidence=80.0,
        reason="Strong bullish momentum on H1",
    )
    base.update(overrides)
    return base


def _short_ticket(**overrides) -> dict:
    base = dict(
        ticket_id="TKT-002",
        symbol="GBPUSD",
        side="short",
        entry_type="breakout",
        timeframe="H4",
        entry_price=1.3000,
        stop_loss=1.3060,
        take_profit_1=1.2900,
        risk_pct=0.8,
        confidence=75.0,
        reason="Bearish breakout below key support",
    )
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Valid drafts
# ---------------------------------------------------------------------------

def test_valid_long_draft_passes():
    ticket = TradeTicketDraft(**_long_ticket())
    assert ticket.side == TradeSide.long
    assert ticket.symbol == "EURUSD"
    assert ticket.paper_only is True
    assert ticket.dry_run is True


def test_valid_short_draft_passes():
    ticket = TradeTicketDraft(**_short_ticket())
    assert ticket.side == TradeSide.short
    assert ticket.symbol == "GBPUSD"
    assert ticket.paper_only is True


# ---------------------------------------------------------------------------
# Symbol normalisation
# ---------------------------------------------------------------------------

def test_symbol_normalised_to_uppercase():
    ticket = TradeTicketDraft(**_long_ticket(symbol="eurusd"))
    assert ticket.symbol == "EURUSD"


def test_symbol_with_whitespace_stripped_and_uppercased():
    ticket = TradeTicketDraft(**_long_ticket(symbol="  eurjpy  "))
    assert ticket.symbol == "EURJPY"


def test_rejects_empty_symbol():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(symbol=""))


def test_rejects_blank_symbol():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(symbol="   "))


# ---------------------------------------------------------------------------
# Risk percentage
# ---------------------------------------------------------------------------

def test_rejects_risk_pct_above_1():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(risk_pct=1.01))


def test_rejects_risk_pct_zero():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(risk_pct=0.0))


def test_accepts_risk_pct_exactly_1():
    ticket = TradeTicketDraft(**_long_ticket(risk_pct=1.0))
    assert ticket.risk_pct == 1.0


# ---------------------------------------------------------------------------
# Confidence
# ---------------------------------------------------------------------------

def test_rejects_confidence_above_100():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(confidence=100.1))


def test_rejects_confidence_below_0():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(confidence=-0.1))


def test_accepts_confidence_at_boundaries():
    t0 = TradeTicketDraft(**_long_ticket(confidence=0.0))
    t100 = TradeTicketDraft(**_long_ticket(confidence=100.0))
    assert t0.confidence == 0.0
    assert t100.confidence == 100.0


# ---------------------------------------------------------------------------
# Reason
# ---------------------------------------------------------------------------

def test_rejects_missing_reason():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(reason=""))


def test_rejects_blank_reason():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(reason="   "))


# ---------------------------------------------------------------------------
# Long geometry
# ---------------------------------------------------------------------------

def test_rejects_long_sl_above_entry():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(stop_loss=1.1100))  # SL > entry


def test_rejects_long_sl_equal_entry():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(stop_loss=1.1000))  # SL == entry


def test_rejects_long_tp1_below_entry():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(take_profit_1=1.0900))  # TP < entry


def test_rejects_long_tp1_equal_entry():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(take_profit_1=1.1000))  # TP == entry


def test_rejects_long_tp2_below_entry():
    with pytest.raises(ValidationError):
        TradeTicketDraft(
            **_long_ticket(take_profit_1=1.1100, take_profit_2=1.0800)
        )


# ---------------------------------------------------------------------------
# Short geometry
# ---------------------------------------------------------------------------

def test_rejects_short_sl_below_entry():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_short_ticket(stop_loss=1.2950))  # SL < entry


def test_rejects_short_sl_equal_entry():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_short_ticket(stop_loss=1.3000))  # SL == entry


def test_rejects_short_tp1_above_entry():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_short_ticket(take_profit_1=1.3100))  # TP > entry


def test_rejects_short_tp1_equal_entry():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_short_ticket(take_profit_1=1.3000))  # TP == entry


def test_rejects_short_tp2_above_entry():
    with pytest.raises(ValidationError):
        TradeTicketDraft(
            **_short_ticket(take_profit_1=1.2900, take_profit_2=1.3100)
        )


# ---------------------------------------------------------------------------
# Immutable safety fields
# ---------------------------------------------------------------------------

def test_rejects_paper_only_false():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(paper_only=False))


def test_rejects_dry_run_false():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(dry_run=False))


def test_rejects_read_only_false():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(read_only=False))


def test_rejects_live_orders_blocked_false():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(live_orders_blocked=False))


def test_rejects_requires_human_review_false():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(requires_human_review=False))


def test_rejects_broker_execution_allowed_true():
    with pytest.raises(ValidationError):
        TradeTicketDraft(**_long_ticket(broker_execution_allowed=True))


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

def test_default_risk_allowed_is_false():
    ticket = TradeTicketDraft(**_long_ticket())
    assert ticket.risk_allowed is False


def test_default_status_is_draft():
    ticket = TradeTicketDraft(**_long_ticket())
    assert ticket.status == TicketStatus.draft


def test_default_risk_validation_status_is_not_checked():
    ticket = TradeTicketDraft(**_long_ticket())
    assert ticket.risk_validation_status == RiskValidationStatus.not_checked


def test_default_execution_mode_is_paper_only_draft():
    ticket = TradeTicketDraft(**_long_ticket())
    assert ticket.execution_mode == "paper_only_draft"
