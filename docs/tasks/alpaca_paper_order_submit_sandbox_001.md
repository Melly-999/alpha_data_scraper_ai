# Alpaca Paper Order Submit Sandbox 001

SOURCE STATUS: Public-safe. No secrets, no credentials, no account IDs. This
task adds a **backend-only, multi-gated, paper-only** order submission sandbox.
It is blocked by default. It is **not** live trading, **not** frontend UX, and
**not** autotrading.

> **Paper sandbox only — blocked by default.** A real Alpaca **Paper** order is
> submitted only when every explicit gate is satisfied. Never a live endpoint,
> never a frontend trigger, never autotrade.

## 1. Purpose

Provide a tightly controlled backend route that can submit a single small order
to Alpaca **Paper** for local/manual sandbox testing — the next step after the
read-only adapter (#309) and the local order draft (#310) — without ever
enabling live trading or product trading UX.

## 2. Scope

New schema + isolated service (with its own paper-only client wrapper) + one
gated POST route + tests + narrow guardrail allowlist registration + this doc.
No frontend, scripts, workflows, package, env files, Docker, or cloud config.

## 3. Why this is risky

This is the only path in the codebase that can place a real (paper) order. A
mistake here could submit unintended orders or leak broker identifiers. It is
therefore: blocked by default; gated by multiple environment flags + an
acknowledgement string + present credentials + per-request confirmation;
validated against the existing draft risk rules; bounded by conservative size
caps; isolated from the legacy live adapter; and limited to a single,
non-retried attempt that returns only redacted identifiers.

## 4. Safety gates

A paper submission is attempted only when **all** of these hold:

- `ALPACA_ENV == "paper"`
- `ALPACA_PAPER_ORDER_SUBMIT_ENABLED == "true"`
- `ALPACA_PAPER_ORDER_SUBMIT_SANDBOX_ACK == "I_UNDERSTAND_THIS_SUBMITS_A_PAPER_ORDER"`
- Alpaca paper credentials present (`ALPACA_API_KEY` + `ALPACA_SECRET_KEY`, or `APCA_*`)
- request `confirm_paper_order == true`
- request `source == "manual_sandbox"`
- draft risk validation passes (side / order_type / time_in_force / exactly-one
  positive quantity|notional / geometry / `max_risk_pct <= 1.0`)
- sandbox size caps: `quantity <= 100`, `notional <= 5000`; order_type ∈
  {market, limit} (limit requires a positive `limit_price`)

If **any** gate fails: no Alpaca call, `accepted=false`,
`submitted_to_alpaca_paper=false`, safe `blocked_reason`, safety flags preserved.

`dry_run_preview_only=true` exercises all gates but never submits.

## 5. Implementation summary

- **Schema** `app/schemas/alpaca_paper_order_submit_sandbox.py` — request +
  response (`extra="forbid"`). Response locks `paper_only=true`,
  `live_trading=false`, `live_orders_blocked=true`, `dry_run=true`,
  `read_only_posture_preserved=true`, `execution_enabled=false`,
  `requires_human_review=true`; returns only `redacted_order_id` /
  `client_order_id` / `order_status`.
- **Service** `app/services/alpaca_paper_order_submit_sandbox_service.py` —
  `AlpacaPaperOrderSubmitSandboxService`. Reuses
  `build_alpaca_paper_order_draft` for risk validation, then sandbox caps, then
  confirmation gates, then env gates. Builds a paper-only client only after all
  gates pass; submits exactly once; redacts the order id. Injected client
  supported for tests.
- **Client factory / wrapper** — `_build_paper_order_client` lazy-imports the
  Alpaca SDK and builds `TradingClient(..., paper=True)` only (paper endpoint).
  `_AlpacaPaperOrderClient.submit_paper_order` lazy-imports the SDK request/enum
  types and calls `submit_order` once. The legacy live adapter
  (`brokers/alpaca_adapter.py`) is **not** imported.
- **Route** `POST /api/alpaca-paper/order-submit-sandbox` — calls the service;
  returns a safe blocked response (HTTP 200) on any gate/validation failure.
- **Redaction** — `redacted_order_id = "alpaca-paper-sub-" + sha256(raw)[:12]`;
  the raw broker order id, account id, and credentials are never represented.

## 6. Route

`POST /api/alpaca-paper/order-submit-sandbox` → `AlpacaPaperOrderSubmitSandboxResponse`.
The only mutating method added. Path is `order-submit-sandbox` (not
`submit-order` / `execute` / `place-order`) and clears the safety validator and
OpenAPI forbidden-segment checks.

## 7. Guardrail changes (narrow, additive)

- `test_safety_invariants.py` — added `("POST", "/api/alpaca-paper/order-submit-sandbox")`
  to `ADMIN_NON_GET_ALLOWLIST` with a justification comment.
- `test_paper_sandbox_guardrails.py` — added the path to
  `SAFE_ADMIN_NON_EXECUTION_PATHS` with a justification comment (paper-only,
  gated, no live endpoint).
- **No broad weakening:** additions are path-specific; no wildcard, no regex
  bypass, no denylist term removed, no protection deleted. A dedicated test
  asserts that `submit-order` / `place-order` / `execute` / `cancel-order` /
  `replace-order` paths are **not** exempted by either allowlist.

## 8. Tests

`tests/app/test_alpaca_paper_order_submit_sandbox.py` (36 tests): blocked by
default; blocked when any env gate / ACK / credential is missing; blocked on
`ALPACA_ENV=live`, `confirm_paper_order=false`, wrong `source`; all draft
validation + sandbox-cap failures blocked before submission; all gates + fake
client → `accepted`/`submitted` with the fake called **exactly once**; redacted
id returned and raw broker id / credentials never leaked; limit order passes
`limit_price`; `dry_run_preview_only` does not submit; raising client degrades
safely; no socket opened in blocked or fake paths; source uses `paper=True` and
no live endpoint URL; route POST blocked-by-default 200; GET/PUT/PATCH/DELETE →
405; OpenAPI POST-only and no live paths; allowlists do not exempt live paths.

## 9. Validation

- `pytest` new sandbox suite → **36 passed**; full `tests/app` → **2451 passed**.
- `python scripts/validate_safety_config.py` → **OVERALL: PASS**.
- `black`, `flake8`, `mypy` (new files) → clean; `git diff --check` → clean.

## 10. Static scan

No secrets / token-shaped strings / DB URLs / API keys / broker credentials /
account IDs / emails / phones / Neon identifiers. No safety-flip values. No
hard-coded live endpoint (`api.alpaca.markets` absent); `paper=True` only. SDK
import and `submit_order` appear **only** inside the gated client builder/wrapper
(reached after all gates pass). The raw order id is redacted before return; the
response carries no raw broker order id / account id / credential.

## 11. Manual smoke policy

A real Alpaca Paper submission is **NOT** run during CI or normal local
validation. An optional manual smoke requires all of: a local-only environment;
real **paper** credentials; `ALPACA_ENV=paper`;
`ALPACA_PAPER_ORDER_SUBMIT_ENABLED=true`;
`ALPACA_PAPER_ORDER_SUBMIT_SANDBOX_ACK=I_UNDERSTAND_THIS_SUBMITS_A_PAPER_ORDER`;
a manually chosen symbol/side/qty (no model-selected symbol); redacted output
(no raw order/account IDs); and a cleanup note (cancel/flatten the paper order in
the Alpaca paper dashboard afterward). **It must not be performed without
separate, explicit user approval.** This task did not perform a manual smoke.

## 12. What remains out of scope

- live broker / live endpoint / live credentials
- frontend trading UI (Buy/Sell/Order/Execute) and connect-live UX
- autotrade / scheduled / background / strategy-generated submission
- order cancellation / replacement
- bracket / OCO / multi-leg orders
- options / crypto / futures
- profit / ROI / win-rate claims; financial advice

## 13. Safety confirmation

- no live trading ✅ · no live endpoint ✅ · no live credentials ✅
- no frontend trading controls ✅ · no connect-live UI ✅
- no autotrade / background / scheduled submission ✅
- no cancellation / replacement / bracket / OCO ✅
- no secrets; no raw broker order id / account id / credential returned ✅
- no profit/ROI/win-rate or financial-advice claims ✅
- global safety posture unchanged: `autotrade=false`, `dry_run=true`,
  `read_only` posture preserved/visible, `live_orders_blocked=true`,
  `max risk <= 1%` (validator PASS). The only new capability is an
  explicitly-gated paper sandbox submission, blocked by default.

## 14. Recommended next step

- **ALPACA-PAPER-ORDER-SUBMIT-SANDBOX-001-PUBLISH** — push + Draft PR.
- Do **not** proceed to live broker activation. Any live path requires a
  separate, explicitly-approved effort with reconciliation, kill-switch, audit,
  and monitoring.

---

*MellyTrade is a read-only, dry-run, paper-only portfolio project. It is not a
commercial platform, not a live trading system, and not financial advice.*
