CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT,
    signal TEXT NOT NULL,
    confidence REAL NOT NULL,
    score INTEGER DEFAULT 0,
    reasons TEXT,
    last_close REAL,
    lstm_delta REAL,
    autotrade_status TEXT,
    raw_payload TEXT
);

CREATE TABLE IF NOT EXISTS equity_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    balance REAL NOT NULL,
    equity REAL NOT NULL,
    profit REAL NOT NULL,
    margin REAL DEFAULT 0,
    free_margin REAL DEFAULT 0,
    drawdown_pct REAL DEFAULT 0,
    daily_pnl_pct REAL DEFAULT 0,
    source TEXT DEFAULT 'mt5'
);

CREATE TABLE IF NOT EXISTS position_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    ticket INTEGER,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    volume REAL NOT NULL,
    price_open REAL,
    price_current REAL,
    sl REAL,
    tp REAL,
    profit REAL DEFAULT 0,
    comment TEXT,
    magic INTEGER
);

CREATE TABLE IF NOT EXISTS risk_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    symbol TEXT,
    signal TEXT,
    confidence REAL,
    status TEXT NOT NULL,
    reason TEXT,
    lot_size REAL DEFAULT 0,
    payload TEXT
);

CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_symbol_created_at ON alerts(symbol, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_equity_created_at ON equity_snapshots(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_positions_created_at ON position_snapshots(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_risk_events_created_at ON risk_events(created_at DESC);
