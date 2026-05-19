# Junie Workflow for MellyTrade

Junie is an IDE-native agent for small scoped tasks in this repository.

## Recommended Modes

- Ask Mode for read-only analysis and safety review.
- Code Mode for small, scoped changes.
- Avoid Brave Mode for MellyTrade work.

## Recommended Task Types

- Safety review
- GET-only endpoint work
- Frontend read-only panel work
- Pytest safety checks
- PR readiness and publish gates

## How Junie Fits with Other Tools

- Claude Code: planner and reviewer.
- Codex: executor for scoped implementation and validation.
- Junie: IDE-native scoped agent for local editing and review.
- OpenCode or local models: optional fallback when appropriate.

## Safe First Tasks

- PAPER-001B GET-only sandbox preview endpoint
- PAPER-001C AI Workspace sandbox preview panel

## Safety Reminder

- No live trading.
- No execution routes.
- No broker, MT5, or IBKR order calls.
- No order buttons.
- No connect-live UX.
- Keep `autotrade=false`, `dry_run=true`, `read_only=true`, and `live_orders_blocked=true`.

