# mellytrade-safety-review

## Purpose

Review a MellyTrade diff for safety, scope, and regression risk.

## When to use

Use before merge, publish, or any approval decision.

## Hard safety boundaries

- Review only.
- No edits.
- No trading or broker actions.
- No secrets exposure.

## Step-by-step procedure

1. Inspect the diff scope.
2. Scan for forbidden runtime changes.
3. Check UI and route surfaces for unsafe controls.
4. Scan for secrets or credential exposure.
5. Review tests and validation results.
6. Summarize concrete findings first.

## Validation expectations

- Diff scope must match the task.
- Tests must support the change.
- Any suspicious change must be called out clearly.

## Final report template

```text
- Findings:
- Scope:
- Tests:
- Safety issues:
- Secrets scan:
- Recommendation:
```
