# iPad PWA Paper Run Preview Showcase

## Feature Summary

MellyTrade now includes a read-only Paper Run Preview flow that runs safely as an iPad-installable PWA.

This showcase is meant for portfolio and README use. It presents the operator dashboard as a paper trading preview, not a live trading system.

## What It Demonstrates

- paper trading preview
- risk-gated decision preview
- deterministic run preview
- GET-only backend endpoints
- frontend Paper Run Preview panel
- iPad / Safari PWA support
- safety-first design

## Safe Architecture Summary

- frontend calls `GET /paper/run/preview`
- no `POST` / `PUT` / `PATCH` / `DELETE` trading mutation endpoints
- no broker execution
- no MT5 / IBKR account data
- no real orders
- backend stayed loopback-only during the iPad LAN smoke
- frontend LAN / Tailscale access was used only for local testing

## Safety Badges

- `READ ONLY`
- `DRY RUN`
- `LIVE ORDERS BLOCKED`
- `HUMAN REVIEW REQUIRED`
- `EXECUTION OFF`

## iPad / PWA Result

- Safari loads the terminal
- Add to Home Screen works
- standalone PWA launch works
- Paper Run Preview panel works
- text / number inputs do not zoom
- Side select does not zoom
- safety chips are visible
- no broker prompts appear
- no `Buy` / `Sell` / `Execute` / `Place Order` controls appear

## Evidence Links

- [DEMO-009 smoke evidence](../demo/demo_009_ipad_pwa_smoke_evidence.md)
- [DEMO-009 screenshot checklist](../demo/demo_009_ipad_pwa_screenshot_checklist.md)
- [iPad PWA smoke test guide](../devices/ipad_pwa_smoke_test.md)

## Portfolio-Safe Wording

Use this showcase as:

- paper trading preview
- read-only simulation
- risk-gated preview
- operator dashboard
- PWA smoke tested on iPad

Do not describe it as:

- live trading
- broker execution
- profitability proof
- guaranteed profit
- production trading readiness
- App Store release
- TestFlight release

## Safety Note

This showcase does not claim live trading capability, and it does not expose broker credentials, MT5 / IBKR account data, or public backend access.
