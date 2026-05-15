"""Backend-only audit writer for SUPA-003.

Writes AuditEventCreate payloads to mellytrade.audit_events in Supabase.
Falls back gracefully (degraded=True, persisted=False) when the client is
unavailable — never raises to the caller.

Public API:
  write_audit_event(event, *, client=None, _insert_fn=None) -> AuditEventRecord

Scope notes:
  - Does NOT expose frontend routes (deferred to SUPA-004).
  - Does NOT use the service role key directly — the caller provides a client.
  - Does NOT read from any table (read queries deferred to SUPA-004+).
  - Payload always includes read_only=True and dry_run=True columns.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from app.schemas.audit_event import AuditEventCreate, AuditEventRecord

logger = logging.getLogger(__name__)

# Supabase table name (schema prefix is handled at the project / RLS level).
_AUDIT_TABLE = "audit_events"


def _build_payload(event: AuditEventCreate) -> dict[str, Any]:
    """Return the dict that will be sent to Supabase insert."""
    return {
        "event_type": event.event_type,
        "severity": event.severity,
        "source": event.source,
        "message": event.message,
        "metadata": event.metadata or {},
        "read_only": True,
        "dry_run": True,
    }


def write_audit_event(
    event: AuditEventCreate,
    *,
    client: Any | None = None,
    _insert_fn: Callable[[str, dict[str, Any]], Any] | None = None,
) -> AuditEventRecord:
    """Write an audit event to Supabase and return the result record.

    Falls back gracefully when the client is None or the insert raises.
    Never re-raises — the caller always receives an AuditEventRecord.

    Parameters
    ----------
    event:
        Validated AuditEventCreate instance.
    client:
        An instantiated Supabase client (from get_safe_supabase_client).
        Pass None to trigger the degraded path immediately.
    _insert_fn:
        Injectable callable ``(table: str, payload: dict) -> response`` used
        by tests to avoid real network calls.  Pass None (default) to use the
        real client.table(...).insert(...).execute() pattern.
    """
    payload = _build_payload(event)

    if client is None and _insert_fn is None:
        logger.warning("audit_writer: no client — event not persisted (degraded)")
        return AuditEventRecord(
            event_type=event.event_type,
            severity=event.severity,
            source=event.source,
            message=event.message,
            metadata=event.metadata,
            read_only=True,
            dry_run=True,
            id=None,
            persisted=False,
            degraded=True,
            degraded_reason="Supabase client is not available",
        )

    try:
        if _insert_fn is not None:
            response = _insert_fn(_AUDIT_TABLE, payload)
        else:
            response = client.table(_AUDIT_TABLE).insert(payload).execute()

        row: dict[str, Any] = {}
        if response is not None:
            data = getattr(response, "data", None)
            if data and isinstance(data, list) and len(data) > 0:
                row = data[0]

        return AuditEventRecord(
            event_type=event.event_type,
            severity=event.severity,
            source=event.source,
            message=event.message,
            metadata=event.metadata,
            read_only=True,
            dry_run=True,
            id=row.get("id"),
            persisted=True,
            degraded=False,
            degraded_reason=None,
        )

    except Exception as exc:  # noqa: BLE001
        logger.warning("audit_writer: insert failed — degraded: %s", exc)
        return AuditEventRecord(
            event_type=event.event_type,
            severity=event.severity,
            source=event.source,
            message=event.message,
            metadata=event.metadata,
            read_only=True,
            dry_run=True,
            id=None,
            persisted=False,
            degraded=True,
            degraded_reason=str(exc),
        )
