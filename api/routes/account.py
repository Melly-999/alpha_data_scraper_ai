"""GET /account — live account snapshot endpoint."""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.account_service import AccountService

logger = logging.getLogger(__name__)
router = APIRouter()

_account_service = AccountService()


class AccountResponse(BaseModel):
    balance: float
    equity: float
    free_margin: float
    drawdown: float
    open_positions: int
    timestamp: datetime


@router.get("/account", response_model=AccountResponse)
def get_account() -> AccountResponse:
    """Return the current account snapshot (balance, equity, drawdown, positions)."""
    try:
        snap = _account_service.get_account_snapshot()
        logger.info("Account endpoint served: balance=%.2f", snap.balance)
        return AccountResponse(
            balance=snap.balance,
            equity=snap.equity,
            free_margin=snap.free_margin,
            drawdown=snap.drawdown,
            open_positions=snap.open_positions,
            timestamp=snap.timestamp,
        )
    except Exception as exc:
        logger.error("Account endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve account data") from exc
