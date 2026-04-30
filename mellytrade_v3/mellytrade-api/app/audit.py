"""Read-only audit feed for the Direction B trader dashboard.

Audit events are derived from the existing `signals` table plus the static
safety posture surfaced by `Settings`. No new mutation paths are introduced
here: the dashboard only consumes events, it never enqueues them.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import Settings
from .models import SignalRecord
from .schemas import AuditEvent

# Subset of `signal.reason` strings that already correspond to a risk gate
# trigger. Anything else is reported under the generic `risk_gate_failed`.
_COOLDOWN_REASONS = {"cooldown_active"}
_GATE_REASONS = {
    "confidence_below_min",
    "risk_above_max",
    "missing_sl_tp",
    "invalid_action",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _split_reason(raw: str) -> tuple[str, Optional[str]]:
    if not raw:
        return "", None
    if ":" in raw:
        head, tail = raw.split(":", 1)
        return head.strip(), tail.strip() or None
    return raw.strip(), None


def _record_to_event(record: SignalRecord) -> AuditEvent:
    """Translate a persisted SignalRecord into a dashboard audit event."""
    reason_code, reason_detail = _split_reason(record.reason or "")
    timestamp = _ensure_aware(record.created_at)

    detail: dict[str, object] = {
        "symbol": record.symbol,
        "action": record.action,
        "confidence": record.confidence,
        "risk_pct": record.risk_percent,
        "source": record.source,
    }
    if reason_detail:
        detail["reason_detail"] = reason_detail
    if reason_code:
        detail["reason"] = reason_code

    if record.status == "accepted":
        return AuditEvent(
            type="signal_accepted",
            timestamp=timestamp,
            severity="info",
            message=f"{record.action} {record.symbol} accepted (confidence "
            f"{record.confidence:g})",
            detail=detail,
            signal_id=record.id,
        )

    # Rejected paths: classify by reason code.
    if reason_code in _COOLDOWN_REASONS:
        event_type = "cooldown_active"
        severity = "warning"
        message = f"Cooldown blocked {record.action} {record.symbol}"
    elif reason_code in _GATE_REASONS:
        event_type = "risk_gate_failed"
        severity = "warning"
        message = f"Risk gate {reason_code} blocked {record.symbol}"
    else:
        event_type = "signal_rejected"
        severity = "warning"
        message = f"{record.action} {record.symbol} rejected"

    return AuditEvent(
        type=event_type,  # type: ignore[arg-type]
        timestamp=timestamp,
        severity=severity,  # type: ignore[arg-type]
        message=message,
        detail=detail,
        signal_id=record.id,
    )


def _safety_state_events(settings: Settings) -> List[AuditEvent]:
    """Static safety posture markers shown at the top of the audit feed."""
    now = _utcnow()
    events: List[AuditEvent] = []

    if settings.dry_run:
        events.append(
            AuditEvent(
                type="dry_run_active",
                timestamp=now,
                severity="info",
                message="dry_run is active; no live orders will be sent",
                detail={"dry_run": True},
            )
        )

    if settings.read_only:
        events.append(
            AuditEvent(
                type="read_only_mode_active",
                timestamp=now,
                severity="info",
                message="read_only mode is active; dashboard cannot place trades",
                detail={"read_only": True},
            )
        )

    live_blocked = (
        settings.dry_run or settings.read_only or not settings.autotrade_enabled
    )
    if live_blocked:
        events.append(
            AuditEvent(
                type="live_orders_blocked",
                timestamp=now,
                severity="info",
                message="Live orders are blocked by safety configuration",
                detail={
                    "dry_run": settings.dry_run,
                    "read_only": settings.read_only,
                    "autotrade_enabled": settings.autotrade_enabled,
                },
            )
        )

    return events


def collect_events(
    db: Session,
    settings: Settings,
    limit: int,
    event_type: Optional[str] = None,
) -> List[AuditEvent]:
    """Return an ordered, read-only feed of audit events for the dashboard."""
    safe_limit = max(1, min(limit, 500))

    rows = (
        db.execute(
            select(SignalRecord)
            .order_by(SignalRecord.created_at.desc())
            .limit(safe_limit)
        )
        .scalars()
        .all()
    )

    derived = [_record_to_event(r) for r in rows]
    static = _safety_state_events(settings)
    combined: List[AuditEvent] = static + derived

    if event_type is not None:
        combined = [e for e in combined if e.type == event_type]

    return combined[:safe_limit]
