"""Drawdown guard for blocking execution when max drawdown is breached."""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DrawdownGuard:
    """Blocks trade execution when current drawdown exceeds the configured maximum."""

    max_drawdown_pct: float = 2.0

    def check(self, current_drawdown_pct: float) -> tuple[bool, str | None]:
        """
        Return (allowed, block_reason).

        current_drawdown_pct: positive value, e.g. 1.5 means 1.5% drawdown.
        """
        if current_drawdown_pct >= self.max_drawdown_pct:
            reason = (
                f"BLOCKED_MAX_DRAWDOWN "
                f"({current_drawdown_pct:.2f}% >= {self.max_drawdown_pct:.2f}%)"
            )
            logger.warning("Drawdown guard triggered: %s", reason)
            return False, reason
        return True, None
