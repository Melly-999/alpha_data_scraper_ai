"""In-memory signal history buffer with duplicate detection."""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, Optional

logger = logging.getLogger(__name__)


@dataclass
class SignalRecord:
    symbol: str
    direction: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class SignalHistoryService:
    """Keeps the last *maxlen* signal records and detects duplicates."""

    def __init__(self, maxlen: int = 50) -> None:
        self._buffer: Deque[SignalRecord] = deque(maxlen=maxlen)

    def append(self, record: SignalRecord) -> None:
        """Append a new signal record; logs a warning if it is a duplicate."""
        if self._is_duplicate(record):
            logger.warning(
                "Duplicate signal detected: %s %s", record.symbol, record.direction
            )
        else:
            logger.info(
                "Signal appended to history: %s %s @ %.1f%%",
                record.symbol,
                record.direction,
                record.confidence,
            )
        self._buffer.append(record)

    def get_latest(self) -> Optional[SignalRecord]:
        """Return the most recently appended record, or None if empty."""
        return self._buffer[-1] if self._buffer else None

    def get_last_n(self, n: int) -> list[SignalRecord]:
        """Return the last *n* records (oldest first)."""
        return list(self._buffer)[-n:]

    def get_latest_signal(self, symbol: str) -> Optional[SignalRecord]:
        """Return the most recent record for *symbol*, or None."""
        for record in reversed(list(self._buffer)):
            if record.symbol == symbol:
                return record
        return None

    def duplicate_signal_guard(self, symbol: str, direction: str) -> bool:
        """Return True (and log a warning) when the last signal for *symbol*
        has the same direction, indicating a duplicate."""
        latest = self.get_latest_signal(symbol)
        if latest and latest.direction == direction:
            logger.warning(
                "Duplicate signal guard triggered: %s %s", symbol, direction
            )
            return True
        return False

    def _is_duplicate(self, record: SignalRecord) -> bool:
        latest = self.get_latest_signal(record.symbol)
        return latest is not None and latest.direction == record.direction
