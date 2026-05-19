# PR Publish Gate

Use this skill before pushing or publishing a PR for MellyTrade.

## Checklist

- Inspect branch and diff scope.
- Verify only the expected files changed.
- Run safety validation.
- Run relevant pytest coverage.
- Run frontend build if frontend changed.
- Perform a static safety scan.

## Rules

- Do not merge automatically.
- Do not widen scope.
- Do not push without explicit instruction.

## Final PR Summary Template

```text
Branch:
Changed files:
Validation:
Safety:
Notes:
```

