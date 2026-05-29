"""Safety assertions for the SUPA-001 Supabase schema draft.

Reads the SQL and markdown files from docs/supabase/ and asserts:
  - No forbidden table names (orders, trades, executions, ...)
  - No forbidden sensitive column names (account_id, secret, ...)
  - Required safety defaults are present in the SQL
  - No active (non-negated) execution-shaped terms appear
  - All required safe tables are declared

These tests are text-based — they do not require a live Supabase connection.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_SQL = REPO_ROOT / "docs" / "supabase" / "supa_001_schema.sql"
SCHEMA_MD = REPO_ROOT / "docs" / "supabase" / "supa_001_audit_schema.md"

# ---------------------------------------------------------------------------
# Forbidden identifiers — must NOT appear as CREATE TABLE names
# ---------------------------------------------------------------------------

FORBIDDEN_TABLES = [
    "orders",
    "trades",
    "executions",
    "live_orders",
    "broker_orders",
    "positions_write",
    "autotrade",
    "account_credentials",
    "api_keys",
    "secrets",
]

# ---------------------------------------------------------------------------
# Forbidden column / field names — must NOT appear in CREATE TABLE bodies
# ---------------------------------------------------------------------------

FORBIDDEN_COLUMNS = [
    "account_id",
    "account_number",
    "password",
    "secret",
    "api_key",
    "credential",
    "service_role",
]

# ---------------------------------------------------------------------------
# Required safety tokens — must appear in the SQL
# ---------------------------------------------------------------------------

REQUIRED_SAFETY_TOKENS = [
    "read_only",
    "dry_run",
    "dry_run_only",
    "risk_allowed",
    "requires_human_review",
]

# ---------------------------------------------------------------------------
# Required table names — must appear as CREATE TABLE statements
# ---------------------------------------------------------------------------

REQUIRED_TABLES = [
    "audit_events",
    "scanner_runs",
    "scanner_results",
    "agent_tasks",
    "system_health_snapshots",
]

# ---------------------------------------------------------------------------
# Terms that indicate live execution risk — must NOT appear as active intent.
# They are allowed only in comments, safety assertions, or forbidden-list docs.
# ---------------------------------------------------------------------------

EXECUTION_RISK_TERMS = [
    "place_order",
    "cancel_order",
    "modify_order",
    "execute_trade",
    "broker_execute",
    "enable_autotrade",
    "disable_dry_run",
    "connect_live",
    "live trading",
    "live order",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sql_text() -> str:
    assert SCHEMA_SQL.exists(), f"Schema SQL not found: {SCHEMA_SQL}"
    return SCHEMA_SQL.read_text(encoding="utf-8")


def _md_text() -> str:
    assert SCHEMA_MD.exists(), f"Schema MD not found: {SCHEMA_MD}"
    return SCHEMA_MD.read_text(encoding="utf-8")


def _create_table_names(sql: str) -> list[str]:
    """Extract table names from CREATE TABLE [IF NOT EXISTS] statements."""
    pattern = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:\w+\.)?(\w+)",
        re.IGNORECASE,
    )
    return pattern.findall(sql)


def _column_names_in_sql(sql: str) -> list[str]:
    """
    Naively extract identifiers from column definitions.
    This deliberately over-matches — a false positive here means a word
    that looks like a forbidden column name appears in the SQL at all.
    """
    # Strip SQL comments to avoid false-negative on commented-out columns
    sql_no_comments = re.sub(r"--[^\n]*", "", sql)
    return re.findall(r"\b(\w+)\b", sql_no_comments)


# ---------------------------------------------------------------------------
# Tests — schema file existence
# ---------------------------------------------------------------------------


def test_schema_sql_file_exists() -> None:
    assert SCHEMA_SQL.exists(), f"Missing: {SCHEMA_SQL}"


def test_schema_md_file_exists() -> None:
    assert SCHEMA_MD.exists(), f"Missing: {SCHEMA_MD}"


# ---------------------------------------------------------------------------
# Tests — forbidden tables
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("table_name", FORBIDDEN_TABLES)
def test_forbidden_table_not_in_sql(table_name: str) -> None:
    sql = _sql_text()
    created = [t.lower() for t in _create_table_names(sql)]
    assert table_name.lower() not in created, (
        f"Forbidden table '{table_name}' found in CREATE TABLE statements. "
        "Trading/execution/credentials tables must not exist in this schema."
    )


@pytest.mark.parametrize("table_name", FORBIDDEN_TABLES)
def test_forbidden_table_not_in_md(table_name: str) -> None:
    md = _md_text().lower()
    # Allow the word to appear only inside the explicit "Forbidden Tables" section.
    # A CREATE TABLE reference outside that section is a violation.
    # We check for 'create table <name>' and 'alter table <name>' patterns.
    pattern = re.compile(
        rf"(?:create|alter)\s+table\s+(?:\w+\.)?{re.escape(table_name)}\b",
        re.IGNORECASE,
    )
    assert not pattern.search(
        md
    ), f"Forbidden table '{table_name}' appears as an active table in the MD doc."


# ---------------------------------------------------------------------------
# Tests — forbidden columns
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("col_name", FORBIDDEN_COLUMNS)
def test_forbidden_column_not_as_column_definition(col_name: str) -> None:
    sql = _sql_text()
    # Strip comments so we only check actual DDL
    sql_no_comments = re.sub(r"--[^\n]*", "", sql)
    # Match the pattern: start of a column definition line (indent + name)
    # e.g. "    account_id  uuid  NOT NULL"
    pattern = re.compile(
        rf"^\s+{re.escape(col_name)}\s+\w",
        re.IGNORECASE | re.MULTILINE,
    )
    assert not pattern.search(sql_no_comments), (
        f"Forbidden column '{col_name}' appears as a column definition in the SQL. "
        "Sensitive/credential column names must not be defined in this schema."
    )


# ---------------------------------------------------------------------------
# Tests — required safety defaults
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("kw", REQUIRED_SAFETY_TOKENS)
def test_required_safety_token_in_sql(kw: str) -> None:
    sql = _sql_text()
    assert kw.lower() in sql.lower(), (
        f"Required safety keyword '{kw}' not found in schema SQL. "
        "All safety defaults must be explicitly present."
    )


# ---------------------------------------------------------------------------
# Tests — required tables present
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("table_name", REQUIRED_TABLES)
def test_required_table_in_sql(table_name: str) -> None:
    sql = _sql_text()
    created = [t.lower() for t in _create_table_names(sql)]
    assert (
        table_name.lower() in created
    ), f"Required table '{table_name}' not found in CREATE TABLE statements."


# ---------------------------------------------------------------------------
# Tests — no active execution-risk terms
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("term", EXECUTION_RISK_TERMS)
def test_no_active_execution_term_in_sql(term: str) -> None:
    sql = _sql_text()
    # Strip comments — execution terms in comments (e.g. "-- do NOT place_order")
    # are acceptable; in active DDL they are not.
    sql_no_comments = re.sub(r"--[^\n]*", "", sql)
    assert term.lower() not in sql_no_comments.lower(), (
        f"Execution-risk term '{term}' found in active SQL (outside comments). "
        "No live trading or execution semantics allowed in this schema."
    )


# ---------------------------------------------------------------------------
# Tests — RLS is enabled
# ---------------------------------------------------------------------------


def test_rls_enabled_for_all_required_tables() -> None:
    sql = _sql_text()
    for table in REQUIRED_TABLES:
        pattern = re.compile(
            rf"ALTER\s+TABLE\s+(?:\w+\.)?{re.escape(table)}\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY",
            re.IGNORECASE,
        )
        assert pattern.search(sql), (
            f"RLS not enabled for table '{table}'. "
            "All tables must have ROW LEVEL SECURITY enabled."
        )


# ---------------------------------------------------------------------------
# Tests — safety CHECK constraints present
# ---------------------------------------------------------------------------


def test_read_only_check_constraint_present() -> None:
    sql = _sql_text()
    assert (
        "CHECK (read_only = true)" in sql
    ), "read_only CHECK constraint missing. Must enforce read_only = true."


def test_dry_run_only_check_constraint_present() -> None:
    sql = _sql_text()
    assert "CHECK (execution_mode = 'dry_run_only')" in sql, (
        "execution_mode CHECK constraint missing. "
        "Must enforce execution_mode = 'dry_run_only'."
    )


def test_risk_allowed_false_check_constraint_present() -> None:
    sql = _sql_text()
    assert (
        "CHECK (risk_allowed = false)" in sql
    ), "risk_allowed CHECK constraint missing. Must enforce risk_allowed = false."


def test_requires_human_review_check_constraint_present() -> None:
    sql = _sql_text()
    assert "CHECK (requires_human_review = true)" in sql, (
        "requires_human_review CHECK constraint missing. "
        "Must enforce requires_human_review = true."
    )


# ---------------------------------------------------------------------------
# Tests — no service_role key in schema text
# ---------------------------------------------------------------------------


def test_no_service_role_key_in_sql() -> None:
    sql = _sql_text()
    sql_no_comments = re.sub(r"--[^\n]*", "", sql)
    # service_role as a column or value literal is forbidden
    # (it is allowed in comments as a documentation reference)
    pattern = re.compile(r"'service_role'", re.IGNORECASE)
    assert not pattern.search(sql_no_comments), (
        "service_role key literal found in active SQL. "
        "Service role keys must never appear in schema definitions."
    )


def test_mellytrade_schema_namespace_present() -> None:
    sql = _sql_text()
    assert "mellytrade." in sql.lower(), (
        "Schema namespace 'mellytrade.' not found. "
        "All tables must be in the mellytrade schema."
    )
