# MellyTrade Safety Review

Use this skill to review any proposed change in MellyTrade before it ships.

## Review Checklist

- Check the changed files and confirm the scope is narrow.
- Scan for forbidden trading surfaces.
- Verify there is no live trading, order execution, broker execution, or secrets exposure.
- Verify the safety flags remain intact:
  - `read_only=true`
  - `dry_run=true`
  - `live_orders_blocked=true`
- Verify tests and validation coverage are present.

## What to Flag

- `SAFE` for docs-only or clearly read-only changes with no safety drift.
- `NEEDS REVIEW` for changes that are ambiguous, larger than expected, or need a closer human look.
- `BLOCKER` for live trading, broker execution, secrets, order buttons, connect-live UX, or workflow escalation.

## Forbidden Surfaces

- Live order routes
- Broker execution paths
- MT5 / IBKR order calls
- Order buttons
- Connect-live flows
- Secret or credential handling
- Workflow or permission escalation

## Final Output Template

```text
Status: SAFE | NEEDS REVIEW | BLOCKER
Scope:
- files:
- summary:
Safety:
- read_only:
- dry_run:
- live_orders_blocked:
Findings:
- ...
Validation:
- ...
```

