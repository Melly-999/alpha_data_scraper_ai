"""Risk state machine for real-time trading gate management."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class RiskState(str, Enum):
    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    HALTED = "HALTED"


@dataclass
class RiskStateMachine:
    """Transitions risk state based on daily PnL thresholds."""

    daily_loss_caution_pct: float = 1.0
    daily_loss_halt_pct: float = 2.0
    _state: RiskState = field(default=RiskState.NORMAL, repr=False, init=False)

    def evaluate(self, daily_pnl_pct: float) -> RiskState:
        """Return updated RiskState given current daily PnL percentage."""
        if daily_pnl_pct <= -self.daily_loss_halt_pct:
            new_state = RiskState.HALTED
        elif daily_pnl_pct <= -self.daily_loss_caution_pct:
            new_state = RiskState.CAUTION
        else:
            new_state = RiskState.NORMAL

        if new_state != self._state:
            logger.warning(
                "Risk state transition: %s -> %s (daily_pnl=%.2f%%)",
                self._state.value,
                new_state.value,
                daily_pnl_pct,
            )
        self._state = new_state
        return self._state

    @property
    def state(self) -> RiskState:
        return self._state
