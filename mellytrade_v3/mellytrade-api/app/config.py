from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional for tests
    pass


def _float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _bool(name: str, default: bool) -> bool:
    """Parse env flag, only loosen safety defaults via explicit truthy values."""
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./mellytrade.db")
    fastapi_key: str = os.getenv("FASTAPI_KEY", "change-me-api-key")
    cf_hub_url: Optional[str] = os.getenv("CF_HUB_URL") or None
    cf_api_secret: Optional[str] = os.getenv("CF_API_SECRET") or None
    cooldown_seconds: int = _int("COOLDOWN_SECONDS", 60)
    min_confidence: float = _float("MIN_CONFIDENCE", 70.0)
    max_risk_percent: float = _float("MAX_RISK_PERCENT", 1.0)
    # Safety posture: locked-on by default. Direction B is read-only and
    # never places live orders. These flags surface to the dashboard so
    # the operator can verify the running mode at a glance.
    dry_run: bool = _bool("DRY_RUN", True)
    autotrade_enabled: bool = _bool("AUTOTRADE_ENABLED", False)
    read_only: bool = _bool("READ_ONLY", True)


def get_settings() -> Settings:
    return Settings()
