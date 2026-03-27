from __future__ import annotations

import pytest

from calculator import position_size


def test_standard_case() -> None:
    # $10 000, 1% risk, 200 pts SL, $1/pt/lot → $100 / $200 = 0.50 lots
    result = position_size(balance=10_000, risk_pct=0.01, sl_points=200, point_value=1.0)
    assert result == 0.50


def test_minimum_lot_floor() -> None:
    # Very large SL → below 0.01 → clamp to 0.01
    result = position_size(balance=100, risk_pct=0.001, sl_points=10_000, point_value=10.0)
    assert result == 0.01


def test_zero_sl_returns_minimum() -> None:
    result = position_size(balance=10_000, risk_pct=0.01, sl_points=0, point_value=1.0)
    assert result == 0.01


def test_zero_balance_returns_minimum() -> None:
    result = position_size(balance=0, risk_pct=0.01, sl_points=200, point_value=1.0)
    assert result == 0.01


def test_rounding() -> None:
    # $5000, 1%, 300 pts, $0.9/pt → $50 / $270 ≈ 0.1851... → rounds to 0.19
    result = position_size(balance=5_000, risk_pct=0.01, sl_points=300, point_value=0.9)
    assert result == pytest.approx(0.19, abs=0.01)
