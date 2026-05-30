# Parallel Claude Code Sessions — MellyTrade DevX

> **Docs-only / dev-tooling.** No runtime, broker, frontend, dependency, or
> safety-config changes. Safety posture unchanged: `autotrade=false`,
> `dry_run=true`, `read_only=true`, `live_orders_blocked=true`,
> `execution_enabled=false`, `max_risk_per_trade <= 1%`.

---

## 1. Why separate git worktrees

Running several Claude Code sessions speeds up CI cleanup and review work, but
**only if each session is isolated**. A git *worktree* gives each session its
own working directory, branch checkout, and index — all sharing one `.git`
object store. This means:

- Sessions never fight over the same files or index lock.
- Each session has a single, clear branch and task.
- A `git switch` in one session cannot yank the rug out from under another.
- Commits/pushes stay attributable to one task at a time.

## 2. ⚠️ Do not run multiple sessions in the same repo folder

Two Claude Code sessions pointed at the **same** working directory will:

- collide on the git index (`.git/index.lock` errors),
- overwrite each other's edits,
- produce mixed-scope commits (violating one-PR-one-purpose),
- make it impossible to tell which session changed what.

**Always give each session its own worktree directory.** Never share a path.

## 3. Recommended max active sessions

**3–4 active sessions.** Beyond that, coordination overhead and CI noise grow
faster than throughput, and the single-committer rule (below) becomes a
bottleneck. Start with 3.

## 4. Folder layout example

```
C:/AI/MellyTrade_Workspace/02_Repo/
├─ alpha_data_scraper_ai            # canonical clone (main; read-only base)
├─ alpha_data_scraper_ai-format-001 # FORMAT-001 (black)
├─ alpha_data_scraper_ai-lint-001   # LINT-001 (flake8)
├─ alpha_data_scraper_ai-type-001a  # TYPE-001A (mypy gate)
├─ alpha_data_scraper_ai-sec-req-004# SEC-REQ-004 (python-dotenv)
└─ alpha_data_scraper_ai-ui-review  # UI review (read-only)
```

Each directory is one worktree = one branch = one session.

## 5. Recommended session roles

| # | Role | Worktree | Mode |
|---|---|---|---|
| 1 | **Lead / PR Monitor** | `…-lead-monitor` | read-only |
| 2 | **Quality Stack Agent** | `…-quality-stack` | edits black/flake8/mypy branches only |
| 3 | **Security Dependency Agent** | `…-security-deps` | edits requirements files only (when approved) |
| 4 | **UI Review Agent** | `…-ui-review` | read-only review of frontend PRs |

(Role startup prompts: see `claude_code_agent_roles.md`.)

## 6. Rules

- **One session = one task.**
- **One session = one worktree.**
- **One session = one branch.**
- **No two sessions on the same branch.**
- **Only one session may commit/push at a time** (the others stay read-only
  until it finishes) — avoids interleaved history and force-push hazards.
- **Merge only by explicit human approval** — no agent merges, marks ready, or
  pushes to `main`.
- **No Claude validation** — never run `claude_ai.py`, `ClaudeAIClient`, or
  `ClaudeAIIntegration`; never call the Claude/Anthropic API from repo code;
  never require `CLAUDE_API_KEY`.
- **No live-trading changes** — the safety posture is invariant across every
  session.

## 7. Quick start

```powershell
# 1. Preview the worktrees that would be created
.\scripts\dev\claude_worktree_setup.ps1 -DryRun

# 2. Create them
.\scripts\dev\claude_worktree_setup.ps1

# 3. In each new folder, open a separate Claude Code session and paste the
#    matching role prompt from docs/dev/claude_code_agent_roles.md

# 4. Check status any time (read-only)
.\scripts\dev\claude_session_status.ps1
```
