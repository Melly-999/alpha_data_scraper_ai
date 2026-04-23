from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from itertools import count

from app.schemas.common import LogCategory, Severity
from app.schemas.log import LogEntry


class LogService:
    def __init__(self) -> None:
        self._entries: deque[LogEntry] = deque(maxlen=500)
        self._counter = count(1)

    def seed(self, entries: list[LogEntry]) -> None:
        for entry in entries:
            self._entries.append(entry)

    def add(
        self,
        *,
        category: LogCategory,
        severity: Severity,
        message: str,
    ) -> LogEntry:
        entry = LogEntry(
            id=f"log-{next(self._counter):04d}",
            timestamp=datetime.now(timezone.utc),
            category=category,
            severity=severity,
            message=message,
        )
        self._entries.appendleft(entry)
        return entry

    def list(
        self,
        *,
        category: LogCategory | None = None,
        severity: Severity | None = None,
        search: str | None = None,
        limit: int = 100,
    ) -> list[LogEntry]:
        items = list(self._entries)
        if category:
            items = [item for item in items if item.category == category]
        if severity:
            items = [item for item in items if item.severity == severity]
        if search:
            needle = search.lower()
            items = [item for item in items if needle in item.message.lower()]
        return items[:limit]
