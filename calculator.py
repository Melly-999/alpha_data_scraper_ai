from __future__ import annotations


def position_size(
    balance: float,
    risk_pct: float,
    sl_points: int,
    point_value: float,
) -> float:
    """Return lot size based on fixed-risk position sizing.

    Args:
        balance:     Account balance in account currency.
        risk_pct:    Fraction of balance to risk (e.g. 0.01 = 1 %).
        sl_points:   Stop-loss distance in broker points.
        point_value: Monetary value of one point per 1 lot.

    Returns:
        Lot size rounded to 2 decimal places (minimum 0.01).
    """
    if sl_points <= 0 or point_value <= 0 or balance <= 0:
        return 0.01
    risk_amount = balance * risk_pct
    raw = risk_amount / (sl_points * point_value)
    return max(0.01, round(raw, 2))
