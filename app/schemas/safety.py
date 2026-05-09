"""Schemas for the central safety status contract.

A single source of truth, exposed via ``GET /api/safety/status``, that the
Terminal V1 frontend (and any tooling) can read to verify the running
backend's safety posture without hand-stitching it from ``/health``,
``/risk/config``, and ``/terminal/events``.

The schemas are deliberately strict (``extra="forbid"``): they cannot grow
new fields silently, and they intentionally omit any execution-shaped
field. There is no schema-level way to express "place an order" through
this contract — that is part of how Terminal V1 stays read-only.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Canonical safety pillars. Each one is a short slug that maps 1:1 to a
# narrative the UI can render. The list is closed (Literal) so adding a
# pillar is a deliberate, version-bumping schema change reviewed in code,
# not a free-form runtime addition.
SafetyPillar = Literal[
    "DRY_RUN_ACTIVE",
    "READ_ONLY_ACTIVE",
    "AUTO_TRADE_DISABLED",
    "LIVE_ORDERS_BLOCKED",
    "MAX_RISK_CAPPED",
]


class SafetyStatusResponse(BaseModel):
    """Central safety posture snapshot for Terminal V1.

    Every field is asserted by ``tests/app/test_safety_status.py``. A drift
    in any boolean below, or a ``max_risk_per_trade_pct`` > 1.0, fails the
    safety regression suite by design.
    """

    model_config = ConfigDict(extra="forbid")

    dry_run: bool = Field(
        ...,
        description=(
            "True when the backend is running in dry-run mode. Terminal V1 "
            "requires this to be True; live order paths are not reachable."
        ),
    )
    auto_trade: bool = Field(
        ...,
        description=(
            "True if autotrade is enabled. Terminal V1 requires this to be "
            "False; the safety regression test fails if it ever flips."
        ),
    )
    read_only: bool = Field(
        ...,
        description=(
            "True when the Terminal V1 surface is read-only. The frontend "
            "uses this to render the READ-ONLY MODE pill."
        ),
    )
    live_orders_blocked: bool = Field(
        ...,
        description=(
            "True when every code path that could submit a live order is "
            "blocked. Terminal V1 requires this to be True."
        ),
    )
    max_risk_per_trade_pct: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Hard ceiling on per-trade risk, expressed as a percentage of "
            "account equity. Capped at 1.0 by repo-wide policy and asserted "
            "in tests."
        ),
    )
    pillars: list[SafetyPillar] = Field(
        ...,
        description=(
            "Closed list of named safety pillars currently asserted by the "
            "backend. Allows the UI to render a per-pillar status without "
            "stringly-typed checks."
        ),
    )
    safety_note: str = Field(
        ...,
        min_length=1,
        description=(
            "Short, human-readable explanation of the current safety "
            "posture. Surfaced next to the safety banner."
        ),
    )
    generated_at: datetime = Field(
        ...,
        description=(
            "Wall-clock time the response was generated. Used by the UI "
            "to detect stale safety telemetry."
        ),
    )
