from __future__ import annotations

from pydantic import BaseModel


class MT5Status(BaseModel):
    connected: bool
    server: str
    account_id: str
    account_name: str
    broker: str
    currency: str
    leverage: str
    last_heartbeat: str
    latency_ms: int
    symbols_loaded: int
    orders_sync: bool
    positions_sync: bool
    build_version: str
    fallback: bool
    connection_logs: list[dict[str, str]]
