from __future__ import annotations

import textwrap
from typing import Literal

import pytest

import app.db.readonly as readonly_module
from app.db.readonly import (
    assert_select_only,
    fetch_all,
    fetch_one,
    readonly_connection,
)


def test_assert_select_only_allows_select():
    assert_select_only("SELECT 1")


def test_assert_select_only_allows_with_and_leading_comments():
    sql = textwrap.dedent("""
        -- leading comment
        /* block comment */
        WITH x AS (SELECT 1 AS id)
        SELECT id FROM x
        """)
    assert_select_only(sql)


def test_assert_select_only_rejects_writes():
    with pytest.raises(ValueError, match="single read-only SELECT or WITH query"):
        assert_select_only("UPDATE memories SET value = '{}'")


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT 1; DROP TABLE memories",
        "SELECT 1; SELECT 2",
        "WITH x AS (SELECT 1) SELECT * FROM x; UPDATE memories SET value = 1",
        "INSERT INTO memories VALUES (1)",
        "UPDATE memories SET value = '{}' ",
        "DELETE FROM memories",
        "DROP TABLE memories",
        "ALTER TABLE memories ADD COLUMN x int",
        "CREATE TABLE memories (id int)",
        "TRUNCATE TABLE memories",
        "GRANT SELECT ON memories TO public",
        "REVOKE SELECT ON memories FROM public",
        "MERGE INTO memories USING src ON 1=1 WHEN MATCHED THEN UPDATE SET id = 1",
        "CALL mutate_memory()",
        "COPY memories TO STDOUT",
        "EXECUTE maintenance_job()",
    ],
)
def test_assert_select_only_rejects_dangerous_and_multi_statement_sql(sql: str):
    with pytest.raises(ValueError, match="single read-only SELECT or WITH query"):
        assert_select_only(sql)


def test_readonly_helpers_use_read_only_transaction_and_params(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, object]] = []

    class _FakeTransaction:
        def __enter__(self) -> "_FakeTransaction":
            calls.append(("transaction_enter", True))
            return self

        def __exit__(self, exc_type, exc, tb) -> Literal[False]:
            calls.append(("transaction_exit", exc_type))
            return False

    class _FakeCursor:
        def __enter__(self) -> "_FakeCursor":
            calls.append(("cursor_enter", None))
            return self

        def __exit__(self, exc_type, exc, tb) -> Literal[False]:
            calls.append(("cursor_exit", exc_type))
            return False

        def execute(self, sql: str, params: tuple[object, ...]) -> None:
            calls.append(("execute", (sql, params)))

        def fetchall(self) -> list[dict[str, int]]:
            return [{"id": 1}, {"id": 2}]

    class _FakeConnection:
        def __enter__(self) -> "_FakeConnection":
            calls.append(("connect_enter", None))
            return self

        def __exit__(self, exc_type, exc, tb) -> Literal[False]:
            calls.append(("connect_exit", exc_type))
            return False

        def transaction(self) -> _FakeTransaction:
            calls.append(("transaction", None))
            return _FakeTransaction()

        def cursor(self) -> _FakeCursor:
            return _FakeCursor()

        def execute(self, sql: str) -> None:
            calls.append(("execute", sql))

    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    monkeypatch.setattr(
        readonly_module.psycopg,
        "connect",
        lambda *args, **kwargs: _FakeConnection(),
    )

    with readonly_connection() as conn:
        assert isinstance(conn, _FakeConnection)

    assert ("transaction", None) in calls
    assert ("execute", "SET TRANSACTION READ ONLY") in calls

    rows = fetch_all("  SELECT * FROM memories WHERE id = %s", (7,))
    assert rows == [{"id": 1}, {"id": 2}]

    first = fetch_one(
        "WITH x AS (SELECT 1 AS id) SELECT id FROM x WHERE id = %s",
        (1,),
    )
    assert first == {"id": 1}

    assert (
        "execute",
        ("  SELECT * FROM memories WHERE id = %s", (7,)),
    ) in calls
    assert (
        "execute",
        ("WITH x AS (SELECT 1 AS id) SELECT id FROM x WHERE id = %s", (1,)),
    ) in calls


def test_readonly_connection_requires_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL is not configured"):
        with readonly_connection():
            pass
