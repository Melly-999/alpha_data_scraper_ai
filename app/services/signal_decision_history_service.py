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


# DATA-001: realistic, varied seed for the dry-run decision history.
#
# Constraints (enforced by tests/app/test_signal_decision_history.py):
#   - AAPL must exist with decision=blocked.
#   - AAPL must NOT exist with decision=dry_run_allowed.
#   - At least one record has decision=blocked.
#   - At least one record has decision=dry_run_allowed.
#   - At least one record has risk_status=pass.
#   - At least one record has direction=BUY.
#
# Every record is dry-run, auto_trade=False, read_only=True, order_placed=False,
# max_risk_per_trade<=0.01. No execution. No broker calls. Display-only seed.
_SEED_DECISIONS: list[SignalDecisionRecord] = [
    # --- Last ~5 minutes: most recent activity ---------------------------
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
        4,
        {
            "dry_run_note": "Dry-run decision only. No order was placed.",
            "broker_status": "disconnected",
            "supports_live_orders": False,
        },
    ),
    _record(
        "sdh-002",
        "NVDA",
        "BUY",
        0.84,
        "signal_service",
        "mtf_confluence",
        "pass",
        "dry_run_allowed",
        None,
        7,
        {
            "dry_run_note": "Dry-run decision only. No order was placed.",
            "stop_loss_required": True,
            "take_profit_required": True,
            "rr": 2.4,
            "mtf_alignment": "M5+H1 confluence; H4 neutral.",
        },
    ),
    _record(
        "sdh-003",
        "EURUSD",
        "SELL",
        0.65,
        "signal_service",
        "rsi_reversal",
        "blocked",
        "blocked",
        "Auto-trade is disabled. Signal recorded for review only.",
        11,
        {
            "dry_run_note": "Dry-run decision only. No order was placed.",
            "rsi_h1": 28.4,
            "session": "london",
        },
    ),
    _record(
        "sdh-004",
        "MSFT",
        "HOLD",
        0.58,
        "signal_service",
        "trend_following",
        "warn",
        "watch_only",
        "Confidence 58% below 70% review threshold. Watch only — no order placed.",
        18,
        {
            "min_confidence": 0.70,
            "atr_pct": 0.92,
            "regime": "ranging",
        },
    ),
    _record(
        "sdh-005",
        "XAUUSD",
        "BUY",
        0.81,
        "signal_service",
        "atr_breakout",
        "pass",
        "dry_run_allowed",
        None,
        24,
        {
            "dry_run_note": "Dry-run decision only. No order was placed.",
            "stop_loss_required": True,
            "take_profit_required": True,
            "atr_pct": 1.38,
            "session": "ny_overlap",
        },
    ),
    # --- 30–90 minutes back: established context ------------------------
    _record(
        "sdh-006",
        "BTCUSD",
        "HOLD",
        0.51,
        "signal_service",
        "sentiment_overlay",
        "warn",
        "watch_only",
        "Confidence below 70% threshold; sentiment net inconclusive.",
        38,
        {
            "min_confidence": 0.70,
            "sentiment_score": 0.04,
            "news_24h_count": 12,
        },
    ),
    _record(
        "sdh-007",
        "SPY",
        "BUY",
        0.79,
        "signal_service",
        "mtf_confluence",
        "pass",
        "dry_run_allowed",
        None,
        52,
        {
            "dry_run_note": "Dry-run decision only. No order was placed.",
            "stop_loss_required": True,
            "take_profit_required": True,
            "rr": 2.1,
            "mtf_alignment": "M5+H1+H4 aligned.",
        },
    ),
    _record(
        "sdh-008",
        "GBPUSD",
        "SELL",
        0.60,
        "signal_service",
        "rsi_reversal",
        "blocked",
        "blocked",
        "Max open positions reached (pre-trade gate). Signal deferred to next window.",
        71,
        {
            "dry_run_note": "Dry-run decision only. No order was placed.",
            "open_positions": 3,
            "open_positions_limit": 3,
        },
    ),
    _record(
        "sdh-009",
        "TSLA",
        "SELL",
        0.74,
        "signal_service",
        "vwap_pullback",
        "warn",
        "watch_only",
        "Cooldown active for TSLA (rejection within last 15 min). Watch only.",
        88,
        {
            "min_confidence": 0.70,
            "cooldown_seconds_remaining": 420,
        },
    ),
    # --- 2–6 hours back: deeper context ---------------------------------
    _record(
        "sdh-010",
        "USDJPY",
        "BUY",
        0.77,
        "signal_service",
        "regime_filter",
        "pass",
        "dry_run_allowed",
        None,
        135,
        {
            "dry_run_note": "Dry-run decision only. No order was placed.",
            "stop_loss_required": True,
            "take_profit_required": True,
            "regime": "trending_up",
            "rr": 1.9,
        },
    ),
    _record(
        "sdh-011",
        "META",
        "HOLD",
        0.49,
        "signal_service",
        "sentiment_overlay",
        "warn",
        "watch_only",
        "Confidence 49% below threshold; conflicting sentiment overlay.",
        180,
        {
            "min_confidence": 0.70,
            "sentiment_score": -0.18,
        },
    ),
    _record(
        "sdh-012",
        "AMZN",
        "BUY",
        0.68,
        "signal_service",
        "mtf_confluence",
        "blocked",
        "blocked",
        "Risk budget exhausted for the session (daily loss cap protection).",
        220,
        {
            "dry_run_note": "Dry-run decision only. No order was placed.",
            "daily_loss_used_pct": 0.98,
        },
    ),
    _record(
        "sdh-013",
        "QQQ",
        "BUY",
        0.83,
        "signal_service",
        "mtf_confluence",
        "pass",
        "dry_run_allowed",
        None,
        260,
        {
            "dry_run_note": "Dry-run decision only. No order was placed.",
            "stop_loss_required": True,
            "take_profit_required": True,
            "rr": 2.6,
        },
    ),
    _record(
        "sdh-014",
        "GOOG",
        "HOLD",
        0.55,
        "signal_service",
        "trend_following",
        "warn",
        "watch_only",
        "Mixed timeframe signals (M5 bullish, H1 bearish). Watch only.",
        310,
        {
            "min_confidence": 0.70,
            "mtf_alignment": "M5+/H1-/H4 neutral",
        },
    ),
    _record(
        "sdh-015",
        "ETHUSD",
        "SELL",
        0.71,
        "signal_service",
        "atr_breakout",
        "blocked",
        "blocked",
        "Emergency-pause flag is set (read-only halt). No execution allowed.",
        420,
        {
            "dry_run_note": "Dry-run decision only. No order was placed.",
            "emergency_pause": True,
        },
    ),
]


class SignalDecisionHistoryService:
    """Returns a read-only signal decision history.

    SUPA-011: Attempts to read real persisted rows from Supabase first.
    Falls back to the in-memory _SEED_DECISIONS fixture when Supabase is
    unavailable or returns no rows.

    No broker calls, no order execution, no secrets.
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
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> SignalDecisionHistoryResponse:
        """Return read-only signal decision history.

        SUPA-014: ``from_date`` / ``to_date`` are inclusive bounds applied to
        each record's ``timestamp``. Both are optional and tolerated even when
        ``from_date > to_date`` (returns an empty list rather than raising).
        Applied server-side via the reader on the real path, and post-filtered
        on the seed fallback path. No write semantics, no execution.
        """
        bounded = max(_LIMIT_MIN, min(limit, _LIMIT_MAX))

        # SUPA-011: attempt real Supabase read first; degrade to seed on failure.
        # Local imports keep the lazy-loading pattern consistent and avoid any
        # circular import risk.
        is_fallback = True
        records: list[SignalDecisionRecord] = []

        try:
            from app.services.signal_decision_reader import read_signal_decisions
            from app.services.supabase_client import get_safe_supabase_client

            real_records = read_signal_decisions(
                symbol=symbol,
                limit=_LIMIT_MAX,
                from_date=from_date,
                to_date=to_date,
                client=get_safe_supabase_client(),
            )
            if real_records:
                records = real_records
                is_fallback = False
        except Exception:  # noqa: BLE001
            pass

        if is_fallback:
            records = list(_SEED_DECISIONS)
            # Apply symbol filter to seed data (reader handles it for real data).
            if symbol is not None:
                upper = symbol.upper()
                records = [r for r in records if r.symbol.upper() == upper]
            # SUPA-014: apply date filters to seed data (reader applies them
            # server-side for real data; seed path applies them here).
            if from_date is not None:
                records = [r for r in records if r.timestamp >= from_date]
            if to_date is not None:
                records = [r for r in records if r.timestamp <= to_date]

        # Apply remaining filters (decision, risk_status, direction) to both
        # real and seed data paths.
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
            fallback=is_fallback,
        )
