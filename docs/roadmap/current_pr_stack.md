# MellyTrade — Current PR Stack

A snapshot of the in-flight pull requests, what they contain, and what
should happen next. Use alongside `docs/roadmap/mellytrade_next_20_steps.md`
when deciding what to merge first.

> Snapshot taken on **2026-05-09**. State below reflects the latest known
> values; verify with `gh pr view <N>` before acting.

---

## Snapshot

| PR | Title | Branch | Base | State | Draft? | Files | +/− | Validation | Notes |
|---|---|---|---|---|---|---|---|---|---|
| **#56** | `docs(demo): add Terminal V1 screenshots` | `feature/terminal-v1-demo-assets-20260508` | `main` | OPEN | ready | 9 | +206 / 0 | local green | rebased onto `main@e758f18` after PR #55 merged |
| **#57** | `feat(safety): add /api/safety/status contract` | `feature/safety-status-contract` | `main` | OPEN | ready | 4 | +260 / 0 | local green | introduces `SafetyStatusResponse` schema + GET-only route + 13 tests |

`origin/main` last known SHA: `e758f189a07f4e7e621e391ed5dd16b6e094e331`
(squash-merged PR #55 — Terminal V1 sprint).

---

## PR #56 — Terminal V1 screenshots

### Purpose
Lands the six portfolio / demo PNGs reserved by PR #55's screenshot plan,
plus the README hero image and the runbook screenshot checklist links.
**Docs / binary assets only — zero production code.**

### Branch
`feature/terminal-v1-demo-assets-20260508` (pushed to origin; rebased
onto `main@e758f18` after PR #55 merged).

### Status
- `gh pr view 56` → `state: OPEN`, `isDraft: false`, `mergeStateStatus: CLEAN`.
- Diff: 9 files (`README.md`, 6 PNGs under `docs/assets/terminal-v1/`,
  `docs/demo/terminal_v1_local_demo.md`, `docs/demo/terminal_v1_screenshot_plan.md`).
- Local validation: `pytest tests/app/ -q` → 145 passed (pre-PR #57 baseline);
  `npm run build` → clean.
- Validation comment posted (substitute for missing CI tick).
- CI: not running — Actions disabled at user-account level.

### Safety confirmation
- ✅ No production source touched.
- ✅ `config.json`, `mt5_*`, `brokers/`, `execution/`, `risk/risk_manager.py` — all untouched.
- ✅ No secrets in any docs file.
- ✅ All six PNGs validated (PNG magic bytes; under 1 MB each).
- ✅ Hero image markdown link in `README.md` resolves to a file that exists.
- ✅ Runbook references resolve to existing files (`../assets/terminal-v1/*.png`).

### Next action
**Human review → merge.** No code review required (binary assets +
markdown only). A reviewer should:

1. Open the PR's "Files changed" tab to verify the six PNGs are the
   expected captures.
2. Confirm the README hero image renders correctly.
3. Squash-merge.

### After PR #56 merges
- `origin/main` advances by one commit.
- Local follow-up:
  ```powershell
  git fetch origin
  git switch main
  git pull --ff-only origin main
  git branch -D feature/terminal-v1-demo-assets-20260508
  ```
- The Terminal V1 milestone visually closes — README hero is live.
- No follow-up PRs are unblocked specifically by #56's merge (it's a
  leaf change). PR #57 is independent.

---

## PR #57 — `/api/safety/status` central safety contract

### Purpose
Adds the central GET-only safety status endpoint. Single source of
truth for `dry_run`, `auto_trade`, `read_only`, `live_orders_blocked`,
`max_risk_per_trade_pct`, the named safety pillars, and a human
`safety_note`. Pulls the per-trade risk ceiling from the live
`RiskConfig`. **The schema enforces `max_risk_per_trade_pct ≤ 1.0` at
the field level** (`Field(..., ge=0.0, le=1.0)`).

### Branch
`feature/safety-status-contract` (pushed to origin).

### Status
- `gh pr view 57` → `state: OPEN`, `isDraft: false`, `mergeStateStatus: CLEAN`.
- Diff: 4 files (`app/schemas/safety.py`, `app/api/routes/safety.py`,
  `app/main.py`, `tests/app/test_safety_status.py`). +260 / 0.
- Local validation: `pytest tests/app/test_safety_status.py -v` → 13/13;
  `pytest tests/app/ -q` → 158 passed (was 145; +13); `npm run build` → clean.
- Validation comment posted.
- CI: not running — Actions disabled.

### Safety confirmation
- ✅ Schema uses Pydantic v2 `extra="forbid"` — no execution-shaped
  field can be added without a deliberate schema change.
- ✅ Endpoint is GET-only; 4 parametrized tests assert
  POST/PUT/PATCH/DELETE return 405.
- ✅ All five canonical safety pillars surfaced
  (`DRY_RUN_ACTIVE`, `READ_ONLY_ACTIVE`, `AUTO_TRADE_DISABLED`,
  `LIVE_ORDERS_BLOCKED`, `MAX_RISK_CAPPED`).
- ✅ `config.json` untouched.
- ✅ `mt5_trader.py`, `brokers/`, `execution/`, `risk/risk_manager.py`
  — all untouched.
- ✅ No secrets introduced.
- ✅ The 39-assertion safety regression test
  (`test_safety_invariants.py`) still passes — its route-inventory
  check correctly identifies `/api/safety/status` as GET-only and its
  admin-allowlist check confirms no new mutating route was added.

### Next action
**Human review → merge.** A reviewer should:

1. Open the PR's "Files changed" tab.
2. Confirm `app/schemas/safety.py` contains no execution-shaped fields,
   uses `extra="forbid"`, and caps `max_risk_per_trade_pct` at 1.0 at
   the schema level.
3. Confirm `app/api/routes/safety.py` is `@router.get` only.
4. Confirm `tests/app/test_safety_status.py` has the 13 assertions
   listed in the PR body.
5. Squash-merge.

### After PR #57 merges
- `origin/main` advances by one commit.
- Local follow-up:
  ```powershell
  git fetch origin
  git switch main
  git pull --ff-only origin main
  git branch -D feature/safety-status-contract
  ```
- The endpoint becomes the canonical safety contract for any future
  PR that needs to read posture programmatically.
- **TERM-001** (Step 16 in the next-20 roadmap) becomes implementable:
  the frontend `<SafetyBanner>` can switch from `/health` + `/risk/config`
  to the new single endpoint.
- **SAFE-008** (Step 7) — the safety architecture document — can
  reference the live endpoint as authoritative.
- **Step 8 (BRK-001 BrokerAdapter Protocol)** is unblocked.

---

## Merge order recommendation

**Merge PR #56 first, then PR #57.**

Why this order:

1. **PR #56 is lower risk** — it's docs and binary assets, zero code
   paths. Reviewing it costs ~5 minutes and the merge is essentially
   risk-free.
2. **PR #57 is the foundation for downstream work.** Merging it second
   means the next several roadmap steps (Step 7 onward) can branch
   directly off `main` with the safety contract in place.
3. **They are independent.** Neither depends on the other; the order is
   chosen for review ergonomics, not for technical reasons.

After both merges, no PRs remain in flight, and the next sprint's
work (roadmap Steps 4–7, then 8 onwards) can begin from a clean
baseline.

---

## Should future tasks branch from `main` or stack?

**Branch from `main` for everything in the next-20 roadmap, except as
noted below.**

Rationale:

- PRs #56 and #57 are independent of each other; neither warrants a
  stacked PR.
- Future tasks (roadmap Steps 4 onward) all branch off the latest
  `main`, on the assumption that PR #57 is merged before Step 4 starts.
- Stacking is a real cost: the stacked branch must be rebased after
  every parent merge, which adds CI time, extra force-pushes, and
  cognitive overhead.

**Exceptions where stacking is reasonable:**

- A task whose tests only make sense after a still-unmerged schema
  lands. For example, if PR #57 hadn't merged yet and you wanted to
  start Step 16 (TERM-001 banner rewiring), stacking on PR #57 would
  be reasonable.
- A multi-step refactor that can't be split cleanly. None of the
  next-20 tasks fall into this category.

**Default rule:** if you can branch from `main`, do. Stacking is
opt-in, not opt-out.

---

## Open follow-up after PR #56 + PR #57 merge

When both have landed on `main`:

1. **Re-pull `main`** locally and delete the merged branches.
2. **Verify the test count baseline** is now 158 (was 145 pre-#57).
3. **Update `docs/roadmap/mellytrade_next_20_steps.md`** to strike
   through Steps 1 and 2 as merged.
4. **Address roadmap Step 3** (re-enable Actions) before opening the
   next PR — see `docs/dev/github_actions_recovery.md`.
5. **Open the next PR for roadmap Step 4** (TEST-001 OpenAPI scan),
   following `docs/dev/pr_workflow_sop.md`.

---

**Last updated**: 2026-05-09
