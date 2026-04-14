from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

try:
    import MetaTrader5 as mt5  # type: ignore
except Exception:  # pragma: no cover
    mt5 = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "db" / "trading.db"
SCHEMA_PATH = PROJECT_ROOT / "db" / "schema.sql"


class LiveBridge:
    def __init__(self) -> None:
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        if not SCHEMA_PATH.exists():
            return
        with sqlite3.connect(DB_PATH) as conn:
            conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    def persist_snapshots(self, snapshots: Iterable[dict[str, Any]]) -> None:
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(DB_PATH) as conn:
            for snap in snapshots:
                signal = snap.get("signal", {})
                conn.execute(
                    """
                    INSERT INTO alerts (
                        created_at,
                        symbol,
                        timeframe,
                        signal,
                        confidence,
                        score,
                        reasons,
                        last_close,
                        lstm_delta,
                        autotrade_status,
                        raw_payload
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        now,
                        snap.get("symbol"),
                        snap.get("timeframe"),
                        signal.get("signal"),
                        signal.get("confidence"),
                        signal.get("score"),
                        json.dumps(signal.get("reasons", [])),
                        snap.get("last_close"),
                        snap.get("lstm_delta"),
                        json.dumps(snap.get("autotrade", {})),
                        json.dumps(snap),
                    ),
                )

    def persist_account_state(self) -> None:
        if mt5 is None:
            return
        if not mt5.initialize():
            return

        try:
            account = mt5.account_info()
            if account is None:
                return

            now = datetime.utcnow().isoformat()

            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    """
                    INSERT INTO equity_snapshots (
                        created_at,
                        balance,
                        equity,
                        profit,
                        margin,
                        free_margin
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        now,
                        float(account.balance),
                        float(account.equity),
                        float(account.profit),
                        float(account.margin),
                        float(account.margin_free),
                    ),
                )
        finally:
            mt5.shutdown()

    def persist_positions(self) -> None:
        if mt5 is None:
            return
        if not mt5.initialize():
            return

        try:
            positions = mt5.positions_get()
            if positions is None:
                return

            now = datetime.utcnow().isoformat()

            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("DELETE FROM position_snapshots")

                for pos in positions:
                    conn.execute(
                        """
                        INSERT INTO position_snapshots (
                            created_at,
                            ticket,
                            symbol,
                            side,
                            volume,
                            price_open,
                            price_current,
                            sl,
                            tp,
                            profit,
                            comment,
                            magic
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            now,
                            int(pos.ticket),
                            pos.symbol,
                            "BUY" if pos.type == 0 else "SELL",
                            float(pos.volume),
                            float(pos.price_open),
                            float(pos.price_current),
                            float(pos.sl),
                            float(pos.tp),
                            float(pos.profit),
                            pos.comment,
                            int(pos.magic),
                        ),
                    )
        finally:
            mt5.shutdown()

    def persist_cycle(self, snapshots: Iterable[dict[str, Any]]) -> None:
        self.persist_snapshots(snapshots)
        self.persist_account_state()
        self.persist_positions()
