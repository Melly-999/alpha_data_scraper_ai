"""Read-only report assembly for Direction B dashboard summaries.

Reports compose existing safety, signal, alert, audit, and risk config state.
They do not persist data and do not introduce execution or mutation paths.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from . import alerts, audit
from .config import Settings
from .models import SignalRecord
from .schemas import (
    AlertOut,
    AuditEvent,
    HealthOut,
    ReportOut,
    ReportPeriod,
    ReportSignalCounts,
    RiskConfigOut,
    RiskGateStatus,
)

REPORT_ALERT_LIMIT = 500
REPORT_AUDIT_LIMIT = 10
_CURRENT_ALERT_SOURCES = {"settings", "placeholder"}
_CURRENT_AUDIT_TYPES = {
    "dry_run_active",
    "read_only_mode_active",
    "live_orders_blocked",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _live_orders_blocked(settings: Settings) -> bool:
    return settings.dry_run or settings.read_only or not settings.autotrade_enabled


def _window(period: ReportPeriod, now: datetime) -> tuple[datetime, datetime]:
    if period == "daily":
        return now.replace(hour=0, minute=0, second=0, microsecond=0), now
    return now - timedelta(days=7), now


def _risk_config(settings: Settings) -> RiskConfigOut:
    return RiskConfigOut(
        min_confidence=settings.min_confidence,
        max_risk_percent=settings.max_risk_percent,
        cooldown_seconds=settings.cooldown_seconds,
        dry_run=settings.dry_run,
        autotrade_enabled=settings.autotrade_enabled,
        read_only=settings.read_only,
        live_orders_blocked=_live_orders_blocked(settings),
        gates=[
            RiskGateStatus(
                name="min_confidence",
                active=True,
                description=(
                    f"Reject signals with confidence < {settings.min_confidence:g}"
                ),
            ),
            RiskGateStatus(
                name="max_risk_percent",
                active=True,
                description=(
                    f"Reject signals with risk_percent > "
                    f"{settings.max_risk_percent:g}"
                ),
            ),
            RiskGateStatus(
                name="cooldown_seconds",
                active=True,
                description=(
                    f"Reject same-symbol BUY/SELL within "
                    f"{settings.cooldown_seconds}s"
                ),
            ),
            RiskGateStatus(
                name="sl_tp_required",
                active=True,
                description="BUY/SELL must include valid stop_loss and take_profit",
            ),
        ],
    )


def _safety_posture(settings: Settings) -> HealthOut:
    return HealthOut(
        cooldown_seconds=settings.cooldown_seconds,
        min_confidence=settings.min_confidence,
        max_risk_percent=settings.max_risk_percent,
        database=settings.database_url.split("://", 1)[0],
        dry_run=settings.dry_run,
        autotrade_enabled=settings.autotrade_enabled,
        read_only=settings.read_only,
        live_orders_blocked=_live_orders_blocked(settings),
    )


def _signals_in_window(
    db: Session,
    window_start: datetime,
    window_end: datetime,
) -> List[SignalRecord]:
    stmt: Select[tuple[SignalRecord]] = (
        select(SignalRecord)
        .where(SignalRecord.created_at >= window_start)
        .where(SignalRecord.created_at <= window_end)
        .order_by(SignalRecord.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def _signal_counts(records: List[SignalRecord]) -> ReportSignalCounts:
    accepted = sum(1 for record in records if record.status == "accepted")
    rejected = sum(1 for record in records if record.status == "rejected")
    return ReportSignalCounts(
        total=len(records),
        accepted=accepted,
        rejected=rejected,
    )


def _alerts_in_window(
    db: Session,
    settings: Settings,
    window_start: datetime,
    window_end: datetime,
) -> List[AlertOut]:
    items = alerts.collect_alerts(
        db=db,
        settings=settings,
        limit=REPORT_ALERT_LIMIT,
    )
    return [
        item
        for item in items
        if item.source in _CURRENT_ALERT_SOURCES
        or window_start <= _ensure_aware(item.timestamp) <= window_end
    ]


def _audit_events(
    db: Session,
    settings: Settings,
    window_start: datetime,
    window_end: datetime,
) -> List[AuditEvent]:
    events = audit.collect_events(
        db=db,
        settings=settings,
        limit=REPORT_AUDIT_LIMIT,
    )
    return [
        event
        for event in events
        if event.type in _CURRENT_AUDIT_TYPES
        or window_start <= _ensure_aware(event.timestamp) <= window_end
    ][:REPORT_AUDIT_LIMIT]


def _markdown_summary(
    period: ReportPeriod,
    signal_counts: ReportSignalCounts,
    alerts_by_severity: dict[str, int],
    alerts_by_category: dict[str, int],
    settings: Settings,
) -> str:
    severity_text = ", ".join(
        f"{key}: {value}" for key, value in sorted(alerts_by_severity.items())
    )
    category_text = ", ".join(
        f"{key}: {value}" for key, value in sorted(alerts_by_category.items())
    )
    return "\n".join(
        [
            f"## {period.title()} MellyTrade Report",
            "",
            "### Safety posture",
            f"- dry_run: {str(settings.dry_run).lower()}",
            f"- read_only: {str(settings.read_only).lower()}",
            f"- autotrade_enabled: {str(settings.autotrade_enabled).lower()}",
            f"- live_orders_blocked: {str(_live_orders_blocked(settings)).lower()}",
            f"- max_risk_percent: {settings.max_risk_percent:g}",
            "",
            "### Signals",
            f"- total: {signal_counts.total}",
            f"- accepted: {signal_counts.accepted}",
            f"- rejected: {signal_counts.rejected}",
            "",
            "### Alerts",
            f"- severity: {severity_text or 'none'}",
            f"- category: {category_text or 'none'}",
            "",
            "This report is read-only and does not place or modify orders.",
        ]
    )


def build_report(db: Session, settings: Settings, period: ReportPeriod) -> ReportOut:
    now = _utcnow()
    window_start, window_end = _window(period, now)

    signal_records = _signals_in_window(db, window_start, window_end)
    signal_counts = _signal_counts(signal_records)
    alert_items = _alerts_in_window(db, settings, window_start, window_end)
    latest_audit_events = _audit_events(db, settings, window_start, window_end)

    alerts_by_severity = dict(Counter(item.severity for item in alert_items))
    alerts_by_category = dict(Counter(item.category for item in alert_items))

    return ReportOut(
        period=period,
        generated_at=now,
        window_start=window_start,
        window_end=window_end,
        safety_posture=_safety_posture(settings),
        signal_counts=signal_counts,
        alert_counts_by_severity=alerts_by_severity,
        alert_counts_by_category=alerts_by_category,
        latest_audit_events=latest_audit_events,
        risk_config_snapshot=_risk_config(settings),
        markdown_summary=_markdown_summary(
            period=period,
            signal_counts=signal_counts,
            alerts_by_severity=alerts_by_severity,
            alerts_by_category=alerts_by_category,
            settings=settings,
        ),
        read_only=settings.read_only,
    )
