from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .config import Settings
from .schemas import AuditEvent, AuditEventFeedResponse, AuditSeverity

_LIMIT_MAX = 200
_LIMIT_MIN = 1


def _event(
    event_id: str,
    event_type: str,
    severity: AuditSeverity,
    source: str,
    message: str,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    return AuditEvent(
        id=event_id,
        timestamp=datetime.now(timezone.utc),
        type=event_type,
        severity=severity,
        source=source,
        message=message,
        read_only=True,
        metadata=metadata or {},
    )


class AuditEventService:
    """Generates deterministic in-memory audit events for mellytrade-api.

    No database writes, no external network calls, no broker connections,
    no order placement, no secrets. Every event has read_only=True.
    """

    def _safety_events(self, settings: Settings) -> list[AuditEvent]:
        return [
            _event(
                "evt-safety-001",
                "dry_run_active",
                "safety",
                "risk",
                "dry_run=true. All execution paths are blocked. No real orders will be placed.",
                {"dry_run": True},
            ),
            _event(
                "evt-safety-002",
                "autotrade_disabled",
                "safety",
                "risk",
                "autotrade.enabled=false. Automated trade execution is disabled.",
                {"auto_trade": False},
            ),
            _event(
                "evt-safety-003",
                "live_orders_blocked",
                "safety",
                "broker",
                "supports_live_orders=false. Live order placement is blocked at adapter level.",
                {"supports_live_orders": False},
            ),
            _event(
                "evt-safety-004",
                "max_risk_cap_verified",
                "safety",
                "risk",
                f"max_risk_percent={settings.max_risk_percent}%. Risk cap is enforced.",
                {"max_risk_percent": settings.max_risk_percent},
            ),
        ]

    def _startup_events(self) -> list[AuditEvent]:
        return [
            _event(
                "evt-startup-001",
                "backend_started",
                "success",
                "fastapi",
                "MellyTrade v3 API started successfully.",
            ),
            _event(
                "evt-startup-002",
                "read_only_mode_confirmed",
                "success",
                "config",
                "System is operating in read-only observability mode. "
                "No order controls are exposed.",
            ),
        ]

    def _broker_events(self) -> list[AuditEvent]:
        return [
            _event(
                "evt-broker-001",
                "broker_disconnected",
                "warning",
                "ibkr_paper",
                "IBKR Paper adapter is not connected. "
                "This is the expected safe state without TWS Paper running. "
                "No orders can be placed.",
                {"adapter": "ibkr_paper", "port": 7497, "supports_live_orders": False},
            ),
            _event(
                "evt-broker-002",
                "ibkr_disconnected",
                "warning",
                "ibkr_paper",
                "ib_insync is not connected or not installed. "
                "No account data available. Safe: no orders can be placed.",
                {"safe": True},
            ),
        ]

    def _mt5_events(self) -> list[AuditEvent]:
        return [
            _event(
                "evt-mt5-001",
                "mt5_disconnected",
                "warning",
                "mt5",
                "MT5 is not connected. Using fallback/demo data. "
                "MT5 execution path is untouched.",
                {"fallback": True},
            ),
        ]

    def _smoke_events(self) -> list[AuditEvent]:
        return [
            _event(
                "evt-smoke-001",
                "smoke_pending",
                "warning",
                "smoke",
                "Smoke test status is pending. "
                "Run scripts/smoke_ibkr_paper.ps1 to validate.",
            ),
            _event(
                "evt-data-001",
                "fallback_data_active",
                "warning",
                "data",
                "System is operating on fixture/demo data. "
                "No live market data is connected.",
                {"fallback": True},
            ),
        ]

    def list_events(
        self,
        settings: Settings,
        *,
        limit: int = 50,
    ) -> AuditEventFeedResponse:
        bounded = max(_LIMIT_MIN, min(limit, _LIMIT_MAX))
        events: list[AuditEvent] = []
        events.extend(self._safety_events(settings))
        events.extend(self._startup_events())
        events.extend(self._broker_events())
        events.extend(self._mt5_events())
        events.extend(self._smoke_events())

        degraded = any(e.severity in {"warning", "error"} for e in events)
        fallback = any(e.type == "fallback_data_active" for e in events)

        return AuditEventFeedResponse(
            dry_run=True,
            auto_trade=False,
            read_only=True,
            degraded=degraded,
            fallback=fallback,
            generated_at=datetime.now(timezone.utc),
            events=events[:bounded],
        )
