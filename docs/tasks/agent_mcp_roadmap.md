# Agent MCP Roadmap

**Current selected milestone:** M2 — GitHub App + MCP read-only Agent MVP

This roadmap tracks the read-only agent layer for MellyTrade. Every task in this
milestone is read-only: the agents inspect repository state, pull requests,
checks, and safety status, and produce reports or task boards. No task in M2
introduces write actions, deployment changes, broker integration, or trading
execution.

## Task Board

| Task | Title | Status | Risk | Scope |
|---|---|---|---|---|
| AGENT-MCP-001 | GitHub App read-only permission matrix | Done | Low | Docs-only |
| AGENT-MCP-002 | MCP read-only contract design | In progress | Low | Docs-only |
| AGENT-MCP-003 | Local repo status collector script | Planned | Low-Med | Script + docs |
| AGENT-MCP-004 | PR/checks task board generator | Planned | Med | Script + docs |
| AGENT-MCP-005 | Safety reviewer prompt pack | Planned | Low | Docs-only |
| AGENT-MCP-006 | Read-only agent demo runbook | Planned | Low | Docs-only |

## Tasks

### AGENT-MCP-001 — GitHub App read-only permission matrix

- **Goal:** Document the minimum safe GitHub App permissions for read-only
  agents, and explain why v1 must not mutate repository state.
- **Allowed files:** `docs/agents/github_app_readonly_permissions.md`,
  `docs/tasks/agent_mcp_roadmap.md`
- **Forbidden files:** `app/*`, `frontend/*`, `brokers/*`,
  `mellytrade_v3/mellytrade-api/app/*`, `config.json`, `requirements*`,
  `.github/workflows/*`, `Dockerfile*`, `.env*`, `secrets/*`, `credentials/*`
- **Validation:** `py -3.11 scripts/validate_safety_config.py`; static
  secret/unsafe-string scan of changed files.
- **Exit criteria:** Docs-only Draft PR; no runtime changes; safety validation
  passes; no real unsafe strings.

### AGENT-MCP-002 — MCP Read-Only Contract Design

**Status:** In progress (this PR).

- **Goal:** Define the read-only MCP contract for safe MellyTrade agents —
  the allowed read operations, the explicitly forbidden mutation functions, the
  command allowlist, output/logging requirements, approval gates, and the
  failure mode. See `docs/agents/mcp_readonly_agent_contract.md`.
- **Allowed files:**
  - `docs/agents/mcp_readonly_agent_contract.md`
  - `docs/tasks/agent_mcp_roadmap.md`
- **Forbidden files:**
  - runtime app code
  - frontend app code
  - brokers
  - `config.json`
  - requirements
  - workflows
  - secrets
  - credentials
- **Validation:**
  - `py -3.11 scripts/validate_safety_config.py`
  - static scan for secrets and unsafe trading strings
- **Exit criteria:**
  - docs-only PR
  - no runtime changes
  - no secrets
  - read-only functions only
  - forbidden write/mutation functions explicitly listed
  - PR remains draft until review

### AGENT-MCP-003 — Local repo status collector script

- **Goal:** A read-only script that reports repo SHA, branch, dirty files,
  worktrees, and open PRs.
- **Allowed files:** `scripts/dev/mellytrade_status_report.ps1`,
  `docs/agents/status_collector_runbook.md`
- **Forbidden files:** runtime app code, config safety flags, secrets.
- **Validation:** safety validator; confirm script performs read-only git/gh
  calls only (no writes); static scan.
- **Exit criteria:** Script + docs PR; script makes no mutating calls.

### AGENT-MCP-004 — PR/checks task board generator

- **Goal:** A read-only script that generates a PR-status markdown board from
  the `gh` CLI, with no GitHub writes.
- **Allowed files:** `scripts/dev/generate_pr_task_board.ps1`,
  `docs/agents/pr_task_board_runbook.md`
- **Forbidden files:** any `gh pr merge` / `gh pr close` / `gh pr edit` /
  `gh pr ready` / `gh api` write endpoints; runtime app code; secrets.
- **Validation:** safety validator; confirm read-only `gh` usage; fixture test.
- **Exit criteria:** Script + docs PR; output is generated from read-only data.

### AGENT-MCP-005 — Safety reviewer prompt pack

- **Goal:** A prompt pack for Claude/Codex safety review of diffs and PRs.
- **Allowed files:** `docs/agents/safety_reviewer_prompt_pack.md`,
  `docs/tasks/agent_mcp_roadmap.md`
- **Forbidden files:** runtime code, secrets, any execution-enabling content.
- **Validation:** static scan; no unsafe execution strings.
- **Exit criteria:** Docs-only PR.

### AGENT-MCP-006 — Read-only agent demo runbook

- **Goal:** Show how to use the read-only agents end to end without changing
  the repository.
- **Allowed files:** `docs/agents/readonly_agent_demo_runbook.md`
- **Forbidden files:** runtime code, secrets, deployment mutations.
- **Validation:** static scan.
- **Exit criteria:** Docs-only PR.

## Global Safety Rules

- no runtime trading changes
- no broker execution
- no secrets
- no live trading
- no write actions in v1
- no order / buy / sell / execute controls

## Suggested Implementation Order

1. AGENT-MCP-001
2. AGENT-MCP-002
3. AGENT-MCP-003
4. AGENT-MCP-004
5. AGENT-MCP-005
6. AGENT-MCP-006
