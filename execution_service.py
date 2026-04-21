"""Central execution evaluation service for the Alpha AI trading pipeline.

Receives signal context, runs all guards, produces an ExecutionDecision,
appends to signal history, and exports a snapshot — all with dry_run as
the immutable default.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from core import config
from drawdown_guard import DrawdownGuard
from execution.guards import confidence_guard, direction_guard, risk_state_guard
from risk.state_machine import RiskState, RiskStateMachine
from services.execution_snapshot_service import ExecutionSnapshotService
from services.signal_history_service import SignalHistoryService, SignalRecord

logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    """Input bundle passed to ExecutionService.evaluate()."""

    symbol: str
    direction: str
    confidence: float
    daily_pnl_pct: float = 0.0
    open_positions: int = 0
    account_balance: float = field(
        default_factory=lambda: float(config.ACCOUNT_BALANCE)
    )


@dataclass
class ExecutionDecision:
    """Result of a single execution evaluation cycle."""

    symbol: str
    direction: str
    confidence_used: float
    should_execute: bool
    block_reason: Optional[str]
    risk_state: str
    mode: str = "dry_run"
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ExecutionService:
    """Orchestrates guards, risk state, history, and snapshot export.

    mode is always 'dry_run' — live trading is never enabled here.
    """

    def __init__(
        self,
        signal_history: Optional[SignalHistoryService] = None,
        snapshot_exporter: Optional[ExecutionSnapshotService] = None,
    ) -> None:
        self._risk_machine = RiskStateMachine(
            daily_loss_caution_pct=float(config.MAX_DAILY_LOSS_PCT) * 0.5,
            daily_loss_halt_pct=float(config.MAX_DAILY_LOSS_PCT),
        )
        self._drawdown_guard = DrawdownGuard(
            max_drawdown_pct=float(config.MAX_DAILY_LOSS_PCT)
        )
        self._signal_history = signal_history or SignalHistoryService()
        self._snapshot_exporter = snapshot_exporter or ExecutionSnapshotService()
        self._latest_decision: Optional[ExecutionDecision] = None

    def evaluate(self, ctx: ExecutionContext) -> ExecutionDecision:
        """Run all guards and return an ExecutionDecision for *ctx*.

        Side effects (always safe):
        - appends to signal history buffer
        - exports snapshot to results/execution/decisions.json
        """
        risk_state: RiskState = self._risk_machine.evaluate(ctx.daily_pnl_pct)

        # Drawdown expressed as a positive percentage
        drawdown_pct = max(0.0, -ctx.daily_pnl_pct)
        dd_ok, dd_reason = self._drawdown_guard.check(drawdown_pct)

        block_reason: Optional[str] = None

        if not dd_ok:
            block_reason = dd_reason
        else:
            for guard_result in (
                direction_guard(ctx.direction),
                confidence_guard(
                    ctx.confidence,
                    min_confidence=float(config.MIN_CONFIDENCE_TO_TRADE),
                ),
                risk_state_guard(risk_state),
            ):
                if not guard_result.passed:
                    block_reason = guard_result.block_reason
                    break

        # Duplicate signal check (only when other guards pass)
        if block_reason is None and self._signal_history.duplicate_signal_guard(
            ctx.symbol, ctx.direction
        ):
            block_reason = f"BLOCKED_DUPLICATE_SIGNAL ({ctx.symbol} {ctx.direction})"

        decision = ExecutionDecision(
            symbol=ctx.symbol,
            direction=ctx.direction,
            confidence_used=ctx.confidence,
            should_execute=block_reason is None,
            block_reason=block_reason,
            risk_state=risk_state.value,
            mode="dry_run",
        )

        self._latest_decision = decision

        # Persist signal to history buffer
        self._signal_history.append(
            SignalRecord(
                symbol=ctx.symbol,
                direction=ctx.direction,
                confidence=ctx.confidence,
            )
        )

        # Export snapshot to disk
        self._snapshot_exporter.export_execution_snapshot(decision)

        logger.info(
            "ExecutionDecision: %s %s | should_execute=%s | risk_state=%s | block=%s",
            ctx.symbol,
            ctx.direction,
            decision.should_execute,
            decision.risk_state,
            decision.block_reason,
        )

        return decision

    def get_latest_decision(self) -> Optional[ExecutionDecision]:
        """Return the most recent decision, or None if evaluate() has not been called."""
        return self._latest_decision
