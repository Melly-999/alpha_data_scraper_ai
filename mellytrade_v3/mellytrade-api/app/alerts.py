"""Read-only alert derivation for the Direction B trader dashboard.

Alerts are synthesized from existing safety posture, audit/risk state, and
placeholder external-data status. They are never persisted by this module and
do not introduce any execution or mutation path.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from .audit import _split_reason
from .config import Settings
from .models import SignalRecord
from .schemas import AlertOut

_RISK_GATE_REASONS = {
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


def _live_orders_blocked(settings: Settings) -> bool:
    return settings.dry_run or settings.read_only or not settings.autotrade_enabled


def _safety_alerts(settings: Settings, now: datetime) -> List[AlertOut]:
    alerts: List[AlertOut] = []
    if settings.dry_run:
        alerts.append(
            AlertOut(
                id="safety-dry-run-active",
                timestamp=now,
                severity="success",
                category="safety",
                title="Dry run active",
                message="No live orders will be sent while dry_run is active.",
                source="settings",
                read_only=settings.read_only,
                metadata={"dry_run": settings.dry_run},
            )
        )

    if settings.read_only:
        alerts.append(
            AlertOut(
                id="safety-read-only-mode-active",
                timestamp=now,
                severity="success",
                category="safety",
                title="Read-only mode active",
                message="Dashboard APIs expose read-only trader context only.",
                source="settings",
                read_only=settings.read_only,
                metadata={"read_only": settings.read_only},
            )
        )

    if _live_orders_blocked(settings):
        alerts.append(
            AlertOut(
                id="safety-live-orders-blocked",
                timestamp=now,
                severity="success",
                category="safety",
                title="Live orders blocked",
                message="Live execution is blocked by Direction B safety gates.",
                source="settings",
                read_only=settings.read_only,
                metadata={
                    "dry_run": settings.dry_run,
                    "read_only": settings.read_only,
                    "autotrade_enabled": settings.autotrade_enabled,
                },
            )
        )

    if settings.max_risk_percent > 1.0:
        alerts.append(
            AlertOut(
                id="backend-max-risk-above-invariant",
                timestamp=now,
                severity="error",
                category="backend_degraded",
                title="Max risk safety invariant exceeded",
                message="Configured max_risk_percent is above the Direction B 1% ceiling.",
                source="settings",
                read_only=settings.read_only,
                metadata={"max_risk_percent": settings.max_risk_percent},
            )
        )

    return alerts


def _signal_alert(record: SignalRecord, read_only: bool) -> AlertOut | None:
    reason_code, reason_detail = _split_reason(record.reason or "")
    if record.status != "rejected":
        return None

    if reason_code == "cooldown_active":
        severity = "warning"
        category = "cooldown_active"
        title = "Cooldown active"
        message = f"Cooldown blocked {record.action} {record.symbol}."
    elif reason_code in _RISK_GATE_REASONS:
        severity = "warning"
        category = "risk_gate_failed"
        title = "Risk gate rejected signal"
        message = f"Risk gate {reason_code} blocked {record.symbol}."
    else:
        severity = "info"
        category = "signal_rejected"
        title = "Signal rejected"
        message = f"{record.action} {record.symbol} was rejected."

    metadata: dict[str, object] = {
        "reason": reason_code,
        "action": record.action,
        "confidence": record.confidence,
        "risk_pct": record.risk_percent,
        "source": record.source,
    }
    if reason_detail:
        metadata["reason_detail"] = reason_detail

    return AlertOut(
        id=f"signal-{record.id}-{category}",
        timestamp=_ensure_aware(record.created_at),
        severity=severity,  # type: ignore[arg-type]
        category=category,
        title=title,
        message=message,
        source="signals",
        symbol=record.symbol,
        signal_id=record.id,
        read_only=read_only,
        metadata=metadata,
    )


def _placeholder_alert(settings: Settings, now: datetime) -> AlertOut:
    return AlertOut(
        id="placeholder-high-impact-news",
        timestamp=now,
        severity="info",
        category="high_impact_news_placeholder",
        title="High-impact news placeholder",
        message="News-driven alerting is reserved for a future read-only data pass.",
        source="placeholder",
        read_only=settings.read_only,
        metadata={"placeholder": True},
    )


def collect_alerts(db: Session, settings: Settings, limit: int) -> List[AlertOut]:
    """Return a bounded, read-only alert list for the dashboard."""
    safe_limit = max(1, min(limit, 500))
    now = _utcnow()

    rows = (
        db.execute(
            select(SignalRecord)
            .order_by(SignalRecord.created_at.desc())
            .limit(safe_limit)
        )
        .scalars()
        .all()
    )

    derived = [
        alert
        for alert in (_signal_alert(record, settings.read_only) for record in rows)
        if alert is not None
    ]
    alerts = (
        _safety_alerts(settings, now) + derived + [_placeholder_alert(settings, now)]
    )
    return alerts[:safe_limit]
