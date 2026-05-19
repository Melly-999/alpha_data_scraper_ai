# DEMO-002 Screenshot Pack

This pack captures the current MellyTrade Terminal as a **read-only,
institutional-style demo surface** after:

- PR #156 red-black terminal frame polish
- PR #158 Paper Sandbox Activity / Audit Rail
- PR #159 / PAPER-003 local read-only demo smoke script

It is intended for portfolio, GitHub README, LinkedIn, and reviewer
materials. It documents what to capture and what must be visible in each
shot.

## What this pack demonstrates

- red-black institutional terminal frame
- AI Workspace
- Paper Sandbox Preview
- Paper Sandbox Activity / Audit Rail
- read-only broker and safety posture
- GET-only paper sandbox smoke flow

## Local setup

Start the backend:

```powershell
py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Start the frontend:

```powershell
cd frontend
npm run dev
```

Run the read-only smoke script:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/demo_paper_sandbox_readonly_smoke.ps1 -BackendBaseUrl http://127.0.0.1:8001 -FrontendBaseUrl http://127.0.0.1:5173
```

If Vite selects a different port, use the displayed localhost URL.

## Screenshot checklist

Use the following capture order when assembling the pack:

1. `/`
2. `/terminal`
3. `/signals`
4. `/brokers`
5. `/portfolio`

### Required viewport

- `1366x768`
- optional `1920x1080`

### What to verify per screenshot

- no horizontal overflow
- safety badges visible
- no order, buy, sell, or execute controls
- no broker execution controls
- no live trading UX
- Paper Sandbox Preview visible where applicable
- Activity / Audit Rail visible where applicable
- red-black frame visible but not overpowering

### Suggested filenames

- `01_terminal_ai_workspace_1366x768.png`
- `02_terminal_paper_sandbox_preview_1366x768.png`
- `03_terminal_activity_audit_rail_1366x768.png`
- `04_signals_readonly_1366x768.png`
- `05_brokers_readonly_1366x768.png`
- `06_portfolio_readonly_1366x768.png`

## Troubleshooting

### Backend offline

If the backend is not running, start it with the command above and rerun
the smoke script before capturing.

### Frontend port changed to 5174

Vite may bind to `5174` if `5173` is busy. That is fine. Use the URL
printed by the dev server and pass it to the smoke script.

### Vite warnings

Standard Vite dev warnings are acceptable.

### React Router future-flag warnings

These warnings are expected in local dev and do not block screenshot
capture.

## Redaction reminder

Do not capture or publish:

- secrets
- API keys
- tokens
- account IDs
- broker credentials
- order IDs
- execution IDs
- live trading indicators

The terminal remains read-only and safe to publish only if the safety
banner and prohibition cues are visible.
