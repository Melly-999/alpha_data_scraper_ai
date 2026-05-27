# DEPLOY-004 — Hosted Backend Smoke Checklist

## 1. Purpose

This is a **checklist only**. Nothing in this document has been executed.
No deployment has been performed. No cloud resources have been created.

Use this checklist after a successful Railway or Render backend deployment
(see `backend_demo_deploy_railway_render.md`) to verify that the hosted
backend is safe, read-only, and demo-ready.

---

## 2. Status

| Field | Value |
|---|---|
| Task | DEPLOY-004 |
| Scope | Hosted backend smoke — planning and checklist |
| Deploy performed | No |
| Cloud resources created | No |
| Secrets committed | No |
| Runtime files changed | No |

---

## 3. Prerequisites

Before executing any hosted smoke check, verify all of the following locally:

- [ ] `runtime.txt` exists at repository root and contains `python-3.11`
- [ ] `Dockerfile.api` exists at repository root (added in DEPLOY-003B)
- [ ] Safety validation passes locally:

  ```powershell
  py -3.11 scripts/validate_safety_config.py
  ```

  Expected: `OVERALL: PASS`

- [ ] Safety regression tests pass locally:

  ```powershell
  py -3.11 -m pytest tests/app/test_openapi_forbidden_paths.py tests/app/test_safety_invariants.py -q
  ```

- [ ] Start command is confirmed:

  ```text
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

  (`$PORT` is injected automatically by Railway and Render.)

- [ ] CORS / allowed origins are configured through the hosting dashboard only — not committed to the repo.
- [ ] No secrets, tokens, passwords, or API keys are committed to the repository.
- [ ] No broker credentials (`MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER`) exist in any deployed config file.

---

## 4. Required Safety Env/Config Notes

These safety invariants must hold in the hosted environment. They are enforced by `config.json` and `app/core/settings.py`. Do not override them via platform environment variables.

| Invariant | Required value | How enforced |
|---|---|---|
| `autotrade.enabled` | `false` | `config.json` + safety regression tests |
| `autotrade.dry_run` | `true` | `config.json` + safety regression tests |
| `read_only` | `true` | every emitted audit event, safety endpoint |
| `live_orders_blocked` | `true` | audit event always emitted |
| `execution_enabled` | `false` | response field on every paper preview |
| `max_risk_pct` | `≤ 1.0` | enforced by paper run preview service |

**Do not set `autotrade.enabled=true`, `dry_run=false`, or `execution_enabled=true` in any hosted environment variable.**

---

## 5. Smoke Endpoints

Replace `<hosted-url>` with the Railway or Render deployment URL.
All requests are `GET` only. No `POST`, `PUT`, `PATCH`, or `DELETE` calls.

### 5.1 Health check

```text
GET https://<hosted-url>/health
```

**Expected:**
- HTTP 200
- `status: ok` or equivalent liveness confirmation

```text
GET https://<hosted-url>/api/health
```

**Expected:**
- HTTP 200
- backend reachable, no broker credentials required

### 5.2 Safety status

```text
GET https://<hosted-url>/api/safety/status
```

**Expected:**
- HTTP 200
- `read_only: true`
- `dry_run: true`
- `autotrade_enabled: false` or `autotrade.enabled: false`
- `live_orders_blocked: true`

### 5.3 Paper Run Preview — valid BUY geometry

```text
GET https://<hosted-url>/api/paper/run/preview
    ?symbol=EURUSD
    &side=BUY
    &quantity=1
    &entry_price=1.0800
    &stop_loss=1.0750
    &take_profit=1.0900
    &confidence=72
    &max_risk_pct=0.5
```

**Expected:**
- HTTP 200
- `allowed: true`
- `paper_run` object present (not null)
- `paper_only: true`
- `dry_run: true`
- `read_only: true`
- `live_orders_blocked: true`
- `requires_human_review: true`
- `execution_enabled: false`
- IDs are paper-scoped (`paper_order_*`, `paper_fill_*`, `paper_pos_*`)
- **No** `account_id`, `broker_order_id`, `execution_id`, `trade_id`, `secret`, `token`, `password`, `api_key`

### 5.4 Paper Run Preview — invalid BUY geometry (stop_loss above entry)

```text
GET https://<hosted-url>/api/paper/run/preview
    ?symbol=EURUSD
    &side=BUY
    &quantity=1
    &entry_price=1.0800
    &stop_loss=1.0900
    &take_profit=1.0700
    &confidence=72
    &max_risk_pct=0.5
```

**Expected:**
- HTTP 200 (not an error — validation failures are handled gracefully)
- `allowed: false`
- `paper_run: null`
- `reason` field present and descriptive
- Safety flags (`paper_only`, `dry_run`, `read_only`, `live_orders_blocked`) still present

### 5.5 Paper Run Preview — max_risk_pct exceeds 1% cap

```text
GET https://<hosted-url>/api/paper/run/preview
    ?symbol=EURUSD
    &side=BUY
    &quantity=1
    &entry_price=1.0800
    &stop_loss=1.0750
    &take_profit=1.0900
    &confidence=72
    &max_risk_pct=1.5
```

**Expected:**
- HTTP 200
- `allowed: false`
- `reason` mentions risk cap exceeded (max_risk_pct must not exceed 1.0)
- `paper_run: null`
- Safety flags still present

### 5.6 Method safety — POST must not be accepted

```text
POST https://<hosted-url>/api/paper/run/preview
```

**Expected:**
- HTTP 405 Method Not Allowed

No `POST`, `PUT`, `PATCH`, or `DELETE` method should succeed against the paper run preview endpoint. The route is `GET` only by design.

### 5.7 OpenAPI schema check

```text
GET https://<hosted-url>/openapi.json
```

**Expected:**
- HTTP 200
- Scan response for: `POST /orders`, `POST /execute`, `POST /trade`, `POST /paper/run`
- **None of the above should be present**
- Only `GET /api/paper/run/preview` should appear under paper-run-preview paths

---

## 6. Browser and Frontend Checks

If the hosted frontend (`VITE_API_BASE_URL` pointing to `<hosted-url>`) is also deployed:

- [ ] Paper Run Preview panel loads and returns a response from the hosted backend
- [ ] Safety chips visible: `READ ONLY` · `DRY RUN` · `LIVE ORDERS BLOCKED` · `HUMAN REVIEW REQUIRED` · `EXECUTION OFF`
- [ ] Melly Pet companion visible in AI Workspace right rail (all four chips: `READ ONLY`, `DRY RUN`, `LIVE ORDERS BLOCKED`, `EXECUTION OFF`)
- [ ] No `Buy` / `Sell` / `Execute` / `Place Order` buttons present anywhere in the demo UI
- [ ] No broker credentials or account data visible in the UI
- [ ] No horizontal overflow at desktop or iPad viewport

---

## 7. Evidence Table

Use this table to record results when the smoke is executed. All evidence files (logs, screenshots) must be saved **outside the repository** — do not commit them.

| # | Check | Expected | Actual | Status | Evidence file (external only) |
|---|---|---|---|---|---|
| 1 | `GET /health` | HTTP 200 | — | ☐ | — |
| 2 | `GET /api/health` | HTTP 200 | — | ☐ | — |
| 3 | `GET /api/safety/status` | `read_only:true`, `dry_run:true` | — | ☐ | — |
| 4 | Paper preview — valid BUY | `allowed:true`, safety flags | — | ☐ | — |
| 5 | Paper preview — invalid geometry | `allowed:false`, `paper_run:null` | — | ☐ | — |
| 6 | Paper preview — risk cap exceeded | `allowed:false` | — | ☐ | — |
| 7 | `POST /api/paper/run/preview` | HTTP 405 | — | ☐ | — |
| 8 | OpenAPI schema — no execution routes | No POST execute/orders/trade | — | ☐ | — |
| 9 | Frontend: safety chips visible | All 5 chips | — | ☐ | — |
| 10 | Frontend: Melly Pet visible | All 4 chips | — | ☐ | — |
| 11 | Frontend: no order buttons | None present | — | ☐ | — |

**External evidence path (do not commit):**

```text
C:\AI\MellyTrade_Workspace\screenshots\deploy-004-hosted-smoke\
```

Recommended filename pattern:

```text
deploy_004_01_health_response.png
deploy_004_02_api_health_response.png
deploy_004_03_safety_status_response.png
deploy_004_04_paper_preview_valid_buy.png
deploy_004_05_paper_preview_invalid_geometry.png
deploy_004_06_paper_preview_risk_cap.png
deploy_004_07_post_405.png
deploy_004_08_openapi_schema.png
deploy_004_09_frontend_safety_chips.png
deploy_004_10_melly_pet_visible.png
deploy_004_11_no_order_buttons.png
```

---

## 8. Rollback and Failure Notes

If any check fails:

- Keep the demo in **local or mock mode** — the existing LAN / Tailscale path documented in `docs/demo/demo_009_ipad_pwa_smoke_evidence.md` remains a valid fallback.
- Do **not** attempt to fix a failed hosted deployment by enabling live execution, relaxing safety flags, or adding broker credentials.
- Do **not** add secrets or credentials to the repository to resolve a startup failure.
- If the backend fails to start, check the hosting platform logs. Common issues:
  - Missing `requirements.txt` dependency — fix in `requirements.txt`, do not modify `Dockerfile.api` without a separate review.
  - `PORT` not injected — confirm the start command uses `$PORT`, not a hardcoded port.
  - Import error — run `py -3.11 -m pytest tests/app/ -q` locally first.
- If safety validation fails on the hosted endpoint, take the service offline and investigate before sharing any demo URL.

---

## 9. Do Not Do List

| Forbidden action | Reason |
|---|---|
| Enable `autotrade.enabled=true` in hosted env | Safety posture — live trading is intentionally disabled |
| Set `dry_run=false` in any deployed config | Safety posture — dry-run must stay enabled |
| Commit secrets, tokens, passwords, or API keys | Security — use platform dashboard only |
| Add `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER` for a demo | No broker account connection needed or permitted |
| Enable a `POST /execute`, `POST /orders`, or `POST /trade` route | No execution routes in a demo deploy |
| Commit screenshots, logs, traces, or videos to the repo | Binary artifacts must stay outside the repo |
| Make live trading or profit claims about the hosted demo | This is a paper-only preview demo |
| Expose `execution_enabled=true` | Hardcoded to false in the paper run preview response |

---

## 10. Cross-References

- [DEPLOY-002 Backend Entrypoint and Health Audit](backend_entrypoint_health_audit.md)
- [Backend Demo Deploy Guide — Railway / Render](backend_demo_deploy_railway_render.md)
- [iPad PWA Paper Run Preview Showcase](../showcase/ipad_pwa_paper_run_preview.md)
- [DEMO-MASCOT-001 Melly Pet Evidence](../demo/demo_mascot_001_melly_pet_evidence.md)
- [DEMO-009 iPad PWA smoke evidence](../demo/demo_009_ipad_pwa_smoke_evidence.md)
- [Safety validation script](../../scripts/validate_safety_config.py)
- [`Dockerfile.api`](../../Dockerfile.api)
- [`runtime.txt`](../../runtime.txt)
