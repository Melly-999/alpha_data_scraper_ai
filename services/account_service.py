"""Account and position snapshot service with MT5 fallback."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class AccountSnapshot:
    balance: float
    equity: float
    free_margin: float
    drawdown: float
    open_positions: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PositionSnapshot:
    symbol: str
    direction: str
    lot: float
    entry_price: float
    sl: Optional[float]
    tp: Optional[float]
    profit: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AccountService:
    """Provides account and position snapshots sourced from MT5 with safe fallback."""

    def get_account_snapshot(self) -> AccountSnapshot:
        try:
            info = self._fetch_account_info()
            positions = self._fetch_raw_positions()
            drawdown = self._compute_drawdown(info)
            snapshot = AccountSnapshot(
                balance=info["balance"],
                equity=info["equity"],
                free_margin=info["free_margin"],
                drawdown=drawdown,
                open_positions=len(positions),
            )
            logger.info(
                "Account snapshot: balance=%.2f equity=%.2f drawdown=%.2f%%",
                snapshot.balance,
                snapshot.equity,
                snapshot.drawdown,
            )
            return snapshot
        except Exception as exc:
            logger.warning("MT5 unavailable for account snapshot, using fallback: %s", exc)
            return self._fallback_snapshot()

    def get_open_positions(self) -> list[PositionSnapshot]:
        try:
            raw = self._fetch_raw_positions()
            positions = [
                PositionSnapshot(
                    symbol=p["symbol"],
                    direction=p["side"],
                    lot=p["volume"],
                    entry_price=p["price_open"],
                    sl=p.get("sl"),
                    tp=p.get("tp"),
                    profit=p["profit"],
                )
                for p in raw
            ]
            logger.info("Fetched %d open positions", len(positions))
            return positions
        except Exception as exc:
            logger.warning("MT5 unavailable for positions, returning empty list: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch_account_info(self) -> dict[str, Any]:
        """Return raw account info dict from MT5."""
        try:
            import MetaTrader5 as mt5  # type: ignore

            if not mt5.initialize():
                raise RuntimeError("MT5 initialisation failed")
            info = mt5.account_info()
            mt5.shutdown()
            if info is None:
                raise RuntimeError("MT5 account_info returned None")
            return {
                "balance": float(info.balance),
                "equity": float(info.equity),
                "profit": float(info.profit),
                "margin": float(info.margin),
                "free_margin": float(info.margin_free),
            }
        except Exception:
            raise

    def _fetch_raw_positions(self) -> list[dict[str, Any]]:
        """Return raw position list from MT5 as plain dicts."""
        try:
            import MetaTrader5 as mt5  # type: ignore

            if not mt5.initialize():
                raise RuntimeError("MT5 initialisation failed")
            raw = mt5.positions_get() or []
            mt5.shutdown()
            return [
                {
                    "symbol": p.symbol,
                    "side": "BUY" if p.type == 0 else "SELL",
                    "volume": float(p.volume),
                    "price_open": float(p.price_open),
                    "price_current": float(p.price_current),
                    "profit": float(p.profit),
                    "sl": float(p.sl),
                    "tp": float(p.tp),
                    "ticket": int(p.ticket),
                }
                for p in raw
            ]
        except Exception:
            raise

    @staticmethod
    def _compute_drawdown(info: dict[str, Any]) -> float:
        balance = info.get("balance", 0.0)
        equity = info.get("equity", 0.0)
        if balance <= 0:
            return 0.0
        return max(0.0, round((1.0 - equity / balance) * 100.0, 2))

    @staticmethod
    def _fallback_snapshot() -> AccountSnapshot:
        from core import config

        return AccountSnapshot(
            balance=float(config.ACCOUNT_BALANCE),
            equity=float(config.ACCOUNT_BALANCE),
            free_margin=float(config.ACCOUNT_BALANCE),
            drawdown=0.0,
            open_positions=0,
        )
