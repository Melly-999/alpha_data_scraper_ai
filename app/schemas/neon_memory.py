"""Pydantic schemas for read-only Neon / ACE memory surfaces."""

from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field

from app.schemas.alpaca_paper import AlpacaPaperSafetyFlags


class NeonMemoryTableCount(BaseModel):
    """Row count for a single ACE memory table."""

    table_name: str
    row_count: int


class NeonMemoryStatus(AlpacaPaperSafetyFlags):
    """Read-only connectivity summary for Neon-backed ACE memory."""

    autotrade: Literal[False] = False
    service_name: str = "neon-memory"
    availability: str
    mode: str = "read-only"
    source: str
    database_configured: bool
    database_reachable: bool
    postgres_version: str | None = None
    current_database: str | None = None
    neon_project_id: str = "fragrant-river-86681973"
    neon_branch: str = "production"
    ace_namespace: str = "mateusz-workspace"
    message: str
    note: str = "GET-only memory introspection. No writes or execution."


class NeonMemorySummary(AlpacaPaperSafetyFlags):
    """Read-only ACE memory table summary."""

    autotrade: Literal[False] = False
    service_name: str = "neon-memory"
    availability: str
    mode: str = "read-only"
    source: str
    ace_namespace: str = "mateusz-workspace"
    tables: List[NeonMemoryTableCount] = Field(default_factory=list)
    total_rows: int = 0
    message: str
    note: str = "Advisory counts only. No mutation paths."
