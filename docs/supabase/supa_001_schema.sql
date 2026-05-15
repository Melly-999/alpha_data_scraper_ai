-- =============================================================================
-- SUPA-001: MellyTrade Supabase Audit & Scanner Schema Foundation
-- =============================================================================
-- Safety class : READ-ONLY / DRY-RUN / ADVISORY
-- Status       : DRAFT — not yet applied to remote Supabase project
-- Branch       : feature/supa-001-audit-schema
-- Last updated : 2026-05-15
--
-- IMPORTANT SAFETY NOTES
-- -----------------------------------------------------------------------
-- 1. This schema contains NO order, trade, execution, or live-trading tables.
-- 2. All write-facing columns carry CHECK constraints enforcing safe defaults:
--      read_only = true
--      execution_mode = 'dry_run_only'
--      risk_allowed = false
--      requires_human_review = true
-- 3. RLS must be enabled before any production deployment (see below).
-- 4. The service_role key must NEVER be sent to the frontend.
-- 5. No credential, account_id, api_key, secret, or token columns exist here.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- Schema
-- ---------------------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS mellytrade;


-- ---------------------------------------------------------------------------
-- Table: mellytrade.audit_events
--
-- Persists audit events emitted by backend services.
-- Advisory and read-only — no execution or trading semantics.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS mellytrade.audit_events (
    id          uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at  timestamptz   NOT NULL DEFAULT now(),
    event_type  text          NOT NULL,
    severity    text          NOT NULL
                              CHECK (severity IN ('info', 'success', 'warning', 'error', 'safety')),
    source      text          NOT NULL,
    message     text          NOT NULL,
    metadata    jsonb,

    -- Safety invariants — these columns must always be true.
    -- A CHECK constraint makes them structurally enforced at the DB level.
    read_only   boolean       NOT NULL DEFAULT true CHECK (read_only = true),
    dry_run     boolean       NOT NULL DEFAULT true CHECK (dry_run = true)
);

-- RLS: must be enabled before production use.
-- With no permissive policy the default is deny-all (safe).
ALTER TABLE mellytrade.audit_events ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE mellytrade.audit_events IS
    'Read-only audit event feed. No trading or execution data. '
    'read_only and dry_run columns are structurally enforced true. '
    'RLS enabled — no public policy defined until auth model is finalised.';


-- ---------------------------------------------------------------------------
-- Table: mellytrade.scanner_runs
--
-- One row per invocation of the read-only signal scanner.
-- Dry-run only — no live execution semantics.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS mellytrade.scanner_runs (
    id             uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at     timestamptz NOT NULL DEFAULT now(),
    source         text        NOT NULL DEFAULT 'scanner',
    symbols        text[]      NOT NULL DEFAULT '{}',

    -- Safety invariants
    read_only      boolean     NOT NULL DEFAULT true  CHECK (read_only = true),
    execution_mode text        NOT NULL DEFAULT 'dry_run_only'
                               CHECK (execution_mode = 'dry_run_only'),

    status         text        NOT NULL DEFAULT 'pending'
                               CHECK (status IN ('pending', 'running', 'complete', 'error')),
    metadata       jsonb
);

ALTER TABLE mellytrade.scanner_runs ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE mellytrade.scanner_runs IS
    'Dry-run-only scanner run log. execution_mode is structurally locked to '
    'dry_run_only. No execution routes, no broker connections. '
    'RLS enabled — deny-all until auth model finalised.';


-- ---------------------------------------------------------------------------
-- Table: mellytrade.scanner_results
--
-- One row per symbol signal produced by a scanner run.
-- Advisory only: risk_allowed = false, requires_human_review = true,
-- execution_mode = dry_run_only are structurally enforced.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS mellytrade.scanner_results (
    id                    uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    -- FK to scanner_runs.id; nullable until FK is enforced in production
    run_id                uuid,
    created_at            timestamptz   NOT NULL DEFAULT now(),
    symbol                text          NOT NULL,
    -- action is advisory only (e.g. BUY_SIGNAL, SELL_SIGNAL, HOLD)
    -- No execution path reads this column.
    action                text          NOT NULL,
    confidence            numeric(5,2)  NOT NULL DEFAULT 0
                                        CHECK (confidence >= 0 AND confidence <= 100),
    reason                text          NOT NULL DEFAULT '',
    source                text          NOT NULL DEFAULT 'scanner',
    metadata              jsonb,

    -- Safety invariants — structurally enforced at DB level.
    risk_allowed          boolean       NOT NULL DEFAULT false CHECK (risk_allowed = false),
    execution_mode        text          NOT NULL DEFAULT 'dry_run_only'
                                        CHECK (execution_mode = 'dry_run_only'),
    requires_human_review boolean       NOT NULL DEFAULT true  CHECK (requires_human_review = true)
);

ALTER TABLE mellytrade.scanner_results ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE mellytrade.scanner_results IS
    'Advisory-only scanner signals. risk_allowed is structurally false. '
    'requires_human_review is structurally true. execution_mode is locked to '
    'dry_run_only. No execution routes, no broker connections. '
    'RLS enabled — deny-all until auth model finalised.';


-- ---------------------------------------------------------------------------
-- Table: mellytrade.agent_tasks
--
-- Task queue for AI dev agents (Codex, Claude Code).
-- Read-only tracking — no execution semantics.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS mellytrade.agent_tasks (
    id                    uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at            timestamptz NOT NULL DEFAULT now(),
    updated_at            timestamptz NOT NULL DEFAULT now(),
    agent_name            text        NOT NULL,
    task_type             text        NOT NULL,
    title                 text        NOT NULL,
    status                text        NOT NULL DEFAULT 'planned'
                                      CHECK (status IN
                                          ('planned', 'ready', 'in_progress', 'done', 'blocked')),
    priority              text        NOT NULL DEFAULT 'p1'
                                      CHECK (priority IN ('p0', 'p1', 'p2', 'p3')),
    metadata              jsonb,

    -- Safety invariants
    read_only             boolean     NOT NULL DEFAULT true CHECK (read_only = true),
    requires_human_review boolean     NOT NULL DEFAULT true CHECK (requires_human_review = true)
);

ALTER TABLE mellytrade.agent_tasks ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE mellytrade.agent_tasks IS
    'AI dev agent task tracking. read_only and requires_human_review are '
    'structurally enforced true. No execution or trading semantics. '
    'RLS enabled — deny-all until auth model finalised.';


-- ---------------------------------------------------------------------------
-- Table: mellytrade.system_health_snapshots
--
-- Periodic snapshots of component health for the dev dashboard.
-- Read-only — no execution semantics.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS mellytrade.system_health_snapshots (
    id         uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    component  text        NOT NULL,
    status     text        NOT NULL
               CHECK (status IN ('ok', 'degraded', 'error', 'unknown')),
    message    text        NOT NULL DEFAULT '',
    metadata   jsonb,

    -- Safety invariant
    read_only  boolean     NOT NULL DEFAULT true CHECK (read_only = true)
);

ALTER TABLE mellytrade.system_health_snapshots ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE mellytrade.system_health_snapshots IS
    'Read-only system health snapshots for dev dashboard. read_only is '
    'structurally enforced true. RLS enabled — deny-all until auth model finalised.';


-- =============================================================================
-- RLS POLICY NOTES (policies are NOT created here — see SUPA-001 doc)
-- =============================================================================
--
-- All tables have RLS enabled. No permissive policies are defined in this
-- migration. The default Supabase behaviour with RLS enabled and no policy
-- is deny-all, which is the correct safe posture until the auth model exists.
--
-- When adding policies in a future migration:
--
--   Backend service writes (INSERT/UPDATE):
--     CREATE POLICY "backend_service_write" ON mellytrade.<table>
--       AS PERMISSIVE FOR INSERT
--       TO service_role        -- never send service_role to frontend
--       USING (true);
--
--   Frontend reads (SELECT) — only after auth model reviewed:
--     CREATE POLICY "authenticated_read" ON mellytrade.<table>
--       AS PERMISSIVE FOR SELECT
--       TO authenticated
--       USING (true);
--
--   Public (anon) access: DO NOT grant until threat model reviewed.
--
-- =============================================================================
-- END OF SUPA-001 SCHEMA DRAFT
-- Apply only after human review. Do not apply automatically.
-- =============================================================================
