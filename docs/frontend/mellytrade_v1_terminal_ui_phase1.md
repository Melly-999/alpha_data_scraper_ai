# MellyTrade V1 Terminal UI Phase 1

## Implemented

- Vite/React/TypeScript terminal app under `frontend/`.
- Route: `/terminal` with `/` redirecting to `/terminal`.
- Terminal shell with top market ticker, left sidebar, right news rail, bottom status bar, and dense command-center panels.
- Boot/loading panel with safety posture checks.
- Global safety badges: `READ ONLY`, `DRY RUN`, `AUTO TRADE OFF`, `LIVE ORDERS BLOCKED`.
- Market overview grid, AI signal preview, risk guardrails, audit events preview, and IBKR Paper read-only broker card.
- GET-only terminal API client with safe fallback data.

## API Mapping

The terminal client calls only GET endpoints:

- `GET /api/terminal/summary`
- `GET /api/market/overview`
- `GET /api/watchlist`
- `GET /api/signals/feed`
- `GET /api/risk/status`
- `GET /api/risk/policy`
- `GET /api/backtest/summary`
- `GET /api/news/sentiment`
- `GET /api/positions`
- `GET /api/mt5/status`
- `GET /api/terminal/events`

If a request fails, the UI displays degraded read-only fallback data.

## Safety Constraints

- No live trading was added.
- No order execution UI was added.
- No order forms, execution buttons, or live trading toggles were added.
- The frontend terminal API client uses `fetch` with `method: "GET"` only.
- IBKR is represented as Paper, read-only, execution disabled, and degraded first.
- Orders and live execution are shown as denied in the permission grid.

## Running Locally

Backend:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173/terminal
```

Optional API base URL:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8001 npm run dev
```

## Known Gaps

- Planned IBKR endpoints are not required for this phase and are not called.
- This phase does not include browser-driven visual regression tests.
- No frontend test framework is configured yet.

## Phase 2 Recommendations

- Add Vitest and React Testing Library for component safety checks.
- Add backend schema contracts for terminal responses.
- Add read-only IBKR paper status endpoints and wire them into the broker card.
- Add Playwright smoke checks for `/terminal` once the frontend test stack is standardized.
