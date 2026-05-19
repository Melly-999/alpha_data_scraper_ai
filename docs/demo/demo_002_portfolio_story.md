# DEMO-002 Portfolio Story

## Problem

Trading dashboards often fail as portfolio material because they either
look generic or imply unsafe execution behavior. A useful demo needs to
show structure, observability, and safety without looking like a retail
trading app.

## Solution

MellyTrade Terminal presents a premium institutional-style terminal with
read-only market visibility, safety badges, and audit-first panels. The
current UI combines:

- a red-black terminal frame
- AI Workspace overview cards
- Paper Sandbox Preview
- Paper Sandbox Activity / Audit Rail
- read-only broker and risk posture

## Safety-first design

The product remains intentionally read-only:

- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- max risk <= 1%

The design shows safety as visible UI state, not hidden implementation
detail. No live order path is exposed in the demo surface.

## What the terminal shows

- Terminal shell / AI Workspace
- Paper sandbox preview state
- Audit rail with recent paper sandbox events
- read-only broker posture
- safety badges and degraded states
- GET-only backend surfaces

## Why read-only matters

Read-only observability lets reviewers evaluate:

- whether safety is visible
- whether execution is blocked
- whether the UI communicates risk clearly
- whether validation is repeatable

It also keeps the demo safe to publish because there are no order
controls, no broker execution controls, and no live trading UX.

## What was validated

- backend safety configuration
- OpenAPI forbidden-path and safety-invariant tests
- frontend production build
- local read-only paper sandbox smoke flow

## Suggested LinkedIn / GitHub copy

> MellyTrade Terminal is a read-only, safety-first trading workstation
> demo built with FastAPI and React/Vite. It combines an institutional
> terminal frame, paper sandbox preview, and audit rail with GET-only
> backend endpoints and enforced dry-run posture.

## Recruiter-friendly bullets

- Built a read-only trading terminal with explicit safety posture
- Designed an institutional dark UI with a premium red-black frame
- Added paper sandbox preview and audit rail panels for observability
- Created a repeatable local smoke flow for reviewer verification
- Kept execution blocked and risk capped at <= 1%

## Technical bullets

- FastAPI backend
- React/Vite frontend
- GET-only paper sandbox endpoints
- paper sandbox preview and audit rail
- safety validation via tests and config checks
- local smoke script for repeatable verification
- UI polish focused on readability and safety
