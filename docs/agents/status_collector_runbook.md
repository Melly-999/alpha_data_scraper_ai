# Status Collector Runbook

## Purpose

AGENT-MCP-003 adds a read-only local status collector for MellyTrade. The
script gathers repository state, recent commits, worktrees, open pull requests,
optional PR checks, and an optional safety validation result without mutating
the repository or GitHub state.

## Script

Path:

`scripts/dev/mellytrade_status_report.ps1`

## Usage

Basic:

```powershell
.\scripts\dev\mellytrade_status_report.ps1
```

Include PR checks:

```powershell
.\scripts\dev\mellytrade_status_report.ps1 -IncludePrChecks
```

Include safety validation:

```powershell
.\scripts\dev\mellytrade_status_report.ps1 -RunSafetyValidation
```

Write report outside repo:

```powershell
.\scripts\dev\mellytrade_status_report.ps1 -OutputPath "C:\AI\MellyTrade_Workspace\_agent_reports\status_report.md"
```

## Read-Only Guarantees

- does not commit
- does not push
- does not merge
- does not close PRs
- does not mark PRs ready
- does not reset or clean
- does not delete branches
- does not remove worktrees
- does not read secrets
- does not deploy
- does not touch broker credentials
- does not enable live trading

## Allowed Commands

| Command | Purpose |
|---|---|
| `git rev-parse HEAD` | Capture the current commit SHA |
| `git branch --show-current` | Capture the current branch |
| `git status --short` | Report dirty files |
| `git worktree list` | Report worktree state |
| `git log --oneline -n 5` | Show recent commits |
| `gh pr list` | List open pull requests |
| `gh pr view` | Inspect a specific pull request if needed |
| `gh pr checks` | Show pull request checks when requested |
| `py -3.11 scripts/validate_safety_config.py` | Run safety validation behind `-RunSafetyValidation` |

## Forbidden Commands

- `git add`
- `git commit`
- `git push`
- `git reset`
- `git clean`
- `git checkout`
- `git switch`
- `git branch -D`
- `git worktree remove`
- `gh pr merge`
- `gh pr close`
- `gh pr ready`
- `gh pr edit`
- `gh workflow run`
- `gh secret`
- `secret list`
- `secret set`

## Failure Modes

- If `gh` is unavailable, the report should note a degraded state and skip PR
  data.
- If the repo path is missing, the script should fail clearly.
- If safety validation fails, the report should include the failure.
- If the denylist detects a forbidden command string, the script should stop
  immediately.

## Safety Posture

- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- `execution_enabled=false`
- `max risk <=1%`
