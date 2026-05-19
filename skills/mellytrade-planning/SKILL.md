# mellytrade-planning

## Purpose

Plan a MellyTrade task without making file changes.

## When to use

Use when you need scope definition, risk review, and a validation plan before
editing anything.

## Hard safety boundaries

- No file modifications.
- No runtime safety weakening.
- No trading, broker, or live-connect changes.
- No secrets or private paths.

## Step-by-step procedure

1. Inspect repo state.
2. Confirm the branch and current commit.
3. Define the task scope.
4. List the files expected to change.
5. List the validation commands.
6. Identify safety risks and assumptions.
7. Stop without editing files.

## Validation expectations

- Planning output must identify the task scope.
- Planning output must include a validation plan.
- Planning output must confirm that no files were changed.

## Final report template

```text
- Branch:
- Commit:
- Scope:
- Expected files:
- Validation plan:
- Safety risks:
- Confirmed no file changes:
```
