# Manual Alpaca Paper Smoke Prep 001

**Task ID:** MANUAL-PAPER-SMOKE-PREP-001
**Status:** PREP ONLY — smoke NOT performed
**Branch:** docs branch (no runtime changes)
**Date prepared:** 2026-06-16

> **This document prepares a manual local-only Alpaca Paper smoke test.**
> It does not run the smoke. No API calls are made. No env vars are set.
> No secrets are printed. No orders are submitted. This is documentation only.

---

## 1. Purpose

This document prepares an exact local-only manual smoke checklist for the Alpaca
Paper order submission sandbox. It captures the required environment, gates,
payload template, command templates, stop conditions, and cleanup steps so that
a human operator can safely perform the smoke manually at a later time.

**This document does not perform the smoke.** The actual smoke execution
(MANUAL-PAPER-SMOKE-RUN-001) requires separate, explicit human approval and is
not authorized by this document.

---

## 2. Current Merged Capabilities

The following PRs are merged to main as of the date of this document:

| PR    | Capability                            | Default state |
|-------|---------------------------------------|---------------|
| #309  | Alpaca Paper read-only adapter        | Enabled for paper env only |
| #310  | Alpaca Paper local order draft        | Always available (no broker call) |
| #311  | Alpaca Paper order submit sandbox     | **Blocked by default** — requires all explicit gates |

The POST route `POST /api/alpaca-paper/order-submit-sandbox` exists in the
codebase but returns a safe blocked response for every request unless every
gate in Section 4 is simultaneously satisfied.

**Manual paper smoke: NOT PERFORMED.**

---

## 3. Absolute Non-Goals

The following are explicitly out of scope for any activity described by this
document:

- No live trading of any kind
- No live broker endpoint (Alpaca live, IBKR, MT5, or any other)
- No frontend trading UI or trading button
- No autotrade (`autotrade.enabled` must remain `false`)
- No strategy-generated orders
- No model-selected symbol
- No AI-generated trade signal
- No real money (paper account only, and only if every gate is met)
- No secrets committed to git
- No credentials printed to any shared channel, log, or screenshot
- No financial advice
- No performance claims (no ROI, no win-rate, no profit projection)
- No deploy or cloud environment change
- No modification of runtime code, tests, workflows, or packages

---

## 4. Required Gates

All of the following must be simultaneously satisfied before any paper order
attempt is made. A failure on any single gate causes the route to return
`accepted=false` with no Alpaca API call.

### 4.1 Environment variable gates (all required)

| Variable | Required value | Notes |
|----------|---------------|-------|
| `ALPACA_ENV` | `paper` | Must be the literal string `paper` |
| `ALPACA_PAPER_ORDER_SUBMIT_ENABLED` | `true` | Must be the literal string `true` |
| `ALPACA_PAPER_ORDER_SUBMIT_SANDBOX_ACK` | `I_UNDERSTAND_THIS_SUBMITS_A_PAPER_ORDER` | Exact string — no whitespace variation |
| `ALPACA_PAPER_API_KEY` | `<local secret only>` | Never share or commit |
| `ALPACA_PAPER_SECRET_KEY` | `<local secret only>` | Never share or commit |

> Credential env vars may also be named `ALPACA_API_KEY` / `ALPACA_SECRET_KEY`
> or `APCA_API_KEY_ID` / `APCA_API_SECRET_KEY` — whichever names the service
> reads. Check the service source before setting. Set for this local session
> only; do not persist to any file.

### 4.2 Per-request gates (all required in the POST body)

| Field | Required value |
|-------|---------------|
| `confirm_paper_order` | `true` |
| `source` | `"manual_sandbox"` |
| `max_risk_pct` | `<= 1.0` |

### 4.3 Sandbox size caps (enforced by service)

| Field | Hard cap |
|-------|----------|
| `quantity` | `<= 100` |
| `notional` | `<= 5000` |
| `order_type` | `market` or `limit` only |

---

## 5. Secret Handling

Secrets must never leave the local machine in any readable form.

**Rules:**

- Never paste API keys or secret keys into any chat, ticket, or document
- Never commit `.env` or any file containing real credentials
- Never take or share a screenshot that shows credentials, order IDs, or
  account IDs
- Never log raw API key, secret, or account ID — the service redacts the
  broker order ID, but terminal history may still contain env var values
- Use local shell session environment only — `$env:VARNAME = "value"` in
  PowerShell; unset after the session
- If sharing output for review, redact all IDs, keys, and secrets before
  pasting (see Section 10)
- Clear terminal history if it contains credentials before sharing screen

---

## 6. Preflight Checklist

Complete every item in order before attempting any gated request.

- [ ] Working on a clean local main (or a branch that does not modify any
      runtime code, tests, or workflows)
- [ ] `git status` shows no unexpected uncommitted changes to source files
- [ ] `python scripts/validate_safety_config.py` returns **PASS** with no
      failures — confirm `autotrade=false`, `dry_run=true`, risk caps present
- [ ] Backend starts locally without errors (`uvicorn app.main:app --reload`
      or project-equivalent command)
- [ ] `GET /api/health` returns `200 OK`
- [ ] `GET /api/safety/status` (or equivalent endpoint) confirms safe posture:
      `autotrade: false`, `dry_run: true`, `live_orders_blocked: true`
- [ ] `POST /api/alpaca-paper/order-submit-sandbox` with no gates set returns
      `accepted: false`, `submitted_to_alpaca_paper: false` — **default-blocked
      confirmed**
- [ ] No frontend trading controls are visible in the UI (no "Submit Order"
      button wired to the sandbox route)
- [ ] No deployment step has been run; no cloud env vars have been changed
- [ ] Credentials are set in local shell session only — not in any file

---

## 7. Safe Manual Payload Template

The following JSON template is a placeholder only. The human operator must
choose every value manually based on their own judgment.

**This is not trade advice. The symbol, side, and quantity below are
placeholders. Do not treat any value here as a recommendation.**

```json
{
  "symbol": "<USER_CHOSEN_SYMBOL>",
  "side": "<buy_or_sell>",
  "quantity": 1,
  "order_type": "market",
  "time_in_force": "day",
  "entry_price": null,
  "stop_loss": null,
  "take_profit": null,
  "max_risk_pct": 0.1,
  "confirm_paper_order": true,
  "source": "manual_sandbox"
}
```

**Notes on the template:**

- Replace `<USER_CHOSEN_SYMBOL>` with a real ticker — operator's choice only
- Replace `<buy_or_sell>` with `"buy"` or `"sell"` — operator's choice only
- `quantity: 1` is an example minimum; operator may choose any value `<= 100`
- `max_risk_pct: 0.1` is a conservative example (0.1% of account); must be
  `<= 1.0`
- `entry_price`, `stop_loss`, `take_profit` are optional for a market order
  but may be required by the risk validation layer; pass `null` or a realistic
  reference price
- For `dry_run_preview_only: true`: add `"dry_run_preview_only": true` to
  exercise all gates without submitting — useful for gate verification before
  a real paper submission

---

## 8. PowerShell Command Templates

All commands below use **placeholders only**. Replace every `<...>` value
before running. Do not include real credentials in any shared document.

### 8.1 Set local session environment variables

```powershell
# Run in a local PowerShell session — NOT committed, NOT shared
$env:ALPACA_ENV = "paper"
$env:ALPACA_PAPER_ORDER_SUBMIT_ENABLED = "true"
$env:ALPACA_PAPER_ORDER_SUBMIT_SANDBOX_ACK = "I_UNDERSTAND_THIS_SUBMITS_A_PAPER_ORDER"
$env:ALPACA_API_KEY = "<YOUR_PAPER_API_KEY>"
$env:ALPACA_SECRET_KEY = "<YOUR_PAPER_SECRET_KEY>"
```

> Set these in the same terminal session that will run the backend.
> Never paste real values into this document.

### 8.2 Start backend

```powershell
# Start from repo root — adjust port if needed
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 8.3 Verify default-blocked (no gates — expected: accepted=false)

```powershell
# Confirm the route is blocked by default before setting any gates
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/api/alpaca-paper/order-submit-sandbox" `
  -ContentType "application/json" `
  -Body '{"symbol":"<SYMBOL>","side":"buy","quantity":1,"max_risk_pct":0.1,"confirm_paper_order":false,"source":""}'
# Expected: accepted=false, submitted_to_alpaca_paper=false
```

### 8.4 Safety status check

```powershell
Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:8000/api/safety/status"
# Confirm: autotrade=false, dry_run=true, live_orders_blocked=true
```

### 8.5 Gated paper submission request (all gates set)

```powershell
# Only after explicit approval is given (see Section 12)
$body = @{
    symbol             = "<USER_CHOSEN_SYMBOL>"
    side               = "<buy_or_sell>"
    quantity           = 1
    order_type         = "market"
    time_in_force      = "day"
    max_risk_pct       = 0.1
    confirm_paper_order = $true
    source             = "manual_sandbox"
} | ConvertTo-Json

Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/api/alpaca-paper/order-submit-sandbox" `
  -ContentType "application/json" `
  -Body $body
```

### 8.6 Dry-run gate verification (no submission, all gates exercised)

```powershell
$body = @{
    symbol                = "<USER_CHOSEN_SYMBOL>"
    side                  = "<buy_or_sell>"
    quantity              = 1
    order_type            = "market"
    time_in_force         = "day"
    max_risk_pct          = 0.1
    confirm_paper_order   = $true
    source                = "manual_sandbox"
    dry_run_preview_only  = $true
} | ConvertTo-Json

Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/api/alpaca-paper/order-submit-sandbox" `
  -ContentType "application/json" `
  -Body $body
# Expected: accepted=true (gates pass), submitted_to_alpaca_paper=false
```

### 8.7 Save redacted output to a local file

```powershell
# Capture and immediately inspect before sharing — redact before any paste
$result = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/api/alpaca-paper/order-submit-sandbox" `
  -ContentType "application/json" `
  -Body $body
$result | ConvertTo-Json -Depth 5 | Out-File -FilePath ".\smoke_logs\<YYYY-MM-DD>_paper_smoke_redacted.json"
# Open the file, manually redact any IDs, then share if needed
```

---

## 9. Stop Conditions

Abort the smoke immediately and restore safe state if any of the following
are observed:

| Condition | Action |
|-----------|--------|
| Any live broker endpoint detected in logs or responses | STOP — unset env vars, stop backend |
| `ALPACA_ENV` is not `paper` | STOP — do not proceed |
| Safety status endpoint shows `autotrade: true` | STOP |
| Safety status endpoint shows `live_orders_blocked: false` | STOP |
| Safety status endpoint shows `dry_run: false` | STOP |
| `read_only_posture_preserved: false` in any response | STOP |
| Response contains a raw `account_id`, `broker_account_id`, or unredacted `order_id` | STOP — review service redaction |
| Any frontend trading button appears wired to the submit route | STOP — do not use |
| Backend logs print a raw API key or secret | STOP — rotate credentials |
| An unexpected POST route appears in the OpenAPI schema (`/execute_trade`, `/place_order`, `/submit_order`, `/live_trade`, `/broker_execute`) | STOP |
| `python scripts/validate_safety_config.py` returns FAIL | STOP |
| Any test or validator failure | STOP |
| Network error suggests a live (non-paper) endpoint was contacted | STOP |

When stopping: unset all env vars, kill the backend, verify `git status` is
clean, and document what triggered the stop before retrying.

---

## 10. Redaction Checklist

Apply before sharing any output, screenshot, or log:

- [ ] Redact all order IDs (including `redacted_order_id` — the prefix is
      safe but the hash suffix should still be omitted from shared docs)
- [ ] Redact all account IDs
- [ ] Redact all API keys and secret keys (from terminal output and history)
- [ ] Redact all request/response headers that may carry authorization tokens
- [ ] Redact terminal history if it contains credentials
      (`Clear-History` in PowerShell, or close and reopen the session)
- [ ] Verify no screenshot frame contains a visible credential, key, or secret
- [ ] Replace any sensitive value with `[REDACTED]` before pasting

---

## 11. Cleanup / After-Smoke Checklist

Complete every item after the smoke session, whether or not it succeeded:

- [ ] Unset all session env vars:
      ```powershell
      Remove-Item Env:\ALPACA_ENV
      Remove-Item Env:\ALPACA_PAPER_ORDER_SUBMIT_ENABLED
      Remove-Item Env:\ALPACA_PAPER_ORDER_SUBMIT_SANDBOX_ACK
      Remove-Item Env:\ALPACA_API_KEY
      Remove-Item Env:\ALPACA_SECRET_KEY
      ```
- [ ] Stop the backend process
- [ ] Verify `git status` shows no unexpected changes (`git status --short`)
- [ ] Verify `.env` was not created or modified (`git diff .env` should be
      empty; `.env` should not appear in `git status`)
- [ ] Verify no screenshot file in the repo contains credentials
- [ ] If a paper order was submitted and the user chooses to verify it: log
      into the Alpaca Paper dashboard manually, confirm order appears, and
      document the result using only redacted identifiers
- [ ] Write a brief post-smoke note (MANUAL-PAPER-SMOKE-RUN-001 result)
      that includes: date, outcome (`accepted`, `submitted_to_alpaca_paper`),
      `order_status` value, and any stop conditions triggered — no raw IDs,
      no credentials

---

## 12. Approval Wording for Actual Smoke

The smoke MUST NOT be performed until the operator provides **exactly this
wording** (or a statement that clearly contains this intent):

> "I explicitly approve one local Alpaca Paper manual smoke using my own
> chosen symbol, side, and quantity. I understand this submits a paper order
> only, not live."

This approval must be given in the current session, by the account owner,
immediately before the gated request is issued. It does not authorize any
live trading, any strategy-generated order, or any future paper order.

---

## 13. Recommended Next Task

**MANUAL-PAPER-SMOKE-RUN-001** — perform the actual manual paper smoke.

This task must be created and executed **only after**:

1. Explicit operator approval (Section 12 wording received)
2. This preflight checklist (Section 6) is fully checked
3. Safety validator returns PASS
4. Default-blocked confirmation received

Do not begin MANUAL-PAPER-SMOKE-RUN-001 without meeting all four conditions.

---

## Appendix: Files Reviewed for This Document

| File | Source branch |
|------|--------------|
| `docs/tasks/alpaca_paper_order_submit_sandbox_001.md` | main |
| `app/api/routes/alpaca_paper.py` | main |
| `app/schemas/alpaca_paper_order_submit_sandbox.py` | main |
| `app/services/alpaca_paper_order_submit_sandbox_service.py` | main |
| `tests/app/test_alpaca_paper_order_submit_sandbox.py` | main |

No source files were modified. Documentation only.
