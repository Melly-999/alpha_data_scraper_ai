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
    # Optional, short, human-readable explanation of the safety implication
    # of this event (one sentence). The Terminal V1 UI surfaces it next to
    # the message so operators can see *why* an event matters for safety
    # without inferring it from the type slug. Optional and nullable for
    # backwards compatibility — older callers and existing fixtures can
    # omit it.
    safety_note: str | None = None
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
