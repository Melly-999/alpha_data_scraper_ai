# Local Demo Tester Smoke Checklist

## Purpose

Verify that the MellyTrade local source-only beta launches cleanly for a tester
and does not produce 404s for expected read-only local-demo endpoints.

## Scope

This checklist is for local tester smoke only.

It does not:
- enable live trading
- connect to real brokers
- request broker credentials
- execute orders
- provide investment advice
- create generated release artifacts
- grant repository access
- send invite messages
- perform live trading
- present order/execution controls
- provide investment advice
- claim guaranteed profit

## Safety posture

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

## Preconditions

- tester has read-only repository access
- repository is cloned locally
- Python 3.11 is available
- Node.js LTS is available
- no broker credentials are required
- no `.env` file is required for this smoke
- no generated EXE/ZIP/MSI is required

## Step 1 - Validate safety config

Command:

```bash
py -3.11 scripts/validate_safety_config.py
```

Expected:

- `OVERALL: PASS`
- `5 checks passed`
- `0 failed`

Stop if:

- safety validator fails
- any flag appears weakened
- tester is asked for broker credentials

## Step 2 - Start local launcher

Command:

```bash
py -3.11 scripts/desktop_launcher.py
```

Alternative no-browser mode:

```bash
py -3.11 scripts/desktop_launcher.py --no-browser
```

Expected:

- backend starts on localhost
- frontend starts on localhost
- safety banner appears
- browser opens `/terminal`, unless `--no-browser` was used

## Step 3 - Open terminal UI

Open:

```text
http://127.0.0.1:5173/terminal
```

Expected visible safety badges:

- READ ONLY
- DRY RUN
- AUTO TRADE OFF
- LIVE ORDERS BLOCKED
- NO ORDER ROUTING or equivalent advisory label

Stop if:

- safety banner is missing
- buy/sell/order/execute controls appear
- order/execution controls appear
- live broker connection controls appear
- app asks for broker credentials
- app claims guaranteed profits
- app presents investment advice
- app claims no live trading is taking place

The tester should treat any UI that looks like live trading as a failure.

The tester should also report if the page states "no live trading",
"no investment advice", or "no guaranteed profit" but still shows any
execution-like control.

## Step 4 - Verify local-demo endpoints

In a browser or PowerShell, check:

```powershell
Invoke-WebRequest http://127.0.0.1:8001/api/backtest/summary -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:8001/api/investment -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:8001/api/signals/feed -UseBasicParsing
```

Expected:

- all three return HTTP 200
- no 404 for these paths
- responses include read-only / dry-run-only / degraded local-demo posture

## Step 5 - Watch backend logs

Expected:

- no repeated 404s for:
  - `/api/backtest/summary`
  - `/api/investment`
  - `/api/signals/feed`
- `200 OK` is acceptable
- degraded local-mode warnings are acceptable if they say no persistence client is configured

Acceptable local degraded warnings:

- audit writer has no client
- signal decision persistence has no client
- persistence is not available in local source-only beta

Stop if:

- warning asks for secrets
- warning asks for broker credentials
- warning suggests live execution
- warning says `dry_run=false` or `read_only=false`

## Step 6 - Smoke verdict

Use one:

- PASS - local demo is safe enough for tester exploration.
- PASS WITH NOTES - local demo works, but warnings or UI rough edges should be documented.
- BLOCKED - safety posture missing, endpoint 404s remain, app asks for credentials, or order/execution controls appear.

## Tester feedback to collect

Ask tester to report:

- did the app start?
- did safety validator pass?
- were safety badges visible?
- did the three endpoint checks return HTTP 200?
- were any 404s visible?
- were any warnings confusing?
- did any UI look like live trading?
- screenshots of terminal UI
- screenshots/logs of any error

## Related static test

- `tests/app/test_local_demo_readonly_endpoints.py`
