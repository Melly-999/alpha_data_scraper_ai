# MellyTrade Closed Beta Screenshots

## Purpose

These screenshots show the local read-only MellyTrade Closed Beta demo.

They are safe demo screenshots only.

## Safety posture

All screenshots must preserve or imply:

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

## Screenshot inventory

| File | Route | Purpose | Safety notes |
|---|---|---|---|
| `terminal-overview.png` | `/terminal` | Main terminal overview | Shows read-only/dry-run/demo posture |
| `ai-scanner-workspace.png` | `/terminal` | Scanner/advisory workspace | Advisory labels, confidence bar, policy gate |
| `risk-manager-readonly.png` | `/risk` | Risk posture | Read-only risk controls |
| `audit-event-rail.png` | `/audit` | Audit/event visibility | Display-only event rail |
| `broker-status-safe-disconnected.png` | `/brokers` | Broker posture | Safe-disconnected/degraded, no live execution |
| `portfolio-reports-placeholder.png` | `/portfolio` | Placeholder/reporting area | No account IDs, no secrets |

## Capture commands

Captured locally with:

```powershell
.\scripts\start_backend_local.ps1
.\scripts\start_frontend_local.ps1
.\scripts\smoke_local_readonly.ps1 -BaseUrl http://127.0.0.1:8001
```

Browser capture used the local Playwright CLI against `http://127.0.0.1:5173`.

## Do not include

Screenshots must not include:

- secrets
- API keys
- account IDs
- broker credentials
- private financial data
- live broker execution controls
- buy/sell/execute buttons

