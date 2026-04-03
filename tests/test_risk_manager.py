"""Unit tests for risk/risk_manager.py."""

from __future__ import annotations

import pytest

from risk.risk_manager import RiskContext, RiskManager
from core import config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _manager(balance=10_000.0, open_positions=0, daily_pnl_pct=0.0) -> RiskManager:
    ctx = RiskContext(
        balance=balance,
        open_positions=open_positions,
        daily_pnl_pct=daily_pnl_pct,
    )
    return RiskManager(ctx=ctx)


# ---------------------------------------------------------------------------
# Blocking gates
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("signal", ["HOLD", "NEUTRAL", "", "hold", "buy"])
def test_non_actionable_signal_is_blocked(signal: str) -> None:
    mgr = _manager()
    result = mgr.evaluate(signal=signal, confidence=80)
    assert result["allowed"] is False
    assert result["lot_size"] == 0.0
    assert result["status"] == "BLOCKED_NO_TRADE_SIGNAL"


def test_buy_signal_not_blocked_by_signal_gate() -> None:
    mgr = _manager()
    result = mgr.evaluate(signal="BUY", confidence=80)
    # May still be blocked by other gates, but NOT by signal gate
    assert result["status"] != "BLOCKED_NO_TRADE_SIGNAL"


def test_sell_signal_not_blocked_by_signal_gate() -> None:
    mgr = _manager()
    result = mgr.evaluate(signal="SELL", confidence=80)
    assert result["status"] != "BLOCKED_NO_TRADE_SIGNAL"


def test_low_confidence_is_blocked() -> None:
    mgr = _manager()
    below_threshold = config.MIN_CONFIDENCE_TO_TRADE - 1
    result = mgr.evaluate(signal="BUY", confidence=below_threshold)
    assert result["allowed"] is False
    assert result["lot_size"] == 0.0
    assert result["status"] == "BLOCKED_LOW_CONFIDENCE"


def test_confidence_at_threshold_is_not_blocked_by_confidence_gate() -> None:
    mgr = _manager()
    result = mgr.evaluate(signal="BUY", confidence=config.MIN_CONFIDENCE_TO_TRADE)
    assert result["status"] != "BLOCKED_LOW_CONFIDENCE"


def test_max_open_positions_is_blocked() -> None:
    mgr = _manager(open_positions=config.MAX_OPEN_POSITIONS)
    result = mgr.evaluate(signal="BUY", confidence=80)
    assert result["allowed"] is False
    assert result["lot_size"] == 0.0
    assert result["status"] == "BLOCKED_MAX_OPEN_POSITIONS"


def test_below_max_positions_is_not_blocked_by_position_gate() -> None:
    mgr = _manager(open_positions=config.MAX_OPEN_POSITIONS - 1)
    result = mgr.evaluate(signal="BUY", confidence=80)
    assert result["status"] != "BLOCKED_MAX_OPEN_POSITIONS"


def test_daily_loss_limit_is_blocked() -> None:
    # Exceeds the limit (e.g. -2.0% threshold, set to -2.1%)
    below_limit = -(abs(config.MAX_DAILY_LOSS_PCT) + 0.1)
    mgr = _manager(daily_pnl_pct=below_limit)
    result = mgr.evaluate(signal="SELL", confidence=80)
    assert result["allowed"] is False
    assert result["lot_size"] == 0.0
    assert result["status"] == "BLOCKED_DAILY_LOSS_LIMIT"


def test_daily_pnl_at_exactly_limit_is_blocked() -> None:
    at_limit = -abs(config.MAX_DAILY_LOSS_PCT)
    mgr = _manager(daily_pnl_pct=at_limit)
    result = mgr.evaluate(signal="BUY", confidence=80)
    assert result["allowed"] is False
    assert result["status"] == "BLOCKED_DAILY_LOSS_LIMIT"


def test_positive_daily_pnl_is_not_blocked_by_loss_gate() -> None:
    mgr = _manager(daily_pnl_pct=1.0)
    result = mgr.evaluate(signal="BUY", confidence=80)
    assert result["status"] != "BLOCKED_DAILY_LOSS_LIMIT"


# ---------------------------------------------------------------------------
# Happy path — trade allowed
# ---------------------------------------------------------------------------

def test_valid_buy_is_allowed() -> None:
    mgr = _manager(balance=10_000.0, open_positions=0, daily_pnl_pct=0.0)
    result = mgr.evaluate(signal="BUY", confidence=80)
    assert result["allowed"] is True
    assert result["lot_size"] >= 0.0
    assert result["status"] == "ALLOWED"


def test_valid_sell_is_allowed() -> None:
    mgr = _manager(balance=10_000.0, open_positions=0, daily_pnl_pct=0.0)
    result = mgr.evaluate(signal="SELL", confidence=75)
    assert result["allowed"] is True
    assert result["lot_size"] >= 0.0
    assert result["status"] == "ALLOWED"


def test_lot_size_is_rounded_to_two_decimals() -> None:
    mgr = _manager(balance=10_000.0)
    result = mgr.evaluate(signal="BUY", confidence=80)
    if result["allowed"]:
        assert result["lot_size"] == round(result["lot_size"], 2)


# ---------------------------------------------------------------------------
# Lot size calculation
# ---------------------------------------------------------------------------

def test_lot_size_formula() -> None:
    """Verify _lot_size_for_risk() matches the expected formula."""
    balance = 50_000.0
    ctx = RiskContext(balance=balance, open_positions=0, daily_pnl_pct=0.0)
    mgr = RiskManager(ctx=ctx)

    risk_amt = balance * (config.RISK_PER_TRADE_PCT / 100.0)
    stop = max(config.STOP_LOSS_PIPS, 1e-9)
    pv = max(config.PIP_VALUE_PER_LOT, 1e-9)
    expected_raw = risk_amt / (stop * pv)
    expected = min(float(config.MAX_POSITION_SIZE_LOTS), max(0.0, expected_raw))

    actual = mgr._lot_size_for_risk()
    assert abs(actual - expected) < 1e-9


def test_lot_size_capped_by_max_position_size() -> None:
    """With a very large balance the result should hit the MAX_POSITION_SIZE_LOTS cap."""
    ctx = RiskContext(balance=1_000_000_000.0, open_positions=0, daily_pnl_pct=0.0)
    mgr = RiskManager(ctx=ctx)
    assert mgr._lot_size_for_risk() <= config.MAX_POSITION_SIZE_LOTS


def test_lot_size_floored_at_zero_for_zero_balance() -> None:
    ctx = RiskContext(balance=0.0, open_positions=0, daily_pnl_pct=0.0)
    mgr = RiskManager(ctx=ctx)
    assert mgr._lot_size_for_risk() >= 0.0


# ---------------------------------------------------------------------------
# Default context uses config values
# ---------------------------------------------------------------------------

def test_default_context_uses_config_balance() -> None:
    mgr = RiskManager()  # no ctx → uses defaults
    assert mgr.ctx.balance == float(config.ACCOUNT_BALANCE)
    assert mgr.ctx.open_positions == 0
    assert mgr.ctx.daily_pnl_pct == 0.0
