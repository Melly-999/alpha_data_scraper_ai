"""Read-only Neon / ACE memory introspection service."""

from __future__ import annotations

import os
from typing import List

from app.db.readonly import fetch_one, get_database_url, is_driver_available
from app.schemas.neon_memory import (
    NeonMemoryStatus,
    NeonMemorySummary,
    NeonMemoryTableCount,
)


def _ace_namespace() -> str:
    return os.environ.get("ACE_NAMESPACE", "example-workspace")


_ACE_TABLES = (
    "memories",
    "decisions",
    "issues",
    "work_logs",
    "episodes",
    "observations",
    "patterns",
    "saved_plans",
)


class NeonMemoryService:
    """Expose safe, read-only views of ACE memory stored in Neon."""

    def get_status(self) -> NeonMemoryStatus:
        database_url = get_database_url()
        if not is_driver_available():
            return NeonMemoryStatus(
                availability="degraded",
                source="driver-missing",
                database_configured=database_url is not None,
                database_reachable=False,
                ace_namespace=_ace_namespace(),
                message=(
                    "psycopg driver is not installed. "
                    "Neon memory routes stay read-only and degraded."
                ),
            )

        if database_url is None:
            return NeonMemoryStatus(
                availability="degraded",
                source="unconfigured",
                database_configured=False,
                database_reachable=False,
                ace_namespace=_ace_namespace(),
                message="DATABASE_URL is not set. Neon memory routes stay read-only.",
            )

        try:
            row = fetch_one(
                "SELECT current_database() AS current_database, version() AS postgres_version"
            )
        except Exception as exc:  # noqa: BLE001 - surface degraded state, not secrets
            return NeonMemoryStatus(
                availability="degraded",
                source="neon-postgres",
                database_configured=True,
                database_reachable=False,
                message=f"Neon database unreachable: {exc.__class__.__name__}",
            )

        return NeonMemoryStatus(
            availability="connected",
            source="neon-postgres",
            database_configured=True,
            database_reachable=True,
            postgres_version=row["postgres_version"] if row else None,
            current_database=row["current_database"] if row else None,
            neon_project_id=os.environ.get("NEON_PROJECT_ID", "example-project"),
            neon_branch=os.environ.get("NEON_BRANCH_LOCAL", "production"),
            ace_namespace=_ace_namespace(),
            message="Neon ACE memory database is reachable in read-only mode.",
        )

    def get_summary(self) -> NeonMemorySummary:
        status = self.get_status()
        if not status.database_reachable:
            return NeonMemorySummary(
                availability=status.availability,
                source=status.source,
                ace_namespace=status.ace_namespace,
                message=status.message,
            )

        tables: List[NeonMemoryTableCount] = []
        total_rows = 0
        for table_name in _ACE_TABLES:
            row = fetch_one(f"SELECT COUNT(*) AS row_count FROM {table_name}")
            row_count = int(row["row_count"]) if row else 0
            tables.append(
                NeonMemoryTableCount(table_name=table_name, row_count=row_count)
            )
            total_rows += row_count

        namespace = _ace_namespace()
        namespace_row = fetch_one(
            "SELECT COUNT(*) AS row_count FROM namespace_registry WHERE slug = %s",
            (namespace,),
        )
        namespace_count = int(namespace_row["row_count"]) if namespace_row else 0

        return NeonMemorySummary(
            availability="connected",
            source="neon-postgres",
            ace_namespace=namespace,
            tables=tables,
            total_rows=total_rows,
            message=(
                f"ACE namespace '{namespace}' "
                f"{'is registered' if namespace_count else 'is not registered yet'}."
            ),
        )
