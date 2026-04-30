from __future__ import annotations

import hmac
import logging

from fastapi import Header, HTTPException, status

from .config import get_settings

log = logging.getLogger(__name__)


async def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    expected = get_settings().fastapi_key
    provided = x_api_key or ""
    if not hmac.compare_digest(provided, expected):
        if not x_api_key:
            log.warning("API auth rejected: missing key")
        else:
            hint = x_api_key[:4] if len(x_api_key) >= 4 else "***"
            log.warning(
                "API auth rejected: invalid key (%d chars, hint=%r)",
                len(x_api_key),
                hint,
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "reason": "unauthorized",
                "detail": "invalid_or_missing_api_key",
            },
        )
    return x_api_key  # type: ignore[return-value]  # None path raises above
