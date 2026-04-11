"""Pre-trade risk checks and position sizing."""

from __future__ import annotations

from dataclasses import dataclass

from core import config


@dataclass
class RiskContext:
    balance: float
    open_positions: int
    daily_pnl_pct: float


class RiskManager:
    """Paper/live-style gates: signal type, confidence, exposure, daily loss."""

    def __init__(self, ctx: RiskContext | None = None) -> None:
        self.ctx = ctx or RiskContext(
            balance=float(config.ACCOUNT_BALANCE),
            open_positions=0,
            daily_pnl_pct=0.0,
        )

    def evaluate(self, signal: str, confidence: int) -> dict:
        """
        Returns dict with allowed (bool), lot_size (float), status (str).
        """
        if signal not in ("BUY", "SELL"):
            return {
                "allowed": False,
                "lot_size": 0.0,
                "status": "BLOCKED_NO_TRADE_SIGNAL",
            }

        if confidence < config.MIN_CONFIDENCE_TO_TRADE:
            return {
                "allowed": False,
                "lot_size": 0.0,
                "status": "BLOCKED_LOW_CONFIDENCE",
            }

        if self.ctx.open_positions >= config.MAX_OPEN_POSITIONS:
            return {
                "allowed": False,
                "lot_size": 0.0,
                "status": "BLOCKED_MAX_OPEN_POSITIONS",
            }

        if self.ctx.daily_pnl_pct <= -abs(config.MAX_DAILY_LOSS_PCT):
            return {
                "allowed": False,
                "lot_size": 0.0,
                "status": "BLOCKED_DAILY_LOSS_LIMIT",
            }

        lots = self._lot_size_for_risk()
        return {
            "allowed": True,
            "lot_size": round(lots, 2),
            "status": "ALLOWED",
        }

    def _lot_size_for_risk(self) -> float:
        risk_amt = self.ctx.balance * (config.RISK_PER_TRADE_PCT / 100.0)
        stop = max(config.STOP_LOSS_PIPS, 1e-9)
        pv = max(config.PIP_VALUE_PER_LOT, 1e-9)
        loss_per_lot = stop * pv
        raw = risk_amt / loss_per_lot
        return min(float(config.MAX_POSITION_SIZE_LOTS), max(0.0, raw))
