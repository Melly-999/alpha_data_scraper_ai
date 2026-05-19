# MellyTrade / alpha_data_scraper_ai

## Role

Use Junie as a safe IDE-native coding agent for small scoped tasks in this repository.

## Safety Defaults

- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- `max risk <= 1%`

## Absolute Prohibitions

- No live trading
- No broker execution
- No MT5/IBKR order calls
- No order routes
- No order buttons
- No connect-live UX
- No `dry_run=false`
- No `autotrade=true`
- No secrets
- No workflow edits unless explicitly requested

## Required Workflow

- Start with `git status --short` and the current branch.
- Avoid dirty trees and do not overwrite unrelated user changes.
- Create small scoped branches for implementation work.
- Add tests for code changes.
- Run validation before final reporting.
- Never push without explicit instruction.

## Validation Commands

- `py -3.11 scripts/validate_safety_config.py`
- `python -m pytest tests/app -q`
- `npm run build` if frontend files changed

## Frontend Rules

- Read-only panels only.
- Safety badges must remain visible.
- No execution controls.
- No live broker controls.

## Backend Rules

- Prefer GET-only endpoints for previews.
- Use advisory, dry-run, read-only response schemas.
- No POST/PUT/PATCH/DELETE unless explicitly scoped and safety-reviewed.

## Final Report Format

- branch
- changed files
- validation run
- safety confirmation
- no push unless requested

