# mellytrade-publish-gate

## Purpose

Gate branch publish and draft PR creation.

## When to use

Use after validation when the branch is ready to push and open a draft PR.

## Hard safety boundaries

- Normal push only.
- No direct push to main.
- No secrets.
- No runtime safety weakening.

## Step-by-step procedure

1. Verify the current branch.
2. Verify the worktree status.
3. Verify the diff scope.
4. Run validation.
5. Push the branch normally.
6. Create a draft PR.
7. Report branch, SHA, and PR URL.

## Validation expectations

- Branch must be correct.
- Diff scope must match the task.
- Validation must pass before publish.

## Final report template

```text
- Branch:
- SHA:
- Diff scope:
- Validation:
- Push status:
- PR URL:
```
