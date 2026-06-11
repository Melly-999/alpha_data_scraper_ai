"""Read-only Postgres access for Neon-backed ACE memory."""

from __future__ import annotations

import os
import re
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row

_SELECT_ONLY = re.compile(r"^\s*(select|with)\b", re.IGNORECASE | re.DOTALL)


def get_database_url() -> str | None:
    """Return DATABASE_URL when configured."""

    value = os.environ.get("DATABASE_URL", "").strip()
    return value or None


def assert_select_only(sql: str) -> None:
    """Reject any statement that is not a read-only SELECT/WITH query."""

    if not _SELECT_ONLY.match(sql):
        raise ValueError("Only read-only SELECT queries are allowed.")


@contextmanager
def readonly_connection() -> Iterator[psycopg.Connection[Any]]:
    """Open a Postgres connection forced into read-only mode."""

    database_url = get_database_url()
    if database_url is None:
        raise RuntimeError("DATABASE_URL is not configured.")

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        conn.execute("SET default_transaction_read_only = on")
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
