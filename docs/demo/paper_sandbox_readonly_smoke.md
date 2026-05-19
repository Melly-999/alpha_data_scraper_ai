# PAPER-003 — Paper Sandbox Read-Only Smoke

This is a local, read-only smoke for the Paper Sandbox Preview and Paper
Sandbox Activity / Audit Rail.

It verifies:

- the backend health endpoint responds
- `GET /api/paper/sandbox/preview` responds
- `GET /api/paper/sandbox/history` responds
- the responses keep the safety posture locked to:
  - `autotrade=false`
  - `dry_run=true`
  - `read_only=true`
  - `live_orders_blocked=true`
  - `max risk <= 1%`
- the frontend terminal routes still render

No mutating request is made. The smoke is GET-only.

---

## Start backend

From the repository root:

```powershell
py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Or use the helper:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
```

Health is probed at both:

- `GET /api/health`
- `GET /health`

The smoke accepts either route.

---

## Start frontend

From the repository root:

```powershell
cd frontend
npm run dev
```

Or use the helper:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_frontend.ps1
```

The default dev server is expected at:

- `http://127.0.0.1:5173`

---

## Run the smoke

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\demo_paper_sandbox_readonly_smoke.ps1
```

Optional frontend skip:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\demo_paper_sandbox_readonly_smoke.ps1 -SkipFrontend
```

Optional alternate ports:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\demo_paper_sandbox_readonly_smoke.ps1 `
  -BackendBaseUrl http://127.0.0.1:8001 `
  -FrontendBaseUrl http://127.0.0.1:5174
```

---

## Expected PASS output

The script should print PASS lines for:

- backend health reachable
- health status `ok`
- safety fields present and locked
- paper sandbox preview reachable
- paper sandbox history reachable
- frontend `/` and `/terminal` when frontend checks are enabled

At the end it should print:

```text
RESULT: PASS
```

---

## Troubleshooting

### Backend offline

If the backend is not running, the script prints a clear start command and
exits non-zero.

Start it first, then rerun the smoke.

### Frontend port busy

If `5173` is already occupied, Vite may choose another port.

Either:

- start Vite with a fixed port, or
- rerun the smoke with `-FrontendBaseUrl` set to the actual port

### Endpoint unreachable

If preview or history fails:

- confirm the backend is on `127.0.0.1:8001`
- confirm the repo is on the updated main branch
- confirm the paper sandbox endpoints are present

---

## Safety contract

This smoke stays inside the read-only paper sandbox contract.

- GET-only checks only
- no POST
- no PUT
- no PATCH
- no DELETE
- no broker execution
- no live trading UX
- no order buttons
- no connect-live UX
- no autotrade toggle
- no dry-run disabling control
- no secrets or account IDs
- max risk remains at or below `1%`

The smoke is intended for reviewer verification after frontend or backend
changes that affect Paper Sandbox Preview or the Audit Rail.
