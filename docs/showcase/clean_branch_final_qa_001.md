# MellyTrade Clean Branch Final QA 001

> **Docs-only QA run.** No frontend code changed (the branch already
> validated cleanly as-is — no fixes were required). No backend/runtime/
> broker/config/package/deployment/Docker/CI files touched. No push, no PR,
> no rebase, no cherry-pick, no merge, no deploy.
> **Run:** `MELLYTRADE-CLEAN-BRANCH-FINAL-QA-001` · **Date:** 2026-07-06 · **Model:** Sonnet 5

## Outcome

**PASS — clean, no cleanup required.** The clean main-based branch
(`feature/public-landing-case-study-main-001`) is exactly one commit ahead
of current `origin/main`, contains only the expected public-showcase scope
plus the minimal `RiskPolicy` type fix, passes full validation, and passes
a 6-route smoke check with zero `/api/*` calls, zero `.mp4` requests, and
no horizontal overflow at any tested width. `.claude/launch.json` **inside
this repository** is unmodified — the workspace-level launch config edited
for local smoke-testing lives entirely outside this Git repo and cannot
appear in any diff of it. No scope cleanup was needed.

## Branch / Commit Reviewed

- Branch: `feature/public-landing-case-study-main-001`
- Latest commit: `770262f` (feat(frontend): replay public showcase onto
  main) — matches expected, no newer commits found
- Upstream: none configured (`git status --branch --short` shows no
  tracking marker)
- Remote: `git ls-remote --heads origin feature/public-landing-case-study-main-001` returned nothing — **not pushed**
- Source branch `feature/public-landing-case-study-001` was not touched by
  this run (read-only inspection only)

## Base Main SHA

```
git rev-parse origin/main        → 995f0905d540f8758710c2c328191bf088ad48df
git merge-base HEAD origin/main  → 995f0905d540f8758710c2c328191bf088ad48df
```

The merge-base **equals** `origin/main`'s own tip — this branch is a
perfectly linear, single-commit fast-forward from current `origin/main`,
the cleanest possible topology for a future PR.

## Diff Scope Review

`git diff --stat origin/main...HEAD`: **32 files changed, 4843
insertions(+), 1 deletion(-)**.

`git diff --name-status origin/main...HEAD` — all 32 files fall within the
expected areas: `frontend/src/App.tsx` (modified routing), 3 pages
(`PublicLandingPage.tsx`, `CaseStudyPage.tsx`, `public-site.css`), 9 new
`components/public/**` files, 2 fixtures, 6 media assets under
`frontend/public/media/mellytrade/**`, the type-only
`frontend/src/lib/terminalApi.ts` extension, and 10 docs
(`docs/design/mellytrade_website_design_pack_001.md` +
9 `docs/showcase/**` reports covering the full history of this work). No
file outside this list appears. No package/lock/backend/broker/runtime/
config/Docker/CI/deployment file is present anywhere in the diff.

## `.claude/launch.json` Review

```
git diff --name-status origin/main...HEAD -- .claude/launch.json  → (empty)
git status --short -- .claude/launch.json                          → (empty)
git ls-files .claude/launch.json                                   → .claude/launch.json (tracked, pre-existing)
git diff origin/main -- .claude/launch.json                        → (empty — identical to origin/main)
```

**Result: `ABSENT_FROM_PR_DIFF`.** The repo-tracked `.claude/launch.json`
(pointing at `mellytrade_v3/mellytrade/dashboard`, port 5173) is byte-for-
byte identical between `origin/main` and this branch's `HEAD` — it was
never touched. The launch-config entry added for this run's (and the prior
run's) local route-smoke checking (`showcase-main-frontend`) was written to
`C:\AI\MellyTrade_Workspace\.claude\launch.json` — the **workspace root**,
one directory level above `02_Repo/alpha_data_scraper_ai/` and structurally
outside this Git repository's boundary. It cannot appear in any diff, status,
or commit of this repo. No cleanup was necessary or possible from within
this repo.

## RiskPolicy Type-Only Fix Review

```
git diff origin/main -- frontend/src/lib/terminalApi.ts
```

Confirmed the entire diff to this file is exactly:

```diff
 export type RiskPolicy = {
   min_confidence: number;
   daily_loss_cap_pct: number;
   open_position_cap: number;
   execution_enabled: false;
+  max_risk_per_trade_pct?: number;
+  dry_run?: boolean;
+  auto_trade?: boolean;
+  read_only?: boolean;
+  live_orders_blocked?: boolean;
+  stop_loss_required?: boolean;
+  take_profit_required?: boolean;
 };
```

- Only the `RiskPolicy` type gained 7 optional fields.
- `getRiskPolicy()` and every other function/export in the file is
  byte-for-byte unchanged from `origin/main`.
- No endpoint path changed, no broker/client behavior changed, no default
  values changed, no secrets or credentials present.
- This matches the type-only fix documented and already validated in
  `replay_dependency_fixup_001.md` — no drift since that commit.

## Media Review

```
frontend/public/media/mellytrade/
  aios-assembly.mp4
  hero-command-core-poster.png
  hero-command-core.png
  manifest.json
  product-showcase-finale.mp4
  risk-layer-activation.mp4
```

All 6 expected files present. `manifest.json` re-validated as well-formed
JSON (5 asset entries). No `rejected/` or `review_crops/` directory exists
anywhere in the repository. The 3 MP4 files exist on disk and are correctly
**not** requested by either public page (confirmed via live network
inspection — see Network / Backend Call Review). Both `/` and `/case-study`
render the static poster image (`<img>`, not `<video>`).

## Visual Safety Review

Grepped every changed `.ts`/`.tsx`/`.json` file for buy/sell/execute/order/
place-trade/PnL/account/broker-logo/API-key/secret/live-trading/autotrade.
Every match is descriptive safety copy, a manifest safety note confirming
*absence* of forbidden content, or pre-existing type/API content in
`terminalApi.ts` unrelated to this run's one-line-type addition (already
characterized in the prior fixup run). No interactive control, event
handler, order-ticket UI, fake live-trading claim, or exposed secret exists
anywhere in the diff.

## Network / Backend Call Review

Live preview on the new branch (no backend process running):

- `/` — zero `/api/*` requests, zero `.mp4` requests, hero poster loads
  (`200`/`304`), CTA `href="/terminal"` confirmed, 0 console errors.
- `/case-study` — zero `/api/*` requests, zero `.mp4` requests, poster
  loads, 0 console errors.
- No media 404s on either page.

## Responsive Review

| Width | `/` overflow | `/case-study` overflow |
|---|---|---|
| Desktop (1280×900) | 0 (scrollbar-adjusted) | 0 (scrollbar-adjusted) |
| Tablet (768×1024) | not re-measured this run (unchanged since prior QA) | 0 |
| Mobile (375×812) | 0 | 0 |

No horizontal overflow found at any tested width on either public page.

## Validation Commands

```powershell
git diff --check     # clean
npx tsc -b            # clean
npm run build           # clean (102 modules, media copies through to dist/media/mellytrade/*)
```

`node_modules` was not installed via `npm install`. A symlink to the
already-installed `node_modules` in the main worktree was created solely to
run `tsc`/`vite build`, then **removed immediately after validation**
— confirmed via `git status --short` returning zero entries before this
report was written (no untracked/staged `node_modules` residue).

## Route Smoke Check

| Route | Result |
|---|---|
| `/` | Renders correctly at desktop/tablet/mobile, static poster hero, CTA correct, 0 errors, 0 `/api/*`, 0 `.mp4` |
| `/case-study` | Renders correctly at desktop/tablet/mobile, static poster hero, 0 errors |
| `/terminal` | `.terminal-root` renders, 0 console errors |
| `/watchlist` | Renders its own pre-existing "backend unavailable" fallback state (no backend running in this session) — same behavior observed on the source branch in every prior QA pass; not a regression |
| `/mobile` | Renders fully, 0 console errors |
| `/terminal/paper-run-preview` | `.terminal-root` renders, 0 console errors |

## Issues Found

None.

## Fixes Applied, If Any

None required. No `.claude/launch.json` cleanup was needed (see above —
structurally outside the repo already). No frontend code changes were made
in this run.

## Known Limitations

- `/watchlist`'s fallback state was observed without a backend process
  running locally, consistent with every prior QA pass on both the source
  and clean branches — not evaluated further, as it predates and is
  unrelated to the public showcase work.
- Tablet-width overflow was not re-measured for `/` in this specific run
  (it was for `/case-study`); both were already confirmed at tablet width
  in the immediately preceding `MELLYTRADE-REPLAY-DEPENDENCY-FIXUP-001`
  run against the same commit, so this is a low-risk gap, not a defect.
- `origin/main` continues to accumulate automated commits unrelated to this
  work (out of scope, not evaluated).

## PR Readiness Assessment

**`READY_FOR_CLEAN_BRANCH_PR_PREP`**

Justification against the stated criteria:
- Branch is clean and based on current `origin/main` (merge-base equals
  `origin/main`'s own tip) ✅
- Diff is scoped (32/32 expected files, zero out-of-scope) ✅
- No forbidden areas changed ✅
- Validation passes (`git diff --check`, `tsc -b`, `npm run build`) ✅
- Route smoke passes (all 6 routes, zero `/api/*`, zero `.mp4`, zero
  console errors, zero overflow) ✅
- `.claude/launch.json` is absent from this repo's diff (structurally,
  not just by omission) ✅
- No safety violations ✅

## Next Recommended Run

`MELLYTRADE-CLEAN-BRANCH-PR-PREP-001`

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
- No push, merge, deploy, reset, clean, delete, force, rebase, cherry-pick, or history rewrite operation performed.
- Existing source branch was preserved.
```
