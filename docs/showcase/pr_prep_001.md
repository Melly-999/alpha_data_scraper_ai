# MellyTrade PR Prep 001

> **Docs/report-only run.** No frontend/backend/runtime/broker/config/
> package/deployment files changed. No Git history changes: no push, no PR
> opened, no rebase, no cherry-pick, no merge, no fetch, no upstream set.
> **Run:** `MELLYTRADE-PR-PREP-001` · **Date:** 2026-07-05 · **Model:** Sonnet 5

## Outcome

**Prepared, decision required from the user before any push or PR.** All
PR materials (title, body, file summary, validation evidence, safety
review) are ready below. The branch's own content is clean and scoped. The
one open item is the base-branch topology — this run recommends
`NEEDS_USER_DECISION` rather than picking a strategy unilaterally, per this
run's own recommendation rule and because no local evidence conclusively
shows the parent branch is safe/intended as a merge base.

## Branch / Commit Reviewed

- Branch: `feature/public-landing-case-study-001`
- Latest local commit: `ecf9e83` (docs(showcase): audit public website
  branch scope)
- Full chain (fork point → tip):
  ```
  0425a46 (feature/alpaca-paper-readonly-card)  ← fork point, not part of this feature
  da74565 feat(frontend): add public landing and case-study routes
  99bde92 fix(frontend): QA fixes for public landing/case-study a11y and touch targets
  5d2ecaa docs(showcase): add pre-media snapshot and readiness check
  bb8aa69 feat(frontend): prepare public website media slots
  ba6fc80 feat(frontend): integrate public website media pack
  d98f292 docs(showcase): add public website final QA
  ecf9e83 (HEAD) docs(showcase): audit public website branch scope
  ```
- Upstream: none configured (`git status --branch --short` shows no
  `...origin/...` tracking marker)
- Pushed: no
- `git branch --contains 0425a46` → `feature/alpaca-paper-readonly-card`,
  `feature/public-landing-case-study-001`
- `git branch --contains ecf9e83` → `feature/public-landing-case-study-001`
  only (confirms `ecf9e83` is this branch's own tip, not shared)

## Topology Finding

Unchanged from the prior branch scope audit, re-verified in this run:

- This branch forks from `0425a46`, the tip of **`feature/alpaca-paper-readonly-card`** — an unrelated, unmerged sibling branch (not `main`).
- `git merge-base HEAD origin/main` → `17702b7` (same value as the prior audit; no fetch was performed in this run, so freshness relative to the real GitHub `main` is still unverified).
- `git log --oneline origin/main..HEAD` → **11 commits**: the 4 commits already on `feature/alpaca-paper-readonly-card` (ahead of `origin/main`) plus this branch's own 7 commits (6 from the prior audit + `ecf9e83` itself).
- Comparing directly against `origin/main` therefore overstates this feature's actual diff by 4 unrelated commits. The clean, accurate scope boundary remains `0425a46`.

## Base Options

| Option | PR base | Pros | Cons | Use if |
|---|---|---|---|---|
| **A — Stacked PR** | `feature/alpaca-paper-readonly-card` | Smallest, cleanest diff; no rebase/cherry-pick now; branch preserved exactly as-is | Parent branch must be reviewed/merged first or alongside; PR chain is more complex to manage on GitHub | Parent branch is intentionally open and safe |
| **B — Wait for parent** | `main`, after parent merges | Clean, normal PR against `main`; avoids rebase/cherry-pick risk entirely | Blocked on the parent branch's own review/merge timeline; this branch may need a refresh (merge/rebase) once the parent lands | Parent branch is close to merging |
| **C — Rebase/cherry-pick onto `main`** | `main`, via a new branch | Fully independent PR against `main`; no dependency on the parent branch | Higher Git risk; must be done as its own explicitly approved task; must carefully preserve exactly the 27 expected files and none of the parent's | Parent branch is stale/blocked and the showcase needs to ship independently |

No option was executed in this run — all three remain proposals only.

## Recommended Strategy

**`NEEDS_USER_DECISION`**

Local evidence does not conclusively show which path is correct: this
session has no visibility into whether `feature/alpaca-paper-readonly-card`
is actively under review, near merge, or abandoned/stale — that is
information only the user (or the GitHub PR/issue history, which this
offline audit did not query) can supply. Per this run's own recommendation
rule, `NEEDS_USER_DECISION` is used rather than guessing.

## Changed Files Summary

`git diff --stat 0425a46...HEAD`: **27 files changed, 3874 insertions(+), 1
deletion(-)** (26 files from the prior branch-scope audit, plus
`docs/showcase/branch_scope_audit_001.md` itself, added in `ecf9e83`).

`git diff --name-status 0425a46...HEAD`:

```
A  docs/design/mellytrade_website_design_pack_001.md
A  docs/showcase/branch_scope_audit_001.md
A  docs/showcase/media_integration_001.md
A  docs/showcase/pre_media_snapshot_001.md
A  docs/showcase/public_showcase_final_qa_001.md
A  docs/showcase/public_website_qa_001.md
A  frontend/public/media/mellytrade/aios-assembly.mp4
A  frontend/public/media/mellytrade/hero-command-core-poster.png
A  frontend/public/media/mellytrade/hero-command-core.png
A  frontend/public/media/mellytrade/manifest.json
A  frontend/public/media/mellytrade/product-showcase-finale.mp4
A  frontend/public/media/mellytrade/risk-layer-activation.mp4
M  frontend/src/App.tsx
A  frontend/src/components/public/CinematicHeroMedia.tsx
A  frontend/src/components/public/GitHubEvidenceSection.tsx
A  frontend/src/components/public/HeroAIOSShowcase.tsx
A  frontend/src/components/public/ProductPreviewGrid.tsx
A  frontend/src/components/public/PublicSafetyContract.tsx
A  frontend/src/components/public/PublicSiteFooter.tsx
A  frontend/src/components/public/PublicSiteNav.tsx
A  frontend/src/components/public/RecruiterCTA.tsx
A  frontend/src/components/public/SectionHUDChip.tsx
A  frontend/src/fixtures/mediaAssets.ts
A  frontend/src/fixtures/publicShowcaseFixtures.ts
A  frontend/src/pages/CaseStudyPage.tsx
A  frontend/src/pages/PublicLandingPage.tsx
A  frontend/src/pages/public-site.css
```

## Scope Confirmation

Every file above matches the expected scope list for this run exactly —
no out-of-scope files found. Explicitly re-verified zero diff on
`frontend/package.json`, `frontend/package-lock.json`, root
`package.json`/`package-lock.json`, and no matches for
package/lock/Dockerfile/docker-compose/CI-workflow/`.env`/broker/execution/
orchestrator/`app/main`/`api/` path patterns anywhere in the changed-file
list.

## Validation Evidence

```powershell
git diff --check     # clean
npx tsc -b            # clean
npm run build           # clean (dist/index.html + 1 CSS bundle + 1 JS bundle,
                         # media assets copy through to dist/media/mellytrade/*)
```

## Safety Review

Grepped every changed `.ts`/`.tsx` file for
buy/sell/execute/order/place-trade/PnL/broker-logo/API-key/secret/
live-trading/autotrade/account. All matches are one of: descriptive safety
copy explicitly stating a control is absent or blocked (e.g. "Autotrade is
off," "No live trading capability exists," "no order button"), a manifest
safety note recording an *absence* of forbidden content in generated media,
or the single previously-reviewed inert fixture value
(`direction: "BUY"` — plain, non-interactive text inside a demo table row,
confirmed safe across every prior QA pass on this branch). No interactive
control, event handler, order ticket, fake live-trading claim, or exposed
secret/credential exists anywhere in the diff.

## Draft PR Title

```text
feat(frontend): add public MellyTrade showcase and case study
```

## Draft PR Body

```md
## Summary

Adds a public MellyTrade showcase surface with a landing page and case-study page, preserving the existing internal terminal routes.

This PR introduces:
- public `/` landing page
- public `/case-study` page
- reusable public showcase components
- static public media pack under `frontend/public/media/mellytrade/`
- QA/evidence docs for media integration, final showcase QA, and branch scope audit

The public pages are read-only/showcase-only and do not call backend APIs.

## Safety

- No broker execution or live trading enabled.
- No Buy/Sell/Execute/Order controls added.
- No public-page `/api/*` calls.
- No secrets exposed.
- No backend/runtime/broker/config/package/deployment files changed.
- No package or lock files changed.
- Media assets are static and validated.
- Rejected media assets were not integrated.

## Validation

- `git diff --check`
- `npx tsc -b`
- `npm run build`

## Routes Verified

- `/`
- `/case-study`
- `/terminal`
- `/watchlist`
- `/mobile`
- `/terminal/paper-run-preview`

## Media Notes

The accepted hero poster is used as a static image on `/` and `/case-study`.

The accepted MP4 clips are present in `frontend/public/media/mellytrade/` and documented in the manifest, but are not rendered/autoplayed on public pages.

C1 was deliberately withheld from hero autoplay because in-context review made the amber line read too much like a "line-go-up" trading visual.

## Topology Note

This branch is currently stacked on top of `feature/alpaca-paper-readonly-card`, not directly on `main`.

Immediate base used for accurate feature scope:
`0425a46`

A direct comparison against `origin/main` may include unrelated parent-branch commits.

Before opening the PR, choose one:
1. Open as stacked PR against `feature/alpaca-paper-readonly-card`
2. Wait for parent branch to merge, then target `main`
3. Create a clean branch from `main` and replay only public showcase commits in a separate approved task
```

## Suggested Push Command, Do Not Run

```bash
git push -u origin feature/public-landing-case-study-001
```

## Suggested PR Command, Do Not Run

Stacked PR (Option A):

```bash
gh pr create \
  --base feature/alpaca-paper-readonly-card \
  --head feature/public-landing-case-study-001 \
  --title "feat(frontend): add public MellyTrade showcase and case study" \
  --body-file docs/showcase/pr_prep_001.md \
  --draft
```

Normal PR after parent merge (Option B):

```bash
gh pr create \
  --base main \
  --head feature/public-landing-case-study-001 \
  --title "feat(frontend): add public MellyTrade showcase and case study" \
  --body-file docs/showcase/pr_prep_001.md \
  --draft
```

Neither command was run in this session.

## User Decision Needed

1. **Is `feature/alpaca-paper-readonly-card` intentionally open right now**,
   or should the public showcase avoid depending on it?
2. If it's intentionally open: **proceed with Option A** (stacked PR
   against that branch) — lowest risk, no Git history changes needed.
3. If it's expected to merge soon: **proceed with Option B** (wait, then PR
   against `main`) — also low risk, just requires patience and a refresh
   after the parent merges.
4. If it's stale, abandoned, or blocked, and the showcase needs to ship
   independently: **approve Option C** as its own explicitly-scoped task
   (`MELLYTRADE-REPLAY-PUBLIC-SHOWCASE-ONTO-MAIN-001`) — this carries real
   Git risk (new branch, replay/cherry-pick of exactly these 7 commits'
   content) and should not be done casually or bundled into a "just also
   fix this" request.

## Next Recommended Run

Depends on the user's decision above:
- Stacked PR chosen → `MELLYTRADE-PUSH-STACKED-PR-001`
- Wait for parent chosen → `MELLYTRADE-WAIT-FOR-PARENT-MERGE-001`
- Independent PR against `main` chosen → `MELLYTRADE-REPLAY-PUBLIC-SHOWCASE-ONTO-MAIN-001`
- Still undecided → `MELLYTRADE-PR-TOPOLOGY-DECISION-001`

## Safety Confirmation

```text
Safety confirmation:
- No broker execution or live trading enabled.
- No Buy/Sell/Execute/Order controls added.
- No secrets printed or exposed.
- No backend/runtime/broker/config/package/deployment files changed by this run.
- No package or lock files changed by this run.
- No external APIs called.
- No Higgsfield MCP/media generation performed.
- No push, merge, deploy, reset, clean, delete, force, rebase, or cherry-pick operation performed.
```
