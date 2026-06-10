# MellyTrade Portfolio Case Study — Post Demo-Freeze

**Candidate:** Mateusz Ozimkiewicz
**Project type:** Portfolio project — self-directed, self-taught
**Role demonstrated:** AI-assisted Python / automation developer, junior backend candidate, fintech workflow builder
**Freeze status:** Demo freeze reached — hosted web demo live, desktop shell built, showcase PRs merged
**Safety posture:** No live trading, no real-money execution, no broker execution, no order-entry UX

---

## One-Sentence Summary

MellyTrade is a read-only AI-assisted fintech workstation that demonstrates safety-first engineering, a supervised AI development workflow, and a complete hosted demo — built by a self-taught candidate with no prior commercial IT employment.

---

## The Problem This Project Solves

Most AI trading tool demos on portfolios:

- Look executable but are not safe to show to a recruiter
- Hide the risk posture or never mention it
- Overpromise what the system actually does

MellyTrade exists to prove the opposite: that a self-taught candidate can build a real, reviewable system with honest safety constraints, documented limitations, and a repeatable validation workflow.

---

## Goal

Reach a hosted demo freeze milestone with:

- A live web terminal on Vercel
- A live API on Render
- A desktop shell (Tauri v2) as a local bonus
- Read-only broker state surfaces (Alpaca Paper)
- Safety badges visible on every public surface
- No live trading, no order buttons, no broker write paths

---

## My Role

| Area | What I did |
|---|---|
| Product direction | Defined scope, milestones, task queues, acceptance criteria |
| AI-assisted dev workflow | Supervised Claude Code, OpenAI Codex, GitHub Copilot, ChatGPT and Ollama/LM Studio at every step |
| Safety gate oversight | Reviewed every diff for safety posture before accepting |
| Frontend / backend integration | Planned API surfaces, approved component structure, validated UX flow |
| CI / PR workflow | Opened PRs, monitored CI, managed CodeRabbit and Sourcery review gates |
| Hosted smoke testing | Read-only QA against live Vercel and Render URLs after demo freeze |
| Documentation | Wrote and reviewed all recruiter docs, roadmaps, agent workflow rules, safety confirmation blocks |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python, FastAPI, Pydantic, REST, JSON |
| Frontend | React, TypeScript, Vite, terminal-style UI |
| Desktop shell | Tauri v2 (Rust-backed, local only) |
| Testing | pytest, safety validation scripts |
| CI/CD | GitHub Actions |
| Frontend hosting | Vercel |
| API hosting | Render |
| Broker surface | Alpaca Paper (read-only status + preview-only) |
| AI dev tools | Claude Code, OpenAI Codex, GitHub Copilot, ChatGPT, Ollama/LM Studio |
| Version control | Git, GitHub, PowerShell, git worktrees |

---

## Key Features

- **Web terminal** — React/TypeScript/Vite, hosted on Vercel, read-only UX
- **Mobile / PWA view** — read-only watchlist and alert concept, safety badges visible
- **Desktop shell** — Tauri v2, local only, mirrors web terminal layout
- **Read-only broker surface** — Alpaca Paper status endpoint surfaced; no write path
- **Paper preview only** — `/api/alpaca-paper/order-preview` returns preview data; no orders placed
- **Safety badges** — `READ ONLY`, `DRY RUN`, `LIVE ORDERS BLOCKED`, `EXECUTION OFF` rendered on all primary surfaces
- **Melly Pet mascot** — `MellyPetMascot.tsx` component integrated in web terminal, mobile view and workspace panel

---

## Safety Architecture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
execution_enabled=false
paper_only=true
requires_human_review=true
max_risk_per_trade <= 1%
```

**Five pillars enforced throughout:**

1. **No live trading** — `autotrade=false` and `dry_run=true` in all config profiles
2. **No broker execution** — no write path to any broker; Alpaca Paper surfaces status only
3. **No order-entry UX** — no buy/sell/order/execute buttons on any public surface; only Refresh and read-only controls
4. **No financial advice** — all public surfaces carry "Analysis only. Not financial advice." disclaimer
5. **No secrets in repo** — no API keys, broker credentials, account IDs or token values in any committed file

---

## Demo Freeze Milestone

Six showcase PRs merged to main in the freeze window:

| PR | Title | Status |
|---|---|---|
| #240 | docs(showcase): add recruiter roadmap and module priority matrix | Squash merged |
| #245 | docs(showcase): add MellyTrade growth pack docs | Squash merged |
| #261 | docs(roadmap): add MellyTrade showcase growth pack | Squash merged |
| #270 | docs(roadmap): add next project decision document | Squash merged |
| #276 | docs(showcase): safety validation and smoke test docs | Squash merged |
| #281 | docs(next): next project decision options post freeze | Squash merged |

Final main SHA after freeze: `90832ce`

Hosted smoke test result (POST-FREEZE-HOSTED-SMOKE-001): **PASS WITH NOTES**

- All safety flags confirmed via `/api/alpaca-paper/status`
- No forbidden controls found in source code
- Safety badges confirmed in `MobileAppPage.tsx`, `BrokerCard.tsx`, `MellyPetMascot.tsx`
- Note: `/api/alpaca-paper/order-preview` returns 404 on bare GET — endpoint requires parameters or a different HTTP method; not a safety concern

---

## What I Learned

- **Product thinking before code** — defining what the system must NOT do is as important as what it does
- **Safety-first engineering** — writing the safety confirmation before the feature, not after
- **CI discipline** — every PR through full CI + CodeRabbit ASSERTIVE + Sourcery before merge
- **AI workflow** — how to supervise AI coding agents, review diffs, and catch scope creep
- **Small PRs and review gates** — one task per branch, one owner per branch, explicit pathspecs
- **Demo packaging** — a hosted live demo with documented safety posture is more credible than code alone

---

## Recruiter Value

| Skill area | Evidence |
|---|---|
| Backend API fundamentals | FastAPI, Pydantic, REST, JSON, service-oriented structure |
| Frontend fundamentals | React, TypeScript, Vite, terminal-style dashboard, mobile view |
| Safety mindset | Safety config enforced at every layer; smoke-tested post-freeze |
| FinTech vocabulary | Broker state, paper trading, order-preview, risk guardrails, audit trail |
| Testing discipline | pytest, safety validation scripts, CI/CD with GitHub Actions |
| Documentation quality | Recruiter docs, roadmaps, agent workflow rules, case study |
| AI-assisted workflow | Claude Code, Codex, Copilot used as supervised assistants with human review |
| Operations bridge | Customer service + CRM/KPI/SLA background applied to technical support and automation |
| Deployment basics | Vercel (frontend), Render (API), local Tauri v2 shell |
| Review gate discipline | CodeRabbit ASSERTIVE + Sourcery gates before every merge |

---

## Honest Limitations

- **Demo only** — this is a portfolio project, not a commercial platform
- **Paper / simulation only** — no real money, no live broker connection, no execution
- **Not financial advice** — no investment signals, no profit claims, no trading recommendations
- **No live trading** — `autotrade=false` and `dry_run=true` enforced by design
- **No broker execution** — Alpaca Paper surfaces account status only; no write path exists
- **`/api/alpaca-paper/order-preview` note** — returns 404 on bare GET; requires parameters; no orders placed
- **Candidate background** — self-taught, no commercial IT employment, matura in progress; presented honestly

---

## Links

| Surface | URL |
|---|---|
| Live web demo (Vercel) | mellytrade.vercel.app |
| Live API (Render) | mellytrade-api.onrender.com |
| GitHub repository | github.com/higherrrrrrr/alpha_data_scraper_ai |
| Recruiter case study | docs/career/recruiter_case_study.md (this file) |
| CV positioning notes | docs/career/cv_positioning_notes.md |
| Module priority matrix | docs/roadmap/module_priority_matrix.md |
| Agent workflow rules | docs/roadmap/vibe_coding_agent_workflow.md |

---

## Best Role Matches (Post-Freeze)

| Role | Fit |
|---|---|
| Technical Support Engineer | Customer operations + API/script/debugging + project documentation evidence |
| SaaS Support Specialist | CRM/KPI/SLA background + technical workflow + hosted demo as proof |
| FinTech Support Specialist | MellyTrade provides broker/risk/audit/paper-trading vocabulary without claiming live trading |
| Customer Success Technical Specialist | Client communication + automation mindset + safety-first product thinking |
| AI Automation Specialist | Python/API/AI tooling + supervised agent workflow + process automation background |
| Junior Python Developer | FastAPI/pytest/Git/CI evidence; honest about junior level |

---

## Interview Talking Points

- Why read-only observability comes before execution in fintech tooling
- How safety defaults are documented, enforced and validated at every layer
- How degraded broker/status states are handled without exposing unsafe UX
- How AI tools were used under human review rather than blindly accepted
- Which parts were personally planned, reviewed and validated versus AI-assisted
- What is still missing before this could become anything beyond a portfolio demo
- How the demo freeze milestone was defined and confirmed with hosted smoke testing

---

## What Not To Claim

- Do not claim commercial IT employment
- Do not claim completed matura or degree unless confirmed
- Do not claim commercial fintech platform
- Do not claim live trading
- Do not claim broker execution
- Do not claim order buttons or autonomous trading
- Do not claim guaranteed trading results
- Do not claim financial advice
- Do not claim "AI wrote the code"

---

## Safety Confirmation

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
execution_enabled=false
paper_only=true
requires_human_review=true
max_risk_per_trade <= 1%
no live trading
no broker execution
no order buttons
no connect-live UX
no financial advice
no profit guarantees
no secrets in repo
```

*MellyTrade is a read-only, paper-trading, research-oriented portfolio project. It is not a commercial platform, not financial advice, and not a live trading system.*
