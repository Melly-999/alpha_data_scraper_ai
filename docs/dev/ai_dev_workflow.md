# MellyTrade — AI Dev Workflow

This document defines how a single human product owner collaborates with
two AI executors (Claude Code and Codex) to ship MellyTrade safely, one
small PR at a time. It is the playbook for the work — `pr_workflow_sop.md`
is the playbook for each individual PR.

---

## Roles

| Role | Who | What they do |
|---|---|---|
| **Product owner / safety gate** | **Human** | Decides direction. Reviews every PR before it's marked ready. Holds the only privilege to merge or to turn safety flags off. Re-enables GitHub Actions, manages billing, rotates secrets. |
| **Planner / structured implementer** | **Claude Code** | Picks one task at a time from the backlog, writes the implementation, runs validation locally, opens draft PRs, posts validation comments. Best at small, well-scoped, safety-aware changes and at code review. |
| **Focused executor** | **Codex** | Implements a single tightly-specified task end-to-end. Best when the prompt already names files, branch, validation, and acceptance criteria. Less appropriate for open-ended planning. |
| **Audit trail** | **GitHub Pull Requests** | Every change ships through a PR. PR body documents intent; the validation comment documents that local checks passed. |
| **Read-only observability** | **MCP** (later phase) | Reads git state, test results, and logs. Never writes. Surfaces in the AI Dev Control Center. |
| **Local dev control center** | **Dashboard `/ai-dev` page** (later phase) | Read-only view of CI, branches, PRs, and the validation panel. |
| **Private mobile access** | **Tailscale** (later phase) | Optional — exposes the local dashboard to your phone over a private tailnet. Never to the public internet. |

The human is **always** the safety gate. AI executors propose; the human disposes.

---

## Daily workflow

A typical day:

1. **Morning: pick one task.**
   Open `docs/roadmap/mellytrade_next_20_steps.md` and pick the lowest-numbered unblocked step.
   If you don't know which step is next, ask the planner: *"What's the next safe step on this branch given the current PR stack?"*

2. **Brief the executor.**
   Use the prompt template in `docs/dev/pr_workflow_sop.md`. The prompt names: branch, files, acceptance criteria, validation commands, hard safety rules.

3. **Watch the executor work.**
   The executor will run local validation before staging anything. Read the diff before approving the commit.

4. **Open a draft PR.**
   Always start as draft. Always with a validation comment. Never as "Ready for review" until you've reviewed the diff yourself.

5. **Mark ready when satisfied.**
   `gh pr ready <PR>`. CI runs (when GitHub Actions is enabled). Otherwise the validation comment is the substitute.

6. **Merge.**
   Squash-merge from the GitHub UI. Pull `main` locally. Delete the merged branch.

7. **Update the backlog.**
   Strike through the merged task in `mellytrade_next_20_steps.md`. If new follow-up tasks emerged, append them to the backlog **without** changing prior task IDs.

If a step takes more than one day, that's a sign the task wasn't decomposed enough. Stop and split it into two.

---

## How to start a task

Before writing any prompt, the human answers four questions:

1. **What is the smallest possible scope?** If the answer is "just the schema" or "just the route" or "just the test", that's correct. If the answer is "the schema, the route, the frontend hook, the card, and the docs", split it.
2. **What invariant must be preserved?** Always: dry-run, read-only, no execution, max risk ≤ 1%, no secrets. Sometimes: backwards compatibility with an existing schema, "the existing test count must not drop".
3. **What's the validation command?** If you can't name the exact pytest path or build command up front, the task isn't ready.
4. **What branch should it land on?** Almost always: a new branch off `main`. Stacking is allowed only when there's a hard dependency on an unmerged PR (and even then, see "How to avoid branch chaos").

Only when those four answers are clear should a prompt be written.

---

## How to write prompts

Good MellyTrade prompts have **six sections** in this order:

1. **Repo + goal.** One sentence each.
2. **Hard safety rules.** Repeated verbatim every time. Yes, every time.
3. **Branch + start procedure.** `git fetch`, `git switch main`, `git pull --ff-only`, `git switch -c <branch>`.
4. **Implementation scope.** Exact files and what each one should contain.
5. **Validation.** Exact commands and expected output.
6. **Stop conditions.** What the executor must *not* do (push, open PR, mark ready, merge).

A good prompt is ~200–500 words. A vague prompt produces a sprawling PR. A 2 000-word prompt is usually a sign the task is too large.

**Examples that work well:**
- "Implement SAFE-001. Add `app/schemas/safety.py` and `app/api/routes/safety.py`. Register in `app/main.py`. Add `tests/app/test_safety_status.py` with at least 13 assertions. Validate with `pytest tests/app/ -q`. Stop at local commit. Do not push."

**Examples that go badly:**
- "Make the dashboard better." — no scope, no acceptance criteria, no safety hooks.
- "Implement Tasks 1–8 from the roadmap." — too many tasks; the executor will bundle them.

---

## How to validate

Before any push:

```powershell
py -3.11 -m pytest tests/app/ -q                 # backend
cd frontend; npm run build; cd ..                # frontend type-check + bundle
```

Plus, depending on the change:

| Change type | Required validation |
|---|---|
| Backend route / schema / service | `pytest tests/app/ -q` (full suite) — must show count ≥ previous |
| Frontend page / hook / component | `npm run build` (must be 0 errors) |
| Docs only | Markdown lint (eyeball is fine); no-secrets grep on the new files |
| Test only | `pytest tests/app/<new_file>.py -v` plus full suite |
| Workflow YAML | **Don't.** This is a human-only change while Actions is disabled. |

The local validation script (`scripts/validate_local.ps1`, planned in TEST-003) wraps all of the above.

---

## How to decide Claude Code vs Codex

| Use Claude Code when… | Use Codex when… |
|---|---|
| Task is exploratory or has design choices | Task is fully specified and you just want execution |
| Task includes any architecture decision | Task is purely "fill in this template" |
| Task touches the safety surface (audit, risk, broker) | Task is in a low-risk corner (docs, tests, small refactors) |
| You want a structured PR description and comment | You want code in fewer round trips |
| You want a brief reasoning of trade-offs in the report | You don't need explanation, just diff |

For MellyTrade specifically, **default to Claude Code** while the safety surface is still being built out (Phases A–C in the roadmap). Once the broker abstraction has landed and the patterns are codified, Codex becomes a great fit for filling in adapter boilerplate.

---

## How to avoid over-automation

The temptation is to chain prompts: "implement Step 4, then Step 5, then Step 6". Don't. The cost of one over-broad PR landing on `main` is much higher than the cost of running three small prompts in series. Specifically:

- **One prompt = one PR.** No exceptions.
- **No "auto-approve and merge" agents.** A human reads every diff before merge.
- **No CI auto-fixers** that rewrite code on push (formatters can run as suggestions, but not as silent rewrites).
- **No auto-deploy on merge to `main`** until the safety regression suite has run on the merged commit.
- **No cross-branch script automation** that rebases / force-pushes without a human-typed command.

Slow is smooth. Smooth is fast.

---

## How to avoid branch chaos

- **Default: branch off latest `main`.** Always. Re-pull `main` before creating a new branch.
- **Stacking is the exception.** Stack only when the new task has a hard dependency on commits that are still in an unmerged PR. If you stack, name it clearly (`stack-on-#57/...`) and rebase when the parent merges.
- **One topic per branch.** Don't bundle "fix typo + add feature + run formatter" into one branch. Each is its own PR (or skip the typo).
- **Delete merged branches.** GitHub auto-deletes after merge if the toggle is on; turn it on.
- **Avoid long-lived feature branches.** A branch older than a week is a sign that the task was too large.
- **Never force-push to `main`.** Force-push is allowed only on a named feature branch you own, only with `--force-with-lease`, only when explicitly approved.

---

## How to avoid huge PRs

| Symptom | Fix |
|---|---|
| `git diff --stat` shows > 10 files | Split. One concern per PR. |
| `git diff` shows > 500 lines added | Split. Or check if a refactor crept in. |
| Multiple unrelated commit messages | Split, even if you've already pushed. Reset, re-stage. |
| The PR description has multiple `## Sections` describing different features | Split. The PR is doing too much. |
| You can't summarize the PR in one sentence | Split. |

A PR that's hard to review is a PR that ships bugs.

---

## What must always be checked before push

A non-negotiable pre-push checklist:

1. `git status --short` is clean — no stray untracked files in the staging area.
2. `git diff --cached --name-only` shows **only** files you intended.
3. Backend tests pass (`pytest tests/app/ -q`).
4. Frontend builds (`npm run build`).
5. No secrets in the diff (grep for `sk-`, `ghp_`, `MT5_PASSWORD=`, `IBKR_PASSWORD=`, `API_KEY=<value>`, password literals).
6. `config.json` is **not** in the diff unless explicitly intended.
7. No file under `mt5_trader.py`, `brokers/` (write paths), `execution/`, `execution_service.py`, `risk/risk_manager.py` is in the diff unless explicitly intended.
8. The new test count is **greater than or equal to** the previous test count (no tests silently deleted).

---

## What must always be included in the final PR comment

Every PR gets a single validation comment with this exact structure:

```markdown
## Local validation summary for PR #<N>

Branch: `<branch-name>`
Commit: `<sha>`
Rebased onto `origin/main` at `<main-tip-sha>` (if applicable).

### Validation results

- `py -3.11 -m pytest tests/app/ -q` → `<N> passed, <K> warning`
- `cd frontend && npm run build` → passed (or "N/A" if no frontend change)

### Safety confirmation

- No live trading changes
- No execution routes / order buttons / mutating terminal API calls
- `config.json` untouched (or explicit reason if not)
- `autotrade.enabled = false` preserved
- `dry_run = true` preserved
- `read_only = true` preserved
- `max_risk_per_trade <= 1%` preserved
- No secrets / credentials / account IDs introduced

### CI note

GitHub Actions may be disabled at the user-account level. If so, this
local validation summary is the substitute for a green CI check.
```

The comment is the audit trail when CI cannot run. Always post it on the same day the PR is opened.

---

## What never to automate

These actions are **human-only** in the MellyTrade workflow:

- Re-enabling GitHub Actions, changing repo permissions, changing billing.
- Flipping `autotrade.enabled` to `true`.
- Flipping `dry_run` to `false`.
- Flipping `read_only` to `false`.
- Raising `max_risk_per_trade` above 1.0.
- Adding any new HTTP `POST/PUT/DELETE/PATCH` endpoint.
- Adding any "Place Order" / "Execute Trade" / "Submit Order" button.
- Adding live broker credentials to any environment, anywhere.
- Pushing to `main`. Period.
- Force-pushing any branch without explicit approval.
- Merging a PR.
- Closing a PR without merging.

If an AI executor proposes any of these, refuse. Send back a corrected scope. Do not relax the rule.

---

## Anti-patterns to avoid

- **"While I'm here…"** — the executor adds an unrelated change to the PR. Reject and split.
- **"This is a quick fix"** — quick fixes get their own PR. They get tested. They get reviewed.
- **"The CI is disabled, so I'll skip the validation comment"** — no. The validation comment is *more* important when CI is disabled.
- **"Let's stack on top of the unmerged PR to save time"** — only with a hard dependency. Otherwise branch off `main`.
- **"I'll temporarily disable that test"** — never. If a test is wrong, fix it. If it's correct, fix the code.
- **"Let me amend the previous commit"** — almost never. Create a new commit. Amending rewrites history and can break stacks.

---

**Last updated**: 2026-05-09
