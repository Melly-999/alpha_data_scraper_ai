from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SignalAction(str, Enum):
    HOLD = "HOLD"
    WATCH = "WATCH"
    LONG_SETUP = "LONG_SETUP"
    SHORT_SETUP = "SHORT_SETUP"
    NO_TRADE = "NO_TRADE"


class SignalScannerResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str
    action: SignalAction
    confidence: float = Field(ge=0, le=100)
    reason: str
    risk_allowed: Literal[False] = False
    execution_mode: Literal["dry_run_only"] = "dry_run_only"
    requires_human_review: Literal[True] = True
    source: Literal["scanner"] = "scanner"
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator("symbol", "reason")
    @classmethod
    def _strip_and_require(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned


class SignalScannerBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    results: list[SignalScannerResult] = Field(default_factory=list)
    read_only: Literal[True] = True
    execution_mode: Literal["dry_run_only"] = "dry_run_only"


# ---------------------------------------------------------------------------
# SIG-UNIVERSE-002 — Universe list response schemas
# ---------------------------------------------------------------------------


class SignalUniversePreset(BaseModel):
    """A single read-only scanner universe preset.

    Carries no execution semantics, order intent, or trading instructions.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    label: str
    symbols: list[str]
    item_count: int
    asset_classes: list[str]
    tags: list[str]
    read_only: Literal[True] = True
    execution_mode: Literal["dry_run_only"] = "dry_run_only"
    requires_human_review: Literal[True] = True


class SignalUniverseListResponse(BaseModel):
    """Response schema for GET /signals/scanner/universes.

    Advisory-only.  No execution, no broker call, no order routing.
    """

    model_config = ConfigDict(extra="forbid")

    read_only: Literal[True] = True
    execution_mode: Literal["dry_run_only"] = "dry_run_only"
    requires_human_review: Literal[True] = True
    universes: list[SignalUniversePreset]
