-- SUPA-011: Signal decision persistence table
-- Migration: 20260516_signal_decisions.sql
--
-- Persists dry-run signal decisions for audit and replay purposes.
-- This table is strictly read-only and dry-run only at the database level.
-- No live trading, no order placement, no broker execution.
--
-- Safety invariants enforced as CHECK constraints:
--   dry_run      = TRUE  (always — structurally enforced)
--   auto_trade   = FALSE (always — structurally enforced)
--   read_only    = TRUE  (always — structurally enforced)
--   order_placed = FALSE (always — structurally enforced)
--
-- No foreign keys. No broker references. No account IDs. No order IDs.
-- No execution IDs. Persistence is for observability and replay only.

CREATE TABLE IF NOT EXISTS mellytrade.signal_decisions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL    DEFAULT now(),

    -- Signal identity
    symbol          TEXT        NOT NULL,
    direction       TEXT        NOT NULL
                                CHECK (direction IN ('BUY', 'SELL', 'HOLD', 'UNKNOWN')),
    confidence      NUMERIC(5,4) NOT NULL
                                CHECK (confidence >= 0.0 AND confidence <= 1.0),
    strategy        TEXT,
    source          TEXT        NOT NULL    DEFAULT 'scanner',

    -- Risk and decision outcome
    risk_status     TEXT        NOT NULL
                                CHECK (risk_status IN ('pass', 'warn', 'blocked', 'unknown')),
    decision        TEXT        NOT NULL
                                CHECK (decision IN ('dry_run_allowed', 'blocked', 'watch_only', 'no_action')),
    blocked_reason  TEXT,

    -- Audit correlation
    audit_event_id  TEXT,

    -- Safety columns — enforced immutably at the database level
    dry_run         BOOLEAN     NOT NULL    DEFAULT TRUE
                                CHECK (dry_run = TRUE),
    auto_trade      BOOLEAN     NOT NULL    DEFAULT FALSE
                                CHECK (auto_trade = FALSE),
    read_only       BOOLEAN     NOT NULL    DEFAULT TRUE
                                CHECK (read_only = TRUE),
    order_placed    BOOLEAN     NOT NULL    DEFAULT FALSE
                                CHECK (order_placed = FALSE)
);

COMMENT ON TABLE mellytrade.signal_decisions IS
    'Dry-run signal decision log. Persistence for audit and replay purposes only. '
    'dry_run=TRUE, auto_trade=FALSE, read_only=TRUE, order_placed=FALSE are '
    'enforced by CHECK constraints and cannot be overridden. '
    'No execution, no live trading, no broker calls, no order placement.';

COMMENT ON COLUMN mellytrade.signal_decisions.dry_run IS
    'Always TRUE. CHECK constraint prevents any other value.';
COMMENT ON COLUMN mellytrade.signal_decisions.auto_trade IS
    'Always FALSE. CHECK constraint prevents any other value.';
COMMENT ON COLUMN mellytrade.signal_decisions.read_only IS
    'Always TRUE. CHECK constraint prevents any other value.';
COMMENT ON COLUMN mellytrade.signal_decisions.order_placed IS
    'Always FALSE. CHECK constraint prevents any other value.';
COMMENT ON COLUMN mellytrade.signal_decisions.audit_event_id IS
    'Optional reference to a correlated mellytrade.audit_events row. '
    'Not a foreign key — loose coupling for observability only.';

-- Index for the primary access pattern: ordered list by recency, filtered by symbol.
CREATE INDEX IF NOT EXISTS signal_decisions_created_at_idx
    ON mellytrade.signal_decisions (created_at DESC);

CREATE INDEX IF NOT EXISTS signal_decisions_symbol_created_at_idx
    ON mellytrade.signal_decisions (symbol, created_at DESC);
