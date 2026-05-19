# Paper Sandbox — Local Demo Guide (PAPER-003)

Read-only, dry-run-only local demonstration of the MellyTrade paper sandbox
dashboard flow:

```
paper ticket draft → sandbox preview → history/audit → UI ready
```

> **This is a local demo only. It does not place trades, does not execute
> orders, and does not call any real broker.**

---

## What this demo shows

| Panel | Endpoint | What it displays |
|---|---|---|
| Paper Sandbox Preview | `GET /api/paper/sandbox/preview` | Current in-memory paper sandbox state — entry count, entries, safety flags |
| Paper Sandbox Activity / Audit Rail | `GET /api/paper/sandbox/history` | Audit event history — event rows, severity chips, safety contract snapshot |

Both panels are **display-only**. There are no order, buy, sell, execute, or
place-order controls anywhere in the demo flow.

---

## Safety posture

The demo enforces the repository-wide paper safety contract:

| Flag | Value |
|---|---|
| `autotrade.enabled` | `false` |
| `autotrade.dry_run` | `true` |
| `read_only` | `true` |
| `live_orders_blocked` | `true` |
| `max_risk_pct` | `<= 1%` |
| `broker_execution_allowed` | `false` |
| `risk_allowed` | `false` |
| `requires_human_review` | `true` |
| `execution_mode` | `dry_run_only` |

These values are asserted by `scripts/validate_safety_config.py` and the
pytest safety suite on every run.

---

## Prerequisites

- Python 3.11
- Node.js + npm (for the frontend)
- Dependencies installed:
  ```
  pip install -r requirements-ci.txt
  npm install   (run inside frontend/)
  ```

---

## How to start the backend

```powershell
# From repo root
py -3.11 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Backend Swagger UI: `http://127.0.0.1:8001/docs`

---

## How to start the frontend

```powershell
# From repo root
cd frontend
npm run dev -- --port 5174
```

AI Workspace route: `http://127.0.0.1:5174/workspace`

---

## How to run the demo smoke script

**Default (degraded-friendly — offline backend exits 0 with warnings):**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/demo_paper_sandbox_local.ps1
```

**Strict mode (offline backend or endpoint failure exits non-zero):**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/demo_paper_sandbox_local.ps1 -Strict
```

**Custom URLs:**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/demo_paper_sandbox_local.ps1 `
    -BackendBaseUrl http://127.0.0.1:8001 `
    -FrontendUrl http://127.0.0.1:5174/workspace `
    -TimeoutSeconds 10
```

---

## What the script checks

| Step | Check |
|---|---|
| 1 | Local safety config — `validate_safety_config.py` reports OVERALL: PASS |
| 2 | Backend health — `GET /health` (fallback: `GET /api/health`) |
| 3 | Paper sandbox preview — `GET /api/paper/sandbox/preview` + safety flags |
| 4 | Paper sandbox history — `GET /api/paper/sandbox/history` + safety flags |
| 5 | Frontend workspace route — `GET http://127.0.0.1:5174/workspace` |
| 6 | Demo URLs and screenshot checklist printed |
| 7 | Safety posture summary printed |

---

## Expected endpoints

```
GET /api/paper/sandbox/preview
GET /api/paper/sandbox/history
```

Both endpoints are read-only GET routes. No POST, PUT, PATCH, or DELETE
routes are called by this demo.

---

## Expected UI at /workspace

Open `http://127.0.0.1:5174/workspace` and verify:

- **AI Workspace** tab is active
- **Paper Sandbox Preview** panel is visible
- **Paper Sandbox Activity / Audit Rail** panel is visible

---

## Expected safety badges

Both panels display the following safety badges at all times, including
when the backend is offline:

| Badge |
|---|
| `READ ONLY` |
| `DRY RUN` |
| `LIVE ORDERS BLOCKED` |
| `BROKER DISABLED` |
| `HUMAN REVIEW` |

---

## Screenshot checklist

Use this checklist when capturing demo screenshots:

```
[ ] Paper Sandbox Preview panel visible
[ ] Paper Sandbox Activity / Audit Rail panel visible
[ ] Endpoint label: GET /api/paper/sandbox/preview
[ ] Endpoint label: GET /api/paper/sandbox/history
[ ] Safety badge: READ ONLY
[ ] Safety badge: DRY RUN
[ ] Safety badge: LIVE ORDERS BLOCKED
[ ] Safety badge: BROKER DISABLED
[ ] Safety badge: HUMAN REVIEW
[ ] Audit event rows visible (if backend has events)  OR  graceful fallback message
[ ] Zero order / buy / sell / execute / place-order buttons visible
[ ] Safety contract snapshot visible in audit rail
```

---

## Offline / degraded behaviour

If the backend is not running, both panels display a graceful fallback
message:

```
Audit history unavailable
Server returned 404 Not Found
Safety posture is unchanged. No broker execution. History endpoint is
offline or unreachable — advisory mode remains active.
```

The safety badges remain visible. The script exits 0 in non-strict mode.

---

## Safety statement

> This demo is a local, dry-run, read-only demonstration only.
>
> - No broker execution is performed.
> - No MT5 or IBKR connections are made.
> - No live orders are placed.
> - No order, buy, sell, or execute controls exist in the UI.
> - All safety flags (`dry_run`, `read_only`, `live_orders_blocked`, etc.)
>   are enforced at the schema, service, and API layer and verified by the
>   test suite on every CI run.
