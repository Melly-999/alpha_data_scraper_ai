from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from time import perf_counter
from typing import Any, Iterator

from app.services.fixture_data import (
    BASE_TIME,
    prototype_account,
    prototype_mt5_status,
    prototype_orders,
    prototype_positions_history,
    prototype_positions_open,
    prototype_watchlist,
)

try:
    import MetaTrader5 as mt5  # type: ignore
except Exception:  # pragma: no cover - optional runtime dependency
    mt5 = None


def _field(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


@dataclass(frozen=True)
class AdapterSnapshot:
    payload: Any
    source: str
    connected: bool
    latency_ms: int


class MT5ReadAdapter:
    def __init__(self) -> None:
        self._available = mt5 is not None

    @property
    def available(self) -> bool:
        return self._available

    @contextmanager
    def _session(self) -> Iterator[tuple[bool, int]]:
        if mt5 is None:
            yield False, 0
            return

        started = perf_counter()
        connected = False
        try:
            connected = bool(mt5.initialize())
            latency_ms = int((perf_counter() - started) * 1000)
            yield connected, latency_ms
        finally:
            if connected:
                mt5.shutdown()

    def read_account_overview(self) -> AdapterSnapshot | None:
        with self._session() as (connected, latency_ms):
            if not connected:
                return None

            account = mt5.account_info()
            if account is None:
                return None

            balance = float(_field(account, "balance", 0.0))
            equity = float(_field(account, "equity", balance))
            margin = float(_field(account, "margin", 0.0))
            profit = float(_field(account, "profit", 0.0))
            daily_pnl = round(profit, 2)
            daily_pnl_pct = round((daily_pnl / balance) * 100, 2) if balance else 0.0
            drawdown = (
                round(((equity - balance) / balance) * 100, 2) if balance else 0.0
            )
            positions = mt5.positions_get() or []

            payload = {
                "balance": balance,
                "equity": equity,
                "margin": margin,
                "free_margin": float(_field(account, "margin_free", 0.0)),
                "margin_level": float(_field(account, "margin_level", 0.0)),
                "drawdown": drawdown,
                "daily_pnl": daily_pnl,
                "daily_pnl_pct": daily_pnl_pct,
                "open_positions": len(positions),
                "today_trades": len(self._read_recent_deals()),
            }
            return AdapterSnapshot(
                payload=payload,
                source="mt5",
                connected=True,
                latency_ms=latency_ms,
            )

    def read_open_positions(self) -> AdapterSnapshot | None:
        with self._session() as (connected, latency_ms):
            if not connected:
                return None

            positions = mt5.positions_get() or []
            now = datetime.now(timezone.utc)
            payload: list[dict[str, Any]] = []
            for position in positions:
                opened = datetime.fromtimestamp(
                    int(_field(position, "time", now.timestamp())),
                    tz=timezone.utc,
                )
                payload.append(
                    {
                        "id": f"mt5-pos-{_field(position, 'ticket', 0)}",
                        "ticket": int(_field(position, "ticket", 0)),
                        "symbol": str(_field(position, "symbol", "UNKNOWN")),
                        "direction": (
                            "BUY" if int(_field(position, "type", 0)) == 0 else "SELL"
                        ),
                        "lots": float(_field(position, "volume", 0.0)),
                        "open_price": float(_field(position, "price_open", 0.0)),
                        "current_price": float(_field(position, "price_current", 0.0)),
                        "sl": (
                            float(_field(position, "sl"))
                            if _field(position, "sl") is not None
                            else None
                        ),
                        "tp": (
                            float(_field(position, "tp"))
                            if _field(position, "tp") is not None
                            else None
                        ),
                        "unrealized_pnl": float(_field(position, "profit", 0.0)),
                        "duration_seconds": int((now - opened).total_seconds()),
                        "signal_id": None,
                        "mt5_synced": True,
                        "open_time": opened,
                    }
                )
            return AdapterSnapshot(
                payload=payload,
                source="mt5",
                connected=True,
                latency_ms=latency_ms,
            )

    def read_position_history(self) -> AdapterSnapshot | None:
        with self._session() as (connected, latency_ms):
            if not connected:
                return None

            deals = self._read_recent_deals(days=5)
            payload: list[dict[str, Any]] = []
            for deal in deals:
                if int(_field(deal, "entry", 0)) != 1:
                    continue
                close_time = datetime.fromtimestamp(
                    int(_field(deal, "time", BASE_TIME.timestamp())),
                    tz=timezone.utc,
                )
                open_time = close_time - timedelta(minutes=45)
                payload.append(
                    {
                        "id": f"mt5-hist-{_field(deal, 'ticket', 0)}",
                        "ticket": int(_field(deal, "ticket", 0)),
                        "symbol": str(_field(deal, "symbol", "UNKNOWN")),
                        "direction": (
                            "BUY" if int(_field(deal, "type", 0)) in {0, 2} else "SELL"
                        ),
                        "lots": float(_field(deal, "volume", 0.0)),
                        "open_price": float(_field(deal, "price", 0.0)),
                        "close_price": float(_field(deal, "price", 0.0)),
                        "realized_pnl": float(_field(deal, "profit", 0.0)),
                        "duration_seconds": int(
                            (close_time - open_time).total_seconds()
                        ),
                        "signal_id": None,
                        "mt5_synced": True,
                        "open_time": open_time,
                        "close_time": close_time,
                    }
                )
            return AdapterSnapshot(
                payload=payload,
                source="mt5",
                connected=True,
                latency_ms=latency_ms,
            )

    def read_orders(self) -> AdapterSnapshot | None:
        with self._session() as (connected, latency_ms):
            if not connected:
                return None

            open_orders = mt5.orders_get() or []
            deals = self._read_recent_deals(days=2)
            payload: list[dict[str, Any]] = []

            for order in open_orders:
                submitted = datetime.fromtimestamp(
                    int(_field(order, "time_setup", BASE_TIME.timestamp())),
                    tz=timezone.utc,
                )
                payload.append(
                    {
                        "id": f"mt5-ord-{_field(order, 'ticket', 0)}",
                        "ticket": int(_field(order, "ticket", 0)),
                        "symbol": str(_field(order, "symbol", "UNKNOWN")),
                        "direction": (
                            "BUY" if int(_field(order, "type", 0)) in {0, 2} else "SELL"
                        ),
                        "type": (
                            "LIMIT"
                            if int(_field(order, "type", 0)) in {2, 3}
                            else "MARKET"
                        ),
                        "lots": float(_field(order, "volume_current", 0.0)),
                        "price": float(_field(order, "price_open", 0.0)),
                        "sl": float(_field(order, "sl", 0.0)) or None,
                        "tp": float(_field(order, "tp", 0.0)) or None,
                        "status": "PENDING",
                        "source": "MANUAL",
                        "confidence": None,
                        "slippage_pips": None,
                        "submitted_at": submitted,
                        "filled_at": None,
                        "notes": "Read-only MT5 order snapshot",
                    }
                )

            for deal in deals[:10]:
                filled_at = datetime.fromtimestamp(
                    int(_field(deal, "time", BASE_TIME.timestamp())),
                    tz=timezone.utc,
                )
                payload.append(
                    {
                        "id": f"mt5-deal-{_field(deal, 'ticket', 0)}",
                        "ticket": int(_field(deal, "ticket", 0)),
                        "symbol": str(_field(deal, "symbol", "UNKNOWN")),
                        "direction": (
                            "BUY" if int(_field(deal, "type", 0)) in {0, 2} else "SELL"
                        ),
                        "type": "MARKET",
                        "lots": float(_field(deal, "volume", 0.0)),
                        "price": float(_field(deal, "price", 0.0)),
                        "sl": None,
                        "tp": None,
                        "status": "FILLED",
                        "source": "MANUAL",
                        "confidence": None,
                        "slippage_pips": None,
                        "submitted_at": filled_at,
                        "filled_at": filled_at,
                        "notes": "Read-only MT5 deal history snapshot",
                    }
                )

            return AdapterSnapshot(
                payload=payload,
                source="mt5",
                connected=True,
                latency_ms=latency_ms,
            )

    def read_status(self, symbols: list[str]) -> AdapterSnapshot | None:
        with self._session() as (connected, latency_ms):
            if not connected:
                return None

            account = mt5.account_info()
            terminal = mt5.terminal_info()
            version = mt5.version()
            heartbeat = datetime.now(timezone.utc).isoformat()
            payload = {
                "connected": True,
                "server": str(_field(account, "server", "MT5")),
                "account_id": str(_field(account, "login", "")),
                "account_name": str(_field(account, "name", "MT5 Account")),
                "broker": str(_field(account, "company", "MT5 Broker")),
                "currency": str(_field(account, "currency", "USD")),
                "leverage": (
                    f"1:{int(_field(account, 'leverage', 0))}"
                    if _field(account, "leverage")
                    else "N/A"
                ),
                "last_heartbeat": heartbeat,
                "latency_ms": latency_ms,
                "symbols_loaded": len(symbols),
                "orders_sync": True,
                "positions_sync": True,
                "build_version": (
                    ".".join(str(part) for part in version)
                    if isinstance(version, tuple)
                    else str(version)
                ),
                "fallback": False,
                "read_only": True,
                "data_source": "mt5",
                "terminal_path": str(_field(terminal, "path", "")),
                "cache_age_seconds": 0,
                "refreshed_at": heartbeat,
                "connection_logs": [
                    {
                        "time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                        "event": "HEARTBEAT",
                        "msg": "Read-only MT5 bridge check succeeded",
                    }
                ],
            }
            return AdapterSnapshot(
                payload=payload,
                source="mt5",
                connected=True,
                latency_ms=latency_ms,
            )

    def read_watchlist(self, symbols: list[str]) -> AdapterSnapshot | None:
        with self._session() as (connected, latency_ms):
            if not connected:
                return None

            payload: list[dict[str, Any]] = []
            for symbol in symbols:
                tick = mt5.symbol_info_tick(symbol)
                if tick is None:
                    continue
                bid = float(_field(tick, "bid", 0.0))
                ask = float(_field(tick, "ask", 0.0))
                last = float(_field(tick, "last", bid or ask or 0.0))
                change = round(((last - bid) / bid) * 100, 2) if bid else 0.0
                payload.append(
                    {
                        "symbol": symbol,
                        "bid": bid,
                        "ask": ask,
                        "change": change,
                    }
                )
            if not payload:
                return None
            return AdapterSnapshot(
                payload=payload,
                source="mt5",
                connected=True,
                latency_ms=latency_ms,
            )

    def fallback_account_overview(self) -> AdapterSnapshot:
        return AdapterSnapshot(
            payload=prototype_account(),
            source="fallback",
            connected=False,
            latency_ms=0,
        )

    def fallback_open_positions(self) -> AdapterSnapshot:
        return AdapterSnapshot(
            payload=prototype_positions_open(),
            source="fallback",
            connected=False,
            latency_ms=0,
        )

    def fallback_position_history(self) -> AdapterSnapshot:
        return AdapterSnapshot(
            payload=prototype_positions_history(),
            source="fallback",
            connected=False,
            latency_ms=0,
        )

    def fallback_orders(self) -> AdapterSnapshot:
        return AdapterSnapshot(
            payload=prototype_orders(),
            source="fallback",
            connected=False,
            latency_ms=0,
        )

    def fallback_status(self) -> AdapterSnapshot:
        payload = prototype_mt5_status()
        payload.update(
            {
                "connected": False,
                "fallback": True,
                "read_only": True,
                "data_source": "fallback",
                "terminal_path": "",
                "cache_age_seconds": 0,
                "refreshed_at": BASE_TIME.isoformat(),
            }
        )
        return AdapterSnapshot(
            payload=payload,
            source="fallback",
            connected=False,
            latency_ms=0,
        )

    def fallback_watchlist(self) -> AdapterSnapshot:
        return AdapterSnapshot(
            payload=prototype_watchlist(),
            source="fallback",
            connected=False,
            latency_ms=0,
        )

    def _read_recent_deals(self, days: int = 1) -> list[Any]:
        if mt5 is None:
            return []
        date_to = datetime.now(timezone.utc)
        date_from = date_to - timedelta(days=days)
        try:
            return list(mt5.history_deals_get(date_from, date_to) or [])
        except Exception:
            return []
