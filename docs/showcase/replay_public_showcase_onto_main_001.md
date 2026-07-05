# MellyTrade Replay Public Showcase Onto Main 001

> **Stopped before branch creation — dependency fixup required first.**
> Phases 1–3 (pre-flight, fetch, orphan dependency check) completed. Phases
> 4–10 (branch creation, replay, commit) were **not executed**, per this
> run's own stop condition: "orphan parent dependency is required but not
> present on updated main." No branch was created, no files were replayed,
> no commit beyond this report was made. The source branch
> (`feature/public-landing-case-study-001`) is untouched. No push, merge,
> rebase, or destructive Git operation was performed.
> **Run:** `MELLYTRADE-REPLAY-PUBLIC-SHOWCASE-ONTO-MAIN-001` · **Date:** 2026-07-05 · **Model:** Sonnet 5

## Outcome

**BLOCKED — real dependency found, not present on `origin/main`.** The
orphan-dependency check (Phase 3) found that `publicShowcaseFixtures.ts`
depends on a type-level change to `RiskPolicy` in
`frontend/src/lib/terminalApi.ts` that exists only in the local-only orphan
commit `b2b7303` — never pushed, never merged, not part of PR #273, and
confirmed absent from the freshly-fetched `origin/main`. Replaying the
public showcase paths onto a clean branch from current `origin/main` as
specified would produce a branch that **fails `npx tsc -b`** the moment
`publicShowcaseFixtures.ts` is checked, because it assigns 7 fields to a
`riskPolicy` object that `origin/main`'s current `RiskPolicy` type does not
declare. This was not executed against a real branch (stopped before
Phase 4), but the dependency is deterministic and does not require
speculation — TypeScript's excess-property checking on nested object
literals is well-defined behavior, confirmed by direct comparison of the
type definitions on both sides (below).

## Source Branch

- Branch: `feature/public-landing-case-study-001`
- Latest commit: `98439c6` (docs(showcase): decide public website PR
  topology) — matches expected; no newer commits found
- Upstream: none; not pushed (re-confirmed)
- Untouched by this run

## New Branch

**Not created.** `feature/public-landing-case-study-main-001` does not
exist locally or on remote (confirmed before and after this run).

## Updated Main Base

```
git fetch origin main
→ From https://github.com/Melly-999/alpha_data_scraper_ai
   * branch            main       -> FETCH_HEAD

git rev-parse origin/main
→ 995f0905d540f8758710c2c328191bf088ad48df
```

`origin/main` advanced significantly beyond the previously-cached
`17702b7` — it now includes a long series of automated
`📊 Auto-trade cycle: ...` commits (most recent: `995f090`, dated
2026-07-03). These appear to be scheduled/bot-authored commits from an
existing CI workflow in this repo (e.g. `trade-signal-commit.yml` /
`auto-commit-results.yml`, per `.github/workflows/` — not inspected in
depth in this run, out of scope). **Noted for awareness, not evaluated
further** — this run's only concern with `origin/main` is whether it
contains PR #273's merged content, which it does (see below).

## Parent PR / Topology Resolution

- `git merge-base --is-ancestor 3d0ad80ae802f20c42201f28d202f9314218547a origin/main` → **YES**. PR #273's merge commit is confirmed present in the freshly-fetched `origin/main`.
- `git merge-base --is-ancestor 4a0f61a72df58645c1071c2ff412b5e387bdbe1e origin/main` → **NO**, but this is expected and benign: `git log --pretty=%P -1 3d0ad80a` shows the merge commit has a **single parent** (`17702b7`), confirming PR #273 was merged via GitHub's "squash and merge," not a two-parent merge commit. The squashed diff is present in `origin/main`; the individual commit `4a0f61a` itself is not part of the ancestry chain, which is exactly how squash merges work — not a red flag.
- **Conclusion: topology resolution from `MELLYTRADE-PR-TOPOLOGY-DECISION-001` stands confirmed.** `origin/main` genuinely contains the parent branch's intended, reviewed, CI-passed content (up to `4a0f61a`) via the squash commit `3d0ad80a`.

## Orphan Parent Dependency Check

Inspected the three local-only orphan commits (`b2b7303`, `5e7f529`,
`0425a46` — everything between `4a0f61a` and the fork point) for any
dependency from the public showcase's expected replay files:

```
git diff --name-status 4a0f61a..0425a46
```

17 files touched, mostly unrelated docs (`agent_sessions/`,
`agent_skills/`, `docs/ai_workflow/*`, `docs/knowledge/*`,
`docs/design/mellytrade_cinematic_showcase_concept.md`). Three code/type
files are relevant to check:

1. **`frontend/src/components/terminal/RiskGuardrailsCard.tsx`** — changed
   to read all safety flags from the `policy` prop instead of `status`.
   **Not a blocking dependency by itself**: `publicShowcaseFixtures.ts`
   already populates *both* `riskStatus` and `riskPolicy` with identical,
   fully-valid values (confirmed by direct inspection of the fixture file),
   so the component renders correctly whether it reads from `status` or
   `policy`. This was originally done in the implementation run to satisfy
   the *fixed* component; it happens to also satisfy the *unfixed* one.

2. **`frontend/src/lib/terminalApi.ts`** — the `RiskPolicy` **type
   definition** itself gained 7 optional fields in this orphan range
   (`max_risk_per_trade_pct?`, `dry_run?`, `auto_trade?`, `read_only?`,
   `live_orders_blocked?`, `stop_loss_required?`, `take_profit_required?`).
   **This is the real, blocking dependency.**
   `publicShowcaseFixtures.ts` assigns exactly these 7 fields on its
   `riskPolicy: RiskPolicy`-typed object literal (part of
   `demoTerminalShellData: TerminalShellData`). Confirmed via
   `git show origin/main:frontend/src/lib/terminalApi.ts` that the current
   `origin/main` `RiskPolicy` type has only the original 4 fields
   (`min_confidence`, `daily_loss_cap_pct`, `open_position_cap`,
   `execution_enabled`) — the 7 extra fields are **absent**. TypeScript's
   excess-property checking on nested object literals assigned within a
   typed literal (exactly this fixture's pattern) would reject the 7
   extra properties as not existing on type `RiskPolicy`, failing
   `npx tsc -b` for the whole project.

3. **`frontend/src/components/terminal/OpenDesignTabsPanel.tsx`** — a
   one-line change (`data.riskStatus.live_orders_blocked` →
   `data.riskPolicy.live_orders_blocked`). **Not a dependency**: this file
   is not imported or referenced anywhere in `frontend/src/components/public/`,
   `PublicLandingPage.tsx`, `CaseStudyPage.tsx`, or
   `publicShowcaseFixtures.ts` (confirmed via grep — no matches).

**Result: one real, confirmed, blocking dependency** — the `RiskPolicy`
type extension in `frontend/src/lib/terminalApi.ts` — required by
`publicShowcaseFixtures.ts` and **not present** on the freshly-fetched
`origin/main`.

## Replay Method

**Not executed.** Per this run's Phase 3 instruction ("If not present and
required, stop and recommend: `MELLYTRADE-REPLAY-DEPENDENCY-FIXUP-001`"),
Phases 4 (branch creation) and 5 (path-based replay) were not attempted.
No `git switch -c`, no `git checkout -- <paths>` from the source branch,
and no new commit were performed.

## Files Replayed

None. No branch exists to replay onto.

## Forbidden Areas Check

Not applicable — no replay was performed. For reference, the orphan
dependency itself (`terminalApi.ts`'s `RiskPolicy` type) is a small,
additive, backward-compatible type change (optional fields only) inside an
existing shared frontend library file — not a backend, broker, execution,
config, package, lock, Docker, or CI file. Resolving it does not require
touching any forbidden area.

## Safety UI / Copy Check

Not applicable — no new code was written or replayed in this run.

## Media Check

Not applicable — media files were not touched in this run (no replay was
performed).

## Validation Commands

```powershell
git fetch origin main   # succeeded
```

`git diff --check`, `npx tsc -b`, and `npm run build` were **not re-run
against a new branch** in this run, since no new branch was created. The
current source branch (`feature/public-landing-case-study-001`) was left
exactly as it was at the start of this run (last validated clean in
`MELLYTRADE-PR-TOPOLOGY-DECISION-001`).

## Route Smoke Check

Not run — no new branch/build exists to smoke-test. Deferred to after the
dependency fixup and a subsequent successful replay.

## Known Limitations

- The dependency conclusion is based on direct comparison of type
  definitions and fixture content (deterministic, not run against a live
  `tsc` invocation on a real new branch, since none was created). High
  confidence given TypeScript's well-defined excess-property-check
  behavior, but the actual fixup run should still re-verify with a real
  `tsc -b` pass once the branch exists.
- `origin/main` has moved substantially (automated "Auto-trade cycle"
  commits observed) since this branch's original planning began. This
  run did not audit those commits' content or safety posture — out of
  scope for a showcase-replay task — but the eventual replay/fixup run
  should be aware `origin/main` is an active, frequently-updated branch,
  not a static reference point.
- Two smaller, non-blocking orphan-commit deltas
  (`RiskGuardrailsCard.tsx`'s status→policy read source,
  `OpenDesignTabsPanel.tsx`'s one-line prop-source change) were evaluated
  and found *not* to require carrying forward — documented above for the
  record, not because they block anything.

## Next Recommended Run

`MELLYTRADE-REPLAY-DEPENDENCY-FIXUP-001`

Scope for that run: on the new (not-yet-created)
`feature/public-landing-case-study-main-001` branch (or as a preparatory
step before creating it), add the 7 optional fields to the `RiskPolicy`
type in `frontend/src/lib/terminalApi.ts` — the smallest possible
type-only, backward-compatible change — then proceed with the path-based
replay exactly as specified in this run's Phases 4–10.

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
