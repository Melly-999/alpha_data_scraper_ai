"""Pre-trade risk checks and position sizing."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from core import config


@dataclass(frozen=True)
class RiskConfig:
    max_risk_per_trade_pct: float = float(config.RISK_PER_TRADE_PCT)
    min_confidence: float = float(config.MIN_CONFIDENCE_TO_TRADE)
    min_rr: float = float(config.MIN_RISK_REWARD)
    max_open_positions: int = int(config.MAX_OPEN_POSITIONS)
    max_daily_loss_pct: float = float(config.MAX_DAILY_LOSS_PCT)
    max_position_size_lots: float = float(config.MAX_POSITION_SIZE_LOTS)
    stop_loss_pips: float = float(config.STOP_LOSS_PIPS)
    pip_value_per_lot: float = float(config.PIP_VALUE_PER_LOT)


@dataclass
class RiskContext:
    balance: float
    open_positions: int
    daily_pnl_pct: float


@dataclass(frozen=True)
class RiskValidation:
    allowed: bool
    lot_size: float
    status: str
    reason: str = ""
    risk_reward: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class RiskManager:
    """Paper/live-style gates: signal type, confidence, exposure, daily loss."""

    def __init__(
        self,
        ctx: RiskContext | None = None,
        risk_config: RiskConfig | None = None,
    ) -> None:
        self.config = risk_config or RiskConfig()
        self.ctx = ctx or RiskContext(
            balance=float(config.ACCOUNT_BALANCE),
            open_positions=0,
            daily_pnl_pct=0.0,
        )
        self._start_balance = self.ctx.balance

    def evaluate(self, signal: str, confidence: int) -> dict:
        """
        Returns dict with allowed (bool), lot_size (float), status (str).
        """
        validation = self.validate(signal=signal, confidence=confidence)
        return validation.to_dict()

    def validate(
        self,
        signal: str,
        confidence: float,
        entry_price: float | None = None,
        stop_loss: float | None = None,
        take_profit: float | None = None,
        open_positions: int | None = None,
    ) -> RiskValidation:
        """Run all pre-trade gates before an order is sent."""
        signal_str = str(signal)
        if signal_str not in ("BUY", "SELL"):
            return RiskValidation(False, 0.0, "BLOCKED_NO_TRADE_SIGNAL")

        if float(confidence) < self.config.min_confidence:
            return RiskValidation(False, 0.0, "BLOCKED_LOW_CONFIDENCE")

        positions = (
            self.ctx.open_positions if open_positions is None else open_positions
        )
        if positions >= self.config.max_open_positions:
            return RiskValidation(False, 0.0, "BLOCKED_MAX_OPEN_POSITIONS")

        if self.ctx.daily_pnl_pct <= -abs(self.config.max_daily_loss_pct):
            return RiskValidation(False, 0.0, "BLOCKED_DAILY_LOSS_LIMIT")

        risk_reward = None
        if any(value is not None for value in (entry_price, stop_loss, take_profit)):
            if entry_price is None or stop_loss is None or take_profit is None:
                return RiskValidation(
                    False,
                    0.0,
                    "BLOCKED_MISSING_SL_TP",
                    "entry_price, stop_loss and take_profit are required together",
                )

            risk = abs(float(entry_price) - float(stop_loss))
            reward = abs(float(take_profit) - float(entry_price))
            if risk <= 0 or reward <= 0:
                return RiskValidation(False, 0.0, "BLOCKED_INVALID_SL_TP")

            risk_reward = reward / risk
            if risk_reward < self.config.min_rr:
                return RiskValidation(
                    False,
                    0.0,
                    "BLOCKED_LOW_RISK_REWARD",
                    risk_reward=round(risk_reward, 4),
                )

        lots = self._lot_size_for_risk()
        return RiskValidation(
            True,
            round(lots, 2),
            "ALLOWED",
            risk_reward=round(risk_reward, 4) if risk_reward is not None else None,
        )

    def _lot_size_for_risk(self) -> float:
        risk_amt = self.ctx.balance * (self.config.max_risk_per_trade_pct / 100.0)
        stop = max(self.config.stop_loss_pips, 1e-9)
        pv = max(self.config.pip_value_per_lot, 1e-9)
        loss_per_lot = stop * pv
        raw = risk_amt / loss_per_lot
        return min(float(self.config.max_position_size_lots), max(0.0, raw))

    def calculate_lot_size(
        self, balance: float | None = None, sl_pips: float | None = None
    ) -> float:
        original_balance = self.ctx.balance
        if balance is not None:
            self.ctx.balance = float(balance)
        if sl_pips is None:
            lots = self._lot_size_for_risk()
        else:
            risk_amt = self.ctx.balance * (self.config.max_risk_per_trade_pct / 100.0)
            lots = risk_amt / (
                max(float(sl_pips), 1e-9) * max(self.config.pip_value_per_lot, 1e-9)
            )
            lots = min(float(self.config.max_position_size_lots), max(0.0, lots))
        self.ctx.balance = original_balance
        return round(lots, 2)

    @property
    def current_balance(self) -> float:
        return self.ctx.balance

    def update_balance(self, balance: float) -> None:
        self.ctx.balance = float(balance)
        if self._start_balance <= 0:
            self._start_balance = self.ctx.balance

    def can_trade(self) -> tuple[bool, str]:
        if self.ctx.open_positions >= self.config.max_open_positions:
            return False, "max open positions reached"
        if self.ctx.daily_pnl_pct <= -abs(self.config.max_daily_loss_pct):
            return False, "daily loss limit reached"
        return True, "ok"

    def register_trade(self, profit: float) -> None:
        self.ctx.balance += float(profit)
        if self._start_balance > 0:
            self.ctx.daily_pnl_pct = (
                (self.ctx.balance - self._start_balance) / self._start_balance * 100.0
            )

    def get_status(self) -> dict:
        return {
            "balance": round(self.ctx.balance, 2),
            "open_positions": self.ctx.open_positions,
            "daily_pnl_pct": round(self.ctx.daily_pnl_pct, 4),
            "risk_config": asdict(self.config),
        }
