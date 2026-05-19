# mellytrade-safe-implementation

## Purpose

Implement a small, safe MellyTrade patch with minimal scope.

## When to use

Use for small docs or code changes that have already been scoped.

## Hard safety boundaries

- Preserve the safety posture.
- Avoid unrelated refactors.
- Do not add execution routes, order buttons, broker execution, or live-connect
  UX.
- Do not modify secrets or risk policy.

## Step-by-step procedure

1. Confirm the branch and scope.
2. Make the smallest viable patch.
3. Keep unrelated code untouched.
4. Run relevant tests.
5. Check for safety drift.
6. Summarize files changed and validation results.

## Validation expectations

- Relevant tests must run.
- Safety posture must remain intact.
- Diff should stay narrow and focused.

## Final report template

```text
- Branch:
- Files changed:
- Tests run:
- Results:
- Safety check:
- Notes:
```
