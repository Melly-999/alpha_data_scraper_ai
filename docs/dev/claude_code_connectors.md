# Claude Code Connectors for MellyTrade

Use connectors to speed up review, debugging, and validation without breaking the repository's read-only trading posture.

## Recommended Stack

### P0

- Datadog MCP
- GitHub CLI, GitHub MCP, or native GitHub integration
- CodeRabbit GitHub app
- Local repo tools: `pytest`, `npm`, and `git`

| Connector | What it gives | Recommended access | Secrets needed | Safe commands | Forbidden usage |
|---|---|---|---|---|---|
| Datadog MCP | Logs, traces, metrics, and dashboards | Read-only observability | Datadog OAuth or client auth only | Inspect logs, metrics, dashboards, monitors | No broker secrets, no live trading, no writes to Datadog config |
| GitHub CLI / GitHub MCP | Branch, PR, issue, and workflow inspection | Repo-scoped, least privilege | GitHub token if needed | `gh pr view`, `gh pr create --draft`, `git status` | No direct push to main, no secret exfiltration, no admin actions |
| CodeRabbit GitHub app | Automated PR review and safety checks | Repository install only | No repo secrets required | Open draft PRs and request review | No bypassing safety review or merge gates |
| Local repo tools | Run tests and build checks locally | Current worktree only | None | `pytest`, `npm run build`, `git diff` | No destructive git commands, no production access |

### P1

| Connector | What it gives | Recommended access | Secrets needed | Safe commands | Forbidden usage |
|---|---|---|---|---|---|
| Docker context or Docker MCP | Container inspection and logs | Read-only container access | None for local Docker context | `docker compose logs`, `docker ps`, `docker inspect` | No modifying production containers, no secret extraction |
| Playwright MCP | UI smoke tests and accessibility checks | Browser-only, localhost-only | None | Open localhost, capture screenshots, run smoke tests | No credential entry, no live trading actions |
| Read-only Postgres or Supabase MCP | Paper-trading DB inspection | Read-only role only | Read-only DB credentials if required | Query current state, inspect schema, validate test data | No writes, no migrations, no account data exposure |
| Filesystem limited to repo/worktree | Direct file inspection and edits | Current repo only | None | Read and edit local source files | No access to home directory secrets or unrelated workspaces |

### P2

| Connector | What it gives | Recommended access | Secrets needed | Safe commands | Forbidden usage |
|---|---|---|---|---|---|
| Slack / Discord / Telegram | Notifications and human review loops | Message-only integration | Bot token if required | Send validation summaries and alerts | No trading instructions, no sensitive data leakage |
| Notion / task board | Task tracking and implementation notes | Read/write only in project space | Workspace token if required | Track task status, note follow-ups | No secrets, no broker data, no execution workflows |
| Grafana | Dashboarding if Datadog is insufficient | Read-only dashboards | Grafana auth only | Inspect dashboards and alerts | No execution, no secret storage, no live trade actions |

## Safe Agent Workflow

1. Create a clean worktree or branch.
2. Inspect the repository before editing.
3. Implement the minimal diff needed for the task.
4. Run validation locally.
5. Open a draft PR.
6. Let CodeRabbit review the changes.
7. Run a staging smoke test if applicable.
8. Inspect Datadog logs and traces for regressions.
9. Mark the PR ready only after the safety gate passes.

## Usage Rules

- Keep all trading actions read-only, paper, or dry-run
- Never allow direct push to main from an agent workflow
- Never expose broker credentials or account IDs to connectors
- Never add order execution routes or buy/sell controls
- Prefer the smallest connector set that satisfies the task
