# MellyTrade Replay Dependency Fixup 001

> **Successful replay onto a clean branch.** No push, no PR, no merge, no
> deploy, no backend/broker/runtime/safety/package/lock/Docker/CI file
> changed. Source branch untouched. All work performed in a separate `git
> worktree` so the source branch's dirty working tree was never touched.
> **Run:** `MELLYTRADE-REPLAY-DEPENDENCY-FIXUP-001` · **Date:** 2026-07-06 · **Model:** Sonnet 5

## Outcome

**Success.** The public showcase now exists on a clean branch built from
current `origin/main`, with the one required type-only dependency fix
applied, all 27 expected showcase paths replayed, and full validation
(`tsc -b`, `npm run build`, safety grep, 6-route smoke check) passing. The
branch is ready for `MELLYTRADE-CLEAN-BRANCH-FINAL-QA-001`.

## Source Branch

- Branch: `feature/public-landing-case-study-001`
- Latest commit at time of replay: `b152874`
- **Left completely untouched.** All replay operations read from this
  branch via `git checkout <branch> -- <paths>` executed from within the
  new branch's own worktree; no commits, resets, or working-tree changes
  were made to the source branch itself.

## New Clean Branch

- Branch: `feature/public-landing-case-study-main-001`
- Created via `git worktree add ../alpha_data_scraper_ai-showcase-main -b feature/public-landing-case-study-main-001 origin/main`, **not** `git switch -c`, because the main worktree has 79 pre-existing unrelated dirty files (including `README.md` and two `docs/design/*` files) that would have been overwritten by a direct `switch`/`checkout` — using a separate worktree guarantees those files were never touched.
- `git worktree add` auto-configured an upstream tracking reference to `origin/main` as a side effect (Git's default `branch.autoSetupMerge` behavior). This was **immediately removed** with `git branch --unset-upstream`, confirmed via `git status --branch --short` showing no tracking marker afterward — the branch has no upstream, exactly as required.
- No upstream; not pushed.

## Updated Main Base

```
git fetch origin main
→ succeeded

git rev-parse origin/main
→ 995f0905d540f8758710c2c328191bf088ad48df   (same tip as the prior blocked-replay run — no further remote movement)

git merge-base --is-ancestor 3d0ad80a origin/main
→ confirmed: PR #273's merge commit is an ancestor of origin/main
```

`origin/main` has advanced substantially since the branch's original
planning (a long series of automated `📊 Auto-trade cycle: ...` commits are
visible in its history — noted, not evaluated, out of scope for this task).

## Dependency Blocker Resolved

Re-confirmed the exact diff from the orphan commit before touching anything:

```
git diff b2b7303^ b2b7303 -- frontend/src/lib/terminalApi.ts
```

This showed **two** distinct changes bundled in that one commit:
1. A type-only extension to `RiskPolicy` (7 new optional fields).
2. A runtime change to `getRiskPolicy()`'s fallback object literal, adding
   concrete values for those same 7 fields.

**Only change (1) was applied.** Change (2) was deliberately **not**
replayed, per this task's explicit instruction ("Do not change runtime
functions... Do not change defaults"). Since the 7 new fields are optional
(`?`), `getRiskPolicy()`'s existing fallback object (which does not set
them) remains perfectly valid against the extended type — no compile error,
zero behavior change.

## RiskPolicy Type-Only Fix

Applied directly on the new branch (not replayed from the source branch,
since this file was never part of the public-showcase replay path list):

```diff
 export type RiskPolicy = {
   min_confidence: number;
   daily_loss_cap_pct: number;
   open_position_cap: number;
   execution_enabled: false;
+  // Safety flags carried by /api/risk/policy alongside the runtime gates.
+  // Optional because older backend builds may omit them.
+  max_risk_per_trade_pct?: number;
+  dry_run?: boolean;
+  auto_trade?: boolean;
+  read_only?: boolean;
+  live_orders_blocked?: boolean;
+  stop_loss_required?: boolean;
+  take_profit_required?: boolean;
 };
```

Verified via `git diff -- frontend/src/lib/terminalApi.ts` that this is the
**entire** diff to this file — no function bodies, API call paths, broker
logic, or default values were touched. `getRiskPolicy()` and every other
export in the file are byte-for-byte unchanged from `origin/main`.

## Replay Method

Controlled path-based replay via `git checkout feature/public-landing-case-study-001 -- <paths>`, executed from the new branch's worktree — not a cherry-pick, not a rebase. All 17 requested paths existed on the source branch and were replayed successfully; none were missing.

## Files Replayed

`git diff --stat HEAD`: **31 files changed, 4596 insertions(+), 1 deletion(-)**
— the 27 files from the original branch-scope audit's expected list, plus
`pr_prep_001.md`, `pr_topology_decision_001.md`, and
`replay_public_showcase_onto_main_001.md` (added to the source branch after
that audit but still within the same "showcase docs" scope), plus the
1-file, 8-line `RiskPolicy` type fix.

```
A  docs/design/mellytrade_website_design_pack_001.md
A  docs/showcase/branch_scope_audit_001.md
A  docs/showcase/media_integration_001.md
A  docs/showcase/pr_prep_001.md
A  docs/showcase/pr_topology_decision_001.md
A  docs/showcase/pre_media_snapshot_001.md
A  docs/showcase/public_showcase_final_qa_001.md
A  docs/showcase/public_website_qa_001.md
A  docs/showcase/replay_public_showcase_onto_main_001.md
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
M  frontend/src/lib/terminalApi.ts
A  frontend/src/pages/CaseStudyPage.tsx
A  frontend/src/pages/PublicLandingPage.tsx
A  frontend/src/pages/public-site.css
```

## Forbidden Areas Check

```
grep -iE "package\.json|package-lock|pnpm-lock|yarn\.lock|dockerfile|
           docker-compose|\.github/workflows|\.env|requirements|
           config\.json|broker/|execution/|scripts/orchestrator|
           app/main|^api/"
→ NO FORBIDDEN-AREA FILES FOUND
```

No package/lock, backend, broker, execution, safety-config, Docker, or CI
workflow file appears anywhere in the diff.

## Safety UI / Copy Check

Grepped every changed `.ts`/`.tsx` file (including `terminalApi.ts`, now
part of the diff for the first time in this run's context) for
buy/sell/execute/order/place-trade/PnL/account/broker-logo/API-key/secret/
live-trading/autotrade. All matches fall into one of: descriptive safety
copy already reviewed across every prior QA pass on the source branch, type
declarations/union literals (`"BUY" | "SELL" | "HOLD"`), or **pre-existing**
content in `terminalApi.ts` that predates this run entirely (this file was
fetched from `origin/main`, not authored here — the only line I added was
the 8-line type extension shown above). No interactive control, event
handler, or exposed secret exists anywhere in the diff.

## Media Check

All 6 expected files present under `frontend/public/media/mellytrade/`;
confirmed copied through to `dist/media/mellytrade/*` during the build. No
`rejected/` or `review_crops/` content present anywhere.

## Validation Commands

```powershell
git diff --check     # clean
npx tsc -b            # clean — confirms the type fix resolves the dependency exactly as predicted
npm run build           # clean (99→102 modules; new build includes assets not present in the older source-branch build, reflecting origin/main's own evolution)
```

`node_modules` was not installed via `npm install` — a symlink to the
already-installed `node_modules` in the main worktree
(`alpha_data_scraper_ai/frontend/node_modules`) was created solely to run
`tsc`/`vite build` without a network fetch, then **removed** immediately
after validation completed (confirmed absent from `git status` before this
report was written).

## Route Smoke Check

Live preview run against the new branch (`showcase-main-frontend` launch
config, port 5173, no backend running):

| Route | Result |
|---|---|
| `/` | Static poster `<img>` hero, CTA `href="/terminal"` confirmed, 0 console errors, 0 `/api/*` calls, 0 `.mp4` requests |
| `/case-study` | Poster hero renders, `h1` correct, 0 console errors |
| `/terminal` | `.terminal-root` renders, 0 console errors |
| `/watchlist` | Renders, 0 console errors |
| `/mobile` | Renders fully (7173 chars body text), 0 console errors |
| `/terminal/paper-run-preview` | `.terminal-root` renders, 0 console errors |

Responsive check on `/` and `/case-study`: no horizontal overflow at
desktop (1280×900: -15, i.e. scrollbar-adjusted zero), tablet (768×1024:
same), or mobile (375×812: 0). An initial `overflow: 19` reading on
`/case-study` was traced to the preview tool's default 280×389 window
before an explicit resize — not a real defect; re-measured at 0 once
resized to the standard presets.

## Known Limitations

- `origin/main` includes an unaudited stream of automated "Auto-trade
  cycle" commits and newer, unrelated frontend files (e.g.
  `AlpacaPaperOrderPreview.tsx`) not present when the original showcase
  branch was built — this run did not evaluate that content; it is outside
  this task's scope (showcase replay + one type fix only).
- Live route smoke was run without a backend process, matching every prior
  QA pass on this feature; `/watchlist`'s backend-unavailable fallback
  behavior (unchanged, pre-existing) was not re-verified in detail here
  since it was already characterized in earlier QA runs.
- The `.claude/launch.json` at the workspace root gained one new entry
  (`showcase-main-frontend`, pointing at the new worktree) to enable this
  route smoke check — a local dev-tooling config, not a deployment or CI
  file, consistent with the pattern used in earlier runs on the source
  branch.

## Next Recommended Run

`MELLYTRADE-CLEAN-BRANCH-FINAL-QA-001`

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
- No push, merge, deploy, reset, clean, delete, force, rebase, or history rewrite operation performed.
- Existing source branch was preserved.
```
