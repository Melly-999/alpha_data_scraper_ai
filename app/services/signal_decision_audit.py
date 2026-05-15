"""Signal decision audit event emitter — SUPA-010.

Emits a single observability event when the GET /signals/decisions endpoint
assembles its decision history, persisting it to Supabase via the established
write_audit_event() writer.  Degrades gracefully when the Supabase client is
unavailable — never raises to the caller.

Design constraints:
  - No route changes, no new API surface.
  - No execution, order, or broker semantics.
  - source="scanner" on the event (signal scanner pipeline).
  - metadata contains ONLY: decision_count (int), symbol_filter (str | None),
    degraded (bool).
    No prices, confidence, direction, account IDs, execution IDs, order IDs,
    credentials, broker data, positions, balances, or execution-shaped payloads.
  - Exactly 1 event: signal_decision_evaluated.

Public API:
  emit_signal_decision_event(
      decision_count, symbol_filter, *, client=None, _insert_fn=None
  ) -> AuditEventRecord
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from app.schemas.audit_event import AuditEventCreate, AuditEventRecord
from app.services.audit_writer import write_audit_event

logger = logging.getLogger(__name__)


def emit_signal_decision_event(
    decision_count: int,
    symbol_filter: str | None,
    *,
    client: Any | None = None,
    _insert_fn: Callable[[str, dict[str, Any]], Any] | None = None,
) -> AuditEventRecord:
    """Emit a signal_decision_evaluated audit event to Supabase.

    Emits exactly 1 event with source="scanner", severity="info".
    Metadata carries only decision_count, symbol_filter, and degraded — no
    prices, confidence values, directions, account IDs, execution IDs,
    order IDs, credentials, or broker data.

    Falls back gracefully when the client is unavailable — always returns
    an AuditEventRecord and never raises to the caller.

    Parameters
    ----------
    decision_count:
        Number of decision records assembled for the response (plain integer).
    symbol_filter:
        The symbol query parameter, if provided.  None when not filtered.
        Only the raw filter string is stored — no derived prices or signals.
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
        Result record.  persisted=False, degraded=True when unavailable or on
        insert failure.
    """
    try:
        # Safe metadata only — no prices, confidence, direction, IDs, secrets,
        # or execution-shaped keys.
        # decision_count is a plain integer count.
        # symbol_filter is the raw query param string or None — not a signal.
        metadata: dict[str, Any] = {
            "decision_count": decision_count,
            "symbol_filter": symbol_filter,
            "degraded": False,
        }

        symbol_note = f" (symbol={symbol_filter!r})" if symbol_filter else ""
        event = AuditEventCreate(
            event_type="signal_decision_evaluated",
            severity="info",
            source="scanner",
            message=(
                f"Signal decision history assembled: {decision_count} record(s)"
                f"{symbol_note}. "
                "read_only=True, execution_mode=dry_run_only."
            ),
            metadata=metadata,
        )
        record = write_audit_event(event, client=client, _insert_fn=_insert_fn)

    except Exception as exc:  # noqa: BLE001
        # Schema construction should never fail for these fixed safe specs,
        # but we defend here anyway so the signals/decisions endpoint is never
        # blocked by an audit write failure.
        logger.warning(
            "signal_decision_audit: failed to write signal_decision_evaluated"
            " — degraded: %s",
            exc,
        )
        record = AuditEventRecord(
            event_type="signal_decision_evaluated",
            severity="info",
            source="scanner",
            message="Signal decision history assembled.",
            metadata={},
            read_only=True,
            dry_run=True,
            persisted=False,
            degraded=True,
            degraded_reason=str(exc),
        )

    return record
