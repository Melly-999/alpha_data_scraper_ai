# Recruiter Loom Demo Script

**Target length:** 3-5 minutes  
**Audience:** Recruiters, technical hiring managers, startup founders  
**Positioning:** Portfolio project, read-only, dry-run, no live trading

## 0:00-0:20 - Intro

Hi, I am Mateusz. This is MellyTrade / Alpha AI, a portfolio project I built to demonstrate practical Python, FastAPI, React/TypeScript, fintech workflow, safety-first UX, and supervised AI-assisted engineering.

Important context: this is not a live trading platform. It is a read-only, dry-run workstation. There is no live trading, no broker execution, no order routes, no order buttons, and no connect-live UX.

## 0:20-0:55 - Problem Solved

The problem I wanted to solve is simple: financial and trading tools are risky if they expose execution before they expose safety, observability and auditability. I designed MellyTrade around the opposite principle: first make the system explainable, inspectable and safe.

The terminal focuses on market context, signal review, risk guardrails, broker/status visibility, paper sandbox previews, and audit events. It is designed for supervised analysis and portfolio demonstration, not autonomous trading.

## 0:55-1:35 - Architecture Overview

The stack is Python, FastAPI and Pydantic on the backend, with React, TypeScript and Vite on the frontend. The backend exposes typed read surfaces and safety/status endpoints. The frontend presents an institutional terminal-style UI with loading, degraded and read-only states.

The architecture separates the terminal UI, API clients, FastAPI routes, schemas, services, broker/status surfaces, risk posture and audit/event views. AI tools were used as supervised engineering assistants for planning, code drafts, documentation and review, but every change still requires human review and local validation.

## 1:35-2:35 - Terminal V1 Walkthrough

Start on the terminal overview. Point out the safety banner and status badges: read-only, dry-run and live orders blocked.

Move to the AI Workspace. Explain that the AI layer is advisory only. It supports signal reasoning and review, but does not place trades. Human review is required.

Open the signals or signal quality view. Show how the system presents confidence, reasoning and risk context instead of pretending certainty.

Open the risk guardrails view. Point out the max risk <=1% posture, `autotrade=false`, `dry_run=true`, `read_only=true` and `live_orders_blocked=true`.

Open the broker card. Explain safe disconnected or paper-state handling. A missing broker session should degrade safely, not crash or encourage reconnect-live behavior.

Open the audit/events feed. Show that safety-relevant events are visible, timestamped and written in a way a reviewer can understand.

## 2:35-3:20 - Safety Posture

MellyTrade is intentionally conservative. The safety contract is:

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
no live trading
no broker execution
no order routes
no order buttons
no connect-live UX
human review required
```

This is the most important part of the project. The goal is to demonstrate responsible fintech engineering habits, not to claim trading performance.

## 3:20-4:05 - AI-Assisted Engineering Workflow

I use Claude Code, OpenAI Codex, GitHub Copilot and local tools like Ollama/LM Studio as supervised engineering assistants. They help with repo navigation, planning, implementation drafts, docs, test ideas and debugging support.

I do not describe this as "AI wrote the code." The workflow is supervised: I define the task, review diffs, check wording, run validation, and keep safety constraints explicit before accepting changes.

## 4:05-4:40 - What This Proves Technically

This project demonstrates backend API design, typed schemas, frontend dashboard UX, safety-first product thinking, audit/event design, local validation scripts, documentation discipline, Git/GitHub workflow, and practical use of AI-assisted engineering.

It also connects my customer operations background with technical support, AI automation, fintech support and junior backend roles.

## 4:40-5:00 - Closing Pitch

If you are reviewing this as a recruiter or hiring manager, the best place to start is the README "For Recruiters" section, then the recruiter case study, the safety validation command and the screenshot checklist.

MellyTrade is a portfolio project, but it is built to show how I think: safety first, clear system boundaries, honest claims, human review and practical engineering workflow.

## Do Not Say

- Do not say this is a commercial fintech product.
- Do not say it places orders.
- Do not say it connects to live trading.
- Do not say AI wrote the code.
- Do not claim guaranteed trading results.
- Do not show private contact data, account IDs, API keys or secrets.
