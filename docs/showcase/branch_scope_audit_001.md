# MellyTrade Branch Scope Audit 001

> **Audit-only run.** Read-only Git inspection plus this docs-only report.
> No frontend/backend/runtime/broker/config/package/deployment files
> changed. No push, merge, deploy, reset, clean, delete, or force operation
> performed.
> **Run:** `MELLYTRADE-BRANCH-SCOPE-AUDIT-001` · **Date:** 2026-07-05 · **Model:** Sonnet 5

## Outcome

**READY_FOR_PR_PREP, with one critical topology note for the PR-prep run to
resolve first.** This branch's own 6 commits are cleanly scoped to exactly
the 26 expected public-showcase files — no backend, runtime, broker, config,
package, lock, or deployment files were touched, no forbidden UI controls or
secrets exist, and validation is fully clean. The one thing PR-prep must
handle deliberately: **this branch was not created from `main`** — it forks
from `feature/alpaca-paper-readonly-card`, an unmerged sibling branch — so a
naive PR straight to `main` would also carry that branch's 4 unrelated
commits. See "Base Comparison" below.

## Branch / Commit Reviewed

- Current branch: `feature/public-landing-case-study-001`
- Latest local commit: `d98f292` (docs(showcase): add public website final QA)
- Upstream: none configured — confirmed via `git status --branch --short`
  showing no `...origin/...` tracking marker; not pushed
- Repo root: `C:/AI/MellyTrade_Workspace/02_Repo/alpha_data_scraper_ai` —
  correct canonical project folder, not a stray path

## Repo Topology

```
git rev-parse --show-toplevel  → C:/AI/MellyTrade_Workspace/02_Repo/alpha_data_scraper_ai
git branch --show-current      → feature/public-landing-case-study-001
git status --branch --short    → ## feature/public-landing-case-study-001  (no upstream)
git remote -v                  → origin  https://github.com/Melly-999/alpha_data_scraper_ai.git
                                  gitlab  https://gitlab.com/Melly-999/mellytrade-sevalla-demo.git
```

No fetch was performed. `origin/main` and local `main` were already present
as cached refs from a prior session — their freshness relative to the
current GitHub state is **unknown** (not re-verified over the network in
this run, per the "no external network operations" constraint).

## Base Comparison

**This branch does not fork from `main`.** Topology check:

```
git branch --all --contains 0425a46
  feature/alpaca-paper-readonly-card
* feature/public-landing-case-study-001
```

`feature/public-landing-case-study-001` was created at commit `0425a46`,
which is the tip of `feature/alpaca-paper-readonly-card` — an unrelated,
**unmerged** sibling feature branch (verified:
`git merge-base --is-ancestor feature/alpaca-paper-readonly-card origin/main`
→ not an ancestor, i.e. not yet merged). That parent branch is itself 4
commits ahead of `origin/main`.

Three merge-base candidates were computed:

| Base | Merge-base SHA | What it represents |
|---|---|---|
| `origin/main` | `17702b7` | Includes this branch's 6 commits **plus** the 4 unrelated commits already on `feature/alpaca-paper-readonly-card` — not a clean scope view |
| local `main` | `17702b7` | Same as above (local `main` and `origin/main` currently agree) |
| `feature/alpaca-paper-readonly-card` (the actual fork point) | `0425a46` | The exact, clean boundary of this feature branch's own work |

**Used for this audit: `0425a46`** (the true fork point) — this is the only
base that isolates exactly what this branch itself contributed, without
conflating it with the parent branch's unrelated, unmerged history.
Confirmed via `git log --oneline feature/alpaca-paper-readonly-card..HEAD`
that this yields exactly the 6 known commits and nothing else.

**PR-prep implication:** opening a PR from this branch directly against
`main` on GitHub will show all 10 commits (4 inherited + 6 own) unless one
of the following happens first: (a) `feature/alpaca-paper-readonly-card` is
merged to `main` and this branch is rebased onto the new `main` tip, (b) a
stacked PR is opened targeting `feature/alpaca-paper-readonly-card` instead
of `main`, or (c) this branch is rebased onto `main` directly (dropping the
dependency, if the parent branch's changes aren't actually needed). This
decision belongs to the user / `MELLYTRADE-PR-PREP-001`, not this audit.

## Commit Chain

```
d98f292 (HEAD -> feature/public-landing-case-study-001) docs(showcase): add public website final QA
ba6fc80 feat(frontend): integrate public website media pack
bb8aa69 feat(frontend): prepare public website media slots
5d2ecaa docs(showcase): add pre-media snapshot and readiness check
99bde92 fix(frontend): QA fixes for public landing/case-study a11y and touch targets
da74565 feat(frontend): add public landing and case-study routes
0425a46 (feature/alpaca-paper-readonly-card) docs(ai): document operator skill adoption decision   ← fork point, not part of this feature
```

All 6 commits match the expected chain exactly as provided in this run's
context. No extra, missing, or reordered commits.

## Changed Files Summary

`git diff --stat 0425a46...HEAD`: **26 files changed, 3625 insertions(+), 1
deletion(-)**. The single deletion is the removed `/ → /terminal` redirect
line in `App.tsx`, replaced by two new routes.

By category:
- Frontend pages/routing: 4 (`App.tsx` modified, `PublicLandingPage.tsx`,
  `CaseStudyPage.tsx`, `public-site.css` new)
- Frontend public components: 9 (all new, under `components/public/`)
- Frontend fixtures: 2 (`mediaAssets.ts`, `publicShowcaseFixtures.ts`)
- Media assets: 6 (under `frontend/public/media/mellytrade/`)
- Docs: 5 (design pack implementation notes + 4 showcase QA/evidence reports)

## Expected Files

All 26 changed files matched the expected-file-areas list from this run's
brief:

- `frontend/src/App.tsx` ✅
- `frontend/src/pages/PublicLandingPage.tsx` ✅
- `frontend/src/pages/CaseStudyPage.tsx` ✅
- `frontend/src/pages/public-site.css` ✅
- `frontend/src/components/public/**` (9 files) ✅
- `frontend/src/fixtures/publicShowcaseFixtures.ts` ✅
- `frontend/src/fixtures/mediaAssets.ts` ✅
- `frontend/public/media/mellytrade/**` (6 files) ✅
- `docs/design/mellytrade_website_design_pack_001.md` ✅
- `docs/showcase/public_website_qa_001.md` ✅
- `docs/showcase/pre_media_snapshot_001.md` ✅
- `docs/showcase/media_integration_001.md` ✅
- `docs/showcase/public_showcase_final_qa_001.md` ✅

## Needs-Review Files

None.

## Out-of-Scope Files

None. `docs/design/mellytrade_aios_platform_scope_001.md` (listed as
"if branch includes it" in the expected areas) is **not** part of this
branch's commits — it exists only as an untracked working-tree file (see
Unrelated Dirty Files below), so there is nothing to flag here.

## Forbidden Areas Check

Explicitly checked `git diff --name-only 0425a46...HEAD` against backend,
broker, execution, config, package/lock, Docker, CI workflow, and env-file
patterns:

```
grep -iE "package\.json|package-lock|pnpm-lock|yarn\.lock|dockerfile|
           docker-compose|\.github/workflows|\.env|requirements|
           config\.json|broker/|execution/|scripts/orchestrator|
           app/main|api/"
→ NO FORBIDDEN-AREA FILES FOUND
```

Also explicitly confirmed zero diff on `frontend/package.json`,
`frontend/package-lock.json`, root `package.json`/`package-lock.json`, and
the Python `requirements*.txt` files. **No backend, runtime, broker,
execution, safety-config, package, lock, Docker, CI, or secrets file was
touched by this branch.**

## Safety UI / Copy Check

Grepped all changed `.ts`/`.tsx`/`.css`/`.json`/`.md` files for
Buy/Sell/Execute/Order/PlaceTrade/PnL/account/broker-logo/API-key/secret/
live-trading/autotrade. Every match across all 12 flagged files is one of:
descriptive safety copy explicitly stating a control is absent (e.g.
"Autotrade is off," "No live trading capability exists," "no order button"),
a manifest safety note recording an *absence* of forbidden content in
generated media, or the previously-reviewed inert fixture value
(`direction: "BUY"` — plain text inside a non-interactive demo table row,
already confirmed safe in the original implementation QA and every
subsequent QA pass on this branch). No interactive control, event handler,
or exposed secret/credential exists anywhere in the diff.

## Media Scope Check

All 6 files under `frontend/public/media/mellytrade/` are present and were
added in the `ba6fc80` commit: `hero-command-core.png`,
`hero-command-core-poster.png`, `aios-assembly.mp4`,
`risk-layer-activation.mp4`, `product-showcase-finale.mp4`,
`manifest.json`. No `rejected/` or `review_crops/` content exists anywhere
in the repo or in this branch's history — confirmed by directory listing
(no matches for `*rejected*` / `*review_crop*` under `frontend/public/`).

## Validation Commands

```powershell
git diff --check     # clean
npx tsc -b            # clean
npm run build           # clean
```

All three pass with no errors or warnings requiring action (only the
pre-existing, benign CRLF line-ending notices from Git on Windows, unrelated
to code correctness).

## Unrelated Dirty Files

`git status --short` reports 79 entries in the working tree beyond this
branch's own committed history — the same set observed identically in
every prior QA/audit pass on this branch this session (docs like
`docs/architecture/BROKER_ARCHITECTURE.md`, `docs/design/
mellytrade_aios_platform_scope_001.md`, `orchestrator/`, `scripts/
orchestrator_denylist.json`, `tests/orchestrator/`, session logs under
`agent_sessions/`, etc.). **None of these files are staged, none overlap
with this branch's 26 committed files, and none were touched by this
audit.** A few of these untracked paths sound sensitive by name (broker
architecture docs, an orchestrator denylist) — worth flagging that whoever
owns that separate work should commit or clean it up in its own session;
it is explicitly out of scope for this audit to act on it.

## PR Readiness Assessment

**`READY_FOR_PR_PREP`**

Justification against the stated criteria:
- Changed files are scoped: yes (26/26 expected) ✅
- No forbidden areas changed: yes ✅
- Validation passes: yes (`git diff --check`, `tsc -b`, `npm run build` all clean) ✅
- Final QA passed: yes (`docs/showcase/public_showcase_final_qa_001.md` — PASS) ✅
- No package/lock/backend/runtime/deployment changes: confirmed ✅
- No safety violations: confirmed ✅

**Caveat carried forward, not a blocker for this branch's own content:** the
branch's base is an unmerged sibling branch, not `main`. `MELLYTRADE-PR-PREP-001`
should decide and document the PR strategy (rebase onto `main`, target the
parent branch, or wait for the parent to merge) before opening anything on
GitHub.

## Recommended Next Run

`MELLYTRADE-PR-PREP-001`

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
- No push, merge, deploy, reset, clean, delete, or force operation performed.
```
