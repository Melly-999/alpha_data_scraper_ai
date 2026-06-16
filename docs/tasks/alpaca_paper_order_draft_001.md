# Alpaca Paper Order Draft 001

SOURCE STATUS: Public-safe. No secrets, no credentials, no account IDs. This
task adds a **local-only** Alpaca paper order *draft* surface. It does **not**
submit orders to Alpaca, does not call any broker, and does not execute.

> **Draft only — not submitted to Alpaca.** The endpoint validates user input
> and returns a structured draft for human review. No Alpaca call, no order
> submission, no execution, no network.

## 1. Purpose

Provide a safe, local-only paper order draft surface that validates a proposed
trade and returns a structured draft — the next step after the read-only adapter
(PR #309) toward eventual paper order *testing*, while still submitting nothing.

## 2. Scope

Backend schema + service + one POST (local-draft) route + tests + an allowlist
registration + this task doc. No frontend, scripts, workflows, package, env, or
Docker changes.

## 3. Files changed

- `app/schemas/alpaca_paper_order_draft.py` (new) — request/draft/response models.
- `app/services/alpaca_paper_order_draft_service.py` (new) — validation + draft
  builder.
- `app/api/routes/alpaca_paper.py` (modified) — new
  `POST /api/alpaca-paper/order-draft`.
- `tests/app/test_alpaca_paper_order_draft.py` (new) — 21 tests.
- `tests/app/test_safety_invariants.py` (modified) — register the new safe
  non-GET route in `ADMIN_NON_GET_ALLOWLIST` with justification.
- `docs/tasks/alpaca_paper_order_draft_001.md` (new).

## 4. Route added

`POST /api/alpaca-paper/order-draft` → `AlpacaPaperOrderDraftResponse`.

The POST verb only means it accepts a request body; **no external broker state
is mutated**. The path is named `order-draft` (not `execute`/`submit-order`) and
clears the safety validator and OpenAPI forbidden-segment checks. It is
registered in the `test_safety_invariants.py` admin allowlist alongside the
existing `/api/paper/tickets/draft` precedent.

## 5. Behaviour / validation

Validates and, on any failure, returns `valid=false` with `draft=null` and a
descriptive `reason` (HTTP 200 — a blocked draft is not an error):

- `side` ∈ {BUY, SELL}
- `order_type` ∈ {market, limit, stop, stop_limit}
- `time_in_force` ∈ {day, gtc, ioc, fok, opg, cls}
- exactly one positive `quantity` **or** `notional`
- `entry_price`, `stop_loss`, `take_profit` required and positive
- `max_risk_pct` in `(0, 1.0]` (per-trade risk cap)
- geometry: BUY `stop_loss < entry_price < take_profit`; SELL inverse

On success: returns `valid=true` with a draft carrying a local, deterministic
`paper-draft-*` id (not a broker order id) and `status="draft"`.

## 6. Safety flags (always present)

`draft_only=true`, `order_submission_enabled=false`, `execution_enabled=false`,
`live_orders_blocked=true`, `dry_run=true`, `read_only=true`,
`requires_human_review=true`, `paper_only=true`. Message:
`"Draft only — not submitted to Alpaca."`

## 7. Sanitization / forbidden fields

Response models use `extra="forbid"`. No `account_id` / `broker_account_id` /
`broker_order_id` / `execution_id` / `api_key` / `secret` / `token` is ever
represented. The service reads no environment variables and stores nothing.

## 8. Read-only / no-broker boundary

The service imports no Alpaca SDK, makes no network/socket calls, and references
no `submit_order` / `place_order` / `cancel_order` / `replace_order` /
`TradingClient` / `MarketOrderRequest` / `OrderSide`. A test opens a socket trap
to prove no network access during a build, and a source-scan test asserts the
absence of SDK/submission references.

## 9. Tests

`tests/app/test_alpaca_paper_order_draft.py` (21 tests): valid BUY/SELL draft;
notional accepted; invalid side / order_type / time_in_force blocked; both /
neither / non-positive quantity-notional blocked; missing stop-loss / take-profit
blocked; bad geometry blocked; `max_risk_pct > 1%` blocked; `draft_only`,
`order_submission_enabled=false`, `execution_enabled=false` and all safety flags
asserted; no forbidden fields; service makes no network call; service source has
no Alpaca/submission references; route POST 200 (valid + blocked); route no
forbidden keys; GET → 405; OpenAPI advertises POST-only and a draft-named path.

## 10. Validation

- `pytest` (order-draft + safety-invariants + openapi-forbidden-paths + demo +
  readonly-adapter + safety-status) → **137 passed**
- `python scripts/validate_safety_config.py` → **OVERALL: PASS**
- `black`, `flake8`, `mypy` (new files) → clean
- `git diff --check` → clean

## 11. Static scan

No secrets / token-shaped strings / DB URLs / API keys / broker credentials /
account IDs / emails / phones / Neon identifiers. No safety-flip values. No
Alpaca SDK import and no mutating-order calls in the new code (matches exist only
in prohibition comments, the denylist, and tests asserting absence).

## 12. What remains out of scope

- Paper order submission (sending the draft to Alpaca).
- Paper order cancellation / replacement.
- Live broker connection / live credentials.
- Live trading / execution.
- Frontend Buy/Sell/Order/Execute controls.
- Profit / ROI / win-rate claims.

## 13. Safety confirmation

- this endpoint does **not** submit orders to Alpaca ✅
- no Alpaca order endpoint called / no Alpaca SDK import ✅
- no order submission / cancellation / replacement / execution ✅
- no live broker / no live endpoint ✅
- no credentials / no secrets / no env changes ✅
- no frontend trading controls ✅
- no profit/ROI/win-rate claims; no financial advice ✅
- autotrade=false · dry_run=true · read_only=true · live_orders_blocked=true ·
  max risk ≤ 1% (validator PASS) ✅

## 14. Recommended next step

- **ALPACA-PAPER-ORDER-DRAFT-001-PUBLISH** — push + Draft PR.
- **ALPACA-PAPER-ORDER-SUBMIT-SANDBOX-001** introduces a mutating submission
  surface and must **not** proceed without explicit, separate approval.

---

*MellyTrade is a read-only, dry-run, paper-only portfolio project. It is not a
commercial platform, not a live trading system, and not financial advice.*
