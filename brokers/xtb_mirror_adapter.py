from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from brokers.base import BrokerAccountInfo, BrokerAdapter, BrokerOrder, BrokerPosition

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "db" / "trading.db"
MIRROR_DIR = PROJECT_ROOT / "results" / "xtb_manual"


class XTBMirrorAdapter(BrokerAdapter):
    """Manual / semi-auto adapter for XTB when direct API execution is unavailable."""

    name = "xtb_mirror"

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        MIRROR_DIR.mkdir(parents=True, exist_ok=True)

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        return None

    def get_account_info(self) -> BrokerAccountInfo | None:
        return None

    def get_positions(self) -> list[BrokerPosition]:
        return []

    def get_latest_price(self, symbol: str) -> float | None:
        return None

    def place_order(self, order: BrokerOrder) -> dict[str, Any]:
        now = datetime.utcnow().isoformat()
        payload = {
            "created_at": now,
            "broker": self.name,
            "mode": "manual",
            "order": asdict(order),
            "checklist": self._build_checklist(order),
        }

        out_file = MIRROR_DIR / f"{order.symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._persist_decision(payload)

        return {
            "status": "mirror_saved",
            "broker": self.name,
            "path": str(out_file),
            "checklist": payload["checklist"],
        }

    def _build_checklist(self, order: BrokerOrder) -> list[str]:
        rr_text = "Verify R:R and spread before execution in xStation"
        return [
            f"Open xStation and locate {order.symbol}",
            f"Direction: {order.side}",
            f"Volume: {order.volume}",
            f"Set SL to {order.sl if order.sl is not None else 'MANUAL_REQUIRED'}",
            f"Set TP to {order.tp if order.tp is not None else 'MANUAL_REQUIRED'}",
            rr_text,
            "Confirm no duplicate trade is already open",
            "Confirm daily loss / FTMO rules still allow execution",
            "After execution, export history or record fill in dashboard",
        ]

    def _persist_decision(self, payload: dict[str, Any]) -> None:
        if not DB_PATH.exists():
            return
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    """
                    INSERT INTO risk_events (
                        created_at,
                        symbol,
                        signal,
                        confidence,
                        status,
                        reason,
                        payload
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload["created_at"],
                        payload["order"].get("symbol"),
                        payload["order"].get("side"),
                        None,
                        "XTB_MIRROR_SIGNAL",
                        "Manual execution checklist created",
                        json.dumps(payload),
                    ),
                )
        except Exception:
            return
