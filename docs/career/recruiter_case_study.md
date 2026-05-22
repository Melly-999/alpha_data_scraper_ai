# MellyTrade Recruiter Case Study - Public-Safe

**Candidate:** Mateusz Ozimkiewicz  
**Project type:** Portfolio project  
**Role demonstrated:** AI-assisted Python / automation developer, junior backend candidate, fintech workflow builder  
**Current status:** Local read-only workstation and paper-trading research prototype  
**Safety posture:** No live trading, no real-money execution, no broker execution, no order-entry UX

## Recruiter Summary

MellyTrade / Alpha AI is a safety-first AI-assisted fintech workstation built as a portfolio project. It demonstrates practical software engineering skills across backend APIs, frontend dashboard UX, read-only broker/status visibility, risk guardrails, auditability, local validation and AI-assisted development workflow.

This is not a commercial trading platform and should not be evaluated as one. Its value is that a self-taught candidate can show a real, reviewable system with safety constraints, documentation, task planning and repeatable validation.

## What This Project Proves

| Area | Evidence |
|---|---|
| Backend/API fundamentals | FastAPI, Pydantic, REST API, JSON, service-oriented project structure |
| Frontend fundamentals | React, TypeScript, Vite, dashboard UI, terminal-style UX |
| Safety mindset | `autotrade=false`, `dry_run=true`, `read_only=true`, `live_orders_blocked=true`, max risk <=1% |
| FinTech awareness | Broker/status visibility, risk guardrails, paper sandbox, audit/event UX |
| Testing discipline | Safety validation script and pytest coverage in the project |
| Documentation quality | README, recruiter docs, task queues, public-safe CV positioning |
| AI-assisted workflow | Claude Code, OpenAI Codex, GitHub Copilot, ChatGPT and Ollama/LM Studio used as supervised assistants |
| Operations background | Customer service, CRM/KPI/SLA process experience translated into technical support and automation context |

## Architecture Snapshot

```text
React / TypeScript terminal UI
    -> typed API clients and polling views
    -> FastAPI backend
    -> schemas and services
    -> broker/status surfaces
    -> safety, audit, risk, signal and dashboard documentation
```

The project is intentionally read-only/dry-run. The portfolio value is in observability, safety guardrails and clear system boundaries rather than order execution.

## Recruiter-Friendly Project Description

Built MellyTrade / Alpha AI, a read-only AI-assisted fintech workstation using FastAPI, React, TypeScript, Pydantic, pytest and local validation scripts. The system presents broker/status surfaces, signal context, safety badges, audit events, paper sandbox previews and risk guardrails in a terminal-style interface. Live trading is intentionally blocked by design: `autotrade=false`, `dry_run=true`, `read_only=true`, `live_orders_blocked=true`, and max risk is capped at <=1%.

## Candidate Ownership

The candidate owns:

- Project direction and product concept.
- Task planning and acceptance criteria.
- Prompt design and agent workflow supervision.
- Diff review and safety validation.
- Documentation and portfolio positioning.
- Local testing / validation runs.
- Frontend/backend integration decisions with AI support.

AI-assisted areas:

- Code drafting.
- Component generation.
- Documentation drafting.
- Test planning.
- Refactor suggestions.
- Repo analysis.
- Debugging support.

Manually reviewed areas:

- Diffs.
- Safety posture.
- Runtime behavior.
- Validation results.
- Documentation wording.
- Task scope.

## Best Role Matches

| Role | Fit |
|---|---|
| Technical Support Engineer | Strong bridge from customer service plus API/script/debugging exposure |
| SaaS Support Specialist | Strong fit for CRM/SLA background plus technical workflow understanding |
| FinTech Support Specialist | Strong fit because project demonstrates risk, audit and broker/status vocabulary |
| Customer Success Technical Specialist | Good fit for customer communication plus automation mindset |
| AI Automation Specialist | Good fit if paired with small business-process automation examples |
| Junior Python Developer | Realistic stretch with FastAPI/pytest/Git portfolio evidence |
| Backend Developer Intern | Good fit for portfolio-first teams |

## Interview Talking Points

- Why read-only observability comes before execution in fintech tooling.
- How safety defaults are documented and validated.
- How degraded broker/status states avoid unsafe UX.
- How AI tools were used under human review rather than blindly accepted.
- Which parts were personally planned, reviewed and validated.
- What is still missing before this could become anything beyond a portfolio demo.

## What Not To Claim

- Do not claim commercial IT employment.
- Do not claim completed matura or degree unless confirmed.
- Do not claim commercial fintech platform.
- Do not claim live trading.
- Do not claim broker execution.
- Do not claim order buttons or autonomous trading.
- Do not claim guaranteed trading results.
- Do not claim financial advice.
- Do not claim "AI wrote the code".

## Current Portfolio Gaps

| Gap | Recommended action |
|---|---|
| Public recruiter proof | Add 5-7 screenshots and a short "For Recruiters" README section |
| CV readiness | Fill private TODOs and create final DOCX/PDF outside the repo |
| LinkedIn | Add target headline, about section and MellyTrade project |
| Proof of communication | Add 2-3 minute Loom demo script |
| Job targeting | Use bridge-role positioning, not only junior developer applications |

## Safety Confirmation

MellyTrade is positioned as read-only, dry-run and research-oriented:

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
no live trading
no broker execution
no order buttons
no connect-live UX
```
