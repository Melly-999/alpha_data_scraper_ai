# Safety Audit Prompt

## When to use

Use this before merge, publish, or any sign-off on a MellyTrade change.

## Safety boundaries

- Audit only.
- No code changes.
- No trading or broker operations.
- No secrets or credentials.

## Copy-paste prompt

```text
Audit this MellyTrade change for safety.

Check:
- autotrade=false
- dry_run=true
- read_only=true
- live_orders_blocked=true
- max risk <=1%
- no execution routes
- no order buttons
- no broker execution
- no connect-live UX
- no secrets
- GET/read-only by default
- tests pass

Report any drift or suspicious findings clearly.
```

## Expected final report format

```text
- Safety posture:
- Route review:
- UI review:
- Secrets scan:
- Tests:
- Verdict:
```
