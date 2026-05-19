# mellytrade-frontend-smoke

## Purpose

Verify frontend changes with browser/devtools smoke checks.

## When to use

Use when frontend/runtime files changed and the app needs browser verification.

## Hard safety boundaries

- Smoke verification only.
- No trading execution.
- No connect-live UX.
- No order buttons.

## Step-by-step procedure

1. Start the app locally if the frontend changed.
2. Open the page in a browser.
3. Verify the page renders.
4. Check console errors.
5. Check failed network calls.
6. Verify no unsafe trading controls appeared.
7. Summarize browser findings.

## Validation expectations

- Browser renders successfully.
- Console remains clean or errors are explained.
- No order or live-connect controls appear.

## Final report template

```text
- App started:
- Render status:
- Console:
- Network:
- Unsafe controls:
- Notes:
```
