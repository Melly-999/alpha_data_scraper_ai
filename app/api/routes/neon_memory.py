"""GET-only Neon / ACE memory routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.schemas.neon_memory import NeonMemoryStatus, NeonMemorySummary
from app.services.neon_memory import NeonMemoryService

router = APIRouter(prefix="/api/neon-memory", tags=["neon-memory"])


def get_neon_memory_service() -> NeonMemoryService:
    """Provide the read-only Neon memory service."""

    return NeonMemoryService()


@router.get("/status", response_model=NeonMemoryStatus)
def get_status(
    service: NeonMemoryService = Depends(get_neon_memory_service),
) -> NeonMemoryStatus:
    return service.get_status()


@router.get("/summary", response_model=NeonMemorySummary)
def get_summary(
    service: NeonMemoryService = Depends(get_neon_memory_service),
) -> NeonMemorySummary:
    return service.get_summary()
