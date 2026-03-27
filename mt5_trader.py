from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    import MetaTrader5 as mt5  # type: ignore
except Exception:  # pragma: no cover - optional runtime dependency
    mt5 = None

mt5_api: Any = mt5


@dataclass
class MT5AutoTrader:
    symbol: str
    enabled: bool = False
    dry_run: bool = True
    min_confidence: float = 70.0
    volume: float = 0.01
    deviation: int = 20
    sl_points: int = 200
    tp_points: int = 300
    magic: int = 20260327

    def maybe_execute(self, signal: str, confidence: float) -> dict[str, Any]:
        if not self.enabled:
            return {"status": "disabled"}

        signal_upper = signal.upper()
        if signal_upper not in {"BUY", "SELL"}:
            return {"status": "no_trade_signal", "signal": signal_upper}

        if confidence < self.min_confidence:
            return {
                "status": "below_confidence",
                "signal": signal_upper,
                "confidence": round(confidence, 2),
                "min_confidence": round(self.min_confidence, 2),
            }

        if mt5_api is None:
            return {"status": "mt5_unavailable"}

        if not mt5_api.initialize():
            return {"status": "init_failed", "error": mt5_api.last_error()}

        try:
            if not mt5_api.symbol_select(self.symbol, True):
                return {
                    "status": "symbol_select_failed",
                    "symbol": self.symbol,
                    "error": mt5_api.last_error(),
                }

            tick = mt5_api.symbol_info_tick(self.symbol)
            info = mt5_api.symbol_info(self.symbol)
            if tick is None or info is None:
                return {
                    "status": "symbol_info_missing",
                    "symbol": self.symbol,
                    "error": mt5_api.last_error(),
                }

            point = float(info.point or 0.0001)
            if signal_upper == "BUY":
                order_type = mt5_api.ORDER_TYPE_BUY
                price = float(tick.ask)
                sl = price - (self.sl_points * point)
                tp = price + (self.tp_points * point)
            else:
                order_type = mt5_api.ORDER_TYPE_SELL
                price = float(tick.bid)
                sl = price + (self.sl_points * point)
                tp = price - (self.tp_points * point)

            request: dict[str, Any] = {
                "action": mt5_api.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": float(self.volume),
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": int(self.deviation),
                "magic": int(self.magic),
                "comment": "grok_alpha_ai",
                "type_time": mt5_api.ORDER_TIME_GTC,
                "type_filling": mt5_api.ORDER_FILLING_IOC,
            }

            if self.dry_run:
                return {
                    "status": "dry_run",
                    "request": {
                        "symbol": request["symbol"],
                        "volume": request["volume"],
                        "side": signal_upper,
                        "price": round(price, 6),
                        "sl": round(float(sl), 6),
                        "tp": round(float(tp), 6),
                    },
                }

            result = mt5_api.order_send(request)
            if result is None:
                return {"status": "order_send_failed", "error": mt5_api.last_error()}

            if result.retcode != mt5_api.TRADE_RETCODE_DONE:
                return {
                    "status": "rejected",
                    "retcode": int(result.retcode),
                    "comment": str(result.comment),
                }

            return {
                "status": "placed",
                "retcode": int(result.retcode),
                "order": int(result.order),
                "deal": int(result.deal),
                "price": round(price, 6),
                "side": signal_upper,
            }
        finally:
            mt5_api.shutdown()
