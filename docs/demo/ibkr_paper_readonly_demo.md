# IBKR Paper Read-Only Demo Checklist

This demo shows the current safe IBKR Paper integration path in
MellyTrade. It is a read-only broker observability demo, not live trading
automation and not financial advice.

## Current Scope

- `ibkr-paper` is a paper-only, read-only broker adapter.
- `safe-disconnected` remains the default broker adapter.
- `ibkr-paper` is exposed through the GET-only broker registry endpoints.
- The dashboard shows `ibkr-paper` through the existing display-only
  `BrokerCard`.
- No live trading support is implemented.
- No order placement is implemented.
- No broker credentials are stored in this repo.
- No account IDs are exposed in the registry card.
- No real TWS or IB Gateway connection is required for this demo.

## Safety Posture

The expected safety posture is:

| Safety control | Expected value |
| --- | --- |
| `autotrade` | `false` |
| `dry_run` | `true` |
| `read_only` | `true` |
| `live_orders_blocked` | `true` |
| max risk per trade | `<= 1%` |
| `execution_enabled` | `false` |
| `can_place_orders` | `false` |
| `can_cancel_orders` | `false` |
| `can_modify_orders` | `false` |

There are no execution routes, no order buttons, no connect-live button,
and no broker execution path in this demo.

## Backend Endpoints

The broker registry demo uses only these GET endpoints:

```text
GET /api/brokers
GET /api/brokers/ibkr-paper/status
GET /api/brokers/ibkr-paper/account
GET /api/brokers/ibkr-paper/positions
```

Expected behavior:

- `ibkr-paper` appears in the broker list.
- Status is a safe disconnected state by default, or a mocked read-only
  paper state in tests.
- Account returns a safe zero snapshot by default, or a mocked
  read-only snapshot in tests.
- Positions returns `[]` by default, or mocked read-only positions in
  tests.
- Non-GET methods remain `405`.
- The OpenAPI forbidden path scan remains clean.

## Local Validation

From the repository root:

```powershell
py -3.11 scripts/validate_safety_config.py
powershell -ExecutionPolicy Bypass -File scripts/validate_local.ps1
py -3.11 -m pytest tests/app/ -q
```

If frontend files changed, also run:

```powershell
cd frontend
npm run build
cd ..
```

For this docs-only checklist, the frontend build is not required unless
frontend source files changed.

## Dashboard Demo Flow

1. Start the backend:

   ```powershell
   py -3.11 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
   ```

2. Start the frontend:

   ```powershell
   cd frontend
   npm run dev
   ```

3. Open the dashboard:

   ```text
   http://127.0.0.1:5173/dashboard
   ```

4. Confirm the `Broker registry: safe-disconnected` card is visible.
5. Confirm the `Broker registry: ibkr-paper` card is visible.
6. Confirm the card shows read-only, execution disabled, and live orders
   blocked labels.
7. Confirm there are no order, trade, execute, connect-live, or
   autotrade controls.
8. Confirm there are no credential inputs.
9. Confirm no account ID is displayed.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `ibkr-paper` card is not visible | Verify `origin/main` includes PR #77 and refresh the frontend dev server. |
| Backend not running | Start FastAPI on `127.0.0.1:8001` and reload the dashboard. |
| Frontend shows stale content | Stop Vite, restart `npm run dev`, and hard-refresh the browser. |
| `/api/brokers` is missing `ibkr-paper` | Verify local main includes PR #76 and rerun backend tests. |
| Validation script fails | Stop and inspect the failing safety check before continuing. |
| GitHub Actions are disabled | Use the local validation commands above as the gating evidence. |
| Local `gh` is unauthenticated | Use the GitHub UI or connector flow for PR state; do not bypass review gates. |

## Portfolio Notes

This is a safe read-only broker integration demo. It demonstrates:

- broker abstraction
- typed broker schemas
- safety gates
- GET-only broker endpoints
- frontend broker observability
- no-order-surface testing

It is not financial advice, does not connect to a live broker, and does
not automate live trading.
