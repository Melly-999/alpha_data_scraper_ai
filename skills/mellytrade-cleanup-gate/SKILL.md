# mellytrade-cleanup-gate

## Purpose

Safely clean up branches and local state after merge.

## When to use

Use after merge to preserve WIP, inspect stashes, and remove only safely merged
branches.

## Hard safety boundaries

- Protect local WIP.
- Never pop/apply stashes automatically.
- Fast-forward main only.
- No force delete without checking unique commits.

## Step-by-step procedure

1. Inspect status and stash list.
2. Preserve any local WIP.
3. Update main with fast-forward only.
4. Check whether the branch is fully merged.
5. Delete only if safe.
6. Summarize the final state.

## Validation expectations

- Main must be aligned to the remote.
- WIP must remain preserved.
- Branch deletion must be justified by Git state.

## Final report template

```text
- Protected WIP:
- Main updated:
- Branch merged:
- Branch deleted:
- Notes:
```
