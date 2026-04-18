from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import Settings
from .models import SignalRecord
from .schemas import SignalIn


@dataclass(frozen=True)
class RiskDecision:
    accepted: bool
    reason: str = ""
    detail: str = ""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def evaluate(signal: SignalIn, settings: Settings, db: Session) -> RiskDecision:
    """Apply hard risk gates before a signal is persisted or published.

    Rules (strict, never loosened at runtime):
    - confidence >= MIN_CONFIDENCE
    - risk_percent <= MAX_RISK_PERCENT
    - BUY/SELL must carry SL and TP (validated in schema)
    - per-symbol cooldown: COOLDOWN_SECONDS since last accepted signal
    """
    if signal.action not in ("BUY", "SELL", "HOLD"):
        return RiskDecision(False, "invalid_action", signal.action)

    if signal.action == "HOLD":
        # HOLD is informational; still enforce confidence for consistency.
        if signal.confidence < settings.min_confidence:
            return RiskDecision(
                False,
                "confidence_below_min",
                f"{signal.confidence} < {settings.min_confidence}",
            )
        return RiskDecision(True)

    if signal.confidence < settings.min_confidence:
        return RiskDecision(
            False,
            "confidence_below_min",
            f"{signal.confidence} < {settings.min_confidence}",
        )

    if signal.risk_percent > settings.max_risk_percent:
        return RiskDecision(
            False,
            "risk_above_max",
            f"{signal.risk_percent} > {settings.max_risk_percent}",
        )

    # SL/TP presence is enforced by SignalIn schema (gt=0). Extra safety:
    if signal.stop_loss <= 0 or signal.take_profit <= 0:
        return RiskDecision(False, "missing_sl_tp")

    last: Optional[SignalRecord] = db.execute(
        select(SignalRecord)
        .where(SignalRecord.symbol == signal.symbol)
        .where(SignalRecord.status == "accepted")
        .order_by(SignalRecord.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    if last is not None:
        last_ts = last.created_at
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=timezone.utc)
        delta = _utcnow() - last_ts
        if delta < timedelta(seconds=settings.cooldown_seconds):
            remaining = settings.cooldown_seconds - int(delta.total_seconds())
            return RiskDecision(
                False,
                "cooldown_active",
                f"{remaining}s remaining for {signal.symbol}",
            )

    return RiskDecision(True)
