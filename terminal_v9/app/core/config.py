from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = os.getenv("APP_NAME", "alpha-trading-terminal-v9")
    ENV = os.getenv("ENV", "local")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DB_PATH = os.getenv("DB_PATH", "data/signals.db")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-me")
    DASHBOARD_VIEWER_API_KEY = os.getenv("DASHBOARD_VIEWER_API_KEY", "viewer-change-me")
    DASHBOARD_OPERATOR_API_KEY = os.getenv("DASHBOARD_OPERATOR_API_KEY", "operator-change-me")
    DASHBOARD_ADMIN_API_KEY = os.getenv("DASHBOARD_ADMIN_API_KEY", "admin-change-me")
    WS_HEARTBEAT_SECONDS = float(os.getenv("WS_HEARTBEAT_SECONDS", "20"))
    WS_REPLAY_DEFAULT_LIMIT = int(os.getenv("WS_REPLAY_DEFAULT_LIMIT", "100"))
    RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60"))
    RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

settings = Settings()
