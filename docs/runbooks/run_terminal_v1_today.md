# MellyTrade Terminal V1 — Local Runbook

## Purpose

This runbook covers the local demo flow for MellyTrade Terminal V1, including
the read-only Audit/Event Feed endpoint added in the `feature/read-only-audit-feed`
milestone.

All endpoints described here are GET-only. No orders can be placed. No
execution controls are exposed.

---

## Prerequisites

- Backend running on `127.0.0.1:8001`
- Frontend running on `127.0.0.1:5173` (optional for API checks)
- TWS Paper optional — disconnected broker state is safe

Start backend:

```powershell
cd C:\Users\highe\Desktop\alpha_data_scraper_ai-phase1-checkpoint
.\scripts\start_backend_ibkr_paper.ps1
```

Start frontend:

```powershell
.\scripts\start_frontend.ps1
```

---

## Audit/Event Feed

### Endpoint

```
GET http://127.0.0.1:8001/api/terminal/events
```

### PowerShell check

```powershell
Invoke-RestMethod http://127.0.0.1:8001/api/terminal/events
```

### Optional limit parameter

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/api/terminal/events?limit=10"
```

Limit is bounded 1–200. Values outside this range are rejected with HTTP 422.

### Expected safety events

The following event types must always be present in the feed:

| Event type | Severity | Description |
|---|---|---|
| `dry_run_active` | safety | `dry_run=true` — no real orders will be placed |
| `autotrade_disabled` | safety | `autotrade.enabled=false` — automated execution is off |
| `live_orders_blocked` | safety | `supports_live_orders=false` at adapter level |
| `max_risk_cap_verified` | safety | `max_risk_per_trade` cap is enforced |
| `backend_started` | success | FastAPI backend started successfully |
| `read_only_mode_confirmed` | success | System is in read-only observability mode |
| `broker_disconnected` | warning | IBKR Paper not connected — expected without TWS |
| `ibkr_disconnected` | warning | ib_insync not connected or not installed |
| `mt5_disconnected` | warning | MT5 not connected — using fallback/demo data |
| `smoke_pending` | warning | Smoke validation is pending |
| `fallback_data_active` | warning | System is on fixture/demo data |

### Response safety flags

Every response includes:

```json
{
  "dry_run": true,
  "auto_trade": false,
  "read_only": true,
  "degraded": true,
  "fallback": true
}
```

`degraded=true` is the normal state in a local disconnected demo session.
`fallback=true` indicates fixture/demo data is active (expected without live
broker connection).

### What this feed is not

- It is **not** an execution interface.
- It does **not** accept POST, PUT, PATCH, or DELETE.
- It does **not** place, cancel, or modify orders.
- It does **not** reconnect brokers.
- It does **not** change risk settings.
- Degraded/disconnected services shown here are safe — they indicate expected
  local demo state, not system failures.

---

## Other key endpoints

| Route | Purpose |
|---|---|
| `GET /health` | Application liveness |
| `GET /api/health` | Backend health + safety flags |
| `GET /api/broker/health` | Broker adapter health, mode, and live-order status |
| `GET /api/broker/account` | Read-only account snapshot |
| `GET /api/local/checklist` | Local safety checklist |
| `GET /api/terminal/events` | Read-only audit/event feed |

---

## Smoke test

```powershell
.\scripts\smoke_ibkr_paper.ps1
```

Validates `/health`, `/api/health`, `/api/broker/health`, `/api/broker/account`,
and `/api/broker/dry-run-report`. No orders are placed.

---

## Dashboard

Open in browser:

```
http://127.0.0.1:5173/dashboard
```

The dashboard includes:
- Broker Card — shows adapter, mode, port, and `Live orders: BLOCKED`
- Local Demo Checklist — reads from `GET /api/local/checklist`
- **Audit Events** — reads from `GET /api/terminal/events`; shows safety and
  degraded-state events; no order controls

---

## mellytrade_v3 API audit feed (v3 signal pipeline)

The `mellytrade_v3/mellytrade-api` service exposes a standalone read-only
audit/event feed at `GET /events` (no `/api` prefix — this is a separate
service from the dashboard backend).

**Endpoint:**

```
GET http://127.0.0.1:8002/events
```

**PowerShell:**

```powershell
Invoke-RestMethod http://127.0.0.1:8002/events
Invoke-RestMethod "http://127.0.0.1:8002/events?limit=10"
```

**Expected safety events:**

| Event type | Severity | Meaning |
|---|---|---|
| `dry_run_active` | safety | dry_run=true, no orders |
| `autotrade_disabled` | safety | autotrade.enabled=false |
| `live_orders_blocked` | safety | supports_live_orders=false |
| `max_risk_cap_verified` | safety | max_risk_percent ≤ 1% |
| `read_only_mode_confirmed` | success | read-only mode active |
| `backend_started` | success | v3 API started |
| `broker_disconnected` | warning | IBKR Paper not connected (safe) |
| `ibkr_disconnected` | warning | ib_insync not connected (safe) |
| `mt5_disconnected` | warning | MT5 not connected (safe) |
| `smoke_pending` | warning | smoke test not yet run |
| `fallback_data_active` | warning | using fixture/demo data |

**Response safety fields:**

- `dry_run: true`
- `auto_trade: false`
- `read_only: true`
- `degraded: true` (expected — warning events present without live connections)
- `fallback: true` (expected — no live market data)

This feed is **observability only**. It does not place orders, connect brokers,
change configuration, or expose secrets.

---

## Safety invariants

These must always hold during local demo:

- `autotrade.enabled=false`
- `dry_run=true`
- `supports_live_orders=false`
- No order buttons in the dashboard
- No reconnect or execution controls
- MT5 execution path untouched
- Risk settings untouched
