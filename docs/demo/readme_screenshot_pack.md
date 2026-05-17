# README Screenshot Pack

## Purpose

This package documents the safe local screenshots used in the MellyTrade README.

The screenshots are captured from the local read-only demo UI only.

## Prerequisites

Use the local helper scripts:

```powershell
.\scripts\start_backend_local.ps1
.\scripts\start_frontend_local.ps1
.\scripts\smoke_local_readonly.ps1 -BaseUrl http://127.0.0.1:8001
```

Expected smoke posture:

- `dry_run=true`
- `auto_trade=false`
- `read_only=true`
- `supports_live_orders=false`
- `risk_allowed=false`
- `execution_mode=dry_run_only`
- `requires_human_review=true`

## Screenshot list

| File | Route | Notes |
|---|---|---|
| `docs/assets/screenshots/closed-beta/terminal-overview.png` | `/terminal` | Terminal overview with safety banner |
| `docs/assets/screenshots/closed-beta/ai-scanner-workspace.png` | `/terminal` | Scanner workspace with advisory labels and policy gate |
| `docs/assets/screenshots/closed-beta/risk-manager-readonly.png` | `/risk` | Read-only risk posture |
| `docs/assets/screenshots/closed-beta/audit-event-rail.png` | `/audit` | Audit/event visibility |
| `docs/assets/screenshots/closed-beta/broker-status-safe-disconnected.png` | `/brokers` | Safe-disconnected broker posture |
| `docs/assets/screenshots/closed-beta/portfolio-reports-placeholder.png` | `/portfolio` | Placeholder reporting area |

## README usage notes

The README should link to:

- the screenshot pack
- the closed beta disclaimer
- the closed beta limitations
- the browser UI smoke checklist

Keep the README section short and safety-focused.

## Recapture checklist

Before recapturing, verify:

- backend is running on `http://127.0.0.1:8001`
- frontend is running on `http://127.0.0.1:5173`
- smoke checks pass
- the terminal still shows read-only / dry-run posture
- no live account IDs or secrets are visible
- no buy/sell/execute controls are visible

## Safe screenshot rules

- Use localhost only
- Do not use live broker data
- Do not show secrets or account IDs
- Do not capture mutation controls
- Do not fabricate placeholder images
- Reuse the local read-only demo only

