from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    api_prefix: str
    host: str
    port: int
    config_path: Path
    repo_root: Path
    allowed_origins: list[str]
    default_symbol: str
    tracked_symbols: list[str]


def load_settings() -> Settings:
    repo_root = Path(__file__).resolve().parents[2]
    config_path = repo_root / "config.json"
    config_data: dict[str, object] = {}
    if config_path.exists():
        config_data = json.loads(config_path.read_text(encoding="utf-8"))

    default_symbol = str(config_data.get("symbol", "EURUSD"))
    tracked_symbols = [default_symbol, "GBPUSD", "USDJPY", "XAUUSD"]
    frontend_origins = os.getenv(
        "MELLYTRADE_ALLOWED_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    )
    origins = [
        origin.strip() for origin in frontend_origins.split(",") if origin.strip()
    ]

    return Settings(
        app_name="MellyTrade Phase 2",
        app_version="0.2.0",
        api_prefix="/api",
        host="127.0.0.1",
        port=8001,
        config_path=config_path,
        repo_root=repo_root,
        allowed_origins=origins,
        default_symbol=default_symbol,
        tracked_symbols=tracked_symbols,
    )
