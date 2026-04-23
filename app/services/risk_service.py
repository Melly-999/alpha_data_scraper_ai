from __future__ import annotations

import json
from datetime import datetime, timezone
from itertools import count
from pathlib import Path
from typing import Any

from app.schemas.common import BlockedReason, LogCategory, Severity
from app.schemas.risk import (
    EmergencyStopResponse,
    RiskConfig,
    RiskConfigUpdate,
    RiskStatus,
    RiskViolation,
)
from app.schemas.signal import RiskGateResult
from app.services.fixture_data import prototype_risk_violations
from app.services.log_service import LogService


class RiskService:
    def __init__(self, config_path: Path, log_service: LogService) -> None:
        self._config_path = config_path
        self._log_service = log_service
        self._violation_counter = count(1)
        self._blocked_count = 0
        self._executed_count = 5
        self._last_signal_by_symbol: dict[str, tuple[str, datetime]] = {}
        self._violations = [
            RiskViolation.model_validate(item) for item in prototype_risk_violations()
        ]
        self._blocked_count = len(self._violations)
        self._config = self._load_initial_config()

    def _load_initial_config(self) -> RiskConfig:
        raw: dict[str, Any] = {}
        if self._config_path.exists():
            raw = json.loads(self._config_path.read_text(encoding="utf-8"))
        autotrade_raw = raw.get("autotrade", {})
        autotrade = autotrade_raw if isinstance(autotrade_raw, dict) else {}
        max_risk = 1.0
        min_conf = int(float(autotrade.get("min_confidence", 70)))
        return self._sanitize_config(
            RiskConfig(
                max_risk_per_trade=max_risk,
                max_daily_loss=2.0,
                max_drawdown=5.0,
                min_confidence=min_conf,
                min_rr=1.5,
                max_open_positions=5,
                max_lot_size=0.5,
                cooldown_seconds=int(autotrade.get("cooldown_seconds", 120)),
                allow_same_signal=bool(autotrade.get("allow_same_signal", False)),
                dry_run=bool(autotrade.get("dry_run", True)),
                auto_trade=bool(autotrade.get("enabled", False)),
                emergency_pause=False,
            )
        )

    def _sanitize_config(self, config: RiskConfig) -> RiskConfig:
        return RiskConfig(
            max_risk_per_trade=min(max(config.max_risk_per_trade, 0.1), 1.0),
            max_daily_loss=max(config.max_daily_loss, 0.1),
            max_drawdown=max(config.max_drawdown, 0.5),
            min_confidence=max(config.min_confidence, 70),
            min_rr=max(config.min_rr, 1.0),
            max_open_positions=max(config.max_open_positions, 1),
            max_lot_size=max(min(config.max_lot_size, 0.5), 0.01),
            cooldown_seconds=max(config.cooldown_seconds, 0),
            allow_same_signal=False,
            dry_run=True,
            auto_trade=False,
            emergency_pause=config.emergency_pause,
        )

    def get_config(self) -> RiskConfig:
        return self._config

    def update_config(self, update: RiskConfigUpdate) -> RiskConfig:
        merged = self._config.model_copy(
            update=update.model_dump(exclude_none=True),
        )
        self._config = self._sanitize_config(merged)
        self._log_service.add(
            category=LogCategory.RISK,
            severity=Severity.INFO,
            message="Risk configuration updated in-memory; conservative guardrails enforced.",
        )
        return self._config

    def get_status(
        self, *, open_positions: int, drawdown: float, daily_loss_used: float
    ) -> RiskStatus:
        return RiskStatus(
            daily_loss_used=round(daily_loss_used, 2),
            daily_loss_limit=self._config.max_daily_loss,
            drawdown_current=round(abs(drawdown), 2),
            drawdown_limit=self._config.max_drawdown,
            open_positions=open_positions,
            open_positions_limit=self._config.max_open_positions,
            trades_blocked=self._blocked_count,
            trades_executed=self._executed_count,
            risk_exposure=round(
                min(open_positions * self._config.max_risk_per_trade / 5, 1.0), 2
            ),
            emergency_pause=self._config.emergency_pause,
        )

    def list_violations(self) -> list[RiskViolation]:
        return list(reversed(self._violations))

    def _record_violation(
        self,
        *,
        violation_type: BlockedReason,
        reason: str,
        severity: Severity,
        signal_ref: str | None,
    ) -> RiskViolation:
        violation = RiskViolation(
            id=f"rv-{next(self._violation_counter):03d}",
            type=violation_type,
            signal_ref=signal_ref,
            reason=reason,
            severity=severity,
            timestamp=datetime.now(timezone.utc),
        )
        self._violations.append(violation)
        self._blocked_count += 1
        self._log_service.add(
            category=LogCategory.RISK,
            severity=severity,
            message=reason,
        )
        return violation

    def trigger_emergency_stop(self) -> EmergencyStopResponse:
        if not self._config.emergency_pause:
            self._config = self._config.model_copy(update={"emergency_pause": True})
        violation = self._record_violation(
            violation_type=BlockedReason.EMERGENCY_STOP,
            reason="Emergency stop engaged. All execution-like paths are blocked.",
            severity=Severity.ERROR,
            signal_ref=None,
        )
        return EmergencyStopResponse(
            stopped=True,
            timestamp=violation.timestamp,
            config=self._config,
            violation=violation,
        )

    def evaluate_signal(
        self,
        *,
        signal_id: str,
        symbol: str,
        direction: str,
        confidence: int,
        sl: float | None,
        tp: float | None,
        rr: float | None,
        timestamp: datetime,
        open_positions: int,
        register: bool = False,
    ) -> tuple[bool, BlockedReason | None, int | None, list[RiskGateResult]]:
        gates: list[RiskGateResult] = []

        emergency_block = self._config.emergency_pause
        gates.append(
            RiskGateResult(
                gate="EMERGENCY_STOP",
                passed=not emergency_block,
                value=self._config.emergency_pause,
                detail="Emergency pause must be disabled for any execution-like path.",
            )
        )
        if emergency_block:
            if register:
                self._record_violation(
                    violation_type=BlockedReason.EMERGENCY_STOP,
                    reason=f"{signal_id} blocked because emergency stop is active.",
                    severity=Severity.ERROR,
                    signal_ref=f"{symbol} {direction}",
                )
            return False, BlockedReason.EMERGENCY_STOP, None, gates

        has_protection = sl is not None and tp is not None
        gates.append(
            RiskGateResult(
                gate="PROTECTION",
                passed=has_protection,
                value="present" if has_protection else "missing",
                detail="Executable signals require both stop loss and take profit.",
            )
        )
        if not has_protection and direction in {"BUY", "SELL"}:
            if register:
                self._record_violation(
                    violation_type=BlockedReason.MISSING_PROTECTION,
                    reason=f"{signal_id} blocked because SL/TP protection is missing.",
                    severity=Severity.WARN,
                    signal_ref=f"{symbol} {direction}",
                )
            return False, BlockedReason.MISSING_PROTECTION, None, gates

        confidence_passed = confidence >= self._config.min_confidence
        gates.append(
            RiskGateResult(
                gate="CONFIDENCE",
                passed=confidence_passed,
                value=confidence,
                threshold=self._config.min_confidence,
            )
        )
        if not confidence_passed:
            if register:
                self._record_violation(
                    violation_type=BlockedReason.LOW_CONFIDENCE,
                    reason=f"{signal_id} blocked because confidence {confidence}% is below {self._config.min_confidence}%.",
                    severity=Severity.WARN,
                    signal_ref=f"{symbol} {direction}",
                )
            return False, BlockedReason.LOW_CONFIDENCE, None, gates

        if direction not in {"BUY", "SELL"}:
            if register:
                self._record_violation(
                    violation_type=BlockedReason.NO_TRADE_SIGNAL,
                    reason=f"{signal_id} is not executable because direction is {direction}.",
                    severity=Severity.INFO,
                    signal_ref=f"{symbol} {direction}",
                )
            return False, BlockedReason.NO_TRADE_SIGNAL, None, gates

        rr_value = rr or 0.0
        rr_passed = rr_value >= self._config.min_rr
        gates.append(
            RiskGateResult(
                gate="RISK_REWARD",
                passed=rr_passed,
                value=round(rr_value, 2),
                threshold=self._config.min_rr,
            )
        )
        if not rr_passed:
            if register:
                self._record_violation(
                    violation_type=BlockedReason.RISK_LIMIT,
                    reason=f"{signal_id} blocked because RR {rr_value:.2f} is below {self._config.min_rr:.2f}.",
                    severity=Severity.WARN,
                    signal_ref=f"{symbol} {direction}",
                )
            return False, BlockedReason.RISK_LIMIT, None, gates

        positions_passed = open_positions < self._config.max_open_positions
        gates.append(
            RiskGateResult(
                gate="MAX_POSITIONS",
                passed=positions_passed,
                value=open_positions,
                threshold=self._config.max_open_positions,
            )
        )
        if not positions_passed:
            if register:
                self._record_violation(
                    violation_type=BlockedReason.MAX_POSITIONS,
                    reason=f"{signal_id} blocked because max open positions was reached.",
                    severity=Severity.INFO,
                    signal_ref=f"{symbol} {direction}",
                )
            return False, BlockedReason.MAX_POSITIONS, None, gates

        cooldown_remaining: int | None = None
        if symbol in self._last_signal_by_symbol:
            last_direction, last_time = self._last_signal_by_symbol[symbol]
            elapsed = int((timestamp - last_time).total_seconds())
            if last_direction == direction and elapsed < self._config.cooldown_seconds:
                cooldown_remaining = self._config.cooldown_seconds - elapsed
                gates.append(
                    RiskGateResult(
                        gate="COOLDOWN",
                        passed=False,
                        remaining_seconds=cooldown_remaining,
                        detail="Same symbol/direction pair is still cooling down.",
                    )
                )
                if register:
                    self._record_violation(
                        violation_type=BlockedReason.COOLDOWN,
                        reason=f"{signal_id} blocked because cooldown has {cooldown_remaining}s remaining.",
                        severity=Severity.WARN,
                        signal_ref=f"{symbol} {direction}",
                    )
                return False, BlockedReason.COOLDOWN, cooldown_remaining, gates

        gates.append(
            RiskGateResult(
                gate="COOLDOWN",
                passed=True,
                remaining_seconds=0,
            )
        )

        if register:
            self._last_signal_by_symbol[symbol] = (direction, timestamp)
            self._executed_count += 1
        return True, None, None, gates
