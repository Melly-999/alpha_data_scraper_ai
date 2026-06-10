# Vibe Coding Agent Workflow

## Purpose

This document defines how multiple agents should collaborate on MellyTrade without stepping on each other’s edits or weakening the safety posture.

## Role Split

### ChatGPT

- planner
- prompt builder
- explanation layer
- task decomposition

### Claude Code

- implementation agent
- code author for scoped changes
- refactor executor when a plan is already approved

### Codex

- review gate
- merge gate
- safety and repo hygiene checker
- final validation coordinator

### OpenCode

- local docs or small executor
- useful for lightweight editing or narrow task execution

### Cursor

- IDE and workspace operator
- best for interactive editing and quick local iteration

### Meta AI

- mobile and social helper only
- useful for visual framing, summaries, and lightweight ideation

## Collaboration Rule

One agent writes, one agent reviews.

Do not let two agents edit the same files at the same time.

## Branch and File Ownership Rules

- one branch per task
- one primary owner per branch
- one agent owns a file set at a time
- if a second agent needs the same file, the first agent must finish and hand off cleanly
- keep docs-only work in docs branches
- keep runtime work in separate branches

Recommended ownership pattern:

- planner agent: defines scope and filenames
- writer agent: makes the patch
- reviewer agent: checks safety, style, and scope

## Avoid Overlapping Edits

- do not split a small doc task across multiple agents
- do not ask one agent to "just tweak" another agent’s in-progress file
- do not combine unrelated changes in one branch
- do not mix docs planning with runtime code changes

## Final Report Template

Use this structure after each task:

```text
Findings:
Scope:
Tests:
Safety issues:
Secrets scan:
Recommendation:
```

## Safety Scan Checklist

- confirm `autotrade=false`
- confirm `dry_run=true`
- confirm `read_only=true`
- confirm `live_orders_blocked=true`
- confirm `max_risk<=1%`
- confirm no live trading language was introduced
- confirm no execution buttons or execution routes were introduced
- confirm no secrets, API keys, passwords, or token values were added
- confirm no broker write path was added
- confirm no buy/sell/order/execute controls were added
- confirm no profit guarantee or investment advice claims were added

## Review Gate Expectations

- keep diffs minimal
- keep docs English-only
- keep safety rules explicit
- keep human review required
- keep paper/simulation/read-only language consistent across docs
- reject any change that weakens the no-live-trading posture
