# SUPA-001 — Supabase Audit & Scanner Schema Foundation

**Task ID:** SUPA-001
**Title:** Supabase schema for audit / events / scanner runs
**Status:** Draft — schema only, no runtime client added
**Safety class:** READ-ONLY / DRY-RUN / ADVISORY — no execution tables
**Last updated:** 2026-05-15
**Branch:** `feature/supa-001-audit-schema`

---

## Goal

Define the Supabase PostgreSQL schema that will persist audit events, scanner
runs, scanner results, agent task records, and system health snapshots.

This document is a **schema foundation only**. It does not add:
- A Supabase client or SDK initialisation
- Any runtime write path in the backend
- Any frontend changes
- Any service role keys or credentials
- Any secrets, account IDs, or broker-linked tables

Those are deferred to SUPA-002 (backend client) and SUPA-003 (audit writer).

---

## Schema Namespace

All tables live in the `mellytrade` PostgreSQL schema inside the Supabase
project. This is consistent with the existing architecture references to
`mellytrade.audit_events` throughout the codebase.

```sql
CREATE SCHEMA IF NOT EXISTS mellytrade;
```

---

## Safety Posture

Every table in this schema enforces the following invariants by default:

| Invariant | Enforcement |
|---|---|
| `read_only = true` | Column default + CHECK constraint |
| `execution_mode = 'dry_run_only'` | Column default + CHECK constraint |
| `risk_allowed = false` | Column default + CHECK constraint (scanner_results) |
| `requires_human_review = true` | Column default + CHECK constraint (scanner_results, agent_tasks) |
| No order / trade / execution tables | Forbidden by schema — not defined here |
| No credential columns | No `api_key`, `secret`, `token`, `password`, `account_id` columns |
| RLS enabled | RLS must be enabled before any production use |

---

## Tables

See [`supa_001_schema.sql`](supa_001_schema.sql) for the full DDL.

### `mellytrade.audit_events`

Purpose: persists audit events emitted by backend services. Read-only feed.
The equivalent in-memory list is already served by `/api/terminal/events`.

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` | Primary key, auto-generated |
| `created_at` | `timestamptz` | Server-side default |
| `event_type` | `text` | E.g. `dry_run_active`, `autotrade_disabled` |
| `severity` | `text` | One of: `info`, `success`, `warning`, `error`, `safety` |
| `source` | `text` | Emitting service name |
| `message` | `text` | Human-readable description |
| `metadata` | `jsonb` | Optional structured payload |
| `read_only` | `boolean` | Default `true`, CHECK `= true` |
| `dry_run` | `boolean` | Default `true`, CHECK `= true` |

### `mellytrade.scanner_runs`

Purpose: records each invocation of the read-only signal scanner. Dry-run only.

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` | Primary key |
| `created_at` | `timestamptz` | Auto |
| `source` | `text` | Default `'scanner'` |
| `symbols` | `text[]` | Symbols analysed |
| `read_only` | `boolean` | Default `true`, CHECK `= true` |
| `execution_mode` | `text` | Default `'dry_run_only'`, CHECK `= 'dry_run_only'` |
| `status` | `text` | E.g. `pending`, `complete`, `error` |
| `metadata` | `jsonb` | Optional |

### `mellytrade.scanner_results`

Purpose: one row per symbol signal produced by a scanner run. Advisory only.
Every result is hard-coded advisory: `risk_allowed = false`,
`requires_human_review = true`, `execution_mode = 'dry_run_only'`.

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` | Primary key |
| `run_id` | `uuid` | FK to `scanner_runs.id` (nullable until FK enforced) |
| `created_at` | `timestamptz` | Auto |
| `symbol` | `text` | Ticker |
| `action` | `text` | E.g. `BUY_SIGNAL`, `SELL_SIGNAL`, `HOLD` — advisory only |
| `confidence` | `numeric(5,2)` | 0–100 scale |
| `reason` | `text` | Human-readable rationale |
| `risk_allowed` | `boolean` | Default `false`, CHECK `= false` |
| `execution_mode` | `text` | Default `'dry_run_only'`, CHECK `= 'dry_run_only'` |
| `requires_human_review` | `boolean` | Default `true`, CHECK `= true` |
| `source` | `text` | Default `'scanner'` |
| `metadata` | `jsonb` | Optional |

### `mellytrade.agent_tasks`

Purpose: task queue for AI dev agents (Codex, Claude Code). Read-only tracking.

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` | Primary key |
| `created_at` | `timestamptz` | Auto |
| `updated_at` | `timestamptz` | Updated on row change |
| `agent_name` | `text` | E.g. `codex`, `claude_code` |
| `task_type` | `text` | E.g. `schema`, `docs`, `tests` |
| `title` | `text` | Human-readable task title |
| `status` | `text` | E.g. `planned`, `in_progress`, `done`, `blocked` |
| `priority` | `text` | E.g. `p0`, `p1`, `p2` |
| `metadata` | `jsonb` | Optional |
| `read_only` | `boolean` | Default `true`, CHECK `= true` |
| `requires_human_review` | `boolean` | Default `true`, CHECK `= true` |

### `mellytrade.system_health_snapshots`

Purpose: periodic snapshots of component health for the dev dashboard.

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` | Primary key |
| `created_at` | `timestamptz` | Auto |
| `component` | `text` | E.g. `backend`, `frontend`, `scanner` |
| `status` | `text` | E.g. `ok`, `degraded`, `error` |
| `message` | `text` | Optional detail |
| `metadata` | `jsonb` | Optional |
| `read_only` | `boolean` | Default `true`, CHECK `= true` |

---

## Forbidden Tables

The following table names **must not** be created in any MellyTrade Supabase
schema. Their absence is asserted by `tests/app/test_supabase_schema_safety.py`.

```
orders
trades
executions
live_orders
broker_orders
positions_write
autotrade
account_credentials
api_keys
secrets
```

---

## Forbidden Columns

No table in this schema may contain columns named:

```
account_id
account_number
password
secret
token
api_key
credential
service_role
```

---

## RLS Policy Notes

RLS (Row Level Security) must be enabled on all tables before any production
or staging deployment. The exact policy set depends on the Supabase auth model
which is not finalised yet. Until that model exists:

1. **Enable RLS immediately** on creation — `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`.
   With RLS enabled and no permissive policy, the default is deny-all.

2. **Backend service writes only** — only the MellyTrade backend service using
   the `service_role` key may INSERT/UPDATE. The `service_role` key must never
   be sent to the frontend or included in any client-side bundle.

3. **Frontend reads** — when a read policy is eventually created, it should be
   scoped to authenticated users and restricted columns. Until auth is modelled,
   the safest posture is to keep all policies disabled (deny-all RLS default).

4. **No public access** — no `anon` role policy should grant SELECT until the
   threat model is reviewed.

5. **Frontend must never receive `service_role` key** — this is an architectural
   invariant. Frontend uses only the `anon`/`authenticated` publishable key.

---

## What Is NOT Done in SUPA-001

| Item | Deferred to |
|---|---|
| Supabase Python client / SDK init | SUPA-002 |
| Runtime audit writes from backend | SUPA-003 |
| GET-only audit/scanner/status API endpoints | SUPA-004 |
| Frontend audit rail | SUPA-005 |
| Applying migration to remote Supabase project | Human — after review |
| Auth model / RLS policies | Future |

---

## Next Steps

1. Human reviews this schema and SQL draft.
2. SUPA-002 adds the backend Supabase client with a safe degraded fallback
   (no Supabase = in-memory mode, no crash).
3. SUPA-003 adds the audit writer service that emits to `mellytrade.audit_events`.
4. SUPA-004 exposes GET-only read endpoints backed by the new tables.
5. Human applies the SQL to the Supabase project after review.
