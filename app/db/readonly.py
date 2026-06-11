"""Read-only Postgres access for Neon-backed ACE memory."""

from __future__ import annotations

import os
import re
from contextlib import contextmanager
from collections.abc import Iterator
from typing import Any

import psycopg
from psycopg.rows import dict_row

_SELECT_ONLY_PATTERN = re.compile(r"^\s*(select|with)\b", re.IGNORECASE | re.DOTALL)
_DANGEROUS_SQL_PATTERN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|merge|call|copy|execute)\b",
    re.IGNORECASE,
)


def get_database_url() -> str | None:
    """Return DATABASE_URL when configured."""

    value = os.environ.get("DATABASE_URL", "").strip()
    return value or None


def _strip_leading_comments(sql: str) -> str:
    """Remove leading whitespace and SQL comments conservatively."""

    remaining = sql.lstrip()
    while remaining.startswith("--") or remaining.startswith("/*"):
        if remaining.startswith("--"):
            newline = remaining.find("\n")
            if newline == -1:
                return ""
            remaining = remaining[newline + 1 :]
        else:
            end = remaining.find("*/")
            if end == -1:
                return ""
            remaining = remaining[end + 2 :]
        remaining = remaining.lstrip()
    return remaining


def assert_select_only(sql: str) -> None:
    """Reject any statement that is not a read-only SELECT/WITH query."""

    statement = _strip_leading_comments(sql)
    if not _SELECT_ONLY_PATTERN.match(statement):
        raise ValueError("Only a single read-only SELECT or WITH query is allowed.")
    if ";" in statement:
        raise ValueError("Only a single read-only SELECT or WITH query is allowed.")
    if _DANGEROUS_SQL_PATTERN.search(statement):
        raise ValueError("Only a single read-only SELECT or WITH query is allowed.")


@contextmanager
def readonly_connection() -> Iterator[psycopg.Connection[Any]]:
    """Open a Postgres connection forced into read-only mode."""

    database_url = get_database_url()
    if database_url is None:
        raise RuntimeError("DATABASE_URL is not configured.")

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.transaction(read_only=True):
            yield conn


def fetch_all(sql: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
    """Run a validated read-only query and return all rows."""

    assert_select_only(sql)
    with readonly_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            return [dict(row) for row in rows]


def fetch_one(sql: str, params: tuple[Any, ...] | None = None) -> dict[str, Any] | None:
    """Run a validated read-only query and return the first row."""

    rows = fetch_all(sql, params)
    return rows[0] if rows else None
