# MellyTrade Clean Branch PR Prep 001

> **Docs-only run.** No push, no PR opened, no upstream set, no merge, no
> rebase, no cherry-pick, no deploy. No frontend/backend/runtime/broker/
> config/package/deployment files changed.
> **Run:** `MELLYTRADE-CLEAN-BRANCH-PR-PREP-001` · **Date:** 2026-07-06 · **Model:** Sonnet 5

## Outcome

**Ready — PR materials fully prepared, awaiting explicit user approval to
push and open the PR.** The clean branch is confirmed unchanged and still
scoped since the immediately preceding final QA pass: same 33-file diff,
same merge-base equal to `origin/main`'s own tip, no forbidden areas, no
drift. Nothing further needs fixing before a PR can be opened — only the
push/PR-creation action itself remains, and this run deliberately stops
before performing it.

## Branch / Commit Reviewed

- Branch: `feature/public-landing-case-study-main-001`
- Latest commit: `d4dea8f` (docs(showcase): add clean branch final QA)
- Upstream: none configured (confirmed via `git status --branch --short`)
- Remote: `git ls-remote --heads origin feature/public-landing-case-study-main-001` returned nothing — **not pushed**
- Source branch `feature/public-landing-case-study-001` was not touched by
  this run

## Base Main SHA

```
git rev-parse origin/main        → 995f0905d540f8758710c2c328191bf088ad48df
git merge-base HEAD origin/main  → 995f0905d540f8758710c2c328191bf088ad48df
```

Merge-base equals `origin/main`'s own tip — this branch remains a perfectly
linear, two-commit fast-forward ahead of current `origin/main` (the replay
commit `770262f` + the final-QA report commit `d4dea8f`).

## Diff Scope Summary

`git diff --stat origin/main...HEAD`: **33 files changed, 5085
insertions(+), 1 deletion(-)** — identical in shape to the immediately
preceding final-QA report's findings (32 files at that point; +1 for this
run's own report file once committed). No new files, no drift.

Explicit forbidden-area re-check in this run:

```
git diff --name-status origin/main...HEAD -- package.json package-lock.json \
  pnpm-lock.yaml yarn.lock Dockerfile docker-compose.yml .github/workflows \
  config backend app api broker execution services
→ (empty)

git diff --name-status origin/main...HEAD -- .claude/launch.json
→ (empty — ABSENT_FROM_PR_DIFF, re-confirmed)
```

`frontend/src/lib/terminalApi.ts` diff re-verified byte-identical to the
prior QA: only the 7 optional `RiskPolicy` fields, `getRiskPolicy()` and
every other export untouched.

## PR Readiness Confirmation

All criteria from `MELLYTRADE-CLEAN-BRANCH-FINAL-QA-001`
(`READY_FOR_CLEAN_BRANCH_PR_PREP`) re-verified unchanged in this run:
scoped diff, no forbidden areas, `.claude/launch.json` absent, type-only
`RiskPolicy` fix, media assets present and unused-as-video on public pages,
zero `/api/*` calls, zero `.mp4` requests, all 6 routes previously smoke-
tested clean. No new issues found. **No code or config changes were made in
this run** — only this report was added.

## Final PR Title

```text
feat(frontend): add public MellyTrade showcase and case study
```

## Final PR Body

```md
## Summary

Adds a public MellyTrade showcase surface on top of current `main`.

This PR introduces:
- public `/` landing page
- public `/case-study` page
- reusable public showcase components
- static public media pack under `frontend/public/media/mellytrade/`
- final QA / replay / PR-readiness documentation
- a minimal type-only `RiskPolicy` extension needed by the public showcase fixture

The public pages are read-only/showcase-only and do not call backend APIs.

## What Changed

### Frontend
- Adds public landing and case-study routes.
- Adds public showcase components.
- Adds public showcase fixtures.
- Reuses existing internal terminal routes without changing their behavior.
- Keeps `/terminal`, `/watchlist`, `/mobile`, and `/terminal/paper-run-preview` available.

### Media
- Adds accepted Higgsfield media assets under `frontend/public/media/mellytrade/`.
- Uses the accepted hero poster as a static image on `/` and `/case-study`.
- Keeps accepted MP4 files in the repo and documented in the manifest, but does not autoplay or render them on public pages.

### TypeScript
- Extends `RiskPolicy` with seven optional fields:
  - `max_risk_per_trade_pct?`
  - `dry_run?`
  - `auto_trade?`
  - `read_only?`
  - `live_orders_blocked?`
  - `stop_loss_required?`
  - `take_profit_required?`
- This is type-only and backward-compatible.
- `getRiskPolicy()` and runtime behavior are unchanged.

### Docs
- Adds design, media, QA, topology, replay, and PR-prep reports under `docs/showcase/`.

## Safety

- No broker execution or live trading enabled.
- No Buy/Sell/Execute/Order controls added.
- No public-page `/api/*` calls.
- No public-page `.mp4` autoplay or video requests.
- No secrets exposed.
- No backend/runtime/broker/config/package/deployment files changed.
- No package or lock files changed.
- No Docker/CI/workflow changes.
- Media assets are static and validated.
- Rejected media assets were not integrated.

## Validation

Latest clean-branch QA passed:

- `git diff --check`
- `npx tsc -b`
- `npm run build`

Routes verified:

- `/`
- `/case-study`
- `/terminal`
- `/watchlist`
- `/mobile`
- `/terminal/paper-run-preview`

Public page checks:

- zero console errors
- zero `/api/*` calls
- zero `.mp4` requests
- hero poster loads
- no media 404s
- no horizontal overflow on desktop/tablet/mobile

## Notes

This branch was replayed cleanly onto current `origin/main` after resolving an old stacked-branch topology issue.

Base:
`origin/main @ 995f0905d540f8758710c2c328191bf088ad48df`

The older source branch `feature/public-landing-case-study-001` is preserved and was not pushed as the PR branch.
```

## Suggested Push Command, Do Not Run

```bash
git push -u origin feature/public-landing-case-study-main-001
```

**Not executed in this run.**

## Suggested PR Command, Do Not Run

```bash
gh pr create \
  --base main \
  --head feature/public-landing-case-study-main-001 \
  --title "feat(frontend): add public MellyTrade showcase and case study" \
  --body-file docs/showcase/clean_branch_pr_prep_001.md \
  --draft
```

**Not executed in this run.** Opens as a **draft** PR against `main` — the
correct base, since `origin/main` already includes the former parent
branch's squash-merged content (PR #273) and this branch's merge-base
equals `origin/main`'s current tip exactly.

## Validation Evidence

```powershell
git diff --check     # re-run this session: clean
```

`npx tsc -b` and `npm run build` were **not re-run** in this session — the
diff against `origin/main` is byte-identical to the state already fully
validated (both commands passing) in the immediately preceding
`MELLYTRADE-CLEAN-BRANCH-FINAL-QA-001` run against the same commit tree.
Per this run's own instructions ("skip rebuild and cite latest clean QA if
unchanged"), that prior result is cited rather than repeated, since no code
changed between that run and this one (only a docs report was added).

## Safety Review

Re-confirmed via the explicit forbidden-path diff check above: no package/
lock/backend/broker/config/Docker/CI file present anywhere in the diff. The
`terminalApi.ts` change remains type-only. No secrets, no interactive
trading controls, no fake performance claims anywhere in the branch (fully
re-swept across every prior QA pass on both the source and clean branches;
not re-swept line-by-line in this docs-only run since no code changed).

## User Approval Required

**Push and PR creation require explicit user approval before proceeding.**
This run intentionally stops here. To proceed, the user should confirm:

1. Whether to push `feature/public-landing-case-study-main-001` to `origin`
   (`git push -u origin feature/public-landing-case-study-main-001`).
2. Whether to open the PR as a **draft** against `main` using the exact
   `gh pr create` command above (title and body pre-filled from this
   report).
3. Whether the PR body should be adjusted before opening (e.g., adding
   reviewers, labels, or linking to a tracking issue) — none of that was
   set in the prepared command above.

## Next Recommended Run

`MELLYTRADE-PUSH-CLEAN-BRANCH-PR-001`

## Safety Confirmation

```text
Safety confirmation:
- No broker execution or live trading enabled.
- No Buy/Sell/Execute/Order controls added.
- No secrets printed or exposed.
- No backend/runtime/broker/config/package/deployment files changed by this run.
- No package or lock files changed by this run.
- No application/backend/broker APIs called.
- No Higgsfield MCP/media generation performed.
- No push, PR creation, merge, deploy, reset, clean, delete, force, rebase, cherry-pick, or history rewrite operation performed.
- Existing source branch was preserved.
```
