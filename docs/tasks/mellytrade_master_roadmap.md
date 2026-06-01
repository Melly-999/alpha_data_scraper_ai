# MellyTrade Master Roadmap

This document explains where the project is, what is done, what remains, and in
what order to continue. It consolidates the Agent MCP track, the demo
deployment plan, the Melly Pet brand plan, and the pending salvage/cleanup
decisions into a single roadmap.

## Current Status

**Foundation:**

- CI/security cleanup completed
- Open Design terminal UI merged via #230
- dependency/security baseline clean
- worktree cleanup mostly complete (18 → 3)
- Agent MCP foundation started with AGENT-MCP-001 (PR #241, now merged) and
  AGENT-MCP-002 (PR #242, Draft)

**Safety posture:**

- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- `execution_enabled=false`
- max risk `<= 1%`

**Current remaining strategic tracks:**

- Agent MCP read-only MVP
- Render/Vercel public demo
- Melly Pet branding / UI / icon
- PR45 read-only terminal API salvage
- Sevalla backup deploy target
- old PR triage
- TYPE-HARDEN-001 later

## Milestone Overview

| Milestone | Name | Status | Goal | Risk |
|---|---|---|---|---|
| M0 | Foundation / Safety / CI cleanup | Mostly done | Green baseline, safe repo | Low |
| M1 | Workspace cleanup | Mostly done | Remove stale worktrees and branches | Low |
| M2 | GitHub App + MCP read-only Agent MVP | In progress | Read-only repo/PR/checks agent | Low |
| M3 | Demo deployment | Planned | Render backend + Vercel frontend | Low-Med |
| M4 | Melly Pet brand + UI + icon | Planned | Mascot, assistant card, app icon | Low-Med |
| M5 | Read-only terminal API salvage | Planned | PR45 GET-only terminal API | Med |
| M6 | Paper Trading / Sandbox next slice | Planned | More paper/sandbox UX, no execution | Med |
| M7 | TYPE-HARDEN-001 | Later | Remove mypy suppressions, fix debt | Low-Med |
| M8 | Release candidate demo | Later | hosted demo + evidence pack | Med |

## Recommended Execution Order

1. Review/merge AGENT-MCP-001 PR #241 *(done — merged into main)*
2. AGENT-MCP-002 — MCP read-only contract *(in Draft PR #242)*
3. AGENT-MCP-003 — Local repo status collector
4. AGENT-MCP-004 — PR/checks task board generator
5. Render backend runbook
6. Vercel frontend runbook
7. Hosted demo smoke/evidence pack
8. Melly Pet docs/spec/icon plan
9. Melly Pet display-only UI card
10. Melly Pet favicon/EXE icon pipeline
11. Sevalla optional backup deploy PR
12. PR45 read-only terminal API salvage
13. Old PR #7 tests-only review
14. Old high-risk PR close/salvage decisions
15. TYPE-HARDEN-001

## Progress Counters

**M2 Agent MCP:**

- Total tasks: 6
- AGENT-MCP-001 merged (#241); AGENT-MCP-002 in Draft (#242)
- Done: 1/6 (001)
- In progress: 1/6 (002)
- Remaining (planned): 4/6 (003–006)

**Demo Deploy:**

- Total tasks: 8
- Done: 0/8
- Remaining: 8/8

**Melly Pet:**

- Total tasks: 5
- Done: 0/5
- Remaining: 5/5

**Cleanup:**

- Worktrees reduced from 18 to 3
- Remaining decisions: Sevalla, PR45, branch cleanup

## Definition of Done for Public Demo

Public demo is ready when:

- Render backend demo is deployed in read-only mode
- Vercel frontend demo points to the Render backend
- safety badges are visible
- no order/buy/sell/execute controls
- health checks pass
- iPad/mobile smoke passes
- a demo screenshot pack exists
- README is product-oriented and no longer recruiter/CV-focused
- no secrets or broker credentials are in the repo

## Definition of Done for Full MVP

Full MVP is ready when:

- public demo is stable
- read-only agent dashboard/tasks are available
- terminal UI is polished
- paper/sandbox previews are stable
- Melly Pet assistant is visible
- EXE/icon plan is implemented if desktop packaging is chosen
- safety tests and docs remain green

## Related Roadmaps — Mobile AI

A Mobile AI workstream extends the PWA-first `/mobile` surface into an AI
chart-review, paper game-plan, and risk-coach experience. It is documented as a
separate track and keeps the standing safety posture (read-only, dry-run, no
broker execution, no order controls, max risk ≤ 1%).

- Mobile AI roadmap: `docs/tasks/mobile_ai_roadmap.md`
- Architecture decision: `docs/mobile/mobile_app_architecture_decision.md`
- Context / history snapshot: `docs/mobile/mobile_ai_context_snapshot.md`
- Workspace setup: `docs/mobile/mobile_ai_workspace_setup.md`
