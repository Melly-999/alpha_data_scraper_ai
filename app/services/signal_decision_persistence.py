"""Signal decision persistence — SUPA-011.

Writes a single SignalDecisionRecord to mellytrade.signal_decisions in Supabase.
Falls back gracefully (degraded=True, persisted=False) when the client is
unavailable — never raises to the caller.

After a successful insert, emits a secondary observability audit event via
write_audit_event() (fire-and-forget; audit failure never blocks persistence
outcome reporting).

Design constraints:
  - No execution, order, or broker semantics.
  - No account IDs, order IDs, execution IDs, credentials, or secrets.
  - Persists ONLY safe bounded fields from SignalDecisionRecord:
      symbol, direction, confidence, strategy, source, risk_status, decision,
      blocked_reason, audit_event_id — plus safety columns forced to their safe
      values (dry_run=True, auto_trade=False, read_only=True, order_placed=False).
  - The safety columns are also enforced by CHECK constraints in the DB schema.
  - Fire-and-forget compatible — never raises.

Public API:
  write_signal_decision(
      record, *, client=None, _insert_fn=None
  ) -> AuditEventRecord
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from app.schemas.audit_event import AuditEventCreate, AuditEventRecord
from app.schemas.signal_decision import SignalDecisionRecord
from app.services.audit_writer import write_audit_event

logger = logging.getLogger(__name__)

# Table name — schema prefix handled at Supabase project level (search_path).
_DECISIONS_TABLE = "signal_decisions"

# Permitted payload keys — safety audit: never include account/order/execution IDs.
_SAFE_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "symbol",
        "direction",
        "confidence",
        "strategy",
        "source",
        "risk_status",
        "decision",
        "blocked_reason",
        "audit_event_id",
        "dry_run",
        "auto_trade",
        "read_only",
        "order_placed",
    }
)


def _build_decision_payload(record: SignalDecisionRecord) -> dict[str, Any]:
    """Return the safe insert payload for mellytrade.signal_decisions.

    Only safe, bounded fields are included.  Safety columns are always forced
    to their invariant values regardless of the record's own fields.
    """
    return {
        # Signal identity — bounded, safe fields only.
        "symbol": record.symbol,
        "direction": record.direction,
        "confidence": record.confidence,
        "strategy": record.strategy,
        "source": record.source,
        # Risk and decision outcome.
        "risk_status": record.risk_status,
        "decision": record.decision,
        "blocked_reason": record.blocked_reason,
        # Audit correlation — optional, loose coupling only.
        "audit_event_id": record.audit_event_id,
        # Safety columns — forced to invariant values; DB CHECK constraints
        # provide a second enforcement layer.
        "dry_run": True,
        "auto_trade": False,
        "read_only": True,
        "order_placed": False,
    }


def _emit_persistence_audit(
    record: SignalDecisionRecord,
    *,
    client: Any | None,
) -> None:
    """Emit a secondary observability audit event after a successful insert.

    Fire-and-forget — any failure is caught by the caller's try/except.
    Uses write_audit_event() with safe-only metadata.
    """
    event = AuditEventCreate(
        event_type="signal_decision_persisted",
        severity="info",
        source="scanner",
        message=(
            f"Signal decision persisted: {record.symbol} {record.direction} "
            f"→ {record.decision}. "
            "dry_run=True, read_only=True, order_placed=False."
        ),
        metadata={
            # Safe bounded metadata only — no prices, IDs, credentials, secrets.
            "decision": record.decision,
            "symbol_filter": record.symbol,
            "degraded": False,
        },
    )
    write_audit_event(event, client=client)


def write_signal_decision(
    record: SignalDecisionRecord,
    *,
    client: Any | None = None,
    _insert_fn: Callable[[str, dict[str, Any]], Any] | None = None,
) -> AuditEventRecord:
    """Persist a signal decision to mellytrade.signal_decisions.

    Emits exactly one record per call.  Falls back gracefully when the client
    is unavailable — always returns an AuditEventRecord and never raises.

    Parameters
    ----------
    record:
        A validated SignalDecisionRecord.  Only safe bounded fields are
        extracted and persisted; safety columns are always forced to their
        invariant values.
    client:
        Supabase client from get_safe_supabase_client().
        Pass None (default) to trigger the degraded path immediately.
    _insert_fn:
        Injectable callable ``(table: str, payload: dict) -> response`` used
        by tests to avoid real network calls.  Pass None (default) to use the
        real client.table(...).insert(...).execute() path.

    Returns
    -------
    AuditEventRecord
        persisted=True, degraded=False on success.
        persisted=False, degraded=True when client unavailable or on failure.
    """
    try:
        payload = _build_decision_payload(record)

        if client is None and _insert_fn is None:
            logger.warning(
                "signal_decision_persistence: no client — decision not persisted"
                " (degraded). symbol=%s decision=%s",
                record.symbol,
                record.decision,
            )
            return AuditEventRecord(
                event_type="signal_decision_persisted",
                severity="info",
                source="scanner",
                message=(
                    f"Signal decision not persisted: Supabase client unavailable. "
                    f"{record.symbol} {record.direction} → {record.decision}."
                ),
                metadata={},
                read_only=True,
                dry_run=True,
                persisted=False,
                degraded=True,
                degraded_reason="Supabase client is not available",
            )

        if _insert_fn is not None:
            _insert_fn(_DECISIONS_TABLE, payload)
        else:
            client.table(_DECISIONS_TABLE).insert(payload).execute()

        # Secondary observability audit event — fire-and-forget; failure is
        # non-blocking and does not affect the return value.
        try:
            _emit_persistence_audit(record, client=client)
        except Exception:  # noqa: BLE001
            pass

        return AuditEventRecord(
            event_type="signal_decision_persisted",
            severity="info",
            source="scanner",
            message=(
                f"Signal decision persisted: {record.symbol} {record.direction} "
                f"→ {record.decision}. "
                "dry_run=True, read_only=True, order_placed=False."
            ),
            metadata={
                "decision": record.decision,
                "symbol_filter": record.symbol,
                "degraded": False,
            },
            read_only=True,
            dry_run=True,
            persisted=True,
            degraded=False,
        )

    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "signal_decision_persistence: failed to persist decision"
            " — degraded: %s. symbol=%s decision=%s",
            exc,
            getattr(record, "symbol", "?"),
            getattr(record, "decision", "?"),
        )
        return AuditEventRecord(
            event_type="signal_decision_persisted",
            severity="info",
            source="scanner",
            message=(
                f"Signal decision persistence failed (degraded). "
                f"{getattr(record, 'symbol', '?')} "
                f"→ {getattr(record, 'decision', '?')}."
            ),
            metadata={},
            read_only=True,
            dry_run=True,
            persisted=False,
            degraded=True,
            degraded_reason=str(exc),
        )
