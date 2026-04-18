from __future__ import annotations

from fastapi import Header, HTTPException, status

from .config import get_settings


async def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    expected = get_settings().fastapi_key
    if not x_api_key or x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "reason": "unauthorized",
                "detail": "invalid_or_missing_api_key",
            },
        )
    return x_api_key
