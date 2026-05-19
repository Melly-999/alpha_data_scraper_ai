# AI Coding Workflow

This workflow keeps AI assistance useful while preserving MellyTrade's read-only
and dry-run safety posture.

## Recommended AI dev loop

1. Plan the change and define the scope.
2. Look up current docs with Context7.
3. Make a small patch.
4. Run tests.
5. If frontend files changed, verify in the browser with DevTools.
6. Review the safety posture.
7. Open a PR.

## Tool roles

### Claude Code

- planner
- reviewer
- architecture and safety review

### Codex

- implementation
- tests
- refactors
- small scoped patches

### OpenCode

- local multi-provider coding shell
- good for quick iteration with approved MCP tools

### LM Studio / Ollama

- local fallback model support
- cheap or offline review
- never the source of truth for current API docs

### Supabase

- audit, event, and task state docs
- safe degraded client work only unless explicitly scoped

### Context7

- external library documentation source
- use before coding against changing APIs

### Chrome DevTools

- UI smoke verification
- console, network, layout, and performance inspection

## MellyTrade safe agent checklist

- no execution routes
- no order buttons
- no broker execution
- no connect-live UX
- no autotrade/dry-run toggle
- no risk weakening
- no secrets
- GET/read-only by default
- tests required

## Prompt templates

### Planning prompt

```text
You are planning a docs-only or code-only change in MellyTrade.
First restate the scope, confirm the safety posture, identify files that may
change, and list the tests or browser checks that will prove the change is safe.
Do not propose trading, execution, live-connect, or risk-weakening changes.
```

### Implementation prompt

```text
Implement the smallest safe patch for this MellyTrade task.
Keep the repository read-only and dry-run-safe.
Use Context7 for current library docs before editing code that depends on
external APIs.
Do not add execution routes, order buttons, live-connect UX, secrets, or risk
weakening.
```

### Review prompt

```text
Review this MellyTrade change for bugs, regressions, and safety drift.
Focus on execution routes, order placement, live-connect affordances, risk
controls, secrets, and whether the change stays read-only and dry-run-safe.
```

### Frontend verification prompt

```text
Use Chrome DevTools MCP to smoke-check the frontend after this change.
Look for console errors, failed requests, layout regressions, and obvious
rendering issues. Report only what you can verify in the browser.
```

### Safety audit prompt

```text
Audit this change for MellyTrade safety posture.
Confirm there are no execution routes, no order buttons, no broker execution,
no connect-live UX, no autotrade/dry-run toggle, no risk weakening, no secrets,
and that GET/read-only defaults remain intact.
```

## Validation commands

```powershell
py -3.11 scripts/validate_safety_config.py
py -3.11 -m pytest tests/app -q
cd frontend
npm run build
```

Run the frontend build only if frontend files changed. If no frontend files
changed, state that the frontend build was skipped in the final report.

## PR rule

Open a PR after validation. Keep the change scoped and avoid mixing runtime,
trading, or workflow changes into docs-only work.
