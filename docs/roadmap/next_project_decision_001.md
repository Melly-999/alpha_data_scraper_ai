# Next-Project Decision — NEXT-PROJECT-OR-REAL-MONEY-ROADMAP-DECISION-001

- **Date:** 2026-06-10
- **Status:** OPEN — awaiting decision
- **Context:** Demo freeze complete (main `df27fa4d`). All showcase PRs merged.

> This document maps the available next-project directions, weighs them against
> portfolio and career goals, and makes a ranked recommendation.

---

## Current State

MellyTrade is at demo freeze. What's live and proven:

| What | State |
|------|-------|
| Web terminal (`/terminal`) | ✅ Live on Vercel |
| Mobile route (`/mobile`) | ✅ Live, true-viewport screenshots |
| Brokers status (`/brokers`) | ✅ Live, `read_only=true` |
| Alpaca Paper read-only status | ✅ Merged (PR #273) |
| Alpaca Paper order preview | ✅ Merged (PR #275) — never submitted |
| Desktop EXE (Tauri v2) | ✅ Merged (PR #271), smoke-tested |
| README showcase V2 | ✅ Merged (PR #277) — financial-terminal format |
| True mobile screenshots | ✅ Merged (PR #278) — 390×844 captures |
| Melly Pet branding | ✅ Merged (PR #279) — all surfaces + Tauri icons |
| Safety regression suite | ✅ Green on every PR |
| Demo freeze report | ✅ Merged (PR #280) |

What exists but is not yet live/polished:

| What | State |
|------|-------|
| Portfolio case study doc | Exists in `docs/career/recruiter_case_study.md` — needs a dedicated PR |
| MOBILE-PWA-POLISH-002 (P1) | Sticky header, quick-action restyle — deferred |
| Paper execution sandbox | Designed only — no implementation |
| Observability polish | Deferred |

---

## The Four Options

### Option A — Deeper MellyTrade Features

Continue building new product features on MellyTrade.

**What this means:**
- Paper trading simulation (Milestone 4 — `docs/roadmap/milestone_4_paper_trading_fasttrack.md`)
- Observability/audit polish
- Mobile PWA P1 items (MOBILE-PWA-POLISH-002)
- IBKR read-only phase (if desired)

**Advantages:**
- Deepens an already-established portfolio project
- Paper trading milestone produces a working demo loop (not just read-only)
- Demonstrates iterative product development
- Doesn't require starting from scratch

**Risks / costs:**
- The project already proves most of what it needs to prove at demo freeze
- Adding more features to one project has diminishing portfolio returns
- Paper trading simulation requires careful safety design to avoid crossing the
  line into live execution patterns

**Portfolio value:** Medium-High — useful if a reviewer asks "what's next?" but
not a step-change improvement in proof points over the current freeze state.

---

### Option B — Second Project

Start a new, distinct portfolio project alongside MellyTrade.

**Best candidates from prior roadmap work:**

| Candidate | Why it helps |
|-----------|-------------|
| AI Job Scanner Agent (`docs/career/job_scanner_agent_design.md`) | Directly serves the career goal; demonstrates agentic AI workflow + FastAPI + async scraping; live product with personal utility |
| Lightweight SaaS tool (non-fintech) | Shows range beyond fintech/trading; good for "Junior Backend" / "AI Automation" CV tracks |
| OpenBB plugin or data pipeline | Plugs into an established OSS ecosystem; demonstrates integration skills |

**Advantages:**
- Demonstrates range — not a one-project candidate
- A second project on a different domain proves adaptability
- A personally-useful tool (job scanner) has intrinsic motivation to finish

**Risks / costs:**
- Starting cold takes time; no existing CI, test suite, or infra
- Splitting focus between two projects reduces depth on both
- Must finish to a demo-quality state to have portfolio value (incomplete > none)

**Portfolio value:** High — a second distinct project materially improves the
portfolio for Junior Backend, AI Automation, and FinTech Support CV tracks.

**Recommendation within this option:** Start with the **AI Job Scanner Agent**.
It's already designed (`CAREER-001–CAREER-004`, `JOBSCAN-001–009`), serves the
immediate job-search goal, and uses the same FastAPI/Python/async stack already
proven in MellyTrade.

---

### Option C — Real-Money Readiness (MellyTrade)

Design and implement the path from paper-only to real-money execution.

**What this means:**
Per the roadmap in `README.md` "Real-money readiness (future only, heavily gated)":
- Reconciliation and P&L tracking
- Risk engine with drawdown circuit-breakers
- Kill switch and emergency stop
- External audit and compliance review
- Weeks of paper/shadow validation before any live path
- Broker live credentials and execution engine

**Hard constraints:**
- This is **intentionally not planned on the demo** and **explicitly blocked**
  at config, API, UI, and test level.
- No live orders, no broker execution, no real-money trading in any public surface.
- Enabling this path would require removing all safety blocks — a deliberate,
  documented, multi-step decision, not a PR.

**Is this the right next step for this stage?**

No. Reasons:
1. There is no demonstrated need yet — the demo freeze proves everything it needs
   to prove without live trading.
2. The candidate has no commercial IT history; live-trading code in a portfolio
   repo without a proper risk/compliance review context could be misconstrued.
3. The engineering prerequisites (reconciliation, kill switch, audit, shadow mode)
   are significant and take weeks to do safely.
4. The portfolio value of "I designed the safety gates for a gated real-money
   execution path" is captured in the roadmap doc and README without implementing it.

**When this becomes the right step:**
- After securing an IT role and gaining commercial context
- After completing paper/shadow validation over weeks
- After a proper risk review with a qualified advisor
- With a clear business case (not just "to say it's done")

**Portfolio value at this stage:** Low — the safety story is already well-told
in the current README. Adding speculative live-execution code without the
surrounding compliance context weakens, not strengthens, the professional signal.

---

### Option D — Portfolio & Career Focus (No New Feature Work)

Pause feature development entirely and focus on:
- PORTFOLIO-CASE-STUDY-001: a polished recruiter-facing case study
- CV updates and job applications using the demo freeze state
- LinkedIn profile refresh
- Certifications (per `docs/career/course_certification_roadmap.md`)
- Actual job applications using the four CV tracks

**Advantages:**
- The portfolio is in the best state it has ever been — use it now
- Job applications have compounding returns; starting earlier is better
- Certifications (AWS, Python) are quick wins for ATS filtering

**Risks / costs:**
- No new engineering proof points added
- Risk of "polishing forever" if not combined with active applications

**Portfolio value:** Immediately highest — the bottleneck is no longer the
project quality; it's getting it in front of hiring managers.

---

## Recommendation

**Primary: Option D → then Option B**

1. **Do Option D now** — spend 1–2 weeks on PORTFOLIO-CASE-STUDY-001, CV
   refresh, and actual job applications. The portfolio is demo-freeze quality;
   use it. Don't delay applications waiting for more features.

2. **Run Option B in parallel or next** — start the AI Job Scanner Agent.
   It's already designed, uses the existing stack, and serves the immediate
   goal. A second live project materially improves the portfolio for all four
   CV tracks.

3. **Option A (Deeper MellyTrade) is low priority** — pick up after securing
   a role if you want to continue, or pick specific high-value items
   (MOBILE-PWA-POLISH-002, observability) if they serve a specific application.

4. **Option C (Real-money readiness) is deferred** — revisit after commercial
   experience, not before.

---

## Immediate Next Actions

| Priority | Task | Notes |
|----------|------|-------|
| P0 | Apply for jobs using current demo freeze state | All four CV tracks ready |
| P0 | PORTFOLIO-CASE-STUDY-001 — finalize and publish | `docs/career/recruiter_case_study.md` exists; needs PR |
| P1 | Start AI Job Scanner Agent (MVP) | Design doc exists; start with CAREER-001 |
| P2 | MOBILE-PWA-POLISH-002 | Sticky header, quick-action restyle — pick up if time |
| P3 | Paper trading milestone | Only if job-search allows bandwidth |
| Deferred | Real-money execution path | Not until after commercial IT role |

---

## What Must Not Change

Regardless of direction:

- `autotrade = false` · `dry_run = true` · `read_only = true` · `live_orders_blocked = true`
- No live orders, no broker execution, no real-money trading in any public demo
- No financial advice, no profit guarantees
- No secrets, provider keys, or broker order IDs in any repository

These are permanent for all public demo surfaces.

---

*MellyTrade — read-only · paper-only · human review required · not financial advice*
