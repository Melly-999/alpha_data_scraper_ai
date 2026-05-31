# Pending Salvage and Cleanup Board

## Remaining Worktrees

Currently:

- canonical main
- `_sevalla_demo_worktree`
- `PR45_feature_direction_b_reports_v1_clean`

## Sevalla Decision

**Status:** Option D — SALVAGE SMALL DEPLOY PR, if Sevalla is desired.
Otherwise keep local only or delete later.

Files from previous review:

- `Dockerfile.sevalla`
- `docs/deployment/sevalla_readonly_demo.md`
- `frontend/.env.sevalla.example`
- `scripts/sevalla_demo_local_smoke.ps1`

**Decision:** Not urgent. Render/Vercel first. The bundle was reviewed as clean
and additive (placeholders only, safety env enforced, no secrets).

## PR45 Decision

**Status:** Option E — SALVAGE BACKEND READ-ONLY.

Keep only the 5 net-new files (if still compatible with main):

- `app/terminal.py`
- `app/terminal_schemas.py`
- `app/terminal_service.py`
- `tests/test_terminal.py`
- `docs/frontend/mellytrade_v1_terminal_ui_phase1.md`

Discard:

- the 28 files already superseded by main

**Safety:**

- endpoints must remain GET-only
- no order/execute routes
- no broker execution
- no config/requirements/workflow changes
- reconcile endpoint contracts with main's current `terminalApi.ts` before merging

## Old PR Triage

| PR | Status | Risk | Recommendation |
|---|---|---|---|
| #18 | Open/Draft | Very High | Do not merge; possible stale/close later |
| #17 | Open | Very High | Do not merge; overlaps #18 |
| #12 | Draft | Very High | Split only safe bits |
| #10 | Draft | Very High | DO_NOT_TOUCH |
| #7 | Draft | Low | Keep/review tests-only first |

## Branch Cleanup

Branch cleanup should happen only after human approval. No branch deletion
should be automatic. Merged-PR branches (e.g. from the worktree cleanup) are
candidates for local deletion later, but each requires explicit sign-off.
