"""Exports the latest ExecutionDecision to results/execution/decisions.json."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from execution_service import ExecutionDecision

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DECISIONS_PATH = _PROJECT_ROOT / "results" / "execution" / "decisions.json"


class ExecutionSnapshotService:
    """Writes the latest execution decision snapshot to disk after each evaluation."""

    def export_execution_snapshot(self, decision: "ExecutionDecision") -> None:
        try:
            DECISIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
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
            DECISIONS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            logger.info("Execution snapshot exported: %s", DECISIONS_PATH)
        except Exception as exc:
            logger.error("Failed to export execution snapshot: %s", exc)
