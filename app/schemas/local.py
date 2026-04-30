from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

ChecklistStatus = Literal["pass", "warn", "fail"]


class LocalChecklistCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    label: str
    status: ChecklistStatus
    detail: str


class LocalChecklistSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool
    auto_trade: bool
    supports_live_orders: bool
    live_orders_blocked: bool
    broker_status: str
    broker_mode: str
    broker_connected: bool
    broker_read_only: bool


class LocalChecklistResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "degraded"]
    service: str
    checks: list[LocalChecklistCheck]
    summary: LocalChecklistSummary
