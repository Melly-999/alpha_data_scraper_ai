# Browser UI Smoke Checklist

## Purpose

Manual UI smoke checklist for local demo/read-only validation.

## Prerequisites

```powershell
.\scripts\start_backend_local.ps1
.\scripts\start_frontend_local.ps1
.\scripts\smoke_local_readonly.ps1 -BaseUrl http://127.0.0.1:8001
```

Open:

`http://127.0.0.1:5173/terminal`

## Global Safety Checks

- `DEMO DATA` is visible
- `READ ONLY` is visible
- `DRY RUN ACTIVE` is visible
- `LIVE ORDERS BLOCKED` is visible
- no Buy/Sell buttons
- no Execute button
- no Connect Live Broker control
- no editable risk controls
- no mutation action controls

## Backend/API Smoke Prerequisite

- `/health` returns `dry_run=true`
- `/health` returns `auto_trade=false`
- smoke script passes
- scanner preview rows have:
  - `risk_allowed=false`
  - `execution_mode=dry_run_only`
  - `requires_human_review=true`

## Terminal Overview Checklist

- page loads without console errors
- degraded services banner visible when fallback/degraded
- banner pills visible:
  - `DEMO DATA`
  - `MT5 · SYNTHETIC` or degraded equivalent
  - `IBKR · DEGRADED` / `SAFE-DISCONNECTED`
  - `READ ONLY`
  - `DRY RUN ACTIVE`
  - `LIVE ORDERS BLOCKED`
- no buttons/actions in banner

## Audit & Events Checklist

- event rail renders
- event cards or empty state visible
- severity borders visible
- event source/message/time readable
- safety note visible when provided
- no action buttons

## Signal Scanner Checklist

- scanner demo rows visible
- rows are educational/advisory
- actions are safe labels:
  - `WATCH`
  - `HOLD`
  - `LONG_SETUP`
  - `SHORT_SETUP`
  - `NO_TRADE`
- no "buy now" or "sell now" wording
- human review required visible if available

## Risk Manager Checklist

- read-only badge visible
- no Save button
- no Emergency Stop mutation button
- numeric fields read-only
- `auto_trade` / `dry_run` toggles disabled/display-only
- risk values visible

## Broker Status Checklist

- safe-disconnected / degraded status visible
- execution disabled visible
- live orders blocked visible
- no connect-live button
- no broker credential input

## Reports / Portfolio Placeholder Checklist

- placeholder/demo state visible
- no real account IDs
- no secrets
- no profit guarantees
- no personalized investment advice

## Responsive / Browser Checks

- desktop `1366x768`
- desktop `1920x1080`
- no horizontal overflow
- cards readable
- sidebar usable
- event rail not clipped

## Failure Triage

- backend not running on `8001`
- frontend wrong API base URL
- port `5173` occupied
- Supabase degraded is expected locally
- MT5/IBKR disconnected is expected locally
- `graphify-out/` is ignored

## Pass/Fail Template

| Area | Pass/Fail | Notes |
|---|---|---|
| Backend smoke |  |  |
| Terminal overview |  |  |
| Degraded banner |  |  |
| Audit rail |  |  |
| Scanner |  |  |
| Risk Manager |  |  |
| Broker status |  |  |
| Reports/Portfolio |  |  |
| Console errors |  |  |
| Safety controls absent |  |  |

## Safety Confirmation

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```
