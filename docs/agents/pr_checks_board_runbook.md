# PR Checks Board Runbook

## Purpose

Generate a **read-only** Markdown board of open pull requests — their draft/merge
state, CI checks summary, a heuristic risk rating, and a recommended action —
plus an old-PR watchlist. The generator never mutates PRs, never touches secrets,
and degrades gracefully when `gh` is unavailable.

This implements **AGENT-MCP-004** under the read-only MCP contract
(`docs/agents/mcp_readonly_agent_contract.md`).

## Script Path

`scripts/dev/mellytrade_pr_checks_board.ps1`

## Usage Examples

```powershell
# Default: print board to stdout (no file written)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/dev/mellytrade_pr_checks_board.ps1

# Include CI checks summary, limit to 10 PRs
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/dev/mellytrade_pr_checks_board.ps1 -IncludeChecks -PrLimit 10

# Include changed-files detail per PR
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/dev/mellytrade_pr_checks_board.ps1 -IncludeFiles -PrLimit 10

# Optionally write to a file (default writes nothing)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/dev/mellytrade_pr_checks_board.ps1 -OutputPath C:/tmp/pr_board.md
```

Parameters: `-PrLimit` (default 30), `-IncludeFiles`, `-IncludeChecks`,
`-OutputPath` (default empty → no file written).

## Read-Only Guarantees

- `OutputPath` defaults to empty, so by default **no file is written**.
- Every external command passes through `Invoke-ReadOnlyCommand`, which **refuses**
  (throws) any command matching the mutation denylist before execution.
- No PR is merged, closed, marked ready, or edited.
- No secrets are read or printed.

## Allowed Commands

- `gh pr list`
- `gh pr view`
- `gh pr checks`
- `git rev-parse HEAD`

## Forbidden Commands (denylist — refused at runtime)

- `gh pr merge`, `gh pr close`, `gh pr ready`, `gh pr edit`
- `gh workflow run`, `gh secret …`
- `git add`, `git commit`, `git push`, `git reset`, `git clean`,
  `git checkout`, `git switch`, `git branch -D`, `git worktree remove`

## Risk Classification

- **LOW:** docs-only, `scripts/dev` read-only, README copy only
- **MEDIUM:** frontend UI changes, CSS/layout, broad tests-only
- **HIGH:** backend application or routing code, broker/risk/trading files,
  configuration, dependency, or workflow files, Docker/deploy runtime, or
  sign-in and sensitive-configuration values
- **BLOCKER:** secret-bearing paths (`.env`, `secrets/`, `credentials/`, `.key`/`.pem`),
  live-trading enablement, order/buy/sell/execute controls, mutation commands outside
  the denylist context

Risk is computed from each PR's changed-file paths (via `gh pr view --json files`).
CI Secret Scanning remains the authoritative secret check.

## Failure Modes

- `gh` not installed → board section is skipped with a "degraded" note; the script
  still exits cleanly.
- `gh` unauthenticated / API error → caught; reported as "unavailable (degraded)".
- A single PR detail failing → that PR's files/checks show "unavailable"; the board
  continues.

## Safety Posture

- `autotrade=false`, `dry_run=true`, `read_only=true`, `live_orders_blocked=true`,
  `execution_enabled=false`, max risk `<= 1%`.
- The generator is observe-and-report only; it performs no mutations.
