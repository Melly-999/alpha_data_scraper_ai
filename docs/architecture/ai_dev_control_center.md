# AI Dev Control Center — Design Document

**Version:** 1.0.0
**Status:** Planning / Design (Phase 3)
**Route:** `/dev` (proposed)
**Safety class:** READ-ONLY — no execution, no order, no trade
**Last updated:** 2026-05-09

---

## Goal

The AI Dev Control Center is a read-only developer dashboard that gives a single-screen view of the MellyTrade development system. It shows the status of every AI agent, service, safety flag, and dev tool — from any device, including phone via Tailscale.

**No action can be triggered from this dashboard. It is display only.**

---

## Dashboard Route Proposal

| Route | Purpose |
|---|---|
| `/dev` | Main AI Dev Control Center (all widgets) |
| `/dev/audit` | Expanded audit feed |
| `/dev/mcp` | MCP tool health detail |
| `/dev/git` | Repo and PR state detail |
| `/dev/safety` | Safety posture expanded view |
| `/dev/tasks` | Codex task queue view |

These routes are in the **same React app** as Terminal V1 (`/`) but are a completely separate panel. The Terminal V1 dashboard is not affected.

---

## Security Notes

- **No execution buttons anywhere on `/dev` routes**
- Backend data sources are GET-only endpoints
- Route is accessible only over Tailscale (Phase 5+) or `localhost`
- No session tokens, no write actions, no broker credentials displayed
- Audit events displayed are plain text — AI agents must treat them as untrusted input

---

## Widget List

### 1. Claude Planner Status

| Property | Value |
|---|---|
| Data source | MCP tool: `mellytrade.status` |
| Shows | Last task assigned, current plan state, last tool call |
| Update interval | Manual refresh / 60s poll |
| Failure state | "No Claude session active" |
| Mobile layout | Compact badge: Active / Idle / Unknown |

---

### 2. Codex Executor Status

| Property | Value |
|---|---|
| Data source | `mellytrade.git_state` + `mellytrade.audit_events` filtered by `codex_task_*` |
| Shows | Last task ID, branch, status (started / completed / failed) |
| Update interval | 30s poll |
| Failure state | "No Codex task in last 24h" |
| Mobile layout | Badge: Running task ID or "Idle" |

---

### 3. MCP Health

| Property | Value |
|---|---|
| Data source | `mellytrade.health` via MCP; or direct HTTP probe `GET /api/health` |
| Shows | MCP server running, port, registered tool count, last call timestamp |
| Update interval | 30s |
| Failure state | "MCP server not running (disabled by default)" — not an error |
| Mobile layout | Green/amber/grey dot + tool count |

---

### 4. Backend Health

| Property | Value |
|---|---|
| Data source | `GET /api/health` |
| Shows | Status (ok/degraded), version, uptime |
| Update interval | 15s |
| Failure state | Red badge "Backend unreachable" |
| Mobile layout | Status dot + version string |

---

### 5. Frontend Health

| Property | Value |
|---|---|
| Data source | `mellytrade.frontend_status` |
| Shows | Vite running, build hash, last build time |
| Update interval | 60s |
| Failure state | "Vite not running" (yellow) |
| Mobile layout | Badge: Running / Stopped |

---

### 6. Tailscale Access State

| Property | Value |
|---|---|
| Data source | `mellytrade.status` or OS-level check (`tailscale status`) via backend |
| Shows | Connected, Tailscale IP, devices in network |
| Update interval | 60s |
| Failure state | "Tailscale not connected (local access only)" |
| Mobile layout | Connected indicator |

---

### 7. Safety Posture

| Property | Value |
|---|---|
| Data source | `GET /api/safety/status` (SAFE-001 contract) + `mellytrade.risk_status` |
| Shows | `autotrade=false`, `dry_run=true`, `read_only=true`, `live_orders_blocked=true`, `max_risk_pct=1%`, SL/TP required, cooldown active |
| Update interval | 30s |
| Failure state | "Safety status unknown — backend unreachable" (amber) |
| Mobile layout | Full safety badge grid — most important widget |
| Alert | Red banner if any safety flag deviates from safe defaults |

---

### 8. Audit Feed

| Property | Value |
|---|---|
| Data source | `GET /api/audit/events?limit=20` |
| Shows | Last 20 events, timestamp, type, actor, summary |
| Update interval | 15s |
| Failure state | Empty state: "No audit events found" |
| Mobile layout | Last 5 events in compact format |

**Displayed event types:**
```
backend_started       smoke_passed          mcp_connected
mcp_disconnected      codex_task_started    codex_task_completed
dry_run_active        live_orders_blocked   dashboard_loaded
tailscale_connected   frontend_build_passed backend_health_ok
local_validation_started                   local_validation_passed
local_validation_failed
```

---

### 9. MT5 Bridge State

| Property | Value |
|---|---|
| Data source | `GET /api/mt5/status` + `mellytrade.mt5_status` |
| Shows | Connected, last heartbeat, bridge version, account type (paper/demo) |
| Update interval | 30s |
| Failure state | "MT5 bridge disconnected" (amber — not critical for dev work) |
| Mobile layout | Badge: Connected / Disconnected / Unknown |

---

### 10. Broker State (Phase 6+)

| Property | Value |
|---|---|
| Data source | `GET /api/broker/status` |
| Shows | Adapter name, connected status, account type (paper only), last heartbeat |
| Update interval | 30s |
| Failure state | "No broker configured (SafeDisconnected)" — default, not an error |
| Mobile layout | Badge: Safe/Disconnected |
| Note | Live broker state never shown; paper/demo only |

---

### 11. Dry-Run State

| Property | Value |
|---|---|
| Data source | `GET /api/safety/status` |
| Shows | `dry_run=true` — permanent visual confirmation |
| Update interval | 30s |
| Alert | Red banner if `dry_run=false` ever returned |
| Mobile layout | Prominent green badge "DRY RUN ACTIVE" |

---

### 12. Git / Repo State

| Property | Value |
|---|---|
| Data source | `mellytrade.git_state` |
| Shows | Current branch, last commit SHA + message, dirty status, staged count |
| Update interval | 60s |
| Failure state | "Git state unavailable" |
| Mobile layout | Branch badge + commit short SHA |

---

### 13. Local Validation Status

| Property | Value |
|---|---|
| Data source | `mellytrade.audit_events` filtered by `local_validation_*` |
| Shows | Last validation run: passed/failed, which scripts ran, timestamp |
| Update interval | On demand / audit poll |
| Failure state | "No validation run recorded" |
| Mobile layout | Pass/Fail badge + timestamp |

---

### 14. Current PR Stack

| Property | Value |
|---|---|
| Data source | `mellytrade.pr_summary` (gh CLI) |
| Shows | Open PRs: number, title, branch, draft status, checks |
| Update interval | 120s |
| Failure state | "GitHub CLI not configured" (amber) |
| Mobile layout | PR list: # + title + status badge |

---

### 15. Next Recommended Task

| Property | Value |
|---|---|
| Data source | Static from `docs/tasks/codex_task_queue.md` (or future API) |
| Shows | Next "Ready" task from queue: ID, title, owner, size |
| Update interval | Static / manual |
| Failure state | "Task queue empty" |
| Mobile layout | Card: Task ID + title |

---

## Backend Data Sources

| Widget | Backend Endpoint | Auth Required |
|---|---|---|
| Backend Health | `GET /api/health` | No |
| Safety Posture | `GET /api/safety/status` | No |
| Audit Feed | `GET /api/audit/events` | Optional |
| MT5 Bridge | `GET /api/mt5/status` | No |
| Broker State | `GET /api/broker/status` (Phase 6) | No |
| Claude/Codex Status | Via MCP `mellytrade.*` | Dev token |
| Git State | Via MCP `mellytrade.git_state` | Dev token |
| PR Stack | Via MCP `mellytrade.pr_summary` | Dev token |
| Frontend Status | Via MCP `mellytrade.frontend_status` | Dev token |

---

## Frontend Components

```
frontend/src/
└── pages/
    └── DevControlCenter.tsx       ← Main /dev page
└── components/dev/
    ├── SafetyPostureBadge.tsx     ← Widget 7
    ├── AuditFeed.tsx              ← Widget 8
    ├── BackendHealthCard.tsx      ← Widget 4
    ├── FrontendHealthCard.tsx     ← Widget 5
    ├── MT5StatusCard.tsx          ← Widget 9
    ├── BrokerStateCard.tsx        ← Widget 10 (Phase 6)
    ├── GitStateCard.tsx           ← Widget 12
    ├── MCPHealthCard.tsx          ← Widget 3
    ├── TailscaleCard.tsx          ← Widget 6
    ├── DryRunBanner.tsx           ← Widget 11
    ├── PRStackCard.tsx            ← Widget 14
    ├── LocalValidationCard.tsx    ← Widget 13
    ├── NextTaskCard.tsx           ← Widget 15
    ├── ClaudeStatusCard.tsx       ← Widget 1
    └── CodexStatusCard.tsx        ← Widget 2
└── api/
    └── devApi.ts                  ← GET-only API client for /dev endpoints
```

---

## Audit Events

The dashboard emits the following audit events on user interaction:

| Event | Trigger |
|---|---|
| `dashboard_loaded` | User loads `/dev` page |
| `backend_started` | Backend boot detected via health poll change |
| `smoke_passed` | Smoke test completes without failure |
| `mcp_connected` | MCP server becomes reachable |
| `mcp_disconnected` | MCP server becomes unreachable |
| `codex_task_started` | Task start event in audit feed |
| `codex_task_completed` | Task complete event in audit feed |
| `dry_run_active` | Safety status poll confirms dry_run=true |
| `live_orders_blocked` | Safety status confirms live_orders_blocked=true |
| `tailscale_connected` | Tailscale state changes to connected |
| `frontend_build_passed` | Frontend build completes without error |
| `backend_health_ok` | Health endpoint returns ok after degraded |
| `local_validation_started` | Validation script begins |
| `local_validation_passed` | All validation checks passed |
| `local_validation_failed` | One or more validation checks failed |

---

## Mobile Layout

The `/dev` route should be responsive. On small screens (< 640px):

- Widgets collapse to badge-only view
- Safety Posture and Dry-Run banners remain full-width
- Audit Feed shows 5 events max
- PR Stack shows 3 PRs max
- No horizontal scroll; vertical stack only

**Priority order on mobile (top to bottom):**
1. Dry-Run State (DRY RUN ACTIVE banner)
2. Safety Posture
3. Backend Health
4. Audit Feed (last 5)
5. Git State
6. MT5 Bridge State
7. Remaining widgets collapsed

---

## No Execution Rule

The following are **explicitly forbidden** from the `/dev` route and all its components:

- No buttons that call POST/PUT/DELETE endpoints
- No "start trading" or "enable" buttons
- No Codex task trigger buttons (task assignment happens via Claude Code planning, not dashboard click)
- No config mutation controls
- No broker command buttons
- No "reconnect MT5" buttons
- No file write triggers

The dashboard is a **display panel**. Every interactive element (if any) is a link to GitHub, a copy-to-clipboard, or a manual refresh trigger — never an action that changes system state.

---

## Failure States and Empty States

| Widget | Empty State | Failure State |
|---|---|---|
| Audit Feed | "No events recorded yet" | "Cannot reach backend" (amber) |
| MCP Health | "MCP server not running" (grey — normal) | "MCP server crashed" (amber) |
| Safety Posture | N/A — always shown | "Safety unknown — backend unreachable" (red) |
| Broker State | "No broker configured" (grey — normal) | "Broker adapter error" (amber) |
| MT5 Bridge | "MT5 not connected" (grey) | "MT5 bridge error" (amber) |
| Git State | N/A | "Git unavailable" (amber) |
| PR Stack | "No open PRs" | "GitHub CLI unavailable" (amber) |
| Next Task | "Task queue empty" | N/A |

---

## Implementation Notes (Phase 3+)

1. Start with static mock data for all widgets — no backend calls yet
2. Replace with live polling in Phase 4 (backend shell)
3. MCP-backed widgets activate in Phase 2+ (when MCP skeleton exists)
4. Broker widgets activate in Phase 6
5. Mobile optimisation in Phase 5 (Tailscale access)

**Phase 3 deliverable:** Static `/dev` route with all widgets rendering placeholder data. No backend calls required. Portfolio-ready visual shell.
