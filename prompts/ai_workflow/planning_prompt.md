# Planning Prompt

## When to use

Use this before any code or docs change to define scope and safety boundaries.

## Safety boundaries

- No code changes during planning.
- No runtime safety weakening.
- No trading, broker, or live-connect changes.
- No secrets or private paths.

## Copy-paste prompt

```text
You are planning a MellyTrade task.

Required output:
1. Inspect repo state.
2. Define the scope.
3. List the files expected to change.
4. List the validation commands.
5. Identify the safety risks.
6. Confirm that no code changes will be made during planning.

Constraints:
- Keep the repository read-only for this step.
- Do not change runtime behavior.
- Do not propose execution routes, order buttons, broker execution, live
  connect UX, autotrade changes, or risk weakening.
- Do not use secrets or private paths.
```

## Expected final report format

```text
- Current branch:
- Repo state:
- Scope:
- Expected files:
- Validation plan:
- Safety risks:
- Confirmed no code changes:
```
