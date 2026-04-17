from __future__ import annotations

import logging
from typing import Any, Dict

import httpx

from .config import Settings

log = logging.getLogger(__name__)


async def publish(payload: Dict[str, Any], settings: Settings) -> bool:
    """Forward accepted signals to the Cloudflare Worker hub.

    Fails soft: logs a warning and returns False on any error so the API
    still returns 200 for the persisted signal.
    """
    if not settings.cf_hub_url:
        return False
    headers = {"Content-Type": "application/json"}
    if settings.cf_api_secret:
        headers["X-Hub-Secret"] = settings.cf_api_secret
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                settings.cf_hub_url, json=payload, headers=headers
            )
            resp.raise_for_status()
        return True
    except Exception as exc:  # pragma: no cover - network failures in prod
        log.warning("CF hub publish failed: %s", exc)
        return False
