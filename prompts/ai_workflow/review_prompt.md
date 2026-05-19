# Review Prompt

## When to use

Use this to review a branch or pull request before merge.

## Safety boundaries

- Review only.
- No code changes.
- No merge unless scope, validation, and safety pass.
- No secrets exposure.

## Copy-paste prompt

```text
Review this MellyTrade branch or PR.

Required checks:
- Diff scope review.
- Tests review.
- Safety review.
- Secrets scan.

Do not approve merge unless:
- the diff stays within scope,
- the validation passed,
- and the safety posture remains intact.

Report concrete findings first, then note any residual risks.
```

## Expected final report format

```text
- Findings:
- Scope check:
- Tests check:
- Safety check:
- Secrets check:
- Merge recommendation:
```
