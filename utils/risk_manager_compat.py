"""Compatibility shims for the legacy top-level ``main.py`` runner.

`main.py` was written against an earlier ``RiskManager`` contract
(``can_trade`` / ``update_balance`` / ``calculate_lot_size`` /
``register_trade`` / ``get_status``) that no longer exists on
``risk.risk_manager.RiskManager``. To keep the CLI runnable without
rewriting ``main.py`` or leaking a second risk implementation, this
module exposes a thin :class:`LegacyRiskManager` shim alongside the
re-exported modern classes.
"""

from __future__ import annotations

from typing import Tuple

from risk.risk_manager import RiskContext, RiskManager

from calculator import position_size
from core import config as core_config

__all__ = ["RiskManager", "RiskContext", "LegacyRiskManager"]


class LegacyRiskManager:
    """Minimal stand-in for the legacy runner.

    The full risk stack lives in :mod:`risk.risk_manager`; this class
    only provides the narrow surface ``main.py`` expects. Defaults are
    intentionally conservative (daily loss cap from ``core.config``,
    position sizing via :func:`calculator.position_size`).
    """

    def __init__(self, balance: float | None = None) -> None:
        self.current_balance: float = float(
            balance if balance is not None else core_config.ACCOUNT_BALANCE
        )
        self._daily_pnl: float = 0.0
        self._trade_count: int = 0
        self._max_daily_loss: float = self.current_balance * (
            abs(core_config.MAX_DAILY_LOSS_PCT) / 100.0
        )

    def can_trade(self) -> Tuple[bool, str]:
        if self._daily_pnl <= -self._max_daily_loss:
            return False, "daily_loss_limit"
        return True, "OK"

    def update_balance(self, balance: float) -> None:
        self.current_balance = float(balance)
        self._max_daily_loss = self.current_balance * (
            abs(core_config.MAX_DAILY_LOSS_PCT) / 100.0
        )

    def calculate_lot_size(self, balance: float, sl_pips: int = 100) -> float:
        return position_size(
            balance=float(balance),
            risk_pct=float(core_config.RISK_PER_TRADE_PCT) / 100.0,
            sl_points=int(sl_pips),
            point_value=float(core_config.PIP_VALUE_PER_LOT),
        )

    def register_trade(self, profit: float) -> None:
        self._daily_pnl += float(profit)
        self._trade_count += 1

    def get_status(self) -> dict:
        return {
            "balance": round(self.current_balance, 2),
            "daily_pnl": round(self._daily_pnl, 2),
            "daily_loss_cap": round(self._max_daily_loss, 2),
            "trades": self._trade_count,
        }
