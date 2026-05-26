# Current PR Stack — MellyTrade

**Version:** 2.1.0
**Last updated:** 2026-05-26
**Current `main` baseline:** `51e0f67` (PR #197 — feat(paper): add paper trading domain model)

---

## Merged PRs (up to date)

| PR | Title | Status | Notes |
|---|---|---|---|
| #197 | feat(paper): add paper trading domain model | **Merged** (`51e0f67`) | PAPER-M4-001: `schemas_paper_trading.py`, 121 tests. All safety Literals enforced. |
| #196 | docs(roadmap): fast-track paper trading simulation milestone | Merged (`f2fc319`) | PAPER-M4-000: M4 roadmap docs, milestone reorder |
| #195 | feat(watchlist): add read-only watchlist v1 | Merged (`5c0afbe`) | QUEUE-019: `GET /watchlist`, `WatchlistPage.tsx`. PR #46 closed as superseded. |
| #194 | feat(audit): add read-only system audit event feed | Merged (`d506175`) | QUEUE-016/017: `GET /events`, `AuditEventService`, `SystemAuditEvent` schema. PR #40 closed as superseded. |
| #193 | feat(config): migrate CloudMCP to unified-router model | Merged | |
| #192 | feat(ai): add safe Anthropic SDK client foundation | Merged | |
| #191 | docs(roadmap): salvage implementation roadmap and AI dev workflow | Merged | |
| #190 | docs(v9): salvage production hardening materials | Merged | |
| Earlier | Terminal V1 read-only UX, paper sandbox, demo docs, risk, alerts | Merged | Foundation on main |

---

## Open PRs

None currently open.

---

## Planned next PRs (M4 Fast Track)

| Branch | Task | Status |
|---|---|---|
| `feat/paper-m4-001-domain-model` | PAPER-M4-001 paper trading domain model | ✅ Merged `51e0f67` |
| `feat/paper-m4-002-decision-service` | PAPER-M4-002 risk-gated paper decision service | ⬜ Next — branch from main |
| `feat/paper-m4-003-audit-trail` | PAPER-M4-003 paper run audit trail | ⬜ After M4-002 |
| `feat/paper-m4-004-state-endpoints` | PAPER-M4-004 GET-only paper state endpoints | ⬜ After M4-003 |
| `feat/paper-m4-005-ui-panel` | PAPER-M4-005 paper sandbox UI panel | ⬜ After M4-004 |
| `feat/paper-m4-006-scenario-replay` | PAPER-M4-006 scenario replay | ⬜ After M4-004 |
| `feat/paper-m4-007-paper-report` | PAPER-M4-007 exportable paper report | ⬜ After M4-006 |
| `docs/paper-m4-008-e2e-demo` | PAPER-M4-008 end-to-end demo script | ⬜ After M4-007 |

See [`docs/roadmap/milestone_4_paper_trading_fasttrack.md`](milestone_4_paper_trading_fasttrack.md)
for the full M4 task breakdown, safety constraints, and acceptance criteria.

---

## Recommended Merge Order

```
main (51e0f67 — PR #197 baseline)
 └── feat/paper-m4-002-decision-service — next M4 task (branch from main)
      └── feat/paper-m4-003-audit-trail — after M4-002 merges
           └── feat/paper-m4-004-state-endpoints — after M4-003 merges
```

**Stacking rule:** M4 implementation PRs are sequential and should not stack.
Each merges to main independently. M4-002 branches from main after M4-001 merges.

---

## What Should Branch From Main

| Branch Purpose | Should branch from |
|---|---|
| New docs | `main` |
| PAPER-M4-002 and each subsequent M4 task | `main` (after previous M4 PR merged) |
| Hotfix | `main` |
| Phase B broker abstraction | `main` (after M4 completes) |

---

## What Should NOT Be Stacked

| Scenario | Reason |
|---|---|
| M4-003 on top of M4-002 | Sequential dependency — wait for M4-002 to merge |
| Broker code before M4 | M4 is the current priority |
| Any execution code on any branch | Never — safety rule |
| Live-trading routes on any branch | Never — safety rule |

---

## GitHub Actions

**Current status:** Actions may be disabled at account/org level.

**Mitigation:** Use local validation scripts before every PR:
```powershell
py -3.11 scripts/validate_safety_config.py
py -3.11 -m pytest mellytrade_v3/mellytrade-api/tests/ -q
```
Include validation output in the PR description.

**Known pre-existing test failures (not caused by any M4 PR):**
- `test_cloudmcp_config.py::test_cloudmcp_disabled_without_url`
- `test_cloudmcp_config.py::test_cloudmcp_enabled_requires_router_url`

Root cause: `CLOUDMCP_ROUTER_URL` is hardcoded as a default value in `cloudmcp_config.py`, so `monkeypatch.delenv` cannot clear it. These fail on `main` independently of any feature work. Do not block M4 merges on these failures.

---

## PR Safety Checklist (Pre-Merge)

---

## PR Safety Checklist (Pre-Merge)

Before merging any PR:

- [ ] `git diff --name-only` — confirm scope of changes
- [ ] No source code changed (for docs PRs)
- [ ] No config changed without human review
- [ ] No workflow YAML changed without explicit instruction
- [ ] No secrets in diff
- [ ] `py -3.11 -m pytest tests/app/ -q` passes locally
- [ ] Safety flags unchanged: `autotrade=false`, `dry_run=true`, `read_only=true`
- [ ] Human has reviewed the diff (not just AI)
- [ ] No "merge" button clicked from phone or automated session
