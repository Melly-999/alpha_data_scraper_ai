"""In-memory signal history buffer with duplicate detection."""

from __future__ import annotations

import logging
import threading
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
    """Keeps the last *maxlen* signal records and detects duplicates.

    All public methods are thread-safe.
    """

    def __init__(self, maxlen: int = 50) -> None:
        self._buffer: Deque[SignalRecord] = deque(maxlen=maxlen)
        self._lock = threading.Lock()

    def append(self, record: SignalRecord) -> None:
        """Append a new signal record; logs a warning if it is a duplicate."""
        with self._lock:
            is_dup = self._is_duplicate_unlocked(record)
            self._buffer.append(record)
        if is_dup:
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

    def get_latest(self) -> Optional[SignalRecord]:
        """Return the most recently appended record, or None if empty."""
        with self._lock:
            return self._buffer[-1] if self._buffer else None

    def get_last_n(self, n: int) -> list[SignalRecord]:
        """Return the last *n* records (oldest first)."""
        with self._lock:
            return list(self._buffer)[-n:]

    def get_latest_signal(self, symbol: str) -> Optional[SignalRecord]:
        """Return the most recent record for *symbol*, or None."""
        with self._lock:
            for record in reversed(list(self._buffer)):
                if record.symbol == symbol:
                    return record
        return None

    def duplicate_signal_guard(self, symbol: str, direction: str) -> bool:
        """Return True (and log a warning) when the last signal for *symbol*
        has the same direction, indicating a duplicate."""
        latest = self.get_latest_signal(symbol)
        if latest and latest.direction == direction:
            logger.warning("Duplicate signal guard triggered: %s %s", symbol, direction)
            return True
        return False

    def _is_duplicate_unlocked(self, record: SignalRecord) -> bool:
        """Check for duplicate without acquiring the lock (caller must hold it)."""
        for existing in reversed(list(self._buffer)):
            if existing.symbol == record.symbol:
                return existing.direction == record.direction
        return False
