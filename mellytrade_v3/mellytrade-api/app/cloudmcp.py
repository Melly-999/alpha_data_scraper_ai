from __future__ import annotations

import logging
from typing import Tuple

import httpx

from .config import CloudMCPConfig, get_cloudmcp_config

log = logging.getLogger(__name__)


def build_client(config: CloudMCPConfig | None = None) -> httpx.Client:
    """Build an HTTP client pointed at the CloudMCP.run unified router.

    All logical servers (``files``, ``web``, ``memory``, …) share one HTTP
    endpoint — the router fans them out internally. Auth is URL-based, so
    no ``Authorization`` header is set here.
    """
    cfg = config or get_cloudmcp_config()
    if not cfg.enabled:
        raise RuntimeError(
            "CloudMCP is disabled. Set CLOUDMCP_ENABLED=true (and "
            "CLOUDMCP_ROUTER_URL) before calling build_client()."
        )
    timeout = httpx.Timeout(cfg.timeout_seconds, connect=cfg.connect_timeout_seconds)
    return httpx.Client(base_url=cfg.router_url, timeout=timeout)


def default_servers(config: CloudMCPConfig | None = None) -> Tuple[str, ...]:
    """Return the configured default-server list (possibly empty).

    The router exposes its own default surface when this is empty — callers
    should treat an empty tuple as "trust the router's default".
    """
    cfg = config or get_cloudmcp_config()
    return cfg.default_servers
