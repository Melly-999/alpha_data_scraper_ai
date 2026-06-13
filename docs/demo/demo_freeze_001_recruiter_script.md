# Demo Freeze 001 — Recruiter / Client Script

Talking points for presenting MellyTrade. Companion to
[demo_freeze_001.md](demo_freeze_001.md).

## 30-second version

> "MellyTrade is a read-only AI trading terminal I built end-to-end —
> FastAPI backend, React frontend, hosted demo, desktop shell. The
> interesting part is the safety architecture: it's a trading-domain system
> that *provably cannot trade* — read-only, dry-run, live orders blocked,
> enforced in config, API, UI, and tests simultaneously. Everything shipped
> through reviewed pull requests with AI-assisted gates, so the GitHub
> history is the proof of work."

## 2-minute version

- **Problem:** trading tools are usually demoed with fake profit claims or
  dangerous live hooks. I wanted to show fintech engineering with the
  opposite posture — safety as the headline feature.
- **Product:** a read-only AI workstation — institutional terminal,
  portfolio/risk overview, AI workspace, paper sandbox previews, audit rail —
  on web, mobile route, and a desktop shell.
- **Architecture:** FastAPI + Pydantic backend, React/TypeScript/Vite
  frontend, Tauri v2 desktop shell, hosted on Render + Vercel.
- **Safety:** autotrade=false, dry_run=true, read-only, live orders blocked,
  max risk capped at 1% — served live by a machine-readable safety endpoint
  and asserted by a pytest regression suite that fails the build if anything
  drifts.
- **AI workflow:** development runs under a written agent operating contract
  in the repo — every change goes Draft PR → review gate → validation →
  merge, with honesty rules ("never claim a validation that didn't run").
- **Deployment:** I also debugged the real-world ops side — a stale hosted
  container caused by a GitHub-access blocker, diagnosed from public
  endpoints alone, then fixed with one approved deploy and verified by smoke
  tests.
- **Evidence:** it's all public — the README, the live endpoints, and a PR
  trail from brand system to backend hardening.

## Technical explanation (when the audience is engineers)

- **Backend:** FastAPI with typed Pydantic schemas; every trading-adjacent
  response carries explicit safety flags; no POST/PUT/PATCH/DELETE on
  trading surfaces; OpenAPI tests assert routes stay GET-only.
- **Frontend:** React + TypeScript + Vite, poll-only API client, safety
  badges rendered from live API state; PWA manifest and official brand
  icon set.
- **Deployment:** Render (API) + Vercel (web), CORS scoped to documented
  origins; SPA deep links; free-tier cold-start handling.
- **Safety validation:** `scripts/validate_safety_config.py` plus a pytest
  safety-invariants suite; CI runs quality (black/flake8/mypy), tests,
  build, Playwright e2e, Bandit SAST, secret scanning, dependency audit.
- **Read-only data layer:** the Neon/ACE memory integration uses a SQL guard
  (single SELECT/WITH only, dangerous-keyword rejection) *plus*
  `SET TRANSACTION READ ONLY` defense-in-depth — and degrades gracefully:
  if the driver or `DATABASE_URL` is absent, the backend boots anyway and
  the route answers with a safe degraded read-only status. That degraded
  response is live on the demo right now, on purpose.
- **Process:** an in-repo agent operating contract
  (`docs/agents/fable_run_contract.md`) governs AI-assisted work — scoped
  branches, explicit pathspecs, review-gate prompts, PASS/BLOCKED reports.
  One PR was even review-gated by the prompt it introduced.

## What this proves

- Python / FastAPI backend engineering
- Frontend integration (React/TypeScript) across web, mobile route, desktop
- Deployment and real-world ops debugging (Render/Vercel, CORS, stale-build
  diagnosis from public evidence)
- CI and safety validation discipline
- Product thinking — positioning, brand system, recruiter-grade README
- Risk-first fintech design — safety as an architectural property, not a
  disclaimer
- Documentation discipline — roadmaps, runbooks, evidence trails
- A repeatable AI-assisted engineering workflow with review gates

## Honest caveats (say them confidently)

- "It's a demo and deliberately read-only — real broker execution is
  intentionally blocked at every layer. That's the point of the design."
- "The memory database is intentionally not connected on the public demo —
  what you see is the graceful-degradation path, which I'd argue is the more
  interesting thing to demonstrate."
- "Next phase is the evidence pack and portfolio presentation — the freeze
  checkpoint you're looking at is documented in the repo."
