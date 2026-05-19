# Cleanup Gate Prompt

## When to use

Use this after merge to clean up branches while preserving any local WIP.

## Safety boundaries

- Protect local WIP.
- Never pop/apply stashes automatically.
- Fast-forward main only.
- Delete branches only if safely merged.
- Never force delete without inspecting unique commits.

## Copy-paste prompt

```text
Run a safe post-merge cleanup for this MellyTrade branch.

Requirements:
- Protect any local WIP first.
- Inspect stashes before making changes.
- Update main using fast-forward only.
- Delete the branch only if Git confirms it is safely merged.
- Never force delete without inspecting unique commits first.
- Report the final state clearly.
```

## Expected final report format

```text
- Protected WIP:
- Main updated:
- Branch merged status:
- Branch deleted:
- Notes:
```
