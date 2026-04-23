from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.core.container import AppContainer

router = APIRouter(tags=["health"])


@router.get("/health")
def health(container: AppContainer = Depends(get_container)) -> dict[str, object]:
    uptime_seconds = int(
        (
            datetime.now(timezone.utc) - container.runtime_state.started_at
        ).total_seconds()
    )
    return {
        "status": "ok",
        "service": container.settings.app_name,
        "version": container.settings.app_version,
        "uptime_seconds": uptime_seconds,
        "dependencies": {
            "mt5": container.dependencies.mt5_available,
            "claude": container.dependencies.claude_available,
            "news": container.dependencies.news_available,
        },
        "fallback_mode": container.dependencies.fallback_mode,
        "workspace": {
            "repo_root": str(container.settings.repo_root),
            "startup_mode": "repo-root-only",
        },
        "safety": container.risk_service.get_config().model_dump(),
    }
