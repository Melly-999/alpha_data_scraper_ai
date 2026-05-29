"""Read-only watchlist assembly for Direction B dashboard context.

The current implementation uses deterministic fallback market rows and enriches
them with persisted signal decisions plus derived alert counts. No live market
adapter or execution path is introduced here.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Dict, Iterable, List

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from . import alerts
from .config import Settings
from .models import SignalRecord
from .schemas import WatchlistItemOut

_FALLBACK_MARKETS: tuple[dict[str, object], ...] = (
    {
        "symbol": "EURUSD",
        "name": "Euro / US Dollar",
        "asset_class": "forex",
        "last_price": 1.085,
        "change_pct": 0.12,
    },
    {
        "symbol": "GBPUSD",
        "name": "British Pound / US Dollar",
        "asset_class": "forex",
        "last_price": 1.253,
        "change_pct": -0.08,
    },
    {
        "symbol": "USDJPY",
        "name": "US Dollar / Japanese Yen",
        "asset_class": "forex",
        "last_price": 156.2,
        "change_pct": 0.18,
    },
    {
        "symbol": "XAUUSD",
        "name": "Gold / US Dollar",
        "asset_class": "metal",
        "last_price": 2338.4,
        "change_pct": -0.21,
    },
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _latest_signals(db: Session) -> Dict[str, SignalRecord]:
    stmt: Select[tuple[SignalRecord]] = select(SignalRecord).order_by(
        SignalRecord.created_at.desc()
    )
    latest: Dict[str, SignalRecord] = {}
    for record in db.execute(stmt).scalars().all():
        latest.setdefault(record.symbol, record)
    return latest


def _alert_counts(db: Session, settings: Settings) -> Counter[str]:
    counts: Counter[str] = Counter()
    for alert in alerts.collect_alerts(db=db, settings=settings, limit=500):
        if alert.symbol:
            counts[alert.symbol] += 1
    return counts


def _symbols(markets: Iterable[dict[str, object]]) -> set[str]:
    return {str(market["symbol"]) for market in markets}


def _signal_market(record: SignalRecord) -> dict[str, object]:
    return {
        "symbol": record.symbol,
        "name": record.symbol,
        "asset_class": "forex",
        "last_price": record.entry_price,
        "change_pct": 0.0,
    }


def _risk_state(record: SignalRecord | None, alert_count: int) -> str:
    if record and record.status == "rejected":
        return "blocked"
    if alert_count > 0:
        return "watch"
    return "clear"


def collect_watchlist(db: Session, settings: Settings) -> List[WatchlistItemOut]:
    """Return a deterministic, read-only watchlist for dashboard scanning."""
    generated_at = _utcnow()
    latest_signals = _latest_signals(db)
    counts_by_symbol = _alert_counts(db, settings)

    markets = list(_FALLBACK_MARKETS)
    fallback_symbols = _symbols(markets)
    for record in latest_signals.values():
        if record.symbol not in fallback_symbols:
            markets.append(_signal_market(record))

    rows: List[WatchlistItemOut] = []
    for market in markets:
        symbol = str(market["symbol"])
        signal = latest_signals.get(symbol)
        alert_count = counts_by_symbol[symbol]
        rows.append(
            WatchlistItemOut(
                symbol=symbol,
                name=str(market["name"]),
                asset_class=str(market["asset_class"]),
                last_price=float(market["last_price"]),
                change_pct=float(market["change_pct"]),
                signal_status=signal.status if signal else "none",
                signal_confidence=signal.confidence if signal else None,
                alert_count=alert_count,
                risk_state=_risk_state(signal, alert_count),  # type: ignore[arg-type]
                source="fallback" if signal is None else "signals",
                generated_at=generated_at,
                read_only=settings.read_only,
            )
        )

    return rows
