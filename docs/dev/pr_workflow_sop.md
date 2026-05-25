# MellyTrade — PR Workflow SOP

A step-by-step Standard Operating Procedure for every MellyTrade PR. Follow
each phase in order. Skipping phases produces sloppy PRs, broken stacks, or
silently-shipped safety drift.

> All commands assume Windows PowerShell on
> `C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai`.
> macOS / Linux equivalents use the same commands minus the `py -3.11`
> launcher (use `python3.11` or `pytest` directly).

---

## Phase 1 — Pre-flight

Before doing anything else, confirm a clean baseline.

```powershell
cd C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai
git status --short                    # must be empty
git branch --show-current             # know where you are
git log --oneline -5                  # know what's behind you
gh pr list --state open               # know what's in flight
```

If `git status --short` is **not** empty, stop. Either commit, stash, or
discard the existing changes before starting a new task.

---

## Phase 2 — Branch from latest `main`

Almost every task should branch off the latest `main`. Stacking is rare.

```powershell
git fetch origin
git switch main
git pull --ff-only origin main        # never use plain `git pull`
git switch -c <branch-name>           # see naming below
```

**Branch naming conventions:**

| Type | Pattern | Example |
|---|---|---|
| Feature | `feature/<task-id>-<slug>` or `feature/<area>-<slug>` | `feature/safety-status-contract`, `feature/broker-adapter-protocol` |
| Test | `test/<slug>` | `test/openapi-forbidden-paths` |
| Tooling | `tooling/<slug>` | `tooling/local-validation-scripts` |
| Docs | `docs/<slug>` | `docs/safety-posture-architecture` |
| Hotfix | `hotfix/<slug>` | `hotfix/disable-stale-import` |
| Stacked | `stack-on-#<N>/<slug>` | `stack-on-#57/use-safety-status-from-frontend` |

Stacked branches are explicit so reviewers know the base isn't `main`.

---

## Phase 3 — Implement one task only

**One PR = one task = one concern.** If you find yourself wanting to also
fix a typo / refactor an adjacent function / format a file, stop. Note it
down for a later PR. Don't bundle.

While implementing:

- Use `Read` / `Grep` / `Glob` first to understand the existing code style
  and patterns.
- Match existing conventions (Pydantic v2 with `extra="forbid"`, `from __future__ import annotations`, `core/logger.get_logger`, dataclasses for structured returns, etc.).
- Don't refactor unrelated code in the same PR.
- Don't reflow whitespace in unrelated files (linter fights).
- Add the minimum tests that lock in the new behaviour.

---

## Phase 4 — Validate

Run the **right** validation matrix for the change type. The generic full
matrix:

```powershell
py -3.11 -m pytest tests/app/ -q
cd frontend; npm run build; cd ..
```

Plus a no-secrets scan on the diff:

```powershell
git diff --name-only
git diff | Select-String -Pattern "sk-|ghp_|MT5_PASSWORD|IBKR_PASSWORD|CLAUDE_API_KEY=|NEWSAPI_KEY=|password|token"
```

**Per-change validation matrix:**

| Change type | Backend | Frontend | Other |
|---|---|---|---|
| **Docs only** (`docs/**`) | not required | not required | markdown lint, no-secrets grep |
| **Screenshot only** (`docs/assets/**`) | not required | not required | PNG magic byte check, file size < 1 MB |
| **Backend only** (`app/**`, `tests/app/**`) | required | not required | route-inventory test, OpenAPI scan |
| **Frontend only** (`frontend/src/**`) | not required | required | safety-invariants frontend scan still passes |
| **Full-stack** (both) | required | required | both |
| **Test only** (`tests/**`) | required | not required | new tests must pass; existing count not drop |
| **Workflow YAML** | n/a | n/a | **don't.** Human-only change. |

Expected baseline numbers as of `main` at `e758f18`:

- `pytest tests/app/ -q` → 145 passed, 1 warning
- `npm run build` → 87 modules, 0 errors

Plus 13 more once SAFE-001 (PR #57) lands → 158 passed.

---

## Phase 5 — Stage exact files only

Never `git add .` Never `git add -A`. Stage by full path.

```powershell
git status --short                    # see all candidates
git diff --name-only                  # see what's actually different

# stage only the files you intended to change
git add app/schemas/safety.py
git add app/api/routes/safety.py
git add app/main.py
git add tests/app/test_safety_status.py

git diff --cached --name-only         # MUST equal the list above
git diff --cached --stat              # sanity check sizes
```

If `git status --short` shows files in the working tree that are *not* in
the staged set, that's correct — they're for a future PR (or unrelated).
Leave them alone.

---

## Phase 6 — Commit

Conventional Commits format. One commit per PR is preferred (squash on
merge anyway), but multiple commits are fine if they tell a clean story.

```powershell
git commit -m "feat(safety): add /api/safety/status contract"
```

**Commit message prefixes:**

- `feat(<area>): …` — new functionality
- `fix(<area>): …` — bug fix
- `test(<area>): …` — tests only
- `docs(<area>): …` — docs only
- `chore(<area>): …` — tooling, gitignore, etc.
- `refactor(<area>): …` — internal change, no behavioural diff

---

## Phase 7 — Push feature branch

Push only the feature branch. **Never push `main`.**

```powershell
git push -u origin <branch-name>      # first push: sets upstream
# or, on subsequent pushes (with rebase):
git push --force-with-lease origin <branch-name>
```

Force-push is only allowed on a named feature branch, only with
`--force-with-lease`, never to `main`.

---

## Phase 8 — Open draft PR

**Always start as draft.** Always with `gh pr create --draft`.

The PR body should live in a temp file *outside* the repo so it doesn't
appear in `git status`. Convention:

```powershell
$bodyFile = "C:\AI\MellyTrade_Workspace\.<short-slug>_pr_body.md"
# write the body via your editor or via a here-string

gh pr create `
  --draft `
  --base main `
  --head <branch-name> `
  --title "feat(<area>): <short summary>" `
  --body-file $bodyFile
```

The PR body should follow this template:

```markdown
## Summary

<one paragraph: what this PR does and why>

## Files

| Path | Purpose |
|---|---|
| `path/to/file` | what changed |

## Validation

- `py -3.11 -m pytest tests/app/ -q` → `<N> passed, <K> warning`
- `cd frontend && npm run build` → passed (or N/A)

## Safety confirmation

- No live trading changes
- No execution routes / order buttons / mutating API calls
- `config.json` untouched (or explicit reason)
- `autotrade.enabled = false` preserved
- `dry_run = true` preserved
- `read_only = true` preserved
- `max_risk_per_trade <= 1%` preserved
- No secrets / credentials / account IDs introduced

## CI note

<copy-paste current Actions status>
```

---

## Phase 9 — Add validation comment

Within the same task / day, post a single validation comment using
`gh pr comment`. Use a separate temp file outside the repo. Content
template lives in `docs/dev/ai_dev_workflow.md` ("What must always be
included in the final PR comment").

```powershell
$commentFile = "C:\AI\MellyTrade_Workspace\.<short-slug>_pr<N>_validation_comment.md"
gh pr comment <N> --body-file $commentFile
```

The validation comment is **especially important when GitHub Actions is
disabled** — it's the substitute for a green CI check.

---

## Phase 10 — Human review

The product owner reads the diff. Specifically checks:

- Files staged match the PR body's "Files" table.
- The diff doesn't touch broker / MT5 / execution / risk-engine files
  unless the PR is *explicitly* about those.
- The validation comment is present and accurate.
- The PR title and body match the actual change.

If any of those fails, request changes. Do not move forward.

---

## Phase 11 — Mark ready

Only after the human review.

```powershell
gh pr ready <N>
```

If GitHub Actions is enabled, CI will run. Otherwise, the validation
comment posted in Phase 9 is the substitute.

If the PR has been sitting as draft for several days with no CI
ticked, **don't** mark ready blindly — re-run local validation first
in case `main` has moved.

---

## Phase 12 — Merge

Squash-merge from the GitHub UI. Do **not** use `gh pr merge` from the
CLI for the first few merges; the UI gives you a chance to edit the
final commit message.

After merge:

- The squash commit lands on `main`.
- The feature branch is auto-deleted (if the repo setting is on; if not,
  delete it manually with `git push origin --delete <branch>`).
- Any dependent stacked branch will need a rebase (Phase 13).

---

## Phase 13 — Post-merge cleanup

```powershell
# 1. Re-sync local main
git fetch origin
git switch main
git pull --ff-only origin main

# 2. Delete the merged feature branch locally
git branch -D <branch-name>

# 3. Delete temp PR-body / comment files outside the repo
Remove-Item "C:\AI\MellyTrade_Workspace\.<slug>_pr_body.md" -ErrorAction SilentlyContinue
Remove-Item "C:\AI\MellyTrade_Workspace\.<slug>_pr<N>_validation_comment.md" -ErrorAction SilentlyContinue

# 4. If you have a dependent stacked branch, rebase it onto the new main
git switch <stacked-branch>
git rebase --onto origin/main <old-base> <stacked-branch>
# Re-validate, then force-push the stacked branch only:
py -3.11 -m pytest tests/app/ -q
cd frontend; npm run build; cd ..
git push --force-with-lease origin <stacked-branch>
```

---

## Per-change validation paths

Detailed scripts for the five common PR shapes.

### Docs-only PR

```powershell
git diff --name-only                          # must show only docs/**
git diff | Select-String -Pattern "sk-|ghp_|MT5_PASSWORD|password|token"
# no pytest, no npm run build required
```

### Screenshot PR

```powershell
git diff --name-only                          # only docs/** + docs/assets/**
ls docs\assets\terminal-v1\*.png | ForEach-Object {
  if ((Get-Item $_).Length -gt 1MB) { Write-Host "TOO LARGE: $_" }
  $bytes = Get-Content $_ -Encoding Byte -TotalCount 4
  if ($bytes[0] -ne 0x89 -or $bytes[1] -ne 0x50) { Write-Host "NOT PNG: $_" }
}
```

### Backend-only PR

```powershell
py -3.11 -m pytest tests/app/ -q              # must be >= previous count
py -3.11 -m pytest tests/app/test_safety_invariants.py -q  # 39+ assertions
```

### Frontend-only PR

```powershell
cd frontend
npm run build                                  # must be 0 errors
cd ..
py -3.11 -m pytest tests/app/test_safety_invariants.py -q  # frontend scan still passes
```

### Full-stack PR

```powershell
py -3.11 -m pytest tests/app/ -q
cd frontend; npm run build; cd ..
git diff --name-only
git diff | Select-String -Pattern "sk-|ghp_|password|token"
```

---

## When GitHub Actions are disabled

When `gh pr checks <N>` reports `no checks reported on the branch` and
`gh workflow run` returns `HTTP 422: Actions has been disabled for this
user.`:

1. **Do not edit workflow YAML** — the issue is account-level, not file-level.
2. **Do not bypass safety checks** — local validation is mandatory.
3. **Do not merge a PR without local validation comment present.**
4. **Do post the local validation comment** (Phase 9) on every PR.
5. **Do follow `docs/dev/github_actions_recovery.md`** to fix the
   underlying account-level block.
6. **Do flag in the PR body** that CI is unavailable and the validation
   comment is the substitute.

---

## Anti-patterns to refuse

| Anti-pattern | Refuse because |
|---|---|
| `git add .` | Stages unintended files. Always stage by exact path. |
| `git push --force` (no `--with-lease`) | Can stomp on remote work without warning. |
| `git push origin HEAD:main` | Bypasses PR review on `main`. Never do this. |
| `git rebase -i` to combine commits across branches | Easy to lose work; rebase only within a single feature branch. |
| `--no-verify` to skip pre-commit | Hooks exist for a reason. Fix the issue, don't bypass it. |
| `gh pr ready` immediately after `gh pr create` | Skip Phase 10 and you skip the safety net. |
| Mixing tasks in one PR | One PR = one concern. Split it. |
| Re-using a feature branch after merge | Create a new branch off `main`. The old one is gone. |

---

**Last updated**: 2026-05-09
