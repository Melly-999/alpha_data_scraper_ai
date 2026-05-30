# MellyTrade Read-Only MCP Server — Design

> **Docs-only design.** No server is implemented here; no code, no secrets.
> Safety posture unchanged: `autotrade=false`, `dry_run=true`, `read_only=true`,
> `live_orders_blocked=true`, `execution_enabled=false`, `max_risk_per_trade <= 1%`.

---

## 1. Overview

**Proposed server name:** `mellytrade-readonly-mcp`

A Model Context Protocol server that exposes **read-only** repo + safety state
to MellyTrade agents (Repo Captain, CI Doctor, Safety Reviewer). It is a thin,
auditable layer over the read-only GitHub App (see
`github_developer_program_setup.md`) plus the repo's own safety/health
endpoints. It must be impossible for this server to mutate the repo, merge PRs,
or touch trading.

Design principles:
- **Read-only by construction.** No tool performs a write or execution.
- **No secrets in responses.** Tools never return tokens, keys, account IDs, or
  broker order IDs.
- **Least privilege.** Backed by the read-only GitHub App scopes only.
- **Auditable.** Every tool call is loggable; logs carry no secrets.

## 2. Read-only tools (initial surface)

| Tool | Purpose | Returns | Never returns |
|---|---|---|---|
| `get_open_prs` | List open PRs. | number, title, head/base, draft state, mergeStateStatus. | secrets, tokens. |
| `get_pr_checks` | CI check rollup for a PR. | per-check name + status (pass/fail/pending). | raw secret logs. |
| `get_pr_diff_summary` | Changed-file summary for a PR. | file paths, +/- counts, category flags (docs/deps/frontend). | full secret values, `.env` contents. |
| `get_safety_status` | Current safety posture snapshot. | the six invariants (autotrade/dry_run/read_only/live_orders_blocked/execution_enabled/max_risk) + degraded flags. | credentials, account IDs. |
| `get_current_milestones` | Roadmap/milestone progress. | milestone names + % + status. | nothing sensitive. |
| `get_next_task` | The single next recommended task. | task_id, summary, allowed/forbidden files, validation commands. | nothing sensitive. |

All tools are **idempotent reads**. None accept a body that mutates state.

## 3. Forbidden tools (must never exist on this server)

| Tool | Why forbidden |
|---|---|
| `merge_pr` | No merging from an agent surface. |
| `push_to_main` | No direct writes to `main`. |
| `enable_live_trading` | Violates the safety contract outright. |
| `place_order` | No order placement, ever. |
| `execute_order` | No execution, ever. |
| `edit_secrets` | Agents must never read or modify secrets. |

These names are listed explicitly so any future PR that adds one is trivially
caught by a denylist scan in CI.

## 4. Future write tools — only after explicit approval

These remain **unbuilt** until a dedicated, separately-approved phase
(see roadmap Phase 5). When introduced, each requires a human-in-the-loop gate
and an audit trail; none may touch trading or secrets.

| Tool | Guarded capability | Gate |
|---|---|---|
| `create_pr_comment` | Post a review comment on a PR. | Explicit approval flag; rate-limited; no secrets in body. |
| `create_issue` | Open a tracking issue. | Explicit approval flag; template-bound. |
| `update_docs_task_board` | Append status to a docs task board file via a reviewed PR. | Explicit approval flag; docs-only path allowlist; still goes through PR review, never direct push. |

Even these "write" tools never merge, never push to `main`, never trade, and
never read/write secrets.

## 5. Safety & data-handling rules

- Backed solely by read-only GitHub App scopes (Contents/PRs/Checks/Metadata = Read).
- Responses are filtered to **strip** any field resembling a secret, token,
  key, account ID, or broker order ID before returning.
- The server holds no broker connection and cannot import broker/MT5/IBKR/XTB
  execution modules.
- No tool can flip a safety flag; `get_safety_status` is read-only reporting.
- All configuration secrets (App private key, webhook secret) live in the host
  secret manager — never in the repo or in tool responses.
