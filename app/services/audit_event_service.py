from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.schemas.risk import RiskConfig
from app.schemas.terminal import AuditEvent, AuditEventFeedResponse, AuditSeverity

_LIMIT_MAX = 200
_LIMIT_MIN = 1

# Vocabulary of every event type this service can emit. Kept as an explicit
# tuple so tests, frontend filters, and downstream consumers can enumerate
# the safe set without grepping the source. Adding a new type here is a
# deliberate, reviewable change.
KNOWN_EVENT_TYPES: tuple[str, ...] = (
    "backend_started",
    "read_only_mode_confirmed",
    "terminal_loaded",
    "risk_policy_loaded",
    "dry_run_active",
    "autotrade_disabled",
    "live_orders_blocked",
    "max_risk_cap_verified",
    "broker_disconnected",
    "ibkr_disconnected",
    "mt5_disconnected",
    "smoke_pending",
    "smoke_passed",
    "fallback_data_active",
)


def _event(
    event_id: str,
    event_type: str,
    severity: AuditSeverity,
    source: str,
    message: str,
    metadata: dict[str, Any] | None = None,
    safety_note: str | None = None,
) -> AuditEvent:
    return AuditEvent(
        id=event_id,
        timestamp=datetime.now(timezone.utc),
        type=event_type,
        severity=severity,
        source=source,
        message=message,
        read_only=True,
        safety_note=safety_note,
        metadata=metadata or {},
    )


class AuditEventService:
    """Generates deterministic in-memory audit events.

    No DB, no external network calls, no broker connection attempts,
    no secrets. Every returned event has read_only=True.
    """

    def build_safety_events(self, risk_config: RiskConfig) -> list[AuditEvent]:
        return [
            _event(
                "evt-safety-001",
                "dry_run_active",
                "safety",
                "risk",
                "dry_run=true. All execution paths are blocked. No real orders will be placed.",
                metadata={"dry_run": True},
                safety_note="No live orders can leave the system while dry_run is true.",
            ),
            _event(
                "evt-safety-002",
                "autotrade_disabled",
                "safety",
                "risk",
                "autotrade.enabled=false. Automated trade execution is disabled.",
                metadata={"auto_trade": False},
                safety_note="The bot will not auto-execute signals while autotrade is disabled.",
            ),
            _event(
                "evt-safety-003",
                "live_orders_blocked",
                "safety",
                "broker",
                "supports_live_orders=false. Live order placement is blocked at adapter level.",
                metadata={"supports_live_orders": False},
                safety_note="Broker adapter rejects live order placement at the API boundary.",
            ),
            _event(
                "evt-safety-004",
                "max_risk_cap_verified",
                "safety",
                "risk",
                f"max_risk_per_trade={risk_config.max_risk_per_trade}%. Risk cap is enforced.",
                metadata={"max_risk_per_trade": risk_config.max_risk_per_trade},
                safety_note=(
                    "Per-trade risk is capped at "
                    f"{risk_config.max_risk_per_trade}% of equity."
                ),
            ),
        ]

    def build_startup_events(self) -> list[AuditEvent]:
        return [
            _event(
                "evt-startup-001",
                "backend_started",
                "success",
                "fastapi",
                "MellyTrade Phase 1 backend started successfully.",
                safety_note="Backend boot completed without execution paths enabled.",
            ),
            _event(
                "evt-startup-002",
                "read_only_mode_confirmed",
                "success",
                "config",
                "System is operating in read-only observability mode. No order controls are exposed.",
                safety_note="UI exposes only GET endpoints; mutating routes are not registered.",
            ),
        ]

    def build_terminal_events(self) -> list[AuditEvent]:
        """Read-only Terminal V1 lifecycle marker.

        Emitted whenever the audit feed is requested so operators can confirm
        the terminal observability surface is online. Static — does not poll
        the broker, MT5, or any external service.
        """
        return [
            _event(
                "evt-terminal-001",
                "terminal_loaded",
                "success",
                "terminal",
                "MellyTrade Terminal V1 read-only feed is online.",
                metadata={"feed": "read-only", "mutating_routes": False},
                safety_note=(
                    "Terminal exposes GET-only endpoints; no order-execution "
                    "controls are wired up."
                ),
            ),
        ]

    def build_risk_policy_events(self, risk_config: RiskConfig) -> list[AuditEvent]:
        """Snapshot of the loaded risk policy.

        Pulls the live risk_config values into a single audit row so a viewer
        can verify the policy without separately calling /risk/config.
        """
        return [
            _event(
                "evt-risk-policy-001",
                "risk_policy_loaded",
                "success",
                "risk",
                (
                    "Risk policy loaded: "
                    f"max_risk_per_trade={risk_config.max_risk_per_trade}%, "
                    f"min_confidence={risk_config.min_confidence}, "
                    f"cooldown_seconds={risk_config.cooldown_seconds}."
                ),
                metadata={
                    "max_risk_per_trade": risk_config.max_risk_per_trade,
                    "min_confidence": risk_config.min_confidence,
                    "cooldown_seconds": risk_config.cooldown_seconds,
                },
                safety_note=(
                    "Risk gates are loaded and reported here for verification; "
                    "they cannot be raised from the Terminal."
                ),
            ),
        ]

    def build_broker_events(self) -> list[AuditEvent]:
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

    def build_mt5_events(self) -> list[AuditEvent]:
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

    def build_smoke_events(self, *, passed: bool = False) -> list[AuditEvent]:
        """Smoke-test status row.

        Defaults to ``smoke_pending`` (warning) when no smoke run has been
        recorded for this session. Callers / tests that have evidence of a
        successful smoke run can pass ``passed=True`` to emit
        ``smoke_passed`` (success). The route handler keeps the default so
        production output never claims a passing smoke run that hasn't
        actually happened.
        """
        if passed:
            smoke_event = _event(
                "evt-smoke-001",
                "smoke_passed",
                "success",
                "smoke",
                "Smoke test passed for this session.",
                safety_note=(
                    "Read-only smoke checks completed; no mutations were "
                    "executed and no live orders were placed."
                ),
            )
        else:
            smoke_event = _event(
                "evt-smoke-001",
                "smoke_pending",
                "warning",
                "smoke",
                "Smoke test status is pending. "
                "Run scripts/smoke_ibkr_paper.ps1 to validate.",
                safety_note=(
                    "Pending status is itself safe — no live orders are "
                    "issued by the smoke check."
                ),
            )
        return [
            smoke_event,
            _event(
                "evt-data-001",
                "fallback_data_active",
                "warning",
                "data",
                "System is operating on fixture/demo data. "
                "No live market data is connected.",
                metadata={"fallback": True},
                safety_note=(
                    "Demo data is clearly labeled; no real broker quotes "
                    "are being used for decision-making."
                ),
            ),
        ]

    def list_events(
        self,
        risk_config: RiskConfig,
        *,
        limit: int = 50,
        smoke_passed: bool = False,
    ) -> AuditEventFeedResponse:
        bounded_limit = max(_LIMIT_MIN, min(limit, _LIMIT_MAX))
        events: list[AuditEvent] = []
        events.extend(self.build_startup_events())
        events.extend(self.build_terminal_events())
        events.extend(self.build_risk_policy_events(risk_config))
        events.extend(self.build_safety_events(risk_config))
        events.extend(self.build_broker_events())
        events.extend(self.build_mt5_events())
        events.extend(self.build_smoke_events(passed=smoke_passed))

        degraded = any(e.severity in {"warning", "error"} for e in events)
        fallback = any(e.type == "fallback_data_active" for e in events)

        return AuditEventFeedResponse(
            dry_run=True,
            auto_trade=False,
            read_only=True,
            events=events[:bounded_limit],
            degraded=degraded,
            fallback=fallback,
            generated_at=datetime.now(timezone.utc),
        )
