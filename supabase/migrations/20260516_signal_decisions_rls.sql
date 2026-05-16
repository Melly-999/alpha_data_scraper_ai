-- SUPA-012: Enable Row Level Security on mellytrade.signal_decisions
-- Migration: 20260516_signal_decisions_rls.sql
--
-- Apply AFTER: 20260516_signal_decisions.sql
--
-- SAFETY POSTURE
-- -------------
-- This migration enables RLS on the signal_decisions table, matching the
-- deny-all posture established for every other mellytrade table in SUPA-001.
--
-- With RLS enabled and NO permissive policy defined, the default behaviour is:
--   - All SELECT / INSERT / UPDATE / DELETE from non-privileged roles → DENIED
--   - service_role (backend FastAPI app) → BYPASSES RLS by design (Supabase default)
--   - anon / authenticated frontend roles → DENIED until an explicit policy is added
--
-- WHY NO POLICY HERE
-- ------------------
-- The frontend does NOT read signal_decisions directly. All reads flow through:
--   GET /api/signals/decisions → FastAPI → signal_decision_reader → Supabase (service_role)
-- The frontend does NOT write signal_decisions. All writes flow through:
--   signal_decision_persistence.write_signal_decision() → Supabase (service_role)
--
-- A future authenticated SELECT policy may be added once the auth model is reviewed.
-- DO NOT add a public/anon SELECT policy without a threat model review.
--
-- WHAT THIS CHANGES
-- -----------------
-- Before: signal_decisions is unprotected at the RLS layer (but safety columns
--         and CHECK constraints still enforce dry_run=TRUE, auto_trade=FALSE etc.)
-- After:  signal_decisions has the same RLS posture as all other mellytrade tables.
--
-- SAFETY NOTE
-- -----------
-- This migration contains no execution, order, account, or trading semantics.
-- No broker calls. No live trading. No order placement.
-- signal_decisions stores dry-run audit records ONLY.
-- dry_run=TRUE, auto_trade=FALSE, read_only=TRUE, order_placed=FALSE are enforced
-- by CHECK constraints at the table level and cannot be overridden by any INSERT.

ALTER TABLE mellytrade.signal_decisions ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE mellytrade.signal_decisions IS
    'Dry-run signal decision log. Persistence for audit and replay purposes only. '
    'dry_run=TRUE, auto_trade=FALSE, read_only=TRUE, order_placed=FALSE are '
    'enforced by CHECK constraints and cannot be overridden. '
    'RLS enabled — deny-all default; service_role bypasses RLS per Supabase design. '
    'No direct frontend access. All reads and writes are mediated by FastAPI. '
    'No execution, no live trading, no broker calls, no order placement.';
