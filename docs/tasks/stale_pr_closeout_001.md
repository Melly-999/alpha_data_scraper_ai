# Stale PR Closeout Audit 001

## 1. Purpose

Read-only audit of all open pull requests to clean the public portfolio
surface after the M8 demo-freeze / recruiter-pack arc. Produces close/keep
recommendations and **draft** close comments. No PRs are closed, merged, or
modified by this task — execution is a separate, explicitly-approved step.

## 2. Baseline

- **main / origin/main SHA:** `40454849f05ed95fa5f2ec36b60f97ab518f5881`
- **Safety validator:** `python scripts/validate_safety_config.py` → OVERALL: PASS
- Audit date: 2026-06-13

## 3. Open PR inventory

Six PRs are open. They are exactly the six audit targets (no others found).

| PR | Title | Draft | Mergeable | Created | Updated | Author |
| --- | --- | --- | --- | --- | --- | --- |
| #283 | docs(career): add MellyTrade public launch pack | yes | MERGEABLE | 2026-06-10 | 2026-06-10 | Melly-999 |
| #18 | Cleanup: CTO hardening pass | yes | CONFLICTING | 2026-04-18 | 2026-04-18 | Melly-999 |
| #17 | fix: align trading pipeline interfaces and harden repo workflow | no | CONFLICTING | 2026-04-18 | 2026-04-18 | Melly-999 |
| #12 | fix optional ensemble bridge compatibility | yes | CONFLICTING | 2026-04-16 | 2026-04-16 | Melly-999 |
| #10 | Integrate MellyTrade v3 risk gateway and dashboard | yes | CONFLICTING | 2026-04-14 | 2026-05-29 | Melly-999 |
| #7 | Add unit tests for untested modules… | yes | CONFLICTING | 2026-04-04 | 2026-04-04 | app/copilot-swe-agent |

## 4. Target PR review (vs current main)

| PR | Files | +/− | Behind main | Ahead | Mergeable |
| --- | --- | --- | --- | --- | --- |
| #283 | 3 (docs/career) | +313/−3 | 14 | 2 | MERGEABLE |
| #18 | 33 (runtime) | +576/−210 | 321 | 6 | CONFLICTING |
| #17 | 32 (runtime/trading) | +910/−301 | 321 | 1 | CONFLICTING |
| #12 | 44 (runtime) | +4740/−753 | 344 | 1 | CONFLICTING |
| #10 | 39 (runtime/v3 rewrite) | +5308/−0 | 360 | 38 | CONFLICTING |
| #7 | 5 (tests) | +805/−2 | 402 | 2 | CONFLICTING |

## 5. Classification table

| PR | Classification | Recommendation |
| --- | --- | --- |
| #283 | **B — KEEP** | Keep; refresh/rebase or fold into the portfolio docs, then gate or close |
| #18 | **A — CLOSE** | Superseded/stale runtime PR, 321 behind, conflicting |
| #17 | **A — CLOSE** | Superseded/stale trading-pipeline PR, 321 behind, conflicting |
| #12 | **A — CLOSE** | Superseded/stale runtime PR, 344 behind, conflicting |
| #10 | **A — CLOSE** | Superseded/stale v3 rewrite, 360 behind, conflicting |
| #7 | **A — CLOSE** | Superseded/stale test PR, 402 behind, conflicting |

## 6. Per-PR analysis

### #283 — docs(career): public launch pack — **KEEP**
- Branch `docs/public-launch-pack-mellytrade`; docs-only (3 files under
  `docs/career/`); CI green; mergeable; only 14 behind / 2 ahead.
- Two of its files already exist on main (`README.md`,
  `recruiter_case_study.md`); one is new (`public_launch_pack.md`).
- **Risk/safety:** docs-only, no runtime/safety impact.
- **Reason to keep:** recent, safe, and thematically adjacent to the merged
  portfolio pack (#298). It overlaps with the newer `docs/portfolio/` layer, so
  the right move is a human decision — refresh it against current main and
  either merge the genuinely-new `public_launch_pack.md` content or close it as
  superseded by #298. Not a clean auto-close.

### #18 — CTO hardening pass — **CLOSE**
- 33 runtime files, **321 commits behind main**, CONFLICTING, untouched since
  2026-04-18. Pre-dates the entire current architecture (brand, Neon, hosted
  deploy, demo freeze). Any safe scope it intended is long since represented on
  main. **Safety:** stale runtime diff; do not attempt to merge.

### #17 — align trading pipeline interfaces — **CLOSE**
- 32 files including trading-pipeline code, 321 behind, CONFLICTING, the only
  non-draft of the old set. Title references trading interfaces — **flag:**
  historical wording only; the current main enforces the read-only safety
  posture regardless. Far too stale to reconcile; close.

### #12 — optional ensemble bridge compatibility — **CLOSE**
- 44 files, +4740/−753, 344 behind, CONFLICTING. A large April compatibility
  change against an architecture that no longer exists. Close.

### #10 — MellyTrade v3 risk gateway and dashboard — **CLOSE**
- 39 files, +5308, 360 behind, 38 ahead, CONFLICTING. A whole alternative "v3"
  rewrite branch (`mellytrade-v3-bootstrap`). The current product on main is the
  delivered direction; this parallel rewrite is obsolete. **Safety:** mentions
  "risk gateway" — historical title only; close, do not merge.

### #7 — copilot unit tests — **CLOSE**
- 5 files, 402 behind, CONFLICTING, authored by the copilot agent on 2026-04-04
  — the oldest open PR. Test coverage has since been built on main through the
  real arc. Close.

## 7. Proposed close comments (drafts — not posted by this task)

- **#18 / #12 / #7:**
  > Closing as superseded by later merged work on main. This branch is ~320–400
  > commits behind and conflicting; its intended scope is now represented in the
  > current architecture and docs. No further action needed on this stale branch.

- **#17:**
  > Closing as a stale, conflicting branch (~321 commits behind main). The
  > current main enforces the read-only / dry-run / live-orders-blocked safety
  > posture; this old pipeline change is obsolete and not reconcilable. No
  > further action needed.

- **#10:**
  > Closing this parallel "v3" rewrite branch as superseded. The delivered
  > product on main is the current direction; this branch is ~360 commits behind
  > and conflicting. Preserved in history; no further action needed.

- **#283 (only if the user decides to close rather than refresh):**
  > Closing as superseded by the merged recruiter portfolio pack (PR #298) and
  > the `docs/portfolio/` set. If `public_launch_pack.md` has unique value, it
  > can be re-opened on a fresh branch from current main.

## 8. Safety scan summary

This audit doc contains historical PR titles ("risk gateway", "trading
pipeline") only as factual context, each explicitly flagged as historical. No
secrets, account IDs, or unsafe enablement claims are introduced. The repo
safety posture is unchanged (validator PASS).

## 9. What was not changed

No PRs closed/merged/marked-ready; no branches or worktrees deleted; no
runtime/config/workflow/package files touched; no comments posted to GitHub; no
deploys; no cloud/env changes.

## 10. Recommended execution order

If/when an EXECUTE task is approved:

1. Close #7, #12, #18 (uncontroversial stale/conflicting, draft) with the
   shared comment.
2. Close #17 (non-draft, trading-pipeline) and #10 (v3 rewrite) with their
   specific comments.
3. Handle #283 last as a deliberate human decision: refresh-and-merge the
   unique `public_launch_pack.md`, or close as superseded by #298.

After closeout, the public open-PR list would reflect only current, intentional
work — improving repo clarity for the portfolio surface (closes M4).
