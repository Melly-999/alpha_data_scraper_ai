"""Scanner audit event emitter — SUPA-008.

Emits a single observability event when the scanner preview endpoint is called,
persisting it to Supabase via the established write_audit_event() writer.
Degrades gracefully when the Supabase client is unavailable — never raises.

Design constraints:
  - No route changes, no new API surface.
  - No execution, order, or broker semantics.
  - source="scanner" on the event.
  - metadata contains ONLY: symbol_count (int), mode (str), degraded (bool).
    No prices, account IDs, execution IDs, order IDs, credentials, broker data,
    positions, balances, or execution-shaped payloads.
  - Exactly 1 event: scanner_preview_fetched.

Public API:
  emit_scanner_preview_event(batch, *, client=None, _insert_fn=None) -> AuditEventRecord
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from app.schemas.audit_event import AuditEventCreate, AuditEventRecord
from app.schemas.signal_scanner import SignalScannerBatch
from app.services.audit_writer import write_audit_event

logger = logging.getLogger(__name__)


def emit_scanner_preview_event(
    batch: SignalScannerBatch,
    *,
    client: Any | None = None,
    _insert_fn: Callable[[str, dict[str, Any]], Any] | None = None,
) -> AuditEventRecord:
    """Emit a scanner_preview_fetched audit event to Supabase.

    Emits exactly 1 event with source="scanner", severity="info".
    Metadata carries only symbol_count, mode, and degraded — no prices,
    account IDs, execution IDs, order IDs, credentials, or broker data.

    Falls back gracefully when the client is unavailable — always returns
    an AuditEventRecord and never raises to the caller.

    Parameters
    ----------
    batch:
        The SignalScannerBatch returned by scan_symbols().
    client:
        Supabase client from get_safe_supabase_client().
        Pass None (default) to use the degraded path immediately.
    _insert_fn:
        Injectable callable ``(table: str, payload: dict) -> response`` used
        by tests to avoid real network calls.  Pass None (default) to use the
        real client path.

    Returns
    -------
    AuditEventRecord
        Result record. persisted=False, degraded=True when unavailable or on
        insert failure.
    """
    try:
        # Safe metadata only — no prices, IDs, secrets, or execution-shaped keys.
        # symbol_count is a plain integer count; mode is a fixed literal string.
        metadata: dict[str, Any] = {
            "symbol_count": len(batch.results),
            "mode": batch.execution_mode,
            "degraded": False,
        }

        event = AuditEventCreate(
            event_type="scanner_preview_fetched",
            severity="info",
            source="scanner",
            message=(
                f"Scanner preview fetched for {len(batch.results)} symbol(s). "
                "read_only=True, execution_mode=dry_run_only."
            ),
            metadata=metadata,
        )
        record = write_audit_event(event, client=client, _insert_fn=_insert_fn)

    except Exception as exc:  # noqa: BLE001
        # Schema construction should never fail for these fixed safe specs,
        # but we defend here anyway so the scanner endpoint is never blocked.
        logger.warning(
            "scanner_audit: failed to write scanner_preview_fetched — degraded: %s",
            exc,
        )
        record = AuditEventRecord(
            event_type="scanner_preview_fetched",
            severity="info",
            source="scanner",
            message="Scanner preview fetched.",
            metadata={},
            read_only=True,
            dry_run=True,
            persisted=False,
            degraded=True,
            degraded_reason=str(exc),
        )

    return record
