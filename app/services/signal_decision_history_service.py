from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.schemas.signal_decision import (
    DecisionDirection,
    DecisionType,
    RiskStatus,
    SignalDecisionHistoryResponse,
    SignalDecisionRecord,
)

_LIMIT_MAX = 200
_LIMIT_MIN = 1


def _ago(minutes: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=minutes)


def _record(
    record_id: str,
    symbol: str,
    direction: str,
    confidence: float,
    source: str,
    strategy: str,
    risk_status: str,
    decision: str,
    blocked_reason: str | None,
    minutes_ago: int,
    metadata: dict[str, Any] | None = None,
) -> SignalDecisionRecord:
    return SignalDecisionRecord(
        id=record_id,
        timestamp=_ago(minutes_ago),
        symbol=symbol,
        direction=direction,  # type: ignore[arg-type]
        confidence=confidence,
        source=source,
        strategy=strategy,
        risk_status=risk_status,  # type: ignore[arg-type]
        decision=decision,  # type: ignore[arg-type]
        blocked_reason=blocked_reason,
        dry_run=True,
        auto_trade=False,
        read_only=True,
        stop_loss_required=True,
        take_profit_required=True,
        max_risk_per_trade=0.01,
        metadata=metadata or {},
    )


_SEED_DECISIONS: list[SignalDecisionRecord] = [
    _record(
        "sdh-001",
        "AAPL",
        "BUY",
        0.72,
        "signal_service",
        "mtf_confluence",
        "blocked",
        "blocked",
        "Broker disconnected; dry-run/read-only mode only. No order was placed.",
        5,
        {"dry_run_note": "Dry-run decision only. No order was placed."},
    ),
    _record(
        "sdh-002",
        "EURUSD",
        "SELL",
        0.65,
        "signal_service",
        "rsi_reversal",
        "blocked",
        "blocked",
        "Auto-trade is disabled. Signal recorded for review only.",
        12,
        {"dry_run_note": "Dry-run decision only. No order was placed."},
    ),
    _record(
        "sdh-003",
        "MSFT",
        "HOLD",
        0.58,
        "signal_service",
        "trend_following",
        "warn",
        "watch_only",
        "Confidence below execution threshold (min 70%). Watch only.",
        20,
        {"min_confidence": 0.70},
    ),
    _record(
        "sdh-004",
        "NVDA",
        "BUY",
        0.84,
        "signal_service",
        "mtf_confluence",
        "pass",
        "dry_run_allowed",
        None,
        35,
        {
            "dry_run_note": "Dry-run decision only. No order was placed.",
            "stop_loss_required": True,
            "take_profit_required": True,
        },
    ),
    _record(
        "sdh-005",
        "BTCUSD",
        "HOLD",
        0.51,
        "signal_service",
        "sentiment_overlay",
        "warn",
        "watch_only",
        "Confidence below threshold; sentiment inconclusive.",
        48,
        {"min_confidence": 0.70},
    ),
    _record(
        "sdh-006",
        "SPY",
        "BUY",
        0.79,
        "signal_service",
        "mtf_confluence",
        "pass",
        "dry_run_allowed",
        None,
        65,
        {
            "dry_run_note": "Dry-run decision only. No order was placed.",
            "stop_loss_required": True,
            "take_profit_required": True,
        },
    ),
    _record(
        "sdh-007",
        "GBPUSD",
        "SELL",
        0.60,
        "signal_service",
        "rsi_reversal",
        "blocked",
        "blocked",
        "Max open positions reached. Signal deferred.",
        80,
        {"dry_run_note": "Dry-run decision only. No order was placed."},
    ),
]


class SignalDecisionHistoryService:
    """Returns a read-only in-memory signal decision history.

    No DB, no network calls, no broker calls, no order execution, no secrets.
    Every record has dry_run=True, auto_trade=False, read_only=True.
    """

    def list_decisions(
        self,
        *,
        limit: int = 50,
        symbol: str | None = None,
        decision: DecisionType | None = None,
        risk_status: RiskStatus | None = None,
        direction: DecisionDirection | None = None,
    ) -> SignalDecisionHistoryResponse:
        bounded = max(_LIMIT_MIN, min(limit, _LIMIT_MAX))
        records = list(_SEED_DECISIONS)

        if symbol is not None:
            upper = symbol.upper()
            records = [r for r in records if r.symbol.upper() == upper]
        if decision is not None:
            records = [r for r in records if r.decision == decision]
        if risk_status is not None:
            records = [r for r in records if r.risk_status == risk_status]
        if direction is not None:
            records = [r for r in records if r.direction == direction]

        paged = records[:bounded]

        return SignalDecisionHistoryResponse(
            dry_run=True,
            auto_trade=False,
            read_only=True,
            total=len(paged),
            decisions=paged,
            generated_at=datetime.now(timezone.utc),
            degraded=any(r.risk_status in {"blocked", "warn"} for r in paged),
            fallback=True,
        )
