# GitHub App Read-Only Permission Matrix

> Task: **AGENT-MCP-001** — part of milestone **M2 (GitHub App + MCP read-only Agent MVP)**.
> Status: docs-only. No runtime code, no secrets, no write actions.

## 1. Purpose

This document defines the **minimum** GitHub App permissions for MellyTrade
read-only agents. The first agent milestone (v1) must be able to **inspect**
repository state, pull requests, checks, and safety status **without** editing
code, changing pull requests, writing comments, merging, closing, marking ready,
or accessing secrets.

In short: the v1 agent **observes and reports**. It never mutates repository
state, never touches deployment, and never has any path to trading execution.

## 2. Safety Contract

The agent must **preserve** the MellyTrade safety posture at all times:

- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- `execution_enabled=false`
- max risk `<= 1%`

The agent must **never**:

- merge pull requests
- close pull requests
- mark pull requests ready for review
- push commits
- edit files
- modify workflows
- read or write secrets
- access broker credentials
- enable live trading
- create order / buy / sell / execute controls

If any requested operation would violate this contract, the agent must refuse
the operation and report it rather than attempt it.

## 3. Minimum Permission Matrix

These are the **only** permissions the v1 read-only agent should be granted.

| GitHub App Permission | Access | Why Needed | Notes |
|---|---|---|---|
| Metadata | Read-only | Basic repository metadata | Required by all GitHub Apps |
| Contents | Read-only | Read files and docs for analysis | No write access |
| Pull requests | Read-only | Inspect PR state, diffs, reviews | No PR edits |
| Checks | Read-only | Inspect CI status | No reruns / write actions |
| Commit statuses | Read-only | Inspect status contexts | No status writes |
| Issues | Read-only or disabled | Optional task-board context | Prefer disabled unless needed |

## 4. Explicitly Forbidden Permissions

These permissions must **not** be granted to the v1 agent under any
circumstances.

| Permission | Access | Reason Forbidden |
|---|---|---|
| Contents | Write | Would allow file edits |
| Pull requests | Write | Would allow ready / close / merge-like actions |
| Actions | Write | Could alter CI or trigger workflows |
| Secrets | Any | Agents must not access secrets |
| Administration | Any | Too powerful (branch protection, settings) |
| Deployments | Write | Could affect hosting |
| Environments | Write | Could alter protected deployment settings |
| Packages | Write | Not needed |
| Codespaces | Write | Not needed |

## 5. Allowed Read-Only Operations

Examples of operations the v1 agent **may** perform:

- list open pull requests
- read PR metadata (title, author, base/head, draft state)
- read changed files for a PR
- read check / CI status
- read the repository tree
- read README and docs
- read branch names
- generate a local report from the above

## 6. Forbidden Operations

Examples of operations the v1 agent **must not** perform:

- `gh pr merge`
- `gh pr close`
- `gh pr ready`
- `gh pr edit`
- `git push`
- writing comments as a bot (deferred from v1)
- modifying files
- accessing secrets
- running deployment mutations
- changing branch protections
- changing workflows

Any trading-related mutation (order placement, buy / sell / execute controls,
broker execution) is permanently out of scope for this agent and is not merely
a v1 deferral.

## 7. Recommended v1 Agent Capabilities

The read-only agent should expose these named capabilities, all backed only by
the read-only permissions above:

- `get_repo_status`
- `get_open_prs`
- `get_pr_checks`
- `get_changed_files`
- `get_safety_status`
- `generate_task_board`
- `generate_review_prompt`

## 8. v1 Non-Goals

Explicitly **not** part of v1:

- no write actions
- no auto-merge
- no auto-fix
- no PR comments
- no deployment
- no broker integration
- no trading execution

## 9. Upgrade Path

Write permissions may be **considered** later, and only after **all** of the
following are true:

- the read-only MVP works and is in use
- a safety review passes
- audit logging exists for every agent action
- explicit human approval is required for every mutation
- write actions are split into a **separate, narrowly scoped** GitHub App
  (the read-only app never gains write scopes)

Until then, the read-only posture is the hard default.

## 10. Setup Checklist

- [ ] create a GitHub App
- [ ] set all permissions to read-only (per the matrix in section 3)
- [ ] install the app only on the MellyTrade repo
- [ ] store the private key **outside** the repository
- [ ] never commit `.pem` / `.key` files
- [ ] use a local environment variable or an external secret manager
- [ ] verify the app cannot write (attempt a no-op write and confirm it is denied)
- [ ] run a dry test using only the read-only endpoints listed in section 5
