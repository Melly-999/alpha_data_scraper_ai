# Current PR Stack — MellyTrade

**Version:** 1.0.0
**Last updated:** 2026-05-09
**Branch this doc lives on:** `docs/full-auto-ai-dev-system`

---

## Merged PRs (Baseline)

| PR | Title | Branch | Status | Notes |
|---|---|---|---|---|
| #55 | Terminal V1 read-only UX, audit feed, safety tests, daily plan, demo docs | `main` | **Merged** | Terminal V1 milestone |
| #54 | feat: add read-only dry-run journal export | `main` | Merged | |
| #53 | feat: add read-only dry-run journal filters | `main` | Merged | |

**PR #55 is the current `main` baseline.** All new branches must start from this commit (`e758f18`).

---

## Open PRs

### PR #56 — Terminal V1 Screenshots / Demo Assets

| Field | Value |
|---|---|
| **PR Number** | #56 |
| **Title** | Terminal V1 screenshots and demo assets |
| **Branch** | Unknown (demo/screenshots branch) |
| **Status** | Open |
| **Type** | Assets / docs |
| **Safety** | Safe — assets only; no source code changes expected |
| **Actions** | May not trigger Actions if they're disabled at account level |
| **Review guidance** | Verify: only image/asset files changed; no source code; no config |
| **Merge order** | Can merge independently; does not block other PRs |
| **Recommended action** | Human review → merge when ready |

---

### PR #57 — SAFE-001: GET /api/safety/status Central Contract

| Field | Value |
|---|---|
| **PR Number** | #57 |
| **Title** | SAFE-001: GET /api/safety/status central contract |
| **Branch** | Unknown (safety-contract branch) |
| **Status** | Open |
| **Type** | Backend feature (read-only endpoint) |
| **Safety** | Safe — adds a GET endpoint for safety status display; no execution |
| **Actions** | May not trigger if Actions disabled |
| **Review guidance** | Verify: endpoint is GET only; returns `dry_run`, `autotrade`, `live_orders_blocked` fields; no POST/PUT added; no side effects |
| **Merge order** | Merge before Phase 1 validation scripts (TEST-003 depends on this endpoint) |
| **Recommended action** | Human review → merge before Phase 1 begins |

---

## Docs-Planning Branches

| Branch | Purpose | Status |
|---|---|---|
| `docs/implementation-roadmap-and-workflow` | Implementation roadmap and AI dev workflow | Exists locally; 1 commit ahead of main |
| `docs/full-auto-ai-dev-system` | This sprint — Safe Full Auto AI Dev System plan | **Current branch** |

### Branch Notes

- `docs/implementation-roadmap-and-workflow` was created before this sprint. It has one doc commit. It should be reviewed and either:
  - Opened as a PR and merged into main (if content is ready), or
  - Kept as a reference and superseded by this sprint's docs
- **Do not rebase either branch** — they are docs-only; no conflicts expected with main
- Both branches should branch from `main` (from PR #55 merge commit)

---

## Recommended Merge Order

```
main (e758f18 — PR #55 baseline)
 ├── PR #56 (Terminal V1 assets) — merge independently
 ├── PR #57 (SAFE-001 contract)  — merge before Phase 1
 ├── docs/implementation-roadmap-and-workflow — review and merge
 └── docs/full-auto-ai-dev-system (this sprint) — open PR after human review
```

**Stacking rule:** These PRs are all independent from each other. None of them need to stack. Open each as a standalone PR against `main`.

---

## What Should Branch From Main

| Branch Purpose | Should branch from |
|---|---|
| New docs | `main` |
| Phase 1 validation scripts | `main` (after PR #57 merged) |
| Phase 2 MCP skeleton | `main` (after Phase 1 merged) |
| Phase 3 planning | `main` (after Phase 0 merged) |
| Hotfix | `main` |

---

## What Should NOT Be Stacked

| Scenario | Reason |
|---|---|
| PR #56 on top of PR #57 | Independent; no dependency |
| MCP skeleton on top of docs | MCP should wait for Phase 0 review |
| Broker code on top of MCP skeleton | Must wait for Phase 6 in roadmap |
| Any execution code on any branch | Never — safety rule |

---

## GitHub Actions Blocker

**Current status:** GitHub Actions may be disabled at account/org level.

**Impact:**
- PRs do not show CI check results
- Merges can proceed without automated test gates (human must manually run tests)
- `docs/` PRs are low risk even without CI

**Mitigation for Phase 1+:**
- Use local validation scripts (TEST-001, TEST-003, TEST-004, OBS-002) to substitute for CI
- Include validation output in PR description when Actions are disabled
- Note in each PR: "Actions disabled at account level; local validation passed — [output]"

**Resolution path:**
1. Check GitHub → Settings → Actions → General
2. If disabled at org level: re-enable for this repo specifically
3. If re-enabled: verify workflows in `.github/workflows/` are still valid
4. Do NOT modify workflow YAML to work around the block

---

## Next Recommended PRs

After this docs sprint is committed:

| Recommended PR | Branch | Priority |
|---|---|---|
| Merge `docs/full-auto-ai-dev-system` | This branch | High — completes Phase 0 |
| Merge `docs/implementation-roadmap-and-workflow` | Existing branch | Medium |
| Merge PR #56 assets | Existing PR | Medium |
| Merge PR #57 SAFE-001 contract | Existing PR | High — unblocks Phase 1 |
| Phase 1 validation scripts | `test/local-validation-suite` | After PR #57 merges |

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
