from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

AuditSeverity = Literal["info", "success", "warning", "error", "safety"]


class AuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    timestamp: datetime
    type: str
    severity: AuditSeverity
    source: str
    message: str
    read_only: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditEventFeedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool = True
    auto_trade: bool = False
    read_only: bool = True
    events: list[AuditEvent]
    degraded: bool
    fallback: bool
    generated_at: datetime
