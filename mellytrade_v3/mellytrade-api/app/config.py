from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional, Tuple

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
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _csv(name: str) -> Tuple[str, ...]:
    raw = os.getenv(name)
    if not raw:
        return ()
    return tuple(item.strip() for item in raw.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./mellytrade.db")
    fastapi_key: str = os.getenv("FASTAPI_KEY", "change-me-api-key")
    cf_hub_url: Optional[str] = os.getenv("CF_HUB_URL") or None
    cf_api_secret: Optional[str] = os.getenv("CF_API_SECRET") or None
    cooldown_seconds: int = _int("COOLDOWN_SECONDS", 60)
    min_confidence: float = _float("MIN_CONFIDENCE", 70.0)
    max_risk_percent: float = _float("MAX_RISK_PERCENT", 1.0)


def get_settings() -> Settings:
    return Settings()


@dataclass(frozen=True)
class CloudMCPConfig:
    """Typed view of the CloudMCP.run unified-router environment.

    The router uses URL-based auth (the per-user subdomain identifies the
    caller), so no bearer token is required. All legacy per-server variables
    (``CLOUDMCP_TOKEN``, ``CLOUDMCP_FILES_*``, ``CLOUDMCP_WEB_*``,
    ``CLOUDMCP_MEMORY_*``) are intentionally unsupported — the migration is
    one-way.
    """

    enabled: bool
    router_url: str
    default_servers: Tuple[str, ...] = field(default_factory=tuple)
    timeout_seconds: float = 30.0
    connect_timeout_seconds: float = 5.0

    @classmethod
    def from_env(cls) -> "CloudMCPConfig":
        enabled = _bool("CLOUDMCP_ENABLED", False)
        router_url = (os.getenv("CLOUDMCP_ROUTER_URL") or "").strip()
        if enabled and not router_url:
            raise RuntimeError(
                "CLOUDMCP_ENABLED is true but CLOUDMCP_ROUTER_URL is not set. "
                "Set CLOUDMCP_ROUTER_URL to your CloudMCP.run router endpoint "
                "(e.g. https://<user-id>.router.cloudmcp.run/mcp) or disable "
                "CLOUDMCP_ENABLED."
            )
        return cls(
            enabled=enabled,
            router_url=router_url,
            default_servers=_csv("CLOUDMCP_DEFAULT_SERVERS"),
            timeout_seconds=_float("CLOUDMCP_TIMEOUT_SECONDS", 30.0),
            connect_timeout_seconds=_float("CLOUDMCP_CONNECT_TIMEOUT_SECONDS", 5.0),
        )


def get_cloudmcp_config() -> CloudMCPConfig:
    """Load and validate CloudMCP settings from the environment.

    Raises ``RuntimeError`` if ``CLOUDMCP_ENABLED`` is true but
    ``CLOUDMCP_ROUTER_URL`` is missing — fail-early so misconfigured
    deployments don't silently fall back to a no-op router.
    """
    return CloudMCPConfig.from_env()
