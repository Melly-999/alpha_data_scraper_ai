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
    allowed_origins: list[str]
    default_symbol: str


def load_settings() -> Settings:
    config_path = Path("config.json")
    config_data: dict[str, object] = {}
    if config_path.exists():
        config_data = json.loads(config_path.read_text(encoding="utf-8"))

    default_symbol = str(config_data.get("symbol", "EURUSD"))
    frontend_origins = os.getenv(
        "MELLYTRADE_ALLOWED_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    )
    origins = [
        origin.strip() for origin in frontend_origins.split(",") if origin.strip()
    ]

    # Tauri desktop thin-shell (EXE-DESKTOP-002) loads the bundled frontend from
    # the WebView2 custom-protocol origins below. They are fixed, local-only
    # desktop origins (never arbitrary web origins), so always allow them in
    # addition to the configured web origins. Read-only paper preview only; no
    # broker execution, no order controls. This is a CORS allowlist entry only.
    desktop_origins = ["http://tauri.localhost", "https://tauri.localhost"]
    for origin in desktop_origins:
        if origin not in origins:
            origins.append(origin)

    return Settings(
        app_name="MellyTrade Phase 1",
        app_version="0.1.0",
        api_prefix="/api",
        host="127.0.0.1",
        port=8001,
        config_path=config_path,
        allowed_origins=origins,
        default_symbol=default_symbol,
    )
