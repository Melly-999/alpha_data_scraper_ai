from __future__ import annotations

import textwrap

import pytest

from app.db.readonly import assert_select_only


def test_assert_select_only_allows_select():
    assert_select_only("SELECT 1")


def test_assert_select_only_allows_with_and_leading_comments():
    sql = textwrap.dedent(
        """
        -- leading comment
        /* block comment */
        WITH x AS (SELECT 1 AS id)
        SELECT id FROM x
        """
    )
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
