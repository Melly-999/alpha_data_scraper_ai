# Current PR Stack — MellyTrade

**Version:** 2.0.0
**Last updated:** 2026-05-26
**Current `main` baseline:** `d506175` (PR #194 — feat(audit): read-only system audit event feed)

---

## Merged PRs (up to date)

| PR | Title | Status | Notes |
|---|---|---|---|
| #194 | feat(audit): add read-only system audit event feed | **Merged** (`d506175`) | QUEUE-016/017: `GET /events`, `AuditEventService`, `SystemAuditEvent` schema. PR #40 closed as superseded. |
| #193 | feat(config): migrate CloudMCP to unified-router model | Merged | |
| #192 | feat(ai): add safe Anthropic SDK client foundation | Merged | |
| #191 | docs(roadmap): salvage implementation roadmap and AI dev workflow | Merged | |
| #190 | docs(v9): salvage production hardening materials | Merged | |
| Earlier | Terminal V1 read-only UX, paper sandbox, demo docs, risk, alerts | Merged | Foundation on main |

---

## Open PRs

### PR #195 — feat(watchlist): add read-only watchlist v1

| Field | Value |
|---|---|
| **PR Number** | #195 |
| **Title** | feat(watchlist): add read-only watchlist v1 |
| **Branch** | `feat/direction-b-watchlist-v1-salvage` |
| **Commit** | `7e12f04` |
| **Status** | Draft — awaiting QUEUE-019 review |
| **Type** | Backend + frontend feature (read-only watchlist) |
| **Scope** | `GET /watchlist`, `watchlist.py`, `WatchlistItemOut`, `WatchlistPage.tsx`, `useWatchlist.ts`, + audit_service.py bug fix from PR #194 |
| **Safety** | Safe — GET-only, `read_only=True` on every row, no execution routes |
| **Review guidance** | Verify: GET only, no POST/PUT/PATCH/DELETE, `require_api_key`, audit_service.py uses System* names |
| **Merge order** | Can merge now; unblocks M4 Fast Track |
| **Recommended action** | QUEUE-019 — human review → squash-merge → close PR #46 as superseded |

---

## Planned next PRs (M4 Fast Track)

| Branch | Task | Status |
|---|---|---|
| `feat/paper-m4-001-domain-model` | PAPER-M4-001 paper trading domain model | ⬜ After QUEUE-019 |
| `feat/paper-m4-002-decision-service` | PAPER-M4-002 risk-gated paper decision service | ⬜ After M4-001 |
| `feat/paper-m4-003-audit-trail` | PAPER-M4-003 paper run audit trail | ⬜ After M4-002 |
| `feat/paper-m4-004-state-endpoints` | PAPER-M4-004 GET-only paper state endpoints | ⬜ After M4-003 |
| `feat/paper-m4-005-ui-panel` | PAPER-M4-005 paper sandbox UI panel | ⬜ After M4-004 |
| `feat/paper-m4-006-scenario-replay` | PAPER-M4-006 scenario replay | ⬜ After M4-004 |
| `feat/paper-m4-007-paper-report` | PAPER-M4-007 exportable paper report | ⬜ After M4-006 |
| `docs/paper-m4-008-e2e-demo` | PAPER-M4-008 end-to-end demo script | ⬜ After M4-007 |
| `docs/m4-paper-trading-fast-track-roadmap` | M4 roadmap docs (this sprint) | Open — current |

See [`docs/roadmap/milestone_4_paper_trading_fasttrack.md`](milestone_4_paper_trading_fasttrack.md)
for the full M4 task breakdown, safety constraints, and acceptance criteria.

---

## Recommended Merge Order

```
main (d506175 — PR #194 baseline)
 └── PR #195 (watchlist v1) — QUEUE-019 review → squash-merge
      └── docs/m4-paper-trading-fast-track-roadmap — merge after PR #195
           └── feat/paper-m4-001-domain-model — first M4 implementation task
```

**Stacking rule:** M4 implementation PRs are sequential and should not stack.
Each merges to main independently. M4-002 branches from main after M4-001 merges.

---

## What Should Branch From Main

| Branch Purpose | Should branch from |
|---|---|
| New docs | `main` |
| PAPER-M4-001 and each subsequent M4 task | `main` (after previous M4 PR merged) |
| Hotfix | `main` |
| Phase B broker abstraction | `main` (after M4 completes) |

---

## What Should NOT Be Stacked

| Scenario | Reason |
|---|---|
| M4-002 on top of M4-001 | Sequential dependency — wait for M4-001 to merge |
| Broker code before M4 | M4 is the current priority |
| Any execution code on any branch | Never — safety rule |
| Live-trading routes on any branch | Never — safety rule |

---

## GitHub Actions

**Current status:** Actions may be disabled at account/org level.

**Mitigation:** Use local validation scripts before every PR:
```powershell
py -3.11 scripts/validate_safety_config.py
py -3.11 -m pytest tests/app/ -q
```
Include validation output in the PR description.

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
