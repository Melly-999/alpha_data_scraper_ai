# MellyTrade PR Topology Decision 001

> **Docs-only, read-only run.** Only local read-only Git commands and
> read-only GitHub metadata checks (`git ls-remote`, `gh pr list`, `gh pr
> view`) were used. No `git fetch`, no push, no PR opened, no rebase, no
> cherry-pick, no merge. No frontend/backend/runtime/broker/config/package/
> deployment files changed.
> **Run:** `MELLYTRADE-PR-TOPOLOGY-DECISION-001` · **Date:** 2026-07-05 · **Model:** Sonnet 5

## Outcome

**Resolved — the topology question has a clear, evidence-based answer, and
it overturns the working assumption from the prior two runs.** The "parent"
branch, `feature/alpaca-paper-readonly-card`, is not an open or blocked
sibling — **its PR (#273) already merged into `main` on 2026-06-10**, with
all CI checks green. What looked like "stacked on an unmerged branch" is
actually: this branch was forked from a *local-only* point 3 commits past
what got merged, and those 3 extra commits were never pushed or PR'd. The
correct path forward is **Option C — replay the public showcase commits
onto a clean branch from (current) `main`** — Options A and B are no longer
applicable because there is no open parent PR to stack against or wait for.

## Branch / Commit Reviewed

- Branch: `feature/public-landing-case-study-001`
- Latest local commit: `c61b74e` (docs(showcase): prepare public website PR)
- Repo root: `C:/AI/MellyTrade_Workspace/02_Repo/alpha_data_scraper_ai` — confirmed canonical
- Upstream: none configured; not pushed (confirmed again — see Remote Branch Check)

## Local Topology

```
git branch --contains 0425a46   → feature/alpaca-paper-readonly-card, feature/public-landing-case-study-001
git branch --contains c61b74e   → feature/public-landing-case-study-001 (only)
git merge-base HEAD origin/main → 17702b7 (cached, unchanged from prior audits)
git log --oneline 0425a46..HEAD → 8 commits (the 7 known + c61b74e itself)
git log --oneline origin/main..HEAD → 12 commits (4 parent-branch + 8 own)
```

Unchanged from the prior two audits — this confirms no local state drift
since `MELLYTRADE-PR-PREP-001`.

Commit chain around the fork point, with remote-tracking decorations:

```
0425a46 (feature/alpaca-paper-readonly-card)          docs(ai): document operator skill adoption decision   ← local fork point (HEAD~8)
5e7f529                                                docs(ai): review operator bootstrap pack
b2b7303                                                fix(terminal): read safety flags from RiskPolicy, not RiskStatus
4a0f61a (origin/feature/alpaca-paper-readonly-card)    feat(frontend): add Alpaca Paper read-only status card   ← remote tip (cached)
17702b7                                                fix(desktop): allow Tauri desktop origins   ← origin/main merge-base (cached)
```

**Key observation:** the local `feature/alpaca-paper-readonly-card` branch
is 3 commits ahead of its own remote tracking ref (`b2b7303`, `5e7f529`,
`0425a46`) — these 3 commits exist only in this local worktree and were
never pushed to `origin/feature/alpaca-paper-readonly-card`.

## Remote Branch Check

```
git ls-remote --heads origin feature/alpaca-paper-readonly-card
→ 4a0f61a72df58645c1071c2ff412b5e387bdbe1e  refs/heads/feature/alpaca-paper-readonly-card
```

- **Exists on remote: yes**, at `4a0f61a` — exactly matching the cached
  `origin/feature/alpaca-paper-readonly-card` ref, confirming that cached
  ref is currently accurate (not stale).
- The branch was **not deleted** after its PR merged (still present on
  `origin` at the pre-merge tip).

```
git ls-remote --heads origin feature/public-landing-case-study-001
→ (no output)
```

- **Exists on remote: no.** Confirms `feature/public-landing-case-study-001`
  has never been pushed — consistent with every prior audit.

## Parent PR Check

```
gh pr list --head feature/alpaca-paper-readonly-card --state all
→ #273  feat(frontend): add Alpaca Paper read-only status card  feature/alpaca-paper-readonly-card  MERGED  2026-06-09T18:42:15Z
```

`gh pr view 273` detail:

- **State: MERGED**
- Base: `main` · Head: `feature/alpaca-paper-readonly-card`
- Merged at: **2026-06-10T08:43:24Z**
- Merge commit: `3d0ad80ae802f20c42201f28d202f9314218547a`
- All status checks **SUCCESS**: Docker Build & Push, Playwright e2e,
  Pytest CI (test + quality), Security Scan (Bandit SAST, Dependency
  Vulnerability Audit, Secret Scanning), CodeRabbit, Sourcery review, two
  Vercel preview checks.

**This is the decisive fact.** The parent branch's own PR completed and
merged nearly a month before this audit. There is no open PR to stack
against and nothing to wait for.

**Stale-cache implication:** since `3d0ad80a` (the PR #273 merge commit)
postdates this session's cached `origin/main` (merge-base `17702b7`, which
sits earlier in the same commit line than the merged branch's tip), the
locally cached `origin/main` ref is **confirmed stale** — real `main` on
GitHub is at least one merge ahead of what this session has cached. No
`git fetch` was run to correct this (out of scope for a read-only topology
check per this run's rules); the next run that actually creates a new
branch from `main` must fetch first.

## Public Showcase PR Check

```
gh pr list --head feature/public-landing-case-study-001 --state all
→ (no output)
```

No PR exists yet for this branch, open or closed — expected, since it has
never been pushed.

## Base Comparison

Unchanged from `MELLYTRADE-PR-PREP-001`: `origin/main`'s cached merge-base
(`17702b7`) predates both the PR #273 merge and this branch's actual fork
point (`0425a46`), so a raw `origin/main` diff would both (a) miss the fact
that the parent's main content is already upstream, and (b) still show the
3 orphaned local-only parent commits as part of any future replay. The
accurate view requires accounting for the PR #273 merge, which is now
confirmed via `gh pr view` rather than assumed.

## Option A — Stacked PR

**Not appropriate.** A stacked PR requires an active/open parent PR to
target. PR #273 is `MERGED`, not open — GitHub would not offer a normal
"stack on this" relationship, and opening a new PR with
`--base feature/alpaca-paper-readonly-card` against an already-merged,
otherwise-dead branch would be confusing to any reviewer and technically
pointless, since that branch's real destination (`main`) already has its
content.

## Option B — Wait For Parent Merge

**Not appropriate — already happened.** The wait condition (parent PR
close to merge) is moot; it merged on 2026-06-10, nearly a month before this
audit. There is nothing left to wait for.

## Option C — Replay Onto Main

**Recommended.** Conditions for this option are met: the "parent" branch is
not intended for further PRs (its own PR already merged), and stacking
against it would create confusing topology. A clean replay is now the
correct, low-confusion path:

1. Fetch (explicitly, in the replay task) to get the current real `main`.
2. Create a new branch from current `main`.
3. Decide, as part of that task, whether the 3 orphaned parent-branch
   commits (`b2b7303`, `5e7f529`, `0425a46`) are needed by the public
   showcase's 27 files, or whether the showcase code is self-contained and
   can be replayed without them. This was not evaluated in this run (out of
   scope — read-only topology decision only) and must be the first step of
   the replay task.
4. Replay only the public-showcase-relevant content (the 8 commits from
   `0425a46..HEAD`, or their squashed/re-created equivalent) onto the new
   branch.
5. Re-run validation (`git diff --check`, `tsc -b`, `npm run build`) and the
   safety grep sweep on the new branch before opening a PR.

## Recommendation

**`REPLAY_ONTO_MAIN_RECOMMENDED`**

## User Decision Needed

None blocking — the technical facts now clearly point to one option. The
only remaining judgment call, to be made *inside* the replay task itself,
is whether the 3 orphaned commits (`b2b7303`, `5e7f529`, `0425a46`) need to
be carried forward or can be safely dropped; this audit did not inspect
their content deeply enough to answer that (it touches `RiskGuardrailsCard`-
adjacent logic per `b2b7303`'s message, which may or may not be depended on
by the showcase's `ProductPreviewGrid.tsx` — worth a quick check at the
start of the replay task, not resolved here).

## Validation Commands

```powershell
git diff --check     # clean
npx tsc -b            # clean
npm run build           # clean
```

No frontend files were changed in this run; validation was re-run to
confirm the working tree remains in the same clean state as the prior
audit.

## Files Changed By This Run

- `docs/showcase/pr_topology_decision_001.md` (new) — this report only.
  No other files were staged or modified.

## Suggested Next Run

`MELLYTRADE-REPLAY-PUBLIC-SHOWCASE-ONTO-MAIN-001`

## Safety Confirmation

```text
Safety confirmation:
- No broker execution or live trading enabled.
- No Buy/Sell/Execute/Order controls added.
- No secrets printed or exposed.
- No backend/runtime/broker/config/package/deployment files changed by this run.
- No package or lock files changed by this run.
- No application/backend/broker APIs called.
- Only read-only Git/GitHub metadata checks were allowed for topology review.
- No Higgsfield MCP/media generation performed.
- No push, merge, deploy, reset, clean, delete, force, rebase, or cherry-pick operation performed.
```
