# Local Demo 404 Regression Checklist

## Purpose

Prevent regression of the local-demo 404 fix for expected read-only tester
endpoints.

## Endpoints that must return 200

- `GET /api/backtest/summary`
- `GET /api/investment`
- `GET /api/signals/feed`

## Expected payload posture

Each endpoint must be:

- read-only
- dry-run-only
- degraded local-demo if no real data provider exists
- deterministic
- free of order/execution intent
- free of broker credential requirements
- free of investment advice
- free of guaranteed-profit claims

## Commands

```powershell
Invoke-WebRequest http://127.0.0.1:8001/api/backtest/summary -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:8001/api/investment -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:8001/api/signals/feed -UseBasicParsing
```

## Backend tests

```bash
py -3.11 -m pytest tests/app/test_local_demo_readonly_endpoints.py -q
```

## Stop conditions

Stop and report if:

- any endpoint returns 404
- any endpoint returns 500
- any endpoint requires credentials
- any endpoint exposes account IDs
- any endpoint contains order/execution fields
- any endpoint suggests live trading
- any endpoint suggests investment advice
- any endpoint claims guaranteed profit

## Acceptance

PASS:

- all three endpoints return HTTP 200
- safety posture present
- no forbidden keys
- no generated artifacts staged

BLOCKED:

- any endpoint 404s
- safety posture missing
- forbidden keys appear
- app asks for broker credentials
- order/execution controls appear
