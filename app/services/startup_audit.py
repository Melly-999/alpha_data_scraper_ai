"""Startup audit event emitter — SUPA-007.

Emits a fixed set of observability events on application boot, persisting them
to Supabase via the established write_audit_event() writer.  Degrades gracefully
when the Supabase client is unavailable — never raises to the caller.

Design constraints:
  - No route changes, no new API surface.
  - No execution, order, or broker semantics.
  - source="system" on all events.
  - metadata is always an empty dict — no account/order/execution IDs, no secrets.
  - Exactly 3 events: backend_started, dry_run_active, read_only_mode_confirmed.

Public API:
  emit_startup_events(*, client=None, _insert_fn=None) -> list[AuditEventRecord]
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from app.schemas.audit_event import AuditEventCreate, AuditEventRecord
from app.services.audit_writer import write_audit_event

logger = logging.getLogger(__name__)

# Fixed boot-time event definitions.
# source and metadata are set at call-site; only event_type / severity / message
# vary per entry.  No account IDs, secrets, or execution-shaped keys.
_STARTUP_EVENT_SPECS: list[dict[str, str]] = [
    {
        "event_type": "backend_started",
        "severity": "success",
        "message": (
            "MellyTrade Phase 1 backend started. "
            "read_only=True, dry_run=True."
        ),
    },
    {
        "event_type": "dry_run_active",
        "severity": "success",
        "message": (
            "dry_run=True. All execution paths are blocked. "
            "No real orders will be placed."
        ),
    },
    {
        "event_type": "read_only_mode_confirmed",
        "severity": "success",
        "message": (
            "System is operating in read-only observability mode. "
            "No order controls are exposed."
        ),
    },
]


def emit_startup_events(
    *,
    client: Any | None = None,
    _insert_fn: Callable[[str, dict[str, Any]], Any] | None = None,
) -> list[AuditEventRecord]:
    """Emit boot-time audit events to Supabase.

    Emits exactly 3 events: backend_started, dry_run_active,
    read_only_mode_confirmed.  All with source="system", severity="success",
    read_only=True, dry_run=True, and empty metadata.

    Falls back gracefully when the client is unavailable — always returns
    a list of 3 AuditEventRecord objects and never raises to the caller.

    Parameters
    ----------
    client:
        Supabase client from get_safe_supabase_client().
        Pass None (default) to use the degraded path immediately.
    _insert_fn:
        Injectable callable ``(table: str, payload: dict) -> response`` used
        by tests to avoid real network calls.  Pass None (default) to use the
        real client path.

    Returns
    -------
    list[AuditEventRecord]
        One record per emitted event (always 3).
        persisted=False, degraded=True when the client is unavailable or the
        insert fails.
    """
    records: list[AuditEventRecord] = []

    for spec in _STARTUP_EVENT_SPECS:
        event_type = spec["event_type"]
        try:
            event = AuditEventCreate(
                event_type=event_type,
                severity=spec["severity"],  # type: ignore[arg-type]
                source="system",
                message=spec["message"],
                metadata={},
            )
            record = write_audit_event(event, client=client, _insert_fn=_insert_fn)
        except Exception as exc:  # noqa: BLE001
            # Schema construction should never fail for these fixed safe specs,
            # but we defend here anyway so startup is never blocked.
            logger.warning(
                "startup_audit: failed to write %r — degraded: %s",
                event_type,
                exc,
            )
            record = AuditEventRecord(
                event_type=event_type,
                severity="info",
                source="system",
                message=spec.get("message", ""),
                metadata={},
                read_only=True,
                dry_run=True,
                persisted=False,
                degraded=True,
                degraded_reason=str(exc),
            )

        records.append(record)

    degraded_count = sum(1 for r in records if r.degraded)
    if degraded_count > 0:
        logger.info(
            "startup_audit: %d/%d events degraded (Supabase unavailable)",
            degraded_count,
            len(records),
        )
    else:
        logger.info(
            "startup_audit: %d startup events persisted to Supabase",
            len(records),
        )

    return records
