from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    import MetaTrader5 as mt5  # type: ignore
except Exception:  # pragma: no cover
    mt5 = None


def _utc_window(days: int = 7) -> tuple[datetime, datetime]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    return start, end


def get_closed_trade_winrate(days: int = 7) -> dict[str, Any]:
    if mt5 is None or not mt5.initialize():
        return {"days": days, "total": 0, "wins": 0, "losses": 0, "winrate_pct": 0.0}
    try:
        start, end = _utc_window(days)
        deals = mt5.history_deals_get(start, end) or []
        closed = [d for d in deals if getattr(d, "entry", None) == 1]
        wins = sum(1 for d in closed if float(getattr(d, "profit", 0.0)) > 0)
        losses = sum(1 for d in closed if float(getattr(d, "profit", 0.0)) < 0)
        total = len(closed)
        return {
            "days": days,
            "total": total,
            "wins": wins,
            "losses": losses,
            "winrate_pct": round((wins / total * 100.0), 2) if total else 0.0,
            "net_profit": round(sum(float(getattr(d, "profit", 0.0)) for d in closed), 2),
        }
    finally:
        mt5.shutdown()


def summarize_exit_reasons(days: int = 3) -> dict[str, Any]:
    if mt5 is None or not mt5.initialize():
        return {"days": days, "sl_hits": 0, "tp_hits": 0, "other": 0, "items": []}
    try:
        start, end = _utc_window(days)
        deals = mt5.history_deals_get(start, end) or []
        closed = [d for d in deals if getattr(d, "entry", None) == 1]
        counts: Counter[str] = Counter()
        items: list[dict[str, Any]] = []
        for d in closed:
            reason_code = int(getattr(d, "reason", -1))
            if reason_code == 4:
                label = "TP_HIT"
            elif reason_code == 5:
                label = "SL_HIT"
            else:
                label = "OTHER"
            counts[label] += 1
            items.append(
                {
                    "symbol": getattr(d, "symbol", ""),
                    "profit": float(getattr(d, "profit", 0.0)),
                    "reason": label,
                    "time": int(getattr(d, "time", 0)),
                    "position_id": int(getattr(d, "position_id", 0)),
                }
            )
        items.sort(key=lambda x: x["time"], reverse=True)
        return {
            "days": days,
            "sl_hits": counts.get("SL_HIT", 0),
            "tp_hits": counts.get("TP_HIT", 0),
            "other": counts.get("OTHER", 0),
            "items": items[:25],
        }
    finally:
        mt5.shutdown()


def extract_cooldown_alerts(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    for row in signals:
        status = str(row.get("autotrade_status", ""))
        if 'cooldown' in status.lower():
            alerts.append(
                {
                    "symbol": row.get("symbol"),
                    "status": "COOLDOWN",
                    "reason": status,
                    "created_at": row.get("created_at"),
                }
            )
    return alerts
