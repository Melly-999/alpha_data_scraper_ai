# MellyTrade — Recruiter Portfolio Pack

> Portfolio project. Read-only / demo-safe. Not a live trading system, not
> investment advice, no profit claims.

A single entry point for recruiters and reviewers. Sources of truth:
[case study](mellytrade_case_study.md) ·
[CV entry](mellytrade_cv_project_entry.md) ·
[LinkedIn summary](mellytrade_linkedin_summary.md) ·
[demo freeze](../demo/demo_freeze_001.md) ·
[evidence pack](../demo/demo_evidence_pack_001.md).

## 1. Portfolio positioning

The builder presents as a **Junior Python / FastAPI developer** and
**AI-assisted backend developer** who builds **fintech / trading-tools
portfolio projects**. MellyTrade is the flagship project. It is explicitly a
learning/portfolio build, not a commercial trading product.

## 2. What MellyTrade is

A **read-only AI trading terminal and portfolio risk platform** — a hosted
demo that shows market/portfolio/safety information, AI workspace concepts,
paper/sandbox previews, and an audit posture, across web, a mobile route, and
a desktop shell, on a shared FastAPI backend. It is designed to *prove it
cannot trade*: read-only, dry-run, live orders blocked.

## 3. What problem it demonstrates

Most "trading bot" portfolio projects lean on fake profit numbers or risky
live hooks. MellyTrade demonstrates the opposite discipline: **safety as an
architectural property** of a fintech system, with the guardrails enforced and
observable, not just claimed in a README.

## 4. What was built

- A FastAPI + Pydantic backend with typed schemas and GET-only trading
  surfaces
- A React/TypeScript/Vite frontend with a safety rail, plus a mobile route and
  a Tauri desktop shell
- A machine-readable safety endpoint and a `validate_safety_config.py` script
- A read-only Neon/ACE memory introspection layer with a SQL guard and
  graceful degradation
- A documented brand system (MT monogram identity + favicon/PWA icons)
- Hosted deployment on Render (API) + Vercel (web)

## 5. Verified evidence summary

From [demo_evidence_pack_001.md](../demo/demo_evidence_pack_001.md)
(captured 2026-06-13, main `a2754ac`/baseline `ff5a889`):

- `GET /api/health` → 200 · `GET /api/safety/status` → 200 ·
  `GET /api/neon-memory/status` → 200 (safe degraded read-only)
- Hosted frontend `/` → 200, `/terminal` deep link → 200
- Safety flags observed live: autotrade=false, dry_run=true, read_only=true,
  live_orders_blocked=true, execution_enabled=false, requires_human_review=true,
  max risk = 1.0%
- CORS echoes the Vercel frontend; no secrets in any response

## 6. Safety-first design summary

The posture is enforced in **four places at once** — config (`config.json`),
backend responses, UI badges, and tests — and served live by a safety
endpoint. A pytest safety-invariants suite fails the build if any invariant
drifts. The Neon layer adds a SQL guard (single SELECT/WITH, dangerous-keyword
rejection) plus `SET TRANSACTION READ ONLY` defense-in-depth, and degrades
safely if the driver or database is absent.

## 7. Technical skills demonstrated

- Python / FastAPI / Pydantic backend development
- React / TypeScript / Vite frontend integration
- REST API design with safety-by-default (GET-only trading surfaces)
- Deployment + ops debugging (Render/Vercel, CORS, stale-build diagnosis)
- CI/quality discipline (black/flake8/mypy, pytest, Playwright, Bandit,
  secret scanning, dependency audit)
- Read-only data-access design (SQL guard, read-only transactions, graceful
  degradation)
- Documentation, release management, and evidence capture

## 8. AI-assisted development workflow

Development runs under an in-repo **agent operating contract**
(`docs/agents/fable_run_contract.md`): scoped branches, explicit pathspecs,
PR review-gate prompts, and PASS/BLOCKED reports with an honesty rule ("never
claim a validation that didn't run"). One PR was even review-gated by the
prompt it introduced — a small but real demonstration of disciplined
AI-assisted engineering.

## 9. GitHub / PR delivery story

Every change shipped through **Draft PR → review gate → validation → squash
merge**. The public PR history (brand system #284–#290, agent contract #291,
Neon feature + hardening #286/#293, deploy unblock + status #295, demo freeze
#296, evidence pack #297) is itself the proof of work and process maturity.

## 10. What to show a recruiter

1. The GitHub repo + branded README (Product Snapshot, safety contract)
2. The live safety endpoints (`/api/safety/status`)
3. The hosted terminal UI with its read-only safety rail
4. The PR trail and the agent operating contract
5. The demo freeze + evidence pack docs

## 11. What not to claim

No live trading, broker execution, production-trading readiness, real user
adoption, or profit/ROI/win-rate/returns. Not investment advice; not a
regulated product. The Neon DB is intentionally unconfigured (safe degraded).

## 12. Interview talking points

- "I built a trading-domain system whose headline feature is that it
  *provably can't trade*."
- "I enforced safety in config, API, UI, and tests simultaneously, and served
  it from a live endpoint so it's verifiable."
- "I debugged a real ops problem — a stale hosted backend caused by a GitHub
  access blocker — diagnosed from public endpoints alone, then fixed and
  verified with smoke tests."
- "I used an AI-assisted workflow with written review gates and honesty rules,
  so the process is auditable in the PR history."

## 13. Next improvements

Mobile/PWA evidence refresh, desktop evidence pack, repo hygiene (stale PR
closeout), and optional Fable lessons backfill. A production database
connection would be a separate, explicitly-gated task — intentionally not done
for the demo.
