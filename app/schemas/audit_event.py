"""Pydantic schemas for SUPA-003 audit event write path.

Separate from the in-memory AuditEvent in terminal.py (which serves the
GET /audit-feed endpoint). This module covers the Supabase persistence schemas.

Public types:
  AuditSeverity      — matches SUPA-001 SQL CHECK constraint values
  AuditEventSource   — allowed source identifiers
  AuditEventCreate   — input schema for audit writes (validated, safe)
  AuditEventRecord   — returned after a write attempt (persisted + degraded fields)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

AuditSeverity = Literal["info", "success", "warning", "error", "safety"]

AuditEventSource = Literal[
    "system",
    "scanner",
    "ai_workspace",
    "broker_registry",
    "supabase",
    "safety",
]

# Metadata keys that must never appear — credentials, IDs, execution triggers.
_FORBIDDEN_METADATA_KEYS: frozenset[str] = frozenset(
    {
        "account_id",
        "order_id",
        "execution_id",
        "trade_id",
        "secret",
        "token",
        "api_key",
        "password",
        "credential",
        "service_role",
    }
)

# Metadata keys that indicate live execution intent.
_EXECUTION_SHAPED_METADATA_KEYS: frozenset[str] = frozenset(
    {
        "place_order",
        "execute_trade",
        "broker_execute",
        "cancel_order",
        "modify_order",
        "enable_autotrade",
        "disable_dry_run",
        "connect_live",
    }
)


def _validate_metadata(value: dict[str, Any]) -> dict[str, Any]:
    """Raise ValueError if metadata contains any forbidden or execution-shaped keys."""
    forbidden_found = _FORBIDDEN_METADATA_KEYS & value.keys()
    if forbidden_found:
        raise ValueError(
            f"Metadata contains forbidden key(s): {sorted(forbidden_found)}. "
            "Credentials, account IDs, and secrets must not appear in audit metadata."
        )
    execution_found = _EXECUTION_SHAPED_METADATA_KEYS & value.keys()
    if execution_found:
        raise ValueError(
            f"Metadata contains execution-shaped key(s): {sorted(execution_found)}. "
            "No live execution semantics in audit metadata."
        )
    return value


class AuditEventCreate(BaseModel):
    """Input schema for writing an audit event to Supabase.

    Safety invariants (enforced by model_validator):
      - read_only is always True
      - dry_run is always True

    Metadata invariants (enforced by field_validator):
      - No forbidden credential/ID keys
      - No execution-shaped keys
    """

    model_config = ConfigDict(extra="forbid")

    event_type: str = Field(..., min_length=1, description="Categorises the audit event.")
    severity: AuditSeverity = Field(
        default="info",
        description="Matches SUPA-001 SQL CHECK constraint values.",
    )
    source: AuditEventSource = Field(
        default="system",
        description="The backend component emitting the event.",
    )
    message: str = Field(..., min_length=1, description="Human-readable event description.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional key/value context. Forbidden keys are rejected.",
    )

    read_only: bool = Field(
        default=True,
        description="Always True — structurally enforced. No write semantics.",
    )
    dry_run: bool = Field(
        default=True,
        description="Always True — structurally enforced.",
    )

    @field_validator("metadata")
    @classmethod
    def _check_metadata_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        return _validate_metadata(value)

    @model_validator(mode="after")
    def _enforce_safety_invariants(self) -> "AuditEventCreate":
        if self.read_only is not True:
            raise ValueError("read_only must always be True for AuditEventCreate")
        if self.dry_run is not True:
            raise ValueError("dry_run must always be True for AuditEventCreate")
        return self


class AuditEventRecord(BaseModel):
    """Returned after a write attempt — includes persistence outcome fields.

    When persisted=False the id and created_at fields may be None/synthetic.
    degraded=True signals the writer fell back gracefully (no exception raised).
    """

    model_config = ConfigDict(extra="forbid")

    event_type: str
    severity: AuditSeverity
    source: AuditEventSource
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    read_only: bool = True
    dry_run: bool = True

    id: str | None = Field(default=None, description="UUID assigned by Supabase on insert.")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Insert timestamp. Synthetic when persisted=False.",
    )
    persisted: bool = Field(
        default=False,
        description="True when the row was successfully inserted into Supabase.",
    )
    degraded: bool = Field(
        default=False,
        description="True when the writer fell back gracefully.",
    )
    degraded_reason: str | None = Field(
        default=None,
        description="Human-readable explanation when degraded=True.",
    )
