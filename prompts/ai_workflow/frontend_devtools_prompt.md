# Frontend DevTools Prompt

## When to use

Use this when frontend files changed and a browser smoke check is needed.

## Safety boundaries

- Smoke verification only.
- No execution or trading interaction.
- No live-connect UX.
- No order buttons.

## Copy-paste prompt

```text
Verify the MellyTrade frontend with browser/devtools checks.

Requirements:
- Start the app locally if frontend files changed.
- Verify the page renders.
- Check console errors.
- Check failed network calls.
- Check that no order buttons, connect-live controls, or live trading UX
  appeared.
- Report only what you can verify in the browser.
```

## Expected final report format

```text
- App started:
- Page rendered:
- Console errors:
- Failed network calls:
- Unsafe UI controls:
- Notes:
```
