from __future__ import annotations
from fastapi import APIRouter, Depends
from app.core.security import require_viewer
from app.services.mt5_health_service import get_mt5_health

router = APIRouter()

@router.get("/mt5-health", dependencies=[Depends(require_viewer)])
def mt5_health():
    return get_mt5_health()
