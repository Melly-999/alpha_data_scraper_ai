"""GET /execution/decision — latest execution decision endpoint."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from execution_service import ExecutionService

logger = logging.getLogger(__name__)
router = APIRouter()

# Injected at startup by api/app.py via set_execution_service()
_execution_service: Optional[ExecutionService] = None


def set_execution_service(svc: ExecutionService) -> None:
    """Wire the shared ExecutionService instance into this route module."""
    global _execution_service
    _execution_service = svc
    logger.info("ExecutionService wired into /execution/decision route")


class ExecutionDecisionResponse(BaseModel):
    symbol: Optional[str]
    direction: Optional[str]
    confidence_used: Optional[float]
    should_execute: Optional[bool]
    block_reason: Optional[str]
    risk_state: Optional[str]
    mode: str
    timestamp: Optional[datetime]


def _null_response() -> ExecutionDecisionResponse:
    return ExecutionDecisionResponse(
        symbol=None,
        direction=None,
        confidence_used=None,
        should_execute=None,
        block_reason=None,
        risk_state=None,
        mode="dry_run",
        timestamp=None,
    )


@router.get("/execution/decision", response_model=ExecutionDecisionResponse)
def get_execution_decision() -> ExecutionDecisionResponse:
    """Return the most recent execution decision, or a null-safe response if none exists."""
    if _execution_service is None:
        logger.warning("ExecutionService not initialised; returning null-safe response")
        return _null_response()

    try:
        decision = _execution_service.get_latest_decision()
        if decision is None:
            logger.info("No execution decision available yet")
            return _null_response()

        logger.info(
            "Execution decision endpoint served: %s %s should_execute=%s",
            decision.symbol,
            decision.direction,
            decision.should_execute,
        )
        return ExecutionDecisionResponse(
            symbol=decision.symbol,
            direction=decision.direction,
            confidence_used=decision.confidence_used,
            should_execute=decision.should_execute,
            block_reason=decision.block_reason,
            risk_state=decision.risk_state,
            mode=decision.mode,
            timestamp=decision.timestamp,
        )
    except Exception as exc:
        logger.error("Execution decision endpoint error: %s", exc)
        return _null_response()
