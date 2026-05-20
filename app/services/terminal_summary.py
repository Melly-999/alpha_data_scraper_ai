"""Read-only Terminal Summary service.

Returns a static, deterministic terminal summary for the Terminal V1
dashboard. Performs zero IO:

* No MT5 calls.
* No broker API calls.
* No live market data fetches.
* No order placement.
* No Supabase writes.
* No mutable global state.

The response is always safe to serve and always returns 200. The
``updated_at`` timestamp is the only field that varies per call.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.schemas.terminal import (
    TerminalBrokerPermissions,
    TerminalBrokerStatus,
    TerminalSafetyState,
    TerminalSummaryResponse,
)

_STATIC_DIAGNOSTICS: tuple[str, ...] = (
    "Paper adapter is read-only. No order placement is possible.",
    "Execution endpoints are disabled. Live trading is blocked.",
    "Fallback mode active — no live broker connection available.",
)

_STATIC_PERMISSIONS = TerminalBrokerPermissions()
_STATIC_SAFETY = TerminalSafetyState()


class TerminalSummaryService:
    """Generate the read-only terminal summary payload."""

    def get_summary(self) -> TerminalSummaryResponse:
        return TerminalSummaryResponse(
            backend="fallback",
            broker=TerminalBrokerStatus(
                diagnostics=list(_STATIC_DIAGNOSTICS),
                permissions=_STATIC_PERMISSIONS,
            ),
            safety=_STATIC_SAFETY,
            updated_at=datetime.now(timezone.utc),
        )
