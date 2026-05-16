# Supabase Migration Runbook

**Safety class**: Read-only / Dry-run / Advisory  
**Last updated**: 2026-05-16  
**Status**: Local — not applied to remote project

---

## Safety Statement

- All mellytrade tables are **audit and advisory only** — no execution, no live trading, no order placement.
- No frontend component reads from or writes to Supabase directly.
- All database access is mediated through the FastAPI backend using the **service_role** key, which is **never sent to the frontend**.
- No columns contain account IDs, order IDs, execution IDs, credentials, or secrets.
- Safety columns (`dry_run`, `auto_trade`, `read_only`, `order_placed`) are enforced by `CHECK` constraints at the database level and **cannot be overridden** by any INSERT or UPDATE.

---

## Migration Apply Order

Apply migrations in the following order. Each migration is idempotent (`CREATE TABLE IF NOT EXISTS`, `ALTER TABLE … ENABLE ROW LEVEL SECURITY` is safe to re-run).

### 1 — SUPA-001: Schema Foundation

**File**: `docs/supabase/supa_001_schema.sql`  
**Creates**:
- `mellytrade` schema
- `mellytrade.audit_events`
- `mellytrade.scanner_runs`
- `mellytrade.scanner_results`
- `mellytrade.agent_tasks`
- `mellytrade.system_health_snapshots`

**RLS**: Enabled on all five tables. No permissive policies — deny-all default.

```sql
-- Apply via Supabase SQL editor or CLI:
-- \i docs/supabase/supa_001_schema.sql
```

### 2 — SUPA-011: Signal Decisions Table

**File**: `supabase/migrations/20260516_signal_decisions.sql`  
**Creates**:
- `mellytrade.signal_decisions` — dry-run signal decision log

**Safety columns enforced by CHECK constraints**:
| Column | Value | Constraint |
|--------|-------|------------|
| `dry_run` | `TRUE` | `CHECK (dry_run = TRUE)` |
| `auto_trade` | `FALSE` | `CHECK (auto_trade = FALSE)` |
| `read_only` | `TRUE` | `CHECK (read_only = TRUE)` |
| `order_placed` | `FALSE` | `CHECK (order_placed = FALSE)` |

**Indexes**:
- `signal_decisions_created_at_idx` on `(created_at DESC)` — primary access pattern
- `signal_decisions_symbol_created_at_idx` on `(symbol, created_at DESC)` — symbol-filtered queries

**RLS**: NOT enabled by this migration (added in step 3).

```sql
-- \i supabase/migrations/20260516_signal_decisions.sql
```

### 3 — SUPA-012: Signal Decisions RLS

**File**: `supabase/migrations/20260516_signal_decisions_rls.sql`  
**Action**: Enables Row Level Security on `mellytrade.signal_decisions`.

**Must be applied after step 2.**

```sql
-- \i supabase/migrations/20260516_signal_decisions_rls.sql
```

---

## Verification

### Verify table exists

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'mellytrade'
  AND table_name = 'signal_decisions';
-- Expected: 1 row
```

### Verify all mellytrade tables

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'mellytrade'
ORDER BY table_name;
-- Expected: agent_tasks, audit_events, scanner_results, scanner_runs,
--           signal_decisions, system_health_snapshots
```

### Verify RLS is enabled on signal_decisions

```sql
SELECT relname, relrowsecurity
FROM pg_class
JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
WHERE pg_namespace.nspname = 'mellytrade'
  AND relname = 'signal_decisions';
-- Expected: relrowsecurity = true
```

### Verify RLS is enabled on all mellytrade tables

```sql
SELECT relname, relrowsecurity
FROM pg_class
JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
WHERE pg_namespace.nspname = 'mellytrade'
ORDER BY relname;
-- Expected: all rows have relrowsecurity = true
```

### Verify safety CHECK constraints

```sql
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'mellytrade.signal_decisions'::regclass
  AND contype = 'c'
ORDER BY conname;
-- Expected: constraints for auto_trade, decision, direction,
--           dry_run, order_placed, read_only, risk_status,
--           confidence, (plus any generated constraint names)
```

### Verify indexes exist

```sql
SELECT indexname
FROM pg_indexes
WHERE schemaname = 'mellytrade'
  AND tablename = 'signal_decisions';
-- Expected: signal_decisions_pkey,
--           signal_decisions_created_at_idx,
--           signal_decisions_symbol_created_at_idx
```

### Verify backend still uses degraded fallback when Supabase unavailable

Run the full validation suite locally. The history service falls back to in-memory seed data when the Supabase client is unavailable:

```powershell
# Windows:
py -3.11 -m pytest tests/app/test_signal_decision_history.py -q
py -3.11 -m pytest tests/app/test_signal_decision_reader.py -q

# The degraded path is tested explicitly:
# TestSupa011FallbackBehaviour.test_fallback_true_when_reader_returns_empty
# TestReadDegradedPath.test_returns_empty_list_when_no_client
```

All tests use `_select_fn` / `_insert_fn` injection or monkeypatching — no real Supabase connection required.

---

## RLS Policy Notes

**No permissive policies are defined in any migration.**

The deny-all default with RLS enabled is intentional and safe:

- The **service_role** key (backend FastAPI only) bypasses RLS at the Supabase level — reads and writes succeed.
- The **anon** key (never sent to frontend for mellytrade tables) is denied by default.
- The **authenticated** key is denied by default.

When adding a policy in a future migration, follow this pattern (for reference only — do not add without threat model review):

```sql
-- Backend service writes (INSERT) — for reference only:
CREATE POLICY "backend_service_insert"
  ON mellytrade.signal_decisions
  AS PERMISSIVE FOR INSERT
  TO service_role
  USING (true);

-- Authenticated read (SELECT) — only after auth model reviewed:
-- CREATE POLICY "authenticated_read"
--   ON mellytrade.signal_decisions
--   AS PERMISSIVE FOR SELECT
--   TO authenticated
--   USING (auth.uid() IS NOT NULL);

-- DO NOT create anon/public SELECT policy without threat model review.
```

---

## Frontend Data Access

The frontend **never** queries Supabase directly. All data flows through FastAPI:

```
Browser → GET /api/signals/decisions → FastAPI → signal_decision_reader
       → Supabase (service_role, bypasses RLS) → signal_decisions table
       → FastAPI serialises SignalDecisionHistoryResponse → Browser
```

The `signal_decisions` table URL and Supabase project keys are **never** sent to the browser. The `service_role` key is backend-only (`SUPABASE_SERVICE_ROLE_KEY` environment variable, never logged or returned by any API endpoint).

---

## Emergency Fallback

If Supabase is unavailable or the `signal_decisions` table does not exist yet:

- `read_signal_decisions()` returns `[]` (never raises)
- `SignalDecisionHistoryService.list_decisions()` falls back to `_SEED_DECISIONS` (7 in-memory records)
- `SignalDecisionHistoryResponse.fallback = True` signals the seed data path to the frontend
- All API endpoints remain functional and return valid responses

No outage, no error surfaced to end users. The degraded path is tested in `tests/app/test_signal_decision_history.py`.
