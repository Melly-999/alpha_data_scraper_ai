# MellyTrade Frontend (React + Vite)

Decision-support trader dashboard for MellyTrade Direction B. Connects to the mellytrade-api backend for read-only signal data, audit trails, and risk snapshots.

**Safety posture:** Read-only, no execution buttons, dry-run and risk limits locked-on by default.

## Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Environment

Create `.env.local` (git-ignored):

```bash
# Optional: Backend API base URL (default: /melly-api via dev proxy)
VITE_MELLY_API_BASE_URL=/melly-api

# Optional: API authentication key (sent as X-API-Key header)
VITE_MELLY_API_KEY=change-me-local-readonly-key
```

Use `frontend/.env.example` as the placeholder template. Do not commit real
API keys. The dashboard never stores API keys in `localStorage`; Vite reads
`VITE_MELLY_API_KEY` from the local environment at startup/build time.

## Development

### Dev Server with Proxy

```bash
npm run dev
```

Starts Vite dev server on `http://localhost:5173` with automatic proxy to backend:
- Requests to `/melly-api/*` are forwarded to `http://localhost:8000/*`
- Hot module reloading enabled
- Configured in `vite.config.ts`

**Prerequisites:** mellytrade-api backend running on `http://localhost:8000`

### Build

```bash
npm run build
```

Outputs optimized bundle to `dist/`.

### Type Check

```bash
npm run type-check
```

TypeScript validation using tsc (no emit).

## Features (Sprint 1B)

### Pages

- **Dashboard**: System overview (legacy, from Sprint 1A)
- **Signals** (new): Signal feed from both legacy API and mellytrade-api
  - Signal review table: symbol, direction, confidence, MTF alignment, risk status
  - Signal detail drawer: entry/SL/TP levels, reasoning, risk gates
  - **API Signal History** (new): read-only table of mellytrade-api signals with:
    - Time, symbol, action (BUY/SELL/HOLD), raw confidence
    - Clamped confidence [33, 85]%, risk %
    - Status (accepted/rejected), rejection reason
    - Mode: dry-run/read-only indicator pills
    - Symbol + status filters (searchable)
- **Audit Trail** (new): Read-only event feed
  - Signal decisions, risk gate results, safety state changes
  - Event type filter (9 options)
  - Severity-colored badges (info=blue, warning=amber, error=red)
- **Alerts**: Read-only Alert Center v1
  - Safety, risk-gate, cooldown, degraded-backend, and placeholder news alerts
  - Severity and category filters
  - No alert action buttons or mutation calls
- **Positions, Trade Blotter, Risk Manager, MT5 Bridge, Logs, Settings**: Placeholder pages

### Components

- **SafetyBanner** (new): Four locked-on indicators
  - DRY RUN | READ-ONLY MODE | LIVE ORDERS BLOCKED | MAX RISK <= 1%
  - Tooltips and color states (green=safe, red=disabled, muted=error)
  - Mounted in AppShell above TopBar
- **AccessStatusBanner**: Local access state for the Melly API
  - Backend online/offline
  - Missing `VITE_MELLY_API_KEY`
  - 401 unauthorized from protected read-only endpoints
  - Degraded backend safety posture
- **Table**: Generic table with sorting, filtering, row click handlers
- **Card**: Reusable container with title, right-aligned badge
- **Badge**: Status indicator with 5 tones (green, red, amber, blue, muted)
- **Drawer**: Side panel for signal detail, closes on backdrop click

### Hooks (New for Sprint 1B)

All hooks poll their endpoints and cache results:

- **`useMellyHealth()`**: Polls `/health` every 30s
  - Returns: `{ data: HealthInfo, loading, error }`
- **`useMellyRiskConfig()`**: Polls `/risk/config` every 60s
  - Returns: `{ data: RiskConfig, loading, error }`
- **`useAuditFeed(query)`**: Polls `/audit` every 12s
  - Params: `eventType?: string`, `since?: string`, `until?: string`, `limit?: number`
  - Returns: `{ data: AuditFeed, loading, error }`
- **`useMellySignals(query)`**: Polls `/signals` every 15s (NEW)
  - Params: `symbol?: string`, `status?: string`, `since?: string`, `until?: string`, `limit?: number`
  - Returns: `{ data: SignalSummary[], loading, error }`
- **`useAlerts(query)`**: Polls `/alerts` every 12s
  - Params: `limit?: number`
  - Returns: `{ data: AlertItem[], loading, error }`

### API Client

All `lib/mellyApi.ts` requests are GET-only. No mutation helpers are exported.
The client uses a 10s timeout and surfaces explicit messages for backend
offline/unreachable, missing API key, and rejected API key states.

**`lib/mellyApi.ts`:**
- `getHealth()` → HealthInfo
- `getSignals(query)` → SignalSummary[] (bare list, no wrapper, no total field)
- `getAuditFeed(query)` → { events: AuditEvent[], dry_run, read_only, live_orders_blocked }
- `getRiskConfig()` → RiskConfig
- `getAlerts(query)` → AlertItem[]

Authentication is configured with `VITE_MELLY_API_KEY` for protected read-only
endpoints. `GET /health` can still load without a key.

## Type System

### Type Separation

Sprint 1A types are in `src/types/melly.ts` (separate from legacy `src/types/api.ts`):
- `Action` (BUY | SELL | HOLD)
- `HealthInfo`, `SignalSummary`, `RiskConfig`
- `AuditEvent`, `AuditEventType` (9 types)
- `SignalsQuery`, `AuditQuery`

This avoids collision with legacy types (e.g., old `SignalSummary` with different shape).

## Testing

No Jest/Vitest setup yet. Manual smoke test available:

```bash
# Bash/Mac/Linux
bash ../scripts/smoke-test.sh

# Windows (PowerShell)
.\scripts\smoke-test.ps1
```

Smoke test validates:
1. Backend health and safety posture
2. Signal feed endpoint
3. Audit feed endpoint
4. Risk config endpoint
5. Dev proxy (`/melly-api/health`)

## Build & Deployment

### Production Build

```bash
npm run build
```

Output: `dist/` directory, ready for static hosting (Nginx, S3, Vercel, etc.)

### Environment (Production)

Point to production backend via:
```bash
VITE_MELLY_API_BASE_URL=https://api.mellytrade.example.com
VITE_MELLY_API_KEY=prod-secret-key
```

## Architecture

```
frontend/
├── src/
│   ├── pages/             # Page components
│   │   ├── SignalsPage.tsx
│   │   ├── AuditTrailPage.tsx
│   │   └── ...
│   ├── components/        # Reusable components
│   │   ├── SafetyBanner.tsx
│   │   ├── shared/
│   │   │   ├── Badge.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Drawer.tsx
│   │   │   └── Table.tsx
│   │   └── ...
│   ├── hooks/             # Custom hooks
│   │   ├── useMellyHealth.ts
│   │   ├── useMellyRiskConfig.ts
│   │   ├── useAuditFeed.ts
│   │   ├── useMellySignals.ts
│   │   └── ...
│   ├── lib/               # Utilities
│   │   ├── mellyApi.ts    # GET-only client
│   │   ├── api.ts         # Legacy API client
│   │   └── ...
│   ├── types/             # TypeScript definitions
│   │   ├── melly.ts       # Sprint 1A contracts
│   │   ├── api.ts         # Legacy types
│   │   └── ...
│   ├── layout/            # Layout components
│   │   ├── AppShell.tsx
│   │   ├── Sidebar.tsx
│   │   └── TopBar.tsx
│   ├── stores/            # Zustand state
│   │   └── useUiStore.ts
│   ├── index.css          # Global styles
│   ├── App.tsx            # Router
│   └── main.tsx           # Entry point
├── vite.config.ts         # Vite + dev proxy
├── tsconfig.json
├── package.json
└── README.md (this file)
```

## Next Steps (Sprint 1C+)

- [ ] Manual smoke test (run backend + frontend, verify SafetyBanner + API Signal History)
- [ ] Backend tests all pass
- [ ] Frontend build succeeds
- [ ] Consider: alerting, audit log export, authentication/RBAC, Direction C scoping

## Support

See `mellytrade_v3/mellytrade-api/README.md` for backend documentation.
