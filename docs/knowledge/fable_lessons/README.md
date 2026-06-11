# Fable Lessons — Project Memory

Folder for short, factual "lessons learned" from Fable 5 / Claude Code runs on
`alpha_data_scraper_ai`. The goal is that any future agent run (or human) can
read this folder and avoid repeating a mistake that already cost a session.

Operating contract: [docs/agents/fable_run_contract.md](../../agents/fable_run_contract.md)

## Purpose

- Persist non-obvious decisions, blockers, and fixes across agent sessions
- Give review gates a place to check "has this failure happened before?"
- Keep the knowledge in the repo, reviewable like any other doc

## Naming

One file per lesson, numbered and slugged:

```text
NNN_short_kebab_slug.md
```

Examples:

- `001_demo_freeze_scope.md`
- `002_no_direct_main_push.md`
- `003_render_cors_deploy_blocker.md`
- `004_neon_ace_readonly_guard.md`

Numbers are allocated sequentially and never reused.

## What each lesson must contain

Use this format:

```markdown
# NNN — Title

- **Date:** YYYY-MM-DD
- **Run/PR:** task id and PR number if applicable

## Context
What was being attempted, on which branch/surface.

## What happened
The factual sequence — what failed, what was observed.

## Evidence
Commands, output excerpts, PR links, file paths. Real output only.

## Decision
What was decided and why.

## Follow-up
Open items, future tasks, or "none".

## Safety impact
Whether the safety posture (autotrade=false, dry_run=true, read-only,
live orders blocked, max risk <= 1%) was ever at risk, and how it was
protected.
```

## Rules

1. **No sensitive content — ever.** Lessons must not contain secrets, tokens,
   API keys, `.env` values, broker credentials, account IDs, private user or
   client data, or screenshots that include private information. If the
   evidence contains any of these, redact before writing the lesson.
2. **Factual and verified only.** Lessons document what actually happened in a
   verified run — real commands, real output, real PR numbers. No speculation
   written as fact; if something is a hypothesis, label it as one.
3. **Small and specific.** One lesson per file, one failure/decision per
   lesson. Link related lessons rather than merging them.
4. **Docs-only.** Adding or editing a lesson never justifies touching runtime,
   config, workflow, or package files in the same change.
