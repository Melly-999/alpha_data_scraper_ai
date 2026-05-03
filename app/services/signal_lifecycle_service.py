from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from app.schemas.signal_decision import SignalDecisionRecord
from app.schemas.signal_lifecycle import (
    LifecycleDecision,
    LifecycleRiskStatus,
    SignalLifecycleRecord,
    SignalLifecycleResponse,
    SignalLifecycleStep,
)
from app.services.signal_decision_history_service import SignalDecisionHistoryService

_LIMIT_MAX = 200
_LIMIT_MIN = 1
_MAX_RISK_PER_TRADE = 0.01


def _audit_event_id(record: SignalDecisionRecord) -> str:
    if record.decision == "dry_run_allowed":
        return "evt-safety-001"
    if record.decision == "blocked":
        return "evt-safety-002"
    if record.decision == "watch_only":
        return "evt-safety-004"
    return "evt-startup-002"


def _confidence_detail(record: SignalDecisionRecord) -> str:
    confidence_pct = round(record.confidence * 100)
    if record.confidence >= 0.70:
        return f"Confidence {confidence_pct}% meets the 70% review threshold."
    return f"Confidence {confidence_pct}% is below the 70% review threshold."


def _reason(record: SignalDecisionRecord) -> str:
    if record.blocked_reason:
        return record.blocked_reason
    if record.decision == "dry_run_allowed":
        return "Dry-run allowed for review only. No order was placed."
    if record.decision == "watch_only":
        return "Signal is watch-only. No order was placed."
    return "No action was taken."


def _steps(record: SignalDecisionRecord) -> list[SignalLifecycleStep]:
    audit_id = _audit_event_id(record)
    risk_step_status: Literal["passed", "blocked"] = (
        "passed" if record.risk_status == "pass" else "blocked"
    )
    dry_run_step_status: Literal["allowed", "blocked"] = (
        "allowed" if record.decision == "dry_run_allowed" else "blocked"
    )
    return [
        SignalLifecycleStep(
            key="signal_received",
            label="Signal received",
            status="received",
            detail=f"{record.symbol} {record.direction} from {record.source}.",
        ),
        SignalLifecycleStep(
            key="confidence_checked",
            label="Confidence checked",
            status="passed" if record.confidence >= 0.70 else "blocked",
            detail=_confidence_detail(record),
        ),
        SignalLifecycleStep(
            key="risk_checked",
            label="Risk checked",
            status=risk_step_status,
            detail=(
                f"Risk status is {record.risk_status}; max risk per trade remains "
                f"{_MAX_RISK_PER_TRADE:.2%}."
            ),
        ),
        SignalLifecycleStep(
            key="broker_safety_checked",
            label="Broker safety checked",
            status="blocked",
            detail="supports_live_orders=false; broker order placement is unavailable.",
        ),
        SignalLifecycleStep(
            key="dry_run_decision",
            label="Dry-run decision",
            status=dry_run_step_status,
            detail=(
                "Dry-run allowed means review-only simulation; no order was placed."
                if record.decision == "dry_run_allowed"
                else "Dry-run did not advance beyond read-only review."
            ),
        ),
        SignalLifecycleStep(
            key="blocked_or_allowed_reason",
            label="Blocked/allowed reason",
            status="recorded",
            detail=_reason(record),
        ),
        SignalLifecycleStep(
            key="audit_event_reference",
            label="Audit event reference",
            status="recorded",
            detail=f"Correlated with audit event {audit_id}.",
            audit_event_id=audit_id,
        ),
    ]


class SignalLifecycleService:
    """Builds a read-only signal lifecycle view from decision history.

    No DB writes, network calls, broker calls, MT5 calls, or order execution.
    The lifecycle explains safety decisions only.
    """

    def __init__(
        self,
        decision_service: SignalDecisionHistoryService | None = None,
    ) -> None:
        self._decision_service = decision_service or SignalDecisionHistoryService()

    def list_lifecycle(
        self,
        *,
        limit: int = 50,
        symbol: str | None = None,
        decision: LifecycleDecision | None = None,
        risk_status: LifecycleRiskStatus | None = None,
    ) -> SignalLifecycleResponse:
        decisions = self._decision_service.list_decisions(
            limit=_LIMIT_MAX,
            symbol=symbol,
        ).decisions
        if decision is not None:
            decisions = [record for record in decisions if record.decision == decision]
        if risk_status is not None:
            decisions = [
                record for record in decisions if record.risk_status == risk_status
            ]

        bounded = max(_LIMIT_MIN, min(limit, _LIMIT_MAX))
        decisions = decisions[:bounded]
        records = [
            SignalLifecycleRecord(
                id=f"slc-{record.id}",
                signal_id=f"sig-{record.id}",
                decision_id=record.id,
                audit_event_id=_audit_event_id(record),
                timestamp=record.timestamp,
                symbol=record.symbol,
                direction=record.direction,
                confidence=record.confidence,
                decision=record.decision,
                risk_status=record.risk_status,
                blocked_reason=record.blocked_reason,
                dry_run=True,
                auto_trade=False,
                read_only=True,
                supports_live_orders=False,
                dry_run_allowed=record.decision == "dry_run_allowed",
                order_placed=False,
                max_risk_per_trade=_MAX_RISK_PER_TRADE,
                steps=_steps(record),
            )
            for record in decisions
        ]

        return SignalLifecycleResponse(
            dry_run=True,
            auto_trade=False,
            read_only=True,
            supports_live_orders=False,
            total=len(records),
            lifecycle=records,
            generated_at=datetime.now(timezone.utc),
            degraded=any(record.decision != "dry_run_allowed" for record in records),
            fallback=True,
        )
