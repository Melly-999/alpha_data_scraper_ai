from __future__ import annotations

from typing import Any, Dict


class PropFirmRiskStream:
    def evaluate(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        drawdown = float(stats.get("drawdown_pct", 0.0) or 0.0)
        daily = float(stats.get("daily_pnl_pct", 0.0) or 0.0)

        if drawdown <= -8.0:
            return {"status": "CRITICAL", "reason": "MAX DD approaching"}

        if daily <= -4.5:
            return {"status": "WARNING", "reason": "Daily DD near FTMO limit"}

        if daily <= -5.0:
            return {"status": "BLOCK", "reason": "Daily loss limit reached"}

        return {"status": "OK", "reason": "Within limits"}
