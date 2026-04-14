from __future__ import annotations

from fastapi import FastAPI
from typing import Any
import sqlite3
from pathlib import Path

from monitoring.trade_history import (
    get_closed_trade_winrate,
    summarize_exit_reasons,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "db" / "trading.db"

app = FastAPI(title="Alpha AI Analytics API")


def _query(sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


@app.get("/confidence-heatmap")
def confidence_heatmap(limit: int = 500) -> list[dict[str, Any]]:
    return _query(
        """
        SELECT symbol, confidence, created_at
        FROM alerts
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    )


@app.get("/equity-curve")
def equity_curve(limit: int = 1000) -> list[dict[str, Any]]:
    return _query(
        """
        SELECT created_at, equity, balance, profit
        FROM equity_snapshots
        ORDER BY created_at ASC
        LIMIT ?
        """,
        (limit,),
    )


@app.get("/equity-curve/{symbol}")
def equity_curve_symbol(symbol: str) -> list[dict[str, Any]]:
    return _query(
        """
        SELECT created_at, last_close, confidence
        FROM alerts
        WHERE symbol = ?
        ORDER BY created_at ASC
        """,
        (symbol,),
    )


@app.get("/closed-trade-winrate")
def closed_trade_winrate(days: int = 7) -> dict[str, Any]:
    return get_closed_trade_winrate(days)


@app.get("/exit-reasons")
def exit_reasons(days: int = 3) -> dict[str, Any]:
    return summarize_exit_reasons(days)
