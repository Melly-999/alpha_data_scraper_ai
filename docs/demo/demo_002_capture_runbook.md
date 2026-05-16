# DEMO-002 — Screenshot Capture Runbook

Step-by-step guide for producing the MellyTrade Read-Only AI Operations
Layer screenshot pack. All screenshots are **display-only, read-only, and
safe to publish** — no broker credentials are required and no orders are
placed at any point.

Companion docs:
- Per-screenshot requirements: [`demo_screenshot_checklist.md`](demo_screenshot_checklist.md)
- Asset directory: [`../assets/screenshots/README.md`](../assets/screenshots/README.md)
- Demo walkthrough: [`professional_demo_walkthrough.md`](professional_demo_walkthrough.md)
- Architecture: [`../architecture/milestone_100_readonly_ai_ops.md`](../architecture/milestone_100_readonly_ai_ops.md)

---

## Prerequisites

| Requirement | Check |
|---|---|
| Python 3.11 available | `py -3.11 --version` |
| Node.js / npm available | `node --version` |
| Repo at `main` (or a demo branch based on it) | `git rev-parse --short HEAD` |
| Working tree clean | `git status --short` |
| No secrets in any open environment file | Visual check |

No broker connection is required. No Supabase connection is required —
the system degrades gracefully to in-memory seed fixtures.

---

## Step 1 — Validate before capture

Run the safety validation suite before starting. If any step fails, stop
and fix before capturing.

```powershell
# Safety config check
py -3.11 scripts/validate_safety_config.py

# Forbidden route test
py -3.11 -m pytest tests/app/test_openapi_forbidden_paths.py -q

# Safety invariant tests (39 assertions)
py -3.11 -m pytest tests/app/test_safety_invariants.py -q
```

Expected output for all three:

```
OVERALL: PASS  (validate_safety_config.py)
21 passed  (test_openapi_forbidden_paths.py)
39 passed  (test_safety_invariants.py)
```

If any check fails: **stop**. Do not capture screenshots from a broken
or non-compliant state.

---

## Step 2 — Start the backend

```powershell
py -3.11 -m uvicorn app.main:app --reload
```

Wait for the log line:

```
INFO:     Application startup complete.
```

Smoke-check the safety posture before opening the browser:

```powershell
# Health endpoint — confirm dry_run=true, auto_trade=false
Invoke-RestMethod http://localhost:8000/health | ConvertTo-Json

# Risk config — confirm max_risk_per_trade <= 0.01
Invoke-RestMethod http://localhost:8000/api/risk/config | ConvertTo-Json
```

If either response is missing `dry_run=true` or shows `auto_trade=true`:
stop. Do not proceed.

---

## Step 3 — Start the frontend

```powershell
cd frontend
npm run dev
```

Wait for:

```
Local:   http://localhost:5173/
```

Open `http://localhost:5173/dashboard` in a Chromium browser
(Chrome or Edge).

**Browser setup:**
- Window size: 1600×1000 px minimum
- Zoom: 90–100%
- DevTools: **closed**
- Theme: default dark

---

## Step 4 — Pre-capture confirmation

Before taking any screenshot, confirm:

- [ ] Safety banner reads: `DRY RUN · READ-ONLY MODE · LIVE ORDERS BLOCKED · MAX RISK ≤ 1%`
- [ ] No `LIVE` indicator visible anywhere on the page
- [ ] Browser DevTools closed
- [ ] Browser address bar does not contain credentials or tokens
- [ ] Window is sized to at least 1440 px wide

---

## Step 5 — Capture sequence

Follow this order. Detailed visible-element requirements for each shot
are in [`demo_screenshot_checklist.md`](demo_screenshot_checklist.md).

### 5.1 — `01-terminal-ai-workspace.png`

1. Navigate to `http://localhost:5173/dashboard`.
2. Wait for all cards to load (system status, equity curve, activity feed).
3. Hard-refresh: Ctrl+Shift+R.
4. Confirm safety banner is fully visible.
5. Capture the full browser window.
6. Save as `docs/assets/screenshots/01-terminal-ai-workspace.png`.

### 5.2 — `07-demo-overview.png`

1. Navigate to `http://localhost:5173/signals`.
2. Wait for all three cards to load: Signal Review, Decision History, Signal Lifecycle.
3. Set Decision History date range to **ALL** (click ALL chip).
4. Zoom to 80–90% so all three cards are visible in one frame.
5. Do not open any drawer.
6. Capture.
7. Save as `docs/assets/screenshots/07-demo-overview.png`.

### 5.3 — `02-signal-decision-history-filters.png`

1. Still on `http://localhost:5173/signals`, zoom back to 90%.
2. Click the **1H** quick-range chip in the Decision History card.
3. Wait for the freshness label to show `updated HH:MM:SS`.
4. Frame the Decision History card: filter controls, date chips, freshness label, table rows.
5. Capture.
6. Save as `docs/assets/screenshots/02-signal-decision-history-filters.png`.

> Note: if no records fall within the last 1 hour (seed data is time-relative,
> so this depends on when the service started), switch to **4H** or **24H**
> to get visible rows, then note the active chip in the filename caption.

### 5.4 — `05-supabase-status-and-stale-indicators.png`

1. Still on `/signals`, Decision History card.
2. Frame the badge row: `read-only` + `live data`/`seed data` + optional `degraded`.
3. Ensure the freshness label is visible.
4. Capture (crop to the top of the Decision History card if the full page is too busy).
5. Save as `docs/assets/screenshots/05-supabase-status-and-stale-indicators.png`.

### 5.5 — `03-signal-reasoning-panel.png`

1. Still on `/signals`.
2. In the Signal Review table, click a row where `confidence ≥ 80%`.
3. The drawer opens on the right.
4. Scroll down inside the drawer to the **AI Reasoning** panel.
5. If the panel is collapsed, click **Expand**.
6. Confirm both `DRY RUN ONLY` and `READ ONLY` badges are visible.
7. Capture.
8. Save as `docs/assets/screenshots/03-signal-reasoning-panel.png`.

### 5.6 — `04-audit-feed-safety-events.png`

1. Navigate to `http://localhost:5173/audit`.
2. Wait for the event feed to load.
3. Scroll to show rows of type `stale_data_warning`, `scanner_evaluated`,
   and `risk_blocked` together in one frame.
4. Capture.
5. Save as `docs/assets/screenshots/04-audit-feed-safety-events.png`.

### 5.7 — `06-broker-readonly-guardrails.png`

1. Navigate to `http://localhost:5173/risk` (or `/dashboard` if `/risk`
   shows less detail).
2. Frame the risk/safety summary: `dry_run=true`, `auto_trade=false`,
   `read_only=true`, `max_risk_per_trade` value.
3. Capture.
4. Save as `docs/assets/screenshots/06-broker-readonly-guardrails.png`.

---

## Step 6 — Post-capture redaction checklist

Run through this list for **every** screenshot before moving to the commit step:

- [ ] No secrets, API keys, or tokens visible
- [ ] No Supabase `service_role` key values (format: `eyJ…`)
- [ ] No broker account numbers or login credentials
- [ ] No order IDs or execution IDs
- [ ] No personal data (email, name, phone)
- [ ] Safety banner visible and reads correctly
- [ ] No `LIVE` indicator anywhere
- [ ] No text saying an order was placed or executed
- [ ] Browser address bar does not show credentials
- [ ] DevTools closed

If any item fails: crop the screenshot to remove the sensitive area, or
recapture. Do not commit a screenshot that fails any check.

---

## Step 7 — File placement

All screenshots go into:

```
docs/assets/screenshots/
```

Final filenames (exact):

```
01-terminal-ai-workspace.png
02-signal-decision-history-filters.png
03-signal-reasoning-panel.png
04-audit-feed-safety-events.png
05-supabase-status-and-stale-indicators.png
06-broker-readonly-guardrails.png
07-demo-overview.png
```

Do not rename or re-sequence without updating:
- `README.md` (Screenshots section)
- `docs/assets/screenshots/README.md` (inventory table)
- `docs/demo/demo_screenshot_checklist.md` (capture requirements)

---

## Step 8 — README update (after screenshots are captured)

Once all seven screenshots are in `docs/assets/screenshots/`, update the
`README.md` Screenshots table:

1. Change `Status` from `planned` to `captured` for each file.
2. Add the actual markdown image embed below the table:

```markdown
![01 — Terminal AI Workspace](docs/assets/screenshots/01-terminal-ai-workspace.png)
```

Only embed images that are actually committed and verified. Do not embed
planned images (broken image links degrade the repo's public appearance).

---

## Step 9 — Commit screenshots

```powershell
git add docs/assets/screenshots/
git status --short
git commit -m "docs(demo): add milestone 100 screenshot pack (DEMO-002)"
```

Do **not** push until the screenshots have passed the redaction checklist
and at least one other set of eyes has confirmed no sensitive data is
visible.

---

## Safety confirmation

This runbook instructs you to:
- Start the backend in read-only mode
- Open the frontend in a browser
- Take screenshots of public-facing pages
- Save to a docs directory

This runbook does **not** instruct you to:
- Connect to a live broker
- Place any order
- Enable `autotrade`
- Change `dry_run` to `false`
- Expose any secret, token, or credential
- Push to `main`

The system cannot produce a screenshot showing a live executed order
because no such code path exists.

```
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max_risk_per_trade <= 0.01
```
