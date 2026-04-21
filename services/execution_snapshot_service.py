"""Exports the latest ExecutionDecision to results/execution/decisions.json."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from core.config import PROJECT_ROOT

if TYPE_CHECKING:
    from execution_service import ExecutionDecision

logger = logging.getLogger(__name__)


class ExecutionSnapshotService:
    """Writes the latest execution decision snapshot to disk after each evaluation.

    All results paths are resolved relative to *results_dir* (defaults to the
    project-root ``results/`` directory) so every component stays consistent
    regardless of the process working directory.
    """

    def __init__(self, results_dir: Optional[Path] = None) -> None:
        self._results_dir = results_dir or (PROJECT_ROOT / "results")

    @property
    def decisions_path(self) -> Path:
        return self._results_dir / "execution" / "decisions.json"

    def export_execution_snapshot(self, decision: "ExecutionDecision") -> None:
        try:
            self.decisions_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "latest_execution_decision": {
                    "symbol": decision.symbol,
                    "direction": decision.direction,
                    "confidence_used": decision.confidence_used,
                    "should_execute": decision.should_execute,
                    "block_reason": decision.block_reason,
                    "risk_state": decision.risk_state,
                    "mode": decision.mode,
                    "timestamp": decision.timestamp.isoformat(),
                }
            }
            self.decisions_path.write_text(
                json.dumps(payload, indent=2), encoding="utf-8"
            )
            logger.info("Execution snapshot exported: %s", self.decisions_path)
        except Exception as exc:
            logger.error("Failed to export execution snapshot: %s", exc)
