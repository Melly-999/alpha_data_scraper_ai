# Final Local Demo Smoke Report

## Purpose

Final local smoke validation for the MellyTrade Closed Beta Demo Ready Candidate.

## Commit under test

- branch: `docs/closed-beta-demo-ready-candidate`
- commit SHA: `cded222`
- origin/main SHA: `cded222`
- date/time: `2026-05-17 03:40 UTC`

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

## Validation commands

- `py -3.11 scripts/validate_safety_config.py`
- `cd frontend && npm run build`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/smoke_local_readonly.ps1 -BaseUrl http://127.0.0.1:8001`

## Smoke results

| Check | Result | Notes |
|---|---|---|
| safety config validation | PASS | `py -3.11 scripts/validate_safety_config.py` passed |
| frontend build | PASS | `cd frontend && npm run build` passed |
| backend local startup | PASS | `scripts/start_backend_local.ps1` started successfully |
| frontend local startup | PASS | `scripts/start_frontend_local.ps1` started successfully |
| local read-only smoke script | PASS | `scripts/smoke_local_readonly.ps1 -BaseUrl http://127.0.0.1:8001` passed |
| terminal route | PASS | `http://127.0.0.1:5173/terminal` returned 200 |
| signals route | PASS | `http://127.0.0.1:5173/signals` returned 200 |
| risk route | PASS | `http://127.0.0.1:5173/risk` returned 200 |
| brokers route | PASS | `http://127.0.0.1:5173/brokers` returned 200 |
| portfolio route | PASS | `http://127.0.0.1:5173/portfolio` returned 200 |
| audit route | PASS | `http://127.0.0.1:5173/audit` returned 200 |
| browser UI smoke | PASS | Local Playwright snapshot confirmed read-only / dry-run badges and advisory scanner content |

## Invariants confirmed

- no live trading
- no broker execution
- no mutation endpoints used
- no order/execution routes used
- scanner remains advisory
- human review required
- safety badges visible in browser smoke
- screenshots already exist in `docs/assets/screenshots/closed-beta`

## Known limitations

- [docs/product/closed_beta_limitations.md](../product/closed_beta_limitations.md)

## Disclaimer

- [docs/product/closed_beta_disclaimer.md](../product/closed_beta_disclaimer.md)

## Result

CANDIDATE PASS

