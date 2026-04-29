from __future__ import annotations

from typing import Any

try:
    import MetaTrader5 as mt5  # type: ignore
except Exception:  # pragma: no cover
    mt5 = None

from core import config
from risk.risk_manager import RiskManager, RiskContext


class RealTimeFTMOGuard:
    """Extends RiskManager with live MT5 account state."""

    def __init__(self) -> None:
        self._baseline_balance: float | None = None

    def _context_from_mt5(self) -> RiskContext:
        if mt5 is None or not mt5.initialize():
            return RiskContext(
                balance=float(config.ACCOUNT_BALANCE),
                open_positions=0,
                daily_pnl_pct=0.0,
            )

        try:
            account = mt5.account_info()
            positions = mt5.positions_get()

            balance = float(account.balance) if account else config.ACCOUNT_BALANCE

            if self._baseline_balance is None:
                self._baseline_balance = balance

            daily_pct = 0.0
            if self._baseline_balance:
                daily_pct = (
                    (balance - self._baseline_balance) / self._baseline_balance
                ) * 100

            return RiskContext(
                balance=balance,
                open_positions=len(positions or []),
                daily_pnl_pct=daily_pct,
            )
        finally:
            mt5.shutdown()

    def evaluate(self, signal: str, confidence: float) -> dict[str, Any]:
        ctx = self._context_from_mt5()
        manager = RiskManager(ctx)
        return manager.evaluate(signal, int(confidence))
