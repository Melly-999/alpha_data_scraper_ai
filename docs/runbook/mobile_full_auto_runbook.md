# Mobile Full Auto Runbook — Windows

**Version:** 1.0.0
**Platform:** Windows 11 (PowerShell)
**Status:** Planning / Docs-only
**Last updated:** 2026-05-09
**Safety class:** DEV-OPS — read-only development workflows only

---

## Safety Checklist — Read Before Remote/Mobile Usage

Complete this checklist before using any remote or mobile development workflow:

- [ ] Backend running and healthy (`GET http://localhost:8000/api/health` returns 200)
- [ ] Frontend accessible (`http://localhost:5173` loads in browser)
- [ ] `dry_run=true` confirmed in backend config
- [ ] `autotrade=false` confirmed in backend config
- [ ] `live_orders_blocked=true` confirmed in backend config
- [ ] Tailscale connected on dev machine (green status in tray)
- [ ] Tailscale connected on phone
- [ ] MCP server NOT started unless explicitly needed
- [ ] No uncommitted changes to execution logic (run `git status`)
- [ ] No secrets in any open editor

---

## 1. Backend Startup (Windows — PowerShell)

### 1.1 Standard Start

```powershell
# Navigate to repo
Set-Location "C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start backend (development mode)
py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process ...
```

### 1.2 Verify Backend Health

```powershell
# Quick health check
Invoke-RestMethod http://localhost:8000/api/health

# Safety status check
Invoke-RestMethod http://localhost:8000/api/safety/status

# Expected: dry_run=true, autotrade=false, live_orders_blocked=true
```

### 1.3 Background Start (if needed for parallel work)

```powershell
Start-Process powershell -ArgumentList '-NoExit', '-Command',
    'Set-Location "C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai"; .\.venv\Scripts\Activate.ps1; py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload'
```

---

## 2. Frontend Startup (Windows — PowerShell)

### 2.1 Standard Start

```powershell
# Navigate to frontend directory
Set-Location "C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai\frontend"

# Install dependencies (if first run or after pull)
npm install

# Start Vite dev server
npm run dev

# Expected output:
#   VITE v5.x.x  ready in xxx ms
#   ➜  Local:   http://localhost:5173/
```

### 2.2 Verify Frontend

```powershell
# Check Vite is serving
Invoke-RestMethod http://localhost:5173/
# Expected: HTML content (React app shell)
```

### 2.3 Frontend Build (for production-style testing)

```powershell
npm run build
# Output in: frontend/dist/
# Only run if testing production build; not required for dev
```

---

## 3. Local Health Checks

Run these before remote/mobile work:

```powershell
# 1. Backend health
Invoke-RestMethod http://localhost:8000/api/health | ConvertTo-Json

# 2. Safety status
Invoke-RestMethod http://localhost:8000/api/safety/status | ConvertTo-Json

# 3. Audit events (last 5)
Invoke-RestMethod "http://localhost:8000/api/audit/events?limit=5" | ConvertTo-Json

# 4. Frontend reachable
(Invoke-WebRequest http://localhost:5173/).StatusCode
# Expected: 200

# 5. Run pytest smoke suite (if available)
py -3.11 -m pytest tests/app/ -q --tb=short
```

---

## 4. Dashboard Access from Phone

### 4.1 Prerequisites

- Tailscale installed and signed in on dev machine
- Tailscale installed and signed in on phone (same account)
- Dev machine and phone in same Tailscale network

### 4.2 Find Dev Machine Tailscale IP

```powershell
# Get Tailscale IP
tailscale ip

# Example output: 100.64.0.1
```

### 4.3 Vite Rebind for Tailscale (Frontend)

By default, Vite binds to `localhost`. To access from phone over Tailscale:

```powershell
# Stop current Vite if running (Ctrl+C), then restart with host flag
npm run dev -- --host 0.0.0.0
# OR add to vite.config.ts: server: { host: '0.0.0.0' }
```

**Note:** `0.0.0.0` binds to all interfaces. Tailscale's firewall ensures only VPN devices can reach it. Do not port-forward this through your router.

### 4.4 Backend Rebind for Tailscale

```powershell
# Restart backend bound to 0.0.0.0 (Tailscale-accessible)
py -3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4.5 Access from Phone

```
Frontend:  http://100.64.0.1:5173
Backend:   http://100.64.0.1:8000/api/health
```

Replace `100.64.0.1` with actual Tailscale IP from step 4.2.

---

## 5. Tailscale Private Access Model

| Scenario | How |
|---|---|
| Same room (LAN) | Use `localhost` or LAN IP |
| Phone (same WiFi) | LAN IP works, but Tailscale preferred |
| Phone (mobile data) | Must use Tailscale IP (`100.x.x.x`) |
| Another machine | Must use Tailscale IP |
| Public internet | **Never** — Tailscale only, no port-forward |

**Tailscale security properties:**
- Encrypted WireGuard tunnel between all devices
- No central server sees your traffic
- Access revokable per-device from admin console
- Works behind CGNAT and symmetric NAT

---

## 6. Tailscale Serve (HTTPS on phone)

For HTTPS access from phone (avoids mixed-content browser warnings):

```powershell
# Serve frontend on Tailscale HTTPS
tailscale serve --bg http://localhost:5173

# This creates: https://<machine-name>.ts.net/ → localhost:5173
# Phone accesses via: https://<machine-name>.ts.net/
```

```powershell
# Serve backend API on Tailscale HTTPS (separate port)
tailscale serve --bg --https=8443 http://localhost:8000

# Phone API access: https://<machine-name>.ts.net:8443/api/health
```

```powershell
# Check what's currently served
tailscale serve status

# Stop serving
tailscale serve --https=8443 off
```

---

## 7. Claude Remote Control Workflow

Claude Code can be used as a remote dev assistant from phone via GitHub Mobile or a secondary terminal:

### 7.1 From Phone — GitHub Mobile

1. Open GitHub Mobile
2. Navigate to `alpha_data_scraper_ai` repo
3. Review open PRs (#56, #57, next)
4. Add review comments or approve
5. Check Actions status (if enabled)

### 7.2 From Phone — Claude Code Web

1. Open `claude.ai/code` in phone browser (over Tailscale for security)
2. Connect to running Claude Code session if available
3. Issue commands: "show me the current safety status", "what's in the audit log"
4. Claude Code reads via MCP tools (Phase 2+); no execution

### 7.3 Claude Code Task Delegation Pattern

```
Human (phone) → Claude Code (planner) → Codex task definition → local execution
                                      ↓
                               MCP tool: mellytrade.status
                               MCP tool: mellytrade.git_state
                               MCP tool: mellytrade.risk_status
```

Claude Code never executes arbitrary commands without human-in-the-loop approval.

---

## 8. GitHub Mobile Workflow

### 8.1 Reviewing PRs from Phone

1. Open GitHub Mobile
2. Check PR #56 (Terminal V1 screenshots) — review assets only
3. Check PR #57 (SAFE-001 contract) — verify no execution routes added
4. Add comments, request changes, or approve
5. **Never merge from phone** — merges require desktop review

### 8.2 Checking Actions Status

1. Go to repo → Actions tab
2. If Actions disabled: note blocker (see Section 13)
3. If Actions enabled: check latest workflow run

### 8.3 Branch Review

```
GitHub Mobile → Code → Branches
```
- Check that `main` only receives PRs through review
- Check that `docs/full-auto-ai-dev-system` is ahead of main by docs commits only
- Never force-push from phone

---

## 9. Codex Task Workflow

### 9.1 From Desktop

```powershell
# 1. Pull latest main
git switch main && git pull --ff-only origin main

# 2. Create task branch
git switch -c <branch-name>

# 3. Open Codex with task definition from docs/tasks/codex_task_queue.md
# 4. Codex executes bounded task
# 5. Review diff before staging
git diff --name-only
git diff

# 6. Stage specific files only (NOT git add -A)
git add docs/path/to/specific/file.md

# 7. Local commit
git commit -m "docs(task): <description>"

# 8. Push only with explicit human decision
# git push origin <branch-name>  ← human decision point
```

### 9.2 From Phone (via GitHub Mobile + Claude)

1. Review Codex task queue: `docs/tasks/codex_task_queue.md`
2. Pick next task; note its ID and branch suggestion
3. Open Claude Code session; provide task ID
4. Claude Code initiates task on desktop (if remote session available)
5. Review result on GitHub Mobile before any push

---

## 10. MCP Local Startup (Disabled by Default)

**MCP server is not started automatically. Only start when needed.**

```powershell
# Phase 2+: Start MCP dev server (local only)
Set-Location "C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai"
.\.venv\Scripts\Activate.ps1

# Set dev token (never commit this)
$env:MCP_DEV_TOKEN = "dev-only-replace-me-with-random-token"

# Start MCP server
py -3.11 -m mellytrade_mcp --dev --bind 127.0.0.1 --port 8765

# Verify tool registry (must show zero forbidden tools)
py -3.11 -m mellytrade_mcp --list-tools

# Stop when done: Ctrl+C
```

---

## 11. Smoke Tests

```powershell
# Run standard smoke suite
py -3.11 -m pytest tests/app/ -q --tb=short

# Run safety-specific tests
py -3.11 -m pytest tests/app/test_safety.py -v

# Run OpenAPI forbidden path scan (TEST-001, when implemented)
py -3.11 scripts/openapi_scan.py

# Manual smoke test against live backend
$base = "http://localhost:8000"
foreach ($path in @("/api/health", "/api/safety/status", "/api/audit/events?limit=1")) {
    $resp = Invoke-RestMethod "$base$path"
    Write-Host "$path → OK"
}
```

---

## 12. Rollback Steps

### 12.1 Revert Last Local Commit (docs-only)

```powershell
# Undo last commit, keep changes staged
git reset HEAD~1

# Verify what would be lost
git status

# If all clear, recommit with correction
git add docs/specific/file.md
git commit -m "docs: corrected version"
```

### 12.2 Discard Docs Changes

```powershell
# Discard unstaged changes to a specific file
git checkout docs/path/to/file.md

# Discard all unstaged changes (CAUTION — review first)
git restore docs/
```

### 12.3 Return to Main (clean)

```powershell
git switch main
# If main is dirty (should not happen): investigate before force-clean
git status
```

### 12.4 Emergency Backend Restart

```powershell
# Kill all uvicorn processes
Stop-Process -Name python -Force
# Restart cleanly
py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 13. Troubleshooting

### Problem: GitHub Actions are disabled

**Symptom:** PRs show "Actions disabled" or workflows don't trigger.

**Resolution:**
1. Go to GitHub → Settings → Actions → General
2. Check if Actions are disabled at org/user level
3. If disabled: run local validation instead
   ```powershell
   py -3.11 -m pytest tests/app/ -q
   ```
4. Note in PR description: "Actions disabled at account level; local validation passed"
5. Do NOT modify workflow YAML to work around this

---

### Problem: Backend is down

**Symptom:** `Invoke-RestMethod http://localhost:8000/api/health` fails with connection refused.

**Steps:**
1. Check if uvicorn process is running: `Get-Process python`
2. Check for port conflict: `netstat -ano | findstr :8000`
3. Check logs: `Get-Content logs/app.log -Tail 50`
4. Check `.env` for missing config: `Get-Content .env`
5. Restart: `py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`

---

### Problem: Frontend build fails

**Symptom:** `npm run build` exits with error.

**Steps:**
1. Check Node version: `node --version` (expect v18+)
2. Clear cache: `Remove-Item -Recurse -Force node_modules/.vite`
3. Reinstall: `npm install`
4. Check for TypeScript errors: `npm run type-check` (if script exists)
5. Check for env variable issues: `Get-Content frontend/.env.local`
6. Review error in `npm run build` output — do NOT remove type checks or linting to force pass

---

### Problem: Tailscale device is offline

**Symptom:** Phone cannot reach dev machine Tailscale IP.

**Steps:**
1. Check Tailscale status on dev machine: `tailscale status`
2. Check Tailscale tray icon — should be green
3. Restart Tailscale: `tailscale down && tailscale up`
4. Check admin console for device status: `https://login.tailscale.com/admin/machines`
5. Re-authenticate if expired: `tailscale login`
6. Verify phone Tailscale is also connected (check Tailscale app on phone)

---

### Problem: MCP server not responding

**Symptom:** AI agent cannot reach `http://127.0.0.1:8765`.

**Steps:**
1. Verify MCP server was explicitly started (it does not auto-start)
2. Check process: `Get-Process python | Where-Object { $_.CommandLine -like '*mellytrade_mcp*' }`
3. Check port: `netstat -ano | findstr :8765`
4. Restart MCP: `py -3.11 -m mellytrade_mcp --dev --bind 127.0.0.1 --port 8765`
5. Verify token is set: `$env:MCP_DEV_TOKEN` (not empty)

---

## 14. Post-Session Shutdown

```powershell
# Stop MCP server (if running): Ctrl+C in its terminal

# Stop frontend (Ctrl+C in its terminal)

# Stop backend (Ctrl+C in its terminal)

# Stop Tailscale serve (if active)
tailscale serve off
tailscale serve --https=8443 off

# Verify no processes left
Get-Process python -ErrorAction SilentlyContinue
```

---

## 15. Quick Reference Card

| Task | Command |
|---|---|
| Start backend | `py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload` |
| Start frontend | `npm run dev` (in `/frontend`) |
| Health check | `Invoke-RestMethod http://localhost:8000/api/health` |
| Safety check | `Invoke-RestMethod http://localhost:8000/api/safety/status` |
| Tailscale IP | `tailscale ip` |
| Run tests | `py -3.11 -m pytest tests/app/ -q` |
| Git state | `git status --short && git branch --show-current` |
| Serve dashboard via Tailscale | `tailscale serve --bg http://localhost:5173` |
| Stop Tailscale serve | `tailscale serve off` |
