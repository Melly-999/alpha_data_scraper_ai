# Parallel Claude Code Task Board — MellyTrade

> **Docs-only.** Coordination board for parallel Claude Code sessions. No
> runtime/safety changes. Posture invariant: `autotrade=false`, `dry_run=true`,
> `read_only=true`, `live_orders_blocked=true`, `execution_enabled=false`,
> `max_risk_per_trade <= 1%`.

---

## Recommended active sessions (start with 3)

| # | Session | Worktree | Mode |
|---|---|---|---|
| 1 | **Lead / PR Monitor** | `…-lead-monitor` | read-only |
| 2 | **Quality Stack (TYPE-001A)** | `…-quality-stack` | committer (one at a time) |
| 3 | **Security Dependency Monitor** | `…-security-deps` | committer (one at a time) |

### Optional later
- **UI Review Agent** (`…-ui-review`, read-only) — for PR #230.
- **Safety Gate Agent** (read-only) — diff safety review.

---

## Current task order

1. **TYPE-001A (Option A)** — mypy gate unblock (mypy.ini config). ✅ authored (#237).
2. **Poll FORMAT/LINT/TYPE stack** — confirm `quality` green on #237. ✅ CI-confirmed.
3. **Prepare merge-gate plan** — bottom-up #234 → #235 → #237 (await approval).
4. **Re-check #233** — FastAPI/Starlette; DepAudit green, blocked only by quality stack.
5. **Re-check #236** — python-dotenv; independent dep fix.
6. **Re-check #231** — observability; rebase after stack + #233 land.
7. **Re-check #230** — frontend UI; rebase + human visual review.
8. **Cleanup worktrees** — only after PRs merge.

---

## Milestone progress (illustrative)

| Milestone | Progress | Notes |
|---|---|---|
| CI quality cleanup | ~90% | FORMAT/LINT/TYPE authored; #237 quality CI-green; merge pending. |
| Security dependency cleanup | ~85% | #233 (starlette) DepAudit green; #232 (requests), #236 (python-dotenv) authored. |
| Observability | ~65% | #231 in scope (docs/config); needs rebase + post-merge setup. |
| UI | ~60% | #230 display-only/safe confirmed; needs rebase + visual review. |
| Repo hygiene | ~50% | worktrees mapped; 1 stale empty worktree flagged; cleanup post-merge. |

---

## Coordination rules

- Lead assigns whose turn it is to commit; only one committer at a time.
- Each session stays in its own worktree/branch.
- No merges, ready-flips, or pushes to `main` without explicit human approval.
- No Claude validation; no broker/live-trading changes; no secrets.
