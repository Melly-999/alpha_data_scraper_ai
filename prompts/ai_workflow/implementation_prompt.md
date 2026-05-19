# Implementation Prompt

## When to use

Use this for a small scoped implementation after planning and docs lookup.

## Safety boundaries

- Fresh branch only.
- Minimal diff only.
- No unrelated refactors.
- No runtime safety weakening.
- No trading, broker, or live-connect changes.

## Copy-paste prompt

```text
Implement the smallest safe MellyTrade patch for the agreed task.

Requirements:
- Work from a fresh branch.
- Keep the diff minimal and scoped.
- Run the relevant tests.
- Do not introduce unrelated refactors.
- Do not weaken runtime safety, trading gates, or risk controls.
- Do not add execution routes, order buttons, broker execution, or live-connect
  UX.
- Report the files changed and the validation results.
```

## Expected final report format

```text
- Branch:
- Files changed:
- Tests run:
- Results:
- Safety check:
- Notes:
```
