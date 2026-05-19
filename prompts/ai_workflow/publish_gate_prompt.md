# Publish Gate Prompt

## When to use

Use this before pushing a branch and opening a draft PR.

## Safety boundaries

- Normal push only.
- No direct push to main.
- No secrets.
- No runtime safety weakening.

## Copy-paste prompt

```text
Prepare this MellyTrade branch for publish.

Requirements:
- Verify the current branch.
- Verify the worktree is clean or contains only the expected docs-only changes.
- Verify the diff scope.
- Run validation.
- Use a normal push only.
- Create a draft PR.
- Do not push directly to main.
- Report the branch, SHA, and PR URL.
```

## Expected final report format

```text
- Branch:
- SHA:
- Diff scope:
- Validation:
- Push status:
- PR URL:
```
