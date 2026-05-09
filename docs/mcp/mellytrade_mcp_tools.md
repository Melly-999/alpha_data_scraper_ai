# MellyTrade MCP Tools — Reference

**Version:** 1.0.0
**Status:** Planning / Docs-only (Phase 2 not yet implemented)
**Safety class:** READ-ONLY — no write, no execute, no trade
**Last updated:** 2026-05-09

---

## Overview

The MellyTrade MCP (Model Context Protocol) server provides a structured, typed tool interface for AI agents (Claude Code, Codex) to query the state of the MellyTrade development system.

**Operating principle:**
> Every tool in this layer is read-only. No tool may write files, execute trades, place orders, modify configuration, or change any system state. This is enforced at registration time and validated by an automated scan (Phase 2 implementation).

**Default state:** Disabled. The MCP server is not started automatically. It must be launched manually with an explicit command.

**Access:** `localhost` only, or Tailscale private subnet. Never exposed to the public internet.

---

## Posture Summary

| Property | Value |
|---|---|
| Default state | Disabled |
| Binding | `127.0.0.1:8765` (configurable) |
| External access | Tailscale private subnet only |
| Write tools | None (zero registered) |
| Trade/execution tools | None (zero registered) |
| Authentication | Local bearer token (dev use); Tailscale auth (remote) |
| Audit logging | Every tool call logged |
| Rate limiting | 60 calls/min per tool (configurable) |

---

## Allowed Tools

### `mellytrade.status`

**Purpose:** Returns the overall system status summary — a single structured snapshot of the dev system's current health.

| Property | Value |
|---|---|
| Read-only guarantee | Yes — queries only; no side effects |
| Expected input | None (no parameters required) |
| Expected output | `{ backend: up/down, frontend: up/down, dry_run: bool, autotrade: bool, live_orders_blocked: bool, safety_posture: safe/degraded/unknown }` |
| Forbidden side effects | None permitted |
| Audit event emitted | `mcp_tool_called: mellytrade.status` |
| Failure behavior | Returns `{ error: "backend_unreachable" }` with HTTP 200; never raises exception to caller |
| Mobile-safe | Yes — lightweight JSON response; safe to poll every 30s from phone |

---

### `mellytrade.health`

**Purpose:** Returns the backend `/api/health` response, indicating service availability, uptime, and version.

| Property | Value |
|---|---|
| Read-only guarantee | Yes |
| Expected input | None |
| Expected output | `{ status: "ok"\|"degraded", version: str, uptime_s: int, timestamp: ISO8601 }` |
| Forbidden side effects | None |
| Audit event emitted | `mcp_tool_called: mellytrade.health` |
| Failure behavior | Returns `{ status: "unreachable", error: str }` |
| Mobile-safe | Yes |

---

### `mellytrade.logs_tail`

**Purpose:** Returns the last N lines of the backend application log for quick diagnostic review.

| Property | Value |
|---|---|
| Read-only guarantee | Yes — reads log file; does not write or rotate |
| Expected input | `{ lines: int (default 50, max 500) }` |
| Expected output | `{ lines: [str], source: "app.log", truncated: bool }` |
| Forbidden side effects | No log rotation; no file writes; no clearing |
| Audit event emitted | `mcp_tool_called: mellytrade.logs_tail` |
| Failure behavior | Returns `{ error: "log_not_found" }` if log path absent |
| Mobile-safe | Yes — limit to 50 lines for mobile view |

---

### `mellytrade.smoke_test`

**Purpose:** Triggers a read-only smoke test sequence against the local backend, returning pass/fail results for critical endpoints.

| Property | Value |
|---|---|
| Read-only guarantee | Yes — only calls GET endpoints; no state mutation |
| Expected input | `{ endpoints: [str] (optional, defaults to standard suite) }` |
| Expected output | `{ passed: int, failed: int, results: [{ endpoint: str, status: int, ok: bool }] }` |
| Forbidden side effects | No writes, no order placement, no config changes |
| Audit event emitted | `smoke_test_started`, `smoke_passed` or `smoke_failed` |
| Failure behavior | Returns per-endpoint failure detail; never aborts without result |
| Mobile-safe | Yes — summary view suitable for phone |

**Standard smoke test suite:**
```
GET /api/health
GET /api/safety/status
GET /api/audit/events?limit=1
GET /api/mt5/status
```

---

### `mellytrade.audit_events`

**Purpose:** Returns recent audit events from the backend audit feed, filtered by type and time range.

| Property | Value |
|---|---|
| Read-only guarantee | Yes |
| Expected input | `{ limit: int (default 20), event_type: str (optional), since: ISO8601 (optional) }` |
| Expected output | `{ events: [{ id, timestamp, type, actor, detail }], total: int }` |
| Forbidden side effects | None |
| Audit event emitted | `mcp_tool_called: mellytrade.audit_events` |
| Failure behavior | Returns empty list with `{ error: str }` on backend failure |
| Mobile-safe | Yes — limit to 10 for mobile view |

---

### `mellytrade.pr_summary`

**Purpose:** Returns a summary of the current open PRs and branch stack from the local git state and GitHub CLI.

| Property | Value |
|---|---|
| Read-only guarantee | Yes — `gh pr list` read-only; no push/merge |
| Expected input | `{ limit: int (default 10) }` |
| Expected output | `{ prs: [{ number, title, branch, status, draft: bool, checks_passing: bool }] }` |
| Forbidden side effects | No push, no merge, no status change |
| Audit event emitted | `mcp_tool_called: mellytrade.pr_summary` |
| Failure behavior | Returns `{ error: "gh_cli_unavailable" }` if gh CLI not configured |
| Mobile-safe | Yes |

---

### `mellytrade.backend_info`

**Purpose:** Returns structured metadata about the running backend — Python version, FastAPI version, active routes, loaded config (non-secret fields only).

| Property | Value |
|---|---|
| Read-only guarantee | Yes |
| Expected input | None |
| Expected output | `{ python_version, fastapi_version, environment, config: { dry_run, autotrade, read_only, max_risk_pct } }` |
| Forbidden side effects | None; secrets never included in output |
| Audit event emitted | `mcp_tool_called: mellytrade.backend_info` |
| Failure behavior | Returns `{ error: "backend_unreachable" }` |
| Mobile-safe | Yes |

**Secret exclusion rule:** Any config key containing `password`, `secret`, `token`, `key`, or `credential` is stripped from output before returning.

---

### `mellytrade.frontend_status`

**Purpose:** Returns the build and serve status of the React/Vite frontend.

| Property | Value |
|---|---|
| Read-only guarantee | Yes |
| Expected input | None |
| Expected output | `{ vite_running: bool, build_hash: str, last_build: ISO8601, url: "http://localhost:5173" }` |
| Forbidden side effects | None |
| Audit event emitted | `mcp_tool_called: mellytrade.frontend_status` |
| Failure behavior | Returns `{ vite_running: false, error: str }` |
| Mobile-safe | Yes |

---

### `mellytrade.risk_status`

**Purpose:** Returns the current risk posture — all safety flags, thresholds, and validation state. This is a read display only; no flag can be changed through this tool.

| Property | Value |
|---|---|
| Read-only guarantee | Yes — display only |
| Expected input | None |
| Expected output | `{ autotrade: false, dry_run: true, read_only: true, live_orders_blocked: true, max_risk_pct: 0.01, cooldown_active: bool, sl_required: bool, tp_required: bool }` |
| Forbidden side effects | Absolutely none — no write path exists |
| Audit event emitted | `mcp_tool_called: mellytrade.risk_status` |
| Failure behavior | Returns last-known safe defaults if backend unreachable |
| Mobile-safe | Yes — safety posture badge |

---

### `mellytrade.dashboard_state`

**Purpose:** Returns the consolidated state object that the AI Dev Control Center dashboard renders — a single call to hydrate all widgets.

| Property | Value |
|---|---|
| Read-only guarantee | Yes |
| Expected input | None |
| Expected output | See AI Dev Control Center widget spec |
| Forbidden side effects | None |
| Audit event emitted | `dashboard_loaded`, `mcp_tool_called: mellytrade.dashboard_state` |
| Failure behavior | Returns partial state with `degraded: true` flag for failed subsystems |
| Mobile-safe | Yes — optimised for mobile JSON payload |

---

### `mellytrade.mt5_status`

**Purpose:** Returns the MT5 bridge connection status and last heartbeat. Read-only display; no bridge commands.

| Property | Value |
|---|---|
| Read-only guarantee | Yes |
| Expected input | None |
| Expected output | `{ connected: bool, last_heartbeat: ISO8601, bridge_version: str, account_type: "paper"\|"demo"\|"unknown" }` |
| Forbidden side effects | No bridge commands, no reconnect triggers |
| Audit event emitted | `mcp_tool_called: mellytrade.mt5_status` |
| Failure behavior | Returns `{ connected: false, error: str }` |
| Mobile-safe | Yes |

---

### `mellytrade.git_state`

**Purpose:** Returns the local git repository state — current branch, last commit, uncommitted changes, and open PR number if available.

| Property | Value |
|---|---|
| Read-only guarantee | Yes — `git status`, `git log`, `git branch` only; no writes |
| Expected input | None |
| Expected output | `{ branch: str, last_commit: { sha, message, author, timestamp }, dirty: bool, staged: int, unstaged: int, pr_number: int\|null }` |
| Forbidden side effects | No commits, no push, no rebase |
| Audit event emitted | `mcp_tool_called: mellytrade.git_state` |
| Failure behavior | Returns `{ error: "git_not_available" }` if not in git repo |
| Mobile-safe | Yes |

---

## Explicitly Forbidden MCP/Tool Actions

The following tool names **must never exist** in any registered tool list. Any tool with these names or equivalent semantics is rejected at registration time:

| Forbidden Tool Name | Reason |
|---|---|
| `execute_trade` | Would place a live order |
| `place_order` | Would place a live order |
| `close_position` | Would close a live position |
| `cancel_orders` | Would cancel live orders |
| `modify_positions` | Would mutate live positions |
| `enable_autotrade` | Would enable autonomous trading |
| `disable_dry_run` | Would disable dry-run mode |
| `modify_risk_policy` | Would weaken safety constraints |
| `broker_execute` | Would call broker execution API |
| `expose_secrets` | Would leak credentials |
| `modify_credentials` | Would change auth config |
| `change_config_runtime` | Would mutate running config |
| `write_file` | Would write to filesystem |
| `git_push` | Would push to remote |
| `git_commit` | Would commit without human review |
| `git_rebase` | Would rebase without human review |
| `git_merge` | Would merge without human review |

---

## Audit Logging Requirements

Every MCP tool call must produce a structured audit event:

```json
{
  "event_type": "mcp_tool_called",
  "tool": "mellytrade.status",
  "caller": "claude_code",
  "timestamp": "2026-05-09T10:00:00Z",
  "input_hash": "sha256:...",
  "result_code": "ok",
  "duration_ms": 42
}
```

Audit events are:
- Append-only (never deleted by automation)
- Stored in `logs/mcp_audit.jsonl`
- Rotated daily (not deleted — archived)
- Available via `mellytrade.audit_events` tool

---

## Rate Limits

| Tool | Calls/min | Notes |
|---|---|---|
| `mellytrade.status` | 60 | Safe for polling |
| `mellytrade.health` | 60 | |
| `mellytrade.logs_tail` | 20 | Disk I/O throttle |
| `mellytrade.smoke_test` | 6 | Test suite load limit |
| `mellytrade.audit_events` | 30 | |
| `mellytrade.pr_summary` | 10 | GitHub CLI rate limit |
| `mellytrade.backend_info` | 30 | |
| `mellytrade.frontend_status` | 30 | |
| `mellytrade.risk_status` | 60 | High-priority safety read |
| `mellytrade.dashboard_state` | 20 | Heavier aggregation call |
| `mellytrade.mt5_status` | 30 | |
| `mellytrade.git_state` | 20 | Git I/O throttle |

---

## Authentication Recommendations

| Mode | Method |
|---|---|
| Local development | Static bearer token in `.env` (not committed) |
| Tailscale access | Tailscale auth + bearer token |
| CI/CD (future) | GitHub Actions OIDC (no secrets stored) |

Token must be at least 32 bytes of random entropy. Never hardcode in source. Never commit to git.

---

## Tailscale-Only Access Option

When the MCP server is started in Tailscale mode:

1. Bind to Tailscale IP (`100.x.x.x`) rather than `127.0.0.1`
2. Use `tailscale serve` to provide HTTPS termination
3. Phone accesses MCP via `https://<device>.ts.net:8765/`
4. Auth token sent in `Authorization: Bearer <token>` header
5. Tailscale ACLs restrict access to developer devices only

**Never expose MCP server to public internet or port-forward through router.**

---

## Threat Model

| Threat | Mitigation |
|---|---|
| Rogue AI agent calls `execute_trade` | Tool does not exist; registration validation rejects it |
| AI agent reads secrets via `mellytrade.backend_info` | Secret keys stripped at serialisation layer |
| Attacker on LAN calls MCP | MCP binds to `127.0.0.1` only (or Tailscale subnet) |
| Token leaked in logs | Tokens never logged; input hashed in audit events |
| Prompt injection via audit events | Audit events are plain text; AI agent should treat as untrusted |
| Rate abuse (DoS via MCP) | Per-tool rate limits enforced |
| MCP auto-starts on boot | Disabled by default; no systemd/service entry in dev mode |

---

## How to Test Safely

```powershell
# Start MCP server (local only, dev mode)
py -3.11 -m mellytrade_mcp --dev --bind 127.0.0.1 --port 8765

# Verify no write tools registered
py -3.11 -m mellytrade_mcp --list-tools | Select-String "write|execute|trade|order|push|commit|merge|rebase"
# Expected: zero matches

# Call status tool manually
$headers = @{ Authorization = "Bearer $env:MCP_DEV_TOKEN" }
Invoke-RestMethod http://127.0.0.1:8765/tools/mellytrade.status -Headers $headers

# Run tool audit log check
py -3.11 tests/mcp/test_tool_registry.py

# Stop MCP server
# Ctrl+C (no persistent process; safe to kill)
```

---

## Local-Only Mode Checklist

Before starting the MCP server, verify:

- [ ] `MCP_DEV_TOKEN` set in `.env` (not committed)
- [ ] No public port-forward exists for 8765
- [ ] Backend is running (`GET /api/health` returns 200)
- [ ] Tailscale connected if remote access needed
- [ ] `--dev` flag used (enables verbose audit logging, disables external exposure)
- [ ] Tool registry scan passes (zero forbidden tool names)
