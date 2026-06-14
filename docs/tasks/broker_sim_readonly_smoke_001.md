# Broker-Sim Read-Only Smoke 001

SOURCE STATUS: Public-safe, read-only evidence. No secrets, no credentials, no
account IDs. This document describes a GET-only smoke checklist for the
simulated / paper broker preview surface. It does not implement, enable, or
recommend any live broker execution.

> **This is not live trading.** The smoke script does **not** connect to a real
> broker, does **not** place / submit / cancel orders, does **not** execute
> trades, and requires **no credentials**. It is GET-only evidence for the
> read-only simulated broker preview described in
> [broker_sim_readiness_audit_001.md](broker_sim_readiness_audit_001.md).

## 1. Purpose

Provide a repeatable, GET-only smoke that verifies the existing simulated /
paper broker preview surface is safe to demo: the documented safety flags hold,
the read-only endpoints respond, and no sensitive fields leak. It produces
demo-readiness evidence without adding any new execution surface.

## 2. Baseline

- Branch: `feat/broker-sim-readonly-smoke-001`
- Base: `origin/main` @ `e5ffe1b0200b7d21ab571e58f1eced5cda519b70` (the merged
  readiness audit, classification **B**).
- Safety validator: `python scripts/validate_safety_config.py` → **OVERALL: PASS**.
- Date: 2026-06-14.

## 3. Scope

In scope:

- `scripts/broker_sim_readonly_smoke.ps1` — a GET-only PowerShell smoke.
- This evidence doc.

Out of scope (explicitly not changed): runtime / frontend / backend / API
implementation, config, workflows, package files, env vars, broker credentials.
No new routes, no mutating verbs, no broker SDK usage.

## 4. Safety posture

The surface under test preserves, and the script asserts:

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
execution_enabled=false
max_risk_per_trade <= 1%
no broker execution
no live trading UX
```

## 5. Endpoints probed (GET only)

Preflight: `GET /health` (also tries `GET /api/health`). If unreachable, the run
is a documented degraded SKIP (exit 0) — not a failure.

Safety anchor (required when the backend is up):

- `GET /api/safety/status`

Read-only surface (missing routes are recorded as SKIP, not failures):

- `GET /api/broker/health`, `GET /api/broker/account`
- `GET /api/brokers` (then, per discovered adapter id:
  `GET /api/brokers/{id}/status`, `/account`, `/positions`)
- `GET /api/alpaca-paper/status`, `/account-preview`, `/market-clock`
- `GET /api/account/overview`
- `GET /api/positions/open`, `GET /api/positions/history`
- `GET /api/orders`
- `GET /api/risk/status`, `GET /api/risk/violations`
- `GET /api/terminal/summary`

For every response body, the script scans (recursively) for forbidden /
sensitive field names and fails if any are present:
`account_id`, `broker_account_id`, `broker_order_id`, `execution_id`,
`secret`, `token`, `api_key`, `private_key`.

## 6. Expected safe outcomes

- `dry_run == true`, `auto_trade == false`, `read_only == true`,
  `live_orders_blocked == true`, `max_risk_per_trade_pct <= 1.0`.
- Read-only endpoints return HTTP 200 (or are absent → SKIP).
- No forbidden / sensitive fields in any response body.
- Broker adapters present on the demo surface are safe/demo
  (e.g. `safe-disconnected`, `ibkr-paper`) and expose no live execution.

## 7. Script usage

```powershell
# Local backend (default: http://127.0.0.1:8001)
.\scripts\broker_sim_readonly_smoke.ps1

# Custom / hosted backend, GET-only
.\scripts\broker_sim_readonly_smoke.ps1 -BaseUrl https://your-backend.example.com -TimeoutSec 15
```

Parameters: `-BaseUrl <url>` (backend base; default local), `-TimeoutSec <int>`
(per-request timeout, default 8).

Exit codes: `0` = read-only surface safe **or** backend offline (degraded);
`1` = a hard safety failure (an unsafe flag value, or a forbidden field in a
response).

## 8. Hosted smoke example

```powershell
.\scripts\broker_sim_readonly_smoke.ps1 -BaseUrl https://your-backend.example.com -TimeoutSec 15
```

The hosted backend is exercised GET-only and requires no credentials. Substitute
your own hosted base URL; none is hard-coded here.

## 9. Local smoke example

Start a local backend, then run the smoke (recorded run, 2026-06-14, local
backend on `127.0.0.1:8011`):

```text
MellyTrade broker-sim read-only smoke  |  backend: http://127.0.0.1:8011
GET-only. No POST/PUT/PATCH/DELETE. No credentials. No execution. No secrets.

[PASS] backend reachable  (/health)
[PASS] GET /api/safety/status -> HTTP 200
[PASS] safety.dry_run=True
[PASS] safety.auto_trade=False
[PASS] safety.read_only=True
[PASS] safety.live_orders_blocked=True
[PASS] safety.max_risk_per_trade_pct<=1.0  (1)
[PASS] safety no forbidden fields
[PASS] GET /api/broker/health -> HTTP 200
[PASS] GET /api/broker/account -> HTTP 200
[PASS] GET /api/brokers -> HTTP 200
[PASS] GET /api/alpaca-paper/status -> HTTP 200
[PASS] GET /api/alpaca-paper/account-preview -> HTTP 200
[PASS] GET /api/alpaca-paper/market-clock -> HTTP 200
[PASS] GET /api/account/overview -> HTTP 200
[PASS] GET /api/positions/open -> HTTP 200
[PASS] GET /api/positions/history -> HTTP 200
[PASS] GET /api/orders -> HTTP 200
[PASS] GET /api/risk/status -> HTTP 200
[PASS] GET /api/risk/violations -> HTTP 200
[PASS] GET /api/terminal/summary -> HTTP 200
[PASS] GET /api/brokers/ibkr-paper/{status,account,positions} -> HTTP 200
[PASS] GET /api/brokers/safe-disconnected/{status,account,positions} -> HTTP 200

  PASS: 47   SAFETY-FAIL: 0   WARN: 0   SKIP: 0
  RESULT: PASS -- read-only surface safe
```

(Per-endpoint "no forbidden fields" PASS lines omitted above for brevity; all
47 checks passed.)

## 10. PASS / FAIL criteria

- **PASS (exit 0):** every present endpoint responds, all safety flags hold, and
  no forbidden fields appear; **or** the backend is offline (degraded SKIP).
- **FAIL (exit 1):** any safety flag has an unsafe value, or any forbidden /
  sensitive field appears in a response body.
- Missing routes (HTTP 404) and transient endpoint errors are recorded as
  SKIP / WARN and are not safety failures.

## 11. Forbidden actions

The script and this task must never:

- use POST / PUT / PATCH / DELETE, or place / submit / cancel orders, or execute
  trades;
- connect to a real broker API or send broker auth headers;
- read `.env` files, print secrets, or use credentials;
- add Buy / Sell / Order / Execute UI;
- change safety config, risk config, runtime, workflows, or package files.

## 12. Known limitations

- The smoke validates the **read-only** surface only; it does not exercise the
  dry-run report or paper-ticket-draft POST endpoints (intentionally — this task
  is GET-only).
- `GET /api/paper/run/preview` requires query parameters and is omitted from the
  default probe set to avoid constructing trade-shaped inputs; it remains a
  GET-only dry-run preview if probed manually.
- Endpoint payload shapes can evolve; the script asserts flags/fields
  defensively and treats absent fields as informational.

## 13. Next steps

- **BROKER-SIM-READONLY-SMOKE-SCRIPT-001-PUBLISH** — wire this smoke into the
  demo/evidence flow (and optionally CI as a non-required, GET-only check).
- **BROKER-SIM-WALKTHROUGH-DOC-001** — a single demo narrative tying the GET
  surface + paper ticket *draft* into one read-only walkthrough.

---

*MellyTrade is a read-only, dry-run, paper-only portfolio project. It is not a
commercial platform, not a live trading system, and not financial advice.*
