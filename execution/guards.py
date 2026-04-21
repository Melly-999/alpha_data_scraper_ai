"""Pre-execution guard functions for the trading execution pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from risk.state_machine import RiskState

logger = logging.getLogger(__name__)


@dataclass
class GuardResult:
    passed: bool
    block_reason: Optional[str] = None


def direction_guard(direction: str) -> GuardResult:
    """Block execution when signal is not a tradeable direction."""
    if direction not in ("BUY", "SELL"):
        reason = f"BLOCKED_NO_TRADE_DIRECTION ({direction})"
        logger.debug("Direction guard failed: %s", reason)
        return GuardResult(passed=False, block_reason=reason)
    return GuardResult(passed=True)


def confidence_guard(confidence: float, min_confidence: float = 70.0) -> GuardResult:
    """Block execution when signal confidence is below the minimum threshold."""
    if confidence < min_confidence:
        reason = f"BLOCKED_LOW_CONFIDENCE ({confidence:.1f} < {min_confidence:.1f})"
        logger.debug("Confidence guard failed: %s", reason)
        return GuardResult(passed=False, block_reason=reason)
    return GuardResult(passed=True)


def risk_state_guard(state: RiskState) -> GuardResult:
    """Block execution when risk state machine is in HALTED state."""
    if state == RiskState.HALTED:
        reason = "BLOCKED_RISK_STATE_HALTED"
        logger.warning("Risk state guard blocked execution: %s", reason)
        return GuardResult(passed=False, block_reason=reason)
    return GuardResult(passed=True)
