from __future__ import annotations

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "db" / "trading.db"

app = FastAPI(title="Alpha AI Realtime API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _query(sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


@app.get("/signals")
def signals(limit: int = 50) -> list[dict[str, Any]]:
    return _query(
        "SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )


@app.get("/positions")
def positions() -> list[dict[str, Any]]:
    return _query("SELECT * FROM position_snapshots ORDER BY created_at DESC")


@app.get("/stats")
def stats() -> dict[str, Any]:
    rows = _query("SELECT * FROM equity_snapshots ORDER BY created_at DESC LIMIT 1")
    return rows[0] if rows else {}


@app.websocket("/equity-stream")
async def equity_stream(ws: WebSocket) -> None:
    await ws.accept()
    while True:
        stats_row = stats()
        positions_rows = positions()
        signals_rows = signals(limit=10)

        payload = {
            "type": "dashboard",
            "stats": stats_row,
            "positions": positions_rows,
            "signals": signals_rows,
        }

        await ws.send_text(json.dumps(payload))
        await asyncio.sleep(1)
