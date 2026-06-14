# Current Status — After Neon/ACE Hardening and Cleanup

- **Last updated:** 2026-06-12 (revised same day: M5 Render unblock completed —
  see [docs/deployment/render_current_status.md](../deployment/render_current_status.md))
- **Audience:** the next agent/maintainer session — use this as the baseline
  for Render/deploy unblock, demo freeze, recruiter/portfolio pack, and final
  evidence work.
- **Supersedes** the snapshot in `current_pr_stack.md` (last updated
  2026-05-26, baseline PR #197) for "what is true now" questions; that file is
  retained as history.

---

## 1. Current main state

- **main / origin/main SHA:** `1ecd14f601fa46dd2cf0224a40d48daa20c3a37e`
  (squash merge of PR #293), local and remote verified identical after sync.
- **Safety validator:** `python scripts/validate_safety_config.py` →
  **OVERALL: PASS** (5 passed, 0 failed, 1 informational note) — run on this
  baseline during the post-merge audit and the Neon cleanup.
- Safety posture unchanged: `autotrade=false`, `dry_run=true`,
  `read_only=true`, `live_orders_blocked=true`, max risk ≤ 1%, no broker
  execution, no buy/sell/order/execute controls, no live trading UX.

## 2. Recently completed PR arc

| PRs | What landed |
| --- | --- |
| #284 → #290 | Brand/showcase chain: visual identity docs, SVG asset pack, PNG/ICO exports, frontend favicon/PWA icons, README banner, portfolio case-study README polish |
| #291 | Fable 5 agent operating contract: `docs/agents/fable_run_contract.md`, PR-review + vision-QA prompts, `docs/knowledge/fable_lessons/` |
| #286 | Neon/ACE read-only memory introspection (GET-only routes, SQL guard, read-only transactions) |
| #293 | Neon/ACE hardening follow-up: restored `.gitignore` / `requirements.txt` / `.env.example`, graceful psycopg degradation (backend boots without the driver), placeholder Neon identifiers, +5 tests |
| #292 | **Closed as superseded** by #293 (no unique content; verified diff vs main) |
| Cleanup | CLEANUP-ROADMAP-POSTMERGE-001 (read-only audit) and CLEANUP-NEON-WORKTREES-001 (Neon worktrees deregistered/removed, local Neon branches deleted, remote branches retained for PR history) — no code changes |
| #302 | Broker-sim readiness audit ([broker_sim_readiness_audit_001.md](../tasks/broker_sim_readiness_audit_001.md), classification **B**); follow-up adds a GET-only read-only smoke (`scripts/broker_sim_readonly_smoke.ps1`, [broker_sim_readonly_smoke_001.md](../tasks/broker_sim_readonly_smoke_001.md)) — docs + read-only smoke, no execution surface |
| #303 → next | Broker-sim read-only smoke merged; follow-up adds a demo walkthrough ([broker_sim_walkthrough_001.md](../tasks/broker_sim_walkthrough_001.md)) — docs-only presenter guide for the read-only simulated broker preview, no execution surface |

## 3. Milestone status

| Milestone | Status | Notes / evidence |
| --- | --- | --- |
| **M1 — GitHub / Portfolio Showcase** | **DONE** (minor polish optional) | PRs #284–#290; README banner + product snapshot + brand system live; optional: social-preview image, screenshot realism pass |
| **M2 — Fable Agent Operating Contract** | **DONE** (optional lessons backfill) | PR #291; contract already exercised on PRs #286/#291/#293 gates |
| **M3 — Neon/ACE Read-only Memory Introspection** | **DONE** | PRs #286 + #293 at `1ecd14f`; 28 tests green; boot-safe without psycopg; optional later: dedicated read-only DB role |
| **M4 — Repo Hygiene / Cleanup** | **IN PROGRESS / MOSTLY DONE** | Neon cleanup done (#292 closed, worktrees/branches removed); stale-PR audit complete ([stale_pr_closeout_001.md](../tasks/stale_pr_closeout_001.md): close #18/#17/#12/#10/#7, decide #283) — awaiting EXECUTE approval; remaining: merged-branch pruning, primary repo dir triage |
| **M5 — Render / Hosted Backend Deploy Unblock** | **DONE** (2026-06-12) | GitHub App access confirmed healthy; one user-approved manual deploy succeeded; hosted backend now serves current main incl. Neon routes (`/api/neon-memory/status` 404 → 200 degraded-read-only); CORS echoes Vercel origin; details in [render_current_status.md](../deployment/render_current_status.md). Neon stays intentionally unconfigured (no `DATABASE_URL` on Render) — safe degraded mode, not a failure |
| **M6 — Desktop EXE / Tauri Demo** | **DONE** (demo-level) | PR #271 merged + hosted smoke; optional: land the local evidence-pack docs branch |
| **M7 — Mobile/PWA Evidence** | **IN PROGRESS / EVIDENCE REFRESHED** | Mobile route live; hosted GET-only smoke re-verified (frontend, `/terminal`, `/manifest.webmanifest`, `/api/health`, `/api/safety/status` all 200) — see [mobile_pwa_evidence_refresh_001.md](../demo/mobile_pwa_evidence_refresh_001.md); remaining: physical iPhone/iPad manual smoke + optional 192px PWA icon if an install audit requires it |
| **M8 — Final Demo Freeze / Recruiter Portfolio Pack** | **NEXT** (unblocked) | README names demo-freeze report as the current phase; `docs/career/` + case study merged; M5 dependency cleared 2026-06-12 — hosted backend is current; remaining soft dependency: M4 leftovers |
| **M9 — Post-demo Product Roadmap** | **BACKLOG** | Paper-trading M4 fast-track design docs exist; design-only, heavily gated, no live paths |

## 4. Remaining task counts (estimates from current repo state, not guarantees)

| Track | Estimated tasks |
| --- | --- |
| Demo-ready portfolio | 3–5 (screenshot realism, freeze report, recruiter pack polish, optional social preview) |
| Hosted working demo | 1–3 (verify Render blocker, re-run deploy smoke) |
| Repo hygiene (after Neon cleanup) | 2–4 (stale PR closeout, branch pruning, primary repo dir triage) |
| Product next phase | 4+ (paper-trading fast-track, design-only) |

## 5. Recommended next task sequence

1. ~~ROADMAP-STATUS-DOCS-001~~ — this document
2. ~~RENDER-DEPLOY-UNBLOCK-001~~ — completed 2026-06-12; hosted backend current
   (see [render_current_status.md](../deployment/render_current_status.md))
3. ~~DEMO-FREEZE-001~~ — checkpoint created: [docs/demo/demo_freeze_001.md](../demo/demo_freeze_001.md)
   (+ checklist + recruiter script) ← **frozen 2026-06-12**
   - Evidence captured 2026-06-13: [docs/demo/demo_evidence_pack_001.md](../demo/demo_evidence_pack_001.md)
   - Recruiter portfolio pack 2026-06-13: [docs/portfolio/mellytrade_recruiter_portfolio_pack.md](../portfolio/mellytrade_recruiter_portfolio_pack.md)
4. **MOBILE-PWA-EVIDENCE-REFRESH-001** — iPad/PWA evidence refresh
5. *Optional:* FABLE-LESSONS-BACKFILL-001 — write the first
   `docs/knowledge/fable_lessons/` entries from the #286→#293 arc
6. *Optional:* STALE-PR-CLOSEOUT-001 — decide #283 and early PRs
   #18/#17/#12/#10/#7

## 6. Open cautions

- The **primary repo directory** (`02_Repo/alpha_data_scraper_ai`, branch
  `feature/alpaca-paper-readonly-card`) is dirty with unrelated local changes
  and needs its own triage task — do not commit from it as-is.
- **PR #283** (public launch pack) is still an open draft — refresh against
  current main, then gate or close.
- **Stale early PRs #18 / #17 / #12 / #10 / #7** predate the current
  architecture — need an explicit close-or-rescope decision.
- The **PR45 worktree** (`PR45_feature_direction_b_reports_v1_clean`) is
  unrelated to recent work — treat with caution, verify before touching.
- One **inert, file-locked directory** may remain at
  `02_Worktrees/alpha_data_scraper_ai-neon-hardening-001` — already
  deregistered from git; safe to delete manually after the locking process
  exits or after a reboot.

## 7. Safety

This file is a roadmap/status document only. No runtime, frontend, backend,
API, config, workflow, or package changes accompany it. No execution controls
exist anywhere in the demo; live trading remains blocked; all trading and
Neon/ACE surfaces remain read-only, advisory-only, and demo-safe.
