# Paper Run Preview iPad Smoke Result Template

**STATUS: TEMPLATE / NOT EXECUTED**

Use this template only after a real iPad / LAN / Tailscale smoke evidence run
has been performed for the Paper Run Preview route.

This document is intentionally docs-only. It must not be used to claim a pass
unless the test was actually run on the target device.

## Safety Posture

The Paper Run Preview route is read-only preview only:

- `autotrade=false`
- `dry_run=true`
- `read_only=true`
- `live_orders_blocked=true`
- `execution_enabled=false`
- max risk remains `<= 1%`
- human review required

No live orders, no broker execution, no MT5 execution, no IBKR execution, no
order routing, no secrets, and no account IDs.

## Report Metadata

- Date / time of test:
- Repo SHA tested:
- Device tested:
- iPadOS version:
- Browser / mode tested:
- Route tested: `/terminal/paper-run-preview`
- LAN URL used:
- Optional Tailscale URL used:
- Backend loopback-only confirmed:
- Frontend LAN-only through Vite confirmed:
- Screenshots captured outside repo:
- Screenshot files committed: **NO**

## Mandatory Evidence Notes

Record the evidence paths locally if you captured screenshots, but keep them
outside the repository. Suggested local folder:

- `C:\AI\MellyTrade_Workspace\screenshots\mobile-pwa-005-paper-run-preview`

Do not commit screenshots, videos, temp smoke files, or generated artifacts.

## What to Verify

### 1. Repo state

- `main` is current
- SHA tested is `6573f22` or newer
- No local artifact files were committed

### 2. Backend safe startup

- Backend started with the existing local command
- Health endpoint responds locally at `http://127.0.0.1:8001/health`
- Backend remains loopback-only
- No live trading is enabled
- No broker execution is enabled

### 3. Frontend LAN startup

- Vite is started with `--host 0.0.0.0`
- Frontend is reachable only over a trusted LAN or Tailscale path
- No secrets, credentials, or API keys are hardcoded or committed

### 4. iPad Safari smoke

- Page loads
- Paper Run Preview panel renders
- Safety chips and copy are visible:
  - `READ ONLY`
  - `DRY RUN`
  - `LIVE ORDERS BLOCKED`
  - `HUMAN REVIEW REQUIRED`
  - `EXECUTION OFF`
- `Load Preview` / `Refresh Preview` works
- Preview request is GET-only if observable
- No horizontal overflow in portrait
- No horizontal overflow in landscape
- No unsafe controls are present:
  - `Buy`
  - `Sell`
  - `Execute`
  - `Place Order`
  - `Submit Order`
  - `Live Trade`
  - `Auto Trade`

### 5. iPad installed PWA smoke

- Added to Home Screen from Safari
- Installed PWA opens correctly
- Route `/terminal/paper-run-preview` loads
- Safety copy remains visible
- `Back to Terminal` works if present
- Route refresh does not break the shell
- No horizontal overflow

### 6. Optional Tailscale smoke

- Only if Tailscale was already configured
- Same route and safety behavior confirmed
- No public exposure introduced
- No secrets or backend credentials exposed

## Pass / Fail Checklist

- [ ] Read-only preview only
- [ ] No live orders
- [ ] No broker execution
- [ ] No MT5 execution
- [ ] No IBKR execution
- [ ] No order routing
- [ ] Human review required
- [ ] Max risk `<= 1%`
- [ ] `autotrade=false`
- [ ] `dry_run=true`
- [ ] `read_only=true`
- [ ] `live_orders_blocked=true`
- [ ] `execution_enabled=false`
- [ ] Screenshots kept outside repo
- [ ] Screenshots not committed

## Troubleshooting Notes

Record exact failures here if any test step fails:

- Failure:
- Route:
- Device / mode:
- Likely cause:
- Safe next action:

## Validation

- `py -3.11 scripts/validate_safety_config.py`
- Static scan of this report file for unsafe execution terms

## Notes

- `POST`, `PUT`, `PATCH`, and `DELETE` must not be used for this smoke.
- `secret`, `token`, and `password` must only appear in security warning
  wording if needed.
- `MT5` and `IBKR` must only be mentioned in the context of no execution or
  do not expose warnings.
