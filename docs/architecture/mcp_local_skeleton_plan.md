# MCP Local Skeleton — Implementation Plan

**Version:** 1.0.0
**Status:** Planning only — do not implement until Phase 2
**Safety class:** READ-ONLY — no execution tools permitted
**Last updated:** 2026-05-09

> **This document is the implementation plan only. The skeleton does not exist yet.**
> Implementation begins in Phase 2. No code is written during Phase 0 or Phase 1.

---

## 1. Suggested Folder Structure

```
alpha_data_scraper_ai/
└── mellytrade_mcp/
    ├── __init__.py          ← Package marker
    ├── __main__.py          ← Entry point: py -3.11 -m mellytrade_mcp
    ├── config.py            ← Config loader (no secrets at import time)
    ├── registry.py          ← Tool registry + startup validator
    ├── server.py            ← MCP server runner (FastAPI or raw HTTP)
    ├── audit.py             ← Audit log writer
    └── tools/
        ├── __init__.py
        ├── status.py        ← mellytrade.status
        ├── health.py        ← mellytrade.health
        ├── logs_tail.py     ← mellytrade.logs_tail
        ├── smoke_test.py    ← mellytrade.smoke_test
        ├── audit_events.py  ← mellytrade.audit_events
        ├── pr_summary.py    ← mellytrade.pr_summary
        ├── backend_info.py  ← mellytrade.backend_info
        ├── frontend_status.py ← mellytrade.frontend_status
        ├── risk_status.py   ← mellytrade.risk_status
        ├── dashboard_state.py ← mellytrade.dashboard_state
        ├── mt5_status.py    ← mellytrade.mt5_status
        └── git_state.py     ← mellytrade.git_state
```

**Why a separate package?** Keeps the MCP server fully isolated from the main FastAPI app. It is an independent process that queries the backend via HTTP — not a module imported by the trading app.

---

## 2. Module Layout

### `__main__.py`

Entry point. Handles CLI arguments:

```
--dev            Enable verbose logging; bind to 127.0.0.1 only
--bind <host>    Override bind host (default: 127.0.0.1)
--port <port>    Override port (default: 8765)
--list-tools     Print registered tool names and exit (no server started)
--validate       Run registry validator and exit
```

### `config.py`

Loads configuration from environment variables only (no hardcoded values, no config files committed). Keys:

```
MCP_BIND_HOST       default: 127.0.0.1
MCP_PORT            default: 8765
MCP_BACKEND_URL     default: http://127.0.0.1:8000
MCP_DEV_TOKEN       required; loaded from .env (not committed)
MCP_LOG_PATH        default: logs/mcp_audit.jsonl
MCP_RATE_LIMIT      default: 60 (calls/min per tool)
```

**Secret loading rule:** Config never reads secrets at import time. Secrets are loaded on server start only, after auth middleware is registered.

### `registry.py`

The tool registry does two things:

1. **Registration:** Collects all tool handler functions and maps them to tool names.
2. **Startup validation:** Before the server starts, it scans registered tool names against the forbidden list and raises `ValueError` if any match is found.

```python
FORBIDDEN_TOOL_NAMES = {
    "execute_trade", "place_order", "close_position",
    "cancel_orders", "modify_positions", "enable_autotrade",
    "disable_dry_run", "modify_risk_policy", "broker_execute",
    "expose_secrets", "modify_credentials", "change_config_runtime",
    "write_file", "git_push", "git_commit", "git_rebase", "git_merge",
}
```

This validation runs at startup and on `--validate`. Server does not start if validation fails.

### `audit.py`

Writes structured JSONL audit events. Rules:
- Append-only file open (`mode='a'`)
- Never truncates or deletes entries
- Rotates daily by creating dated files (e.g., `mcp_audit.2026-05-09.jsonl`)
- Never logs bearer token values; only logs presence/absence

---

## 3. Read-Only Tool Contract

Every tool implementation must satisfy this contract:

```python
class ReadOnlyToolContract:
    """
    A valid MCP tool must:
    1. Accept structured input (dict or None)
    2. Return structured output (dict)
    3. Never write to filesystem (except audit log, via audit.py)
    4. Never call broker execution APIs
    5. Never modify runtime config
    6. Never expose secret values in output
    7. Never raise an uncaught exception — return error dict instead
    8. Log an audit event for every call
    """
```

Tools are pure query functions. They call existing backend endpoints via HTTP GET, read files (read-only), or run read-only shell commands (`git status`, `git log`).

---

## 4. Disabled-by-Default Configuration

The MCP server **must not** start automatically. Required design choices:

| Requirement | Implementation |
|---|---|
| No systemd/Windows service entry | Do not add any auto-start config |
| No import-time server start | `server.py` only starts when `__main__.py` is invoked |
| No background thread in main app | MCP is a separate process, not a thread |
| No `startup.ps1` that starts MCP | Runbook explicitly says "start manually" |

Default config in `config.py` reflects this:
```python
MCP_AUTOSTART = False  # Never set to True in code
```

---

## 5. Logging Plan

| Log file | Content | Retention |
|---|---|---|
| `logs/mcp_audit.jsonl` | All tool calls: name, input hash, result code, duration | 30 days |
| `logs/mcp_server.log` | Server lifecycle: start, stop, errors | 7 days |
| `logs/mcp_registry.log` | Tool registration events, validation results | 7 days |

Log format for audit events:
```json
{
  "ts": "2026-05-09T10:00:00.000Z",
  "event": "mcp_tool_called",
  "tool": "mellytrade.status",
  "caller_hint": "claude_code",
  "input_hash": "sha256:abc123...",
  "result_code": "ok",
  "duration_ms": 42,
  "error": null
}
```

---

## 6. Audit Plan

Every tool call must emit:
1. `mcp_tool_called` event to `logs/mcp_audit.jsonl`
2. Optional: forward to backend `POST /api/audit/events` (if backend is running)

Backend forwarding is best-effort: if the backend is down, the local JSONL log is the source of truth.

---

## 7. Local-Only Networking

| Scenario | Config | Notes |
|---|---|---|
| Standard dev | `--bind 127.0.0.1` | Loopback only; not reachable from LAN or phone |
| Tailscale access | `--bind 100.x.x.x` (Tailscale IP) | Only accessible from Tailscale devices |
| Testing with Tailscale Serve | Use `tailscale serve --bg http://127.0.0.1:8765` | Tailscale handles HTTPS |

**Never bind to `0.0.0.0` without Tailscale ACLs in place.**

---

## 8. Authentication

| Mode | Method | Notes |
|---|---|---|
| Local dev | `Authorization: Bearer <MCP_DEV_TOKEN>` | Token set in `.env`, not committed |
| Remote (Tailscale) | Same bearer token + Tailscale device auth | Layered: Tailscale filters, then bearer token |
| No auth (disabled) | Not supported | Always require token, even in dev |

Token validation middleware runs before any tool handler. Invalid or missing token → HTTP 401. The token value is never logged.

---

## 9. Tailscale Exposure Rules

| Rule | Details |
|---|---|
| Bind IP | Tailscale subnet IP (`100.x.x.x`) or loopback |
| Port | 8765 (default); not port-forwarded through router |
| HTTPS | Via `tailscale serve`; plain HTTP never exposed externally |
| ACLs | Tailscale admin ACLs restrict to developer-tagged devices only |
| Token rotation | Bearer token rotated monthly; stored in `.env` |

---

## 10. Tests

| Test file | What it tests |
|---|---|
| `tests/mcp/test_tool_registry.py` | Registry contains only allowed tools; forbidden names rejected |
| `tests/mcp/test_status_tool.py` | `mellytrade.status` returns correct structure; no side effects |
| `tests/mcp/test_risk_status_tool.py` | `mellytrade.risk_status` returns `dry_run=true`; never returns wrong values |
| `tests/mcp/test_audit.py` | Audit events written; no token values in log |
| `tests/mcp/test_auth.py` | Missing token → 401; wrong token → 401; correct token → 200 |
| `tests/mcp/test_rate_limit.py` | Rate limit enforced; excess calls return 429 |
| `tests/mcp/test_no_write_tools.py` | Confirms no write/execute tool names in registry |

---

## 11. Smoke Test

After server starts, run automated smoke test:

```powershell
# Verify server is up
Invoke-RestMethod http://127.0.0.1:8765/health -Headers @{ Authorization = "Bearer $env:MCP_DEV_TOKEN" }

# Verify tool list
$tools = Invoke-RestMethod http://127.0.0.1:8765/tools -Headers @{ Authorization = "Bearer $env:MCP_DEV_TOKEN" }
Write-Host "Registered tools: $($tools.Count)"

# Verify no forbidden tools
$forbidden = @("execute_trade","place_order","close_position","cancel_orders","modify_positions","enable_autotrade","disable_dry_run","modify_risk_policy","broker_execute","write_file","git_push","git_commit","git_rebase","git_merge")
foreach ($name in $forbidden) {
    if ($tools.name -contains $name) {
        Write-Error "FORBIDDEN TOOL REGISTERED: $name"
        exit 1
    }
}
Write-Host "No forbidden tools found — OK"

# Call status tool
Invoke-RestMethod http://127.0.0.1:8765/tools/mellytrade.status -Headers @{ Authorization = "Bearer $env:MCP_DEV_TOKEN" }
```

---

## 12. How to Verify No Write Tools Exist

At startup (`registry.py`):
```python
for tool_name in registered_tools:
    if tool_name in FORBIDDEN_TOOL_NAMES:
        raise ValueError(f"Forbidden tool registered: {tool_name}")
```

In tests (`test_no_write_tools.py`):
```python
def test_no_forbidden_tools_registered():
    registry = get_tool_registry()
    for name in registry.tool_names():
        assert name not in FORBIDDEN_TOOL_NAMES, f"Forbidden tool found: {name}"
```

In CI (when Actions re-enabled):
```yaml
- run: py -3.11 -m mellytrade_mcp --validate
```

---

## 13. How to Verify No Trading/Execution Tools Exist

Secondary scan using regex pattern on tool source files:

```powershell
# Scan for execution-related code in MCP tool files
Select-String -Path mellytrade_mcp/tools/*.py -Pattern "place_order|execute_trade|close_position|cancel_order|modify_position|enable_autotrade|disable_dry_run" -CaseSensitive
# Expected: zero matches
```

This scan is included in the pre-commit validation script (`TEST-001` family).

---

## 14. Rollback Plan

| Scenario | Action |
|---|---|
| MCP skeleton causes test failures | `git restore mellytrade_mcp/` and re-run tests |
| Forbidden tool accidentally registered | Registry raises ValueError on startup; server does not start; fix registry |
| Auth bypass discovered | Rotate `MCP_DEV_TOKEN`; patch auth middleware; re-test |
| Performance issue (slow tools) | Reduce rate limits; add caching to slow query tools |
| MCP server crashes | Ctrl+C or `Stop-Process`; MCP has no auto-restart; safe to kill |

---

## 15. Implementation Checklist (Phase 2)

Before starting Phase 2 implementation:

- [ ] Phase 0 docs complete and committed
- [ ] Phase 1 local validation scripts pass
- [ ] `docs/mcp/mellytrade_mcp_tools.md` reviewed and approved
- [ ] `MCP_DEV_TOKEN` generated and stored in `.env` (not committed)
- [ ] Backend health endpoint returning 200

Phase 2 implementation order:
1. `mellytrade_mcp/__init__.py` + `__main__.py` (CLI skeleton)
2. `config.py` (env-only config loader)
3. `registry.py` (registration + forbidden-name validator)
4. `audit.py` (JSONL writer)
5. `tools/status.py` (first tool; reference implementation)
6. `tests/mcp/test_tool_registry.py` (validate before adding more tools)
7. Remaining tools (one per commit, each with a test)
8. `server.py` (HTTP server wrapping registry)
9. Full smoke test pass
10. PR for human review — do not merge until human reviews
