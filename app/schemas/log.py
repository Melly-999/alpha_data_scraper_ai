from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import LogCategory, Severity


class LogEntry(BaseModel):
    id: str
    timestamp: datetime
    category: LogCategory
    severity: Severity
    message: str
