# MCP Read-Only Agent Contract

> Task: **AGENT-MCP-002** — part of milestone **M2 (GitHub App + MCP read-only Agent MVP)**.
> Status: docs-only. No runtime code, no secrets, no write actions.
> Companion: see `docs/agents/github_app_readonly_permissions.md` (AGENT-MCP-001).

## 1. Purpose

This document defines the **read-only MCP contract** for MellyTrade agents. MCP
tools must help **inspect** repository state, pull requests, checks, docs, and
safety posture **without** modifying code, changing pull requests, accessing
secrets, or enabling trading.

The contract is the behavioral counterpart to the read-only GitHub App
permission matrix: even if a tool *could* technically be wired to a write
action, this contract forbids it for v1.

## 2. Contract Summary

The v1 MCP agent is **inspection-only**.

**Allowed:**

- read repo status
- read current branch / SHA
- read dirty files
- list worktrees
- list open PRs
- read PR metadata
- read PR changed files
- read CI / check status
- read docs and source files
- generate local markdown reports
- generate task boards
- generate review prompts

**Forbidden:**

- edit files
- write commits
- push branches
- merge PRs
- close PRs
- mark PRs ready
- edit PR metadata
- comment on PRs (deferred from v1)
- access secrets
- read private keys
- modify workflows
- trigger deployments
- change runtime config
- change trading safety flags
- enable live trading

## 3. Safety Invariants

The MCP system must **preserve**:

- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- `execution_enabled=false`
- max risk `<= 1%`

The MCP system must **never** introduce:

- broker execution
- order placement
- buy / sell / execute controls
- production mutation trading endpoints
- broker credentials
- account IDs
- live execution toggles

## 4. Allowed Tool Categories

| Tool Category | Allowed in v1? | Examples | Notes |
|---|---|---|---|
| Git read status | Yes | branch, SHA, status, worktrees | no write commands |
| GitHub PR read | Yes | open PRs, PR metadata, changed files | read-only only |
| GitHub checks read | Yes | check status, CI summary | no reruns in v1 |
| File read | Yes | docs / source inspection | no file writes |
| Report generation | Yes | local markdown reports outside repo or explicitly approved docs | no auto-commit |
| Secrets access | No | any secret store | forbidden |
| PR mutation | No | merge / close / ready / edit / comment | forbidden in v1 |
| Deployment mutation | No | deploy / restart / promote | forbidden |
| Trading mutation | No | order / trade / execute | forbidden |

## 5. Allowed MCP Functions

All v1 functions are read-only. None may stage, commit, push, or otherwise
mutate the repository, deployment, or trading state.

### get_repo_status

- **Purpose:** Return current repository branch, SHA, dirty files, and worktree list.
- **Inputs:** none (operates on the canonical repo path).
- **Output:** branch, SHA, dirty-file list, worktree list.
- **Allowed commands:** `git rev-parse HEAD`, `git branch --show-current`, `git status --short`, `git worktree list`
- **Forbidden:** `git add`, `git commit`, `git push`, `git checkout` without explicit approval, `git reset`, `git clean`

### get_worktree_inventory

- **Purpose:** Enumerate all registered worktrees with branch/SHA/dirty state.
- **Inputs:** none.
- **Output:** table of worktree path, branch or detached SHA, clean/dirty.
- **Allowed commands:** `git worktree list --porcelain`, `git -C <path> status --short`, `git -C <path> rev-parse HEAD`
- **Forbidden:** `git worktree add`, `git worktree remove`, `git worktree prune`

### get_open_prs

- **Purpose:** List open pull requests.
- **Inputs:** optional state filter (default `open`).
- **Output:** PR number, title, head/base, draft state.
- **Allowed commands:** `gh pr list --state open`
- **Forbidden:** `gh pr merge`, `gh pr close`, `gh pr ready`, `gh pr edit`

### get_pr_summary

- **Purpose:** Read metadata for a specific PR.
- **Inputs:** PR number.
- **Output:** title, author, state, draft, base/head, mergeStateStatus.
- **Allowed commands:** `gh pr view <PR> --json ...`
- **Forbidden:** any `gh pr` mutation subcommand

### get_pr_changed_files

- **Purpose:** List files changed by a PR.
- **Inputs:** PR number.
- **Output:** file path list.
- **Allowed commands:** `gh pr diff <PR> --name-only`
- **Forbidden:** writing the diff into the repo; applying patches

### get_pr_checks

- **Purpose:** Read CI / check status for a PR.
- **Inputs:** PR number.
- **Output:** check name, status, conclusion.
- **Allowed commands:** `gh pr checks <PR>`
- **Forbidden:** `gh run rerun`, `gh workflow run`, any check/workflow mutation

### get_recent_commits

- **Purpose:** Read recent commit history.
- **Inputs:** optional count (default 10).
- **Output:** SHA, date, subject per commit.
- **Allowed commands:** `git log -n <count> --oneline`
- **Forbidden:** `git commit`, `git rebase`, `git cherry-pick`, history rewrite

### get_safety_status

- **Purpose:** Report the local safety posture.
- **Inputs:** none.
- **Output:** result of the safety validator and the key invariants.
- **Allowed commands:** `py -3.11 scripts/validate_safety_config.py`
- **Forbidden:** editing `config.json`; changing any safety flag

### get_dependency_audit_status

- **Purpose:** Report dependency audit status (read-only).
- **Inputs:** requirements file path.
- **Output:** audit summary (pass/fail and advisories).
- **Allowed commands:** `py -3.11 -m pip_audit -r <file>` (read-only), `py -3.11 -m pip check`
- **Forbidden:** `pip install`, `pip uninstall`, editing `requirements*`

### generate_pr_task_board

- **Purpose:** Produce a markdown board of PR status from read-only data.
- **Inputs:** PR list (from `get_open_prs`).
- **Output:** markdown table (rendered to stdout or an explicitly approved doc).
- **Allowed commands:** read-only `gh pr` reads only
- **Forbidden:** auto-commit; pushing; PR mutation

### generate_cleanup_plan

- **Purpose:** Propose (not execute) worktree/branch cleanup based on read-only inventory.
- **Inputs:** worktree + branch + PR data.
- **Output:** recommendation table with "approval needed" flags.
- **Allowed commands:** read-only git/gh reads only
- **Forbidden:** `git worktree remove`, `git branch -d/-D`, `git push --delete`

### generate_review_prompt

- **Purpose:** Produce a safety-review prompt for a diff or PR.
- **Inputs:** PR number or diff scope.
- **Output:** markdown prompt text.
- **Allowed commands:** read-only diff reads only
- **Forbidden:** calling external model APIs from this function; committing output

## 6. Forbidden MCP Functions

These function names must **not** exist in the v1 read-only agent:

- `merge_pr`
- `close_pr`
- `mark_pr_ready`
- `edit_pr`
- `comment_on_pr`
- `push_branch`
- `write_file`
- `delete_file`
- `modify_workflow`
- `read_secret`
- `deploy_app`
- `restart_service`
- `enable_autotrade`
- `place_order`
- `execute_order`
- `connect_live_broker`
- `update_risk_config`

## 7. Command Allowlist

| Command | Allowed? | Conditions |
|---|---|---|
| `git status --short` | Yes | read-only |
| `git rev-parse HEAD` | Yes | read-only |
| `git branch --show-current` | Yes | read-only |
| `git worktree list` | Yes | read-only |
| `git diff --name-only` | Yes | read-only |
| `gh pr list` | Yes | read-only |
| `gh pr view` | Yes | read-only |
| `gh pr checks` | Yes | read-only |
| `gh pr diff --name-only` | Yes | read-only |
| `py -3.11 scripts/validate_safety_config.py` | Yes | read-only validation |
| `git add` | No | write action |
| `git commit` | No | write action |
| `git push` | No | write action |
| `gh pr merge` | No | mutation |
| `gh pr close` | No | mutation |
| `gh pr ready` | No | mutation |
| `gh pr edit` | No | mutation |
| `gh workflow run` | No | workflow mutation |
| `gh secret list` | No | secrets access |
| `gh secret set` | No | secrets mutation |

## 8. Output Requirements

Every MCP report should include:

- scope
- commands run
- files inspected
- findings
- risk classification
- safety posture confirmation
- recommended next action
- approval needed
- an explicit **"no mutations performed"** statement

## 9. Approval Gates

Human approval is required before any of:

- any file edit
- any commit
- any push
- any branch deletion
- any worktree deletion
- any PR mutation
- any deployment action
- any workflow action
- any secret handling
- any runtime config change

## 10. Logging and Audit Trail

The agent should record in its final report:

- timestamp (if available)
- repo
- branch
- SHA
- task ID
- commands run
- whether any mutation occurred
- safety result
- next approval needed

The agent must **not** log:

- secrets
- private keys
- token values
- broker credentials
- account IDs

## 11. Failure Mode

If the MCP agent detects any of:

- a real secret
- live trading enablement
- an unsafe mutation route
- a broker credential
- an account ID
- an unexpected dirty runtime file
- an unknown branch / worktree state

it must:

- stop immediately
- report the exact file / path
- avoid printing secret values
- avoid modifying the repo
- request human review

## 12. Future Upgrade Path

Write actions may be considered only in a **separate v2 contract**, and only
after **all** of the following hold:

- the read-only MVP is proven in use
- audit logs exist for every action
- least-privilege app permissions have been reviewed
- every mutation requires explicit human approval
- the write-scoped GitHub App is **separate** from the read-only app
- the safety test suite has been expanded to cover the new surface
