from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class PropRiskConfig:
    max_daily_loss: float = 0.05  # fraction of daily start equity
    max_drawdown: float = 0.10  # fraction of overall peak equity
    daily_profit_target: float = 0.03  # fraction of daily start equity
    max_daily_trades: int = 5
    confidence_threshold: int = 60


class PropRiskManager:
    """
    Lightweight risk guard for prop-like rules.

    - Daily rules reset when local date changes.
    - Daily PnL is measured from start-of-day equity.
    - Overall drawdown is measured from peak equity seen since start.
    """

    def __init__(self, cfg: PropRiskConfig, initial_equity: float):
        self.cfg = cfg
        self._today = date.today()

        self.initial_equity = float(initial_equity)
        self.peak_equity = float(initial_equity)

        self.daily_start_equity = float(initial_equity)
        self.daily_trades = 0

    def _roll_day_if_needed(self, current_equity: float) -> None:
        today = date.today()
        if today == self._today:
            return
        self._today = today
        self.daily_start_equity = float(current_equity)
        self.daily_trades = 0

    def update_equity(self, current_equity: float) -> None:
        self._roll_day_if_needed(current_equity)
        if current_equity > self.peak_equity:
            self.peak_equity = float(current_equity)

    def get_daily_pnl(self, current_equity: float) -> float:
        self._roll_day_if_needed(current_equity)
        return float(current_equity) - float(self.daily_start_equity)

    def can_trade(self, current_equity: float, confidence: int) -> tuple[bool, str]:
        self.update_equity(current_equity)

        if confidence < self.cfg.confidence_threshold:
            return False, f"Low confidence {confidence} < {self.cfg.confidence_threshold}"

        if self.daily_trades >= self.cfg.max_daily_trades:
            return False, "Max daily trades"

        daily_pnl = self.get_daily_pnl(current_equity)
        daily_loss_limit = self.cfg.max_daily_loss * self.daily_start_equity
        daily_profit_target = self.cfg.daily_profit_target * self.daily_start_equity
        if daily_pnl <= -daily_loss_limit:
            return False, "Daily loss limit"
        if daily_pnl >= daily_profit_target:
            return False, "Daily profit target reached"

        drawdown = self.peak_equity - float(current_equity)
        max_drawdown = self.cfg.max_drawdown * self.peak_equity
        if drawdown > max_drawdown:
            return False, "Max drawdown"

        return True, "OK"

    def record_trade(self) -> None:
        self.daily_trades += 1

