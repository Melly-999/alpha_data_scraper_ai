# Broker-Sim Readiness Audit 001

SOURCE STATUS: Public-safe, read-only audit. No secrets, no credentials, no
account IDs. This document inventories existing surfaces and classifies
readiness for **simulated / paper** broker testing. It does not implement,
enable, or recommend any live broker execution.

## 1. Purpose

Determine whether MellyTrade is ready for simulated / paper broker testing —
i.e. showing broker, account, position and ticket information from **local /
demo / fallback data only**, with no secrets and no order execution. The audit
maps current backend, frontend, docs, and test coverage, classifies readiness,
and lays out a concrete task breakdown to reach safe simulated broker testing.

## 2. Baseline

- main / origin/main SHA: `f758a31c9430bd262205e14a010bb70d5753317a`
- Safety validator: `python scripts/validate_safety_config.py` → **OVERALL: PASS**
- Live safety endpoint (verified read-only GET): `/api/safety/status` →
  `dry_run=true, auto_trade=false, read_only=true, live_orders_blocked=true,
  max_risk_per_trade_pct=1.0`
- Audit date: 2026-06-14

## 3. Current milestone status

- M4 Repo hygiene / stale-PR arc — DONE
- M5 Render hosted backend — DONE
- M7 Mobile/PWA evidence — refreshed (PR #301)
- M8 / M8.5 Demo, portfolio & public launch readiness — DONE
- Open PR count: 0

## 4. Current safety posture

Enforced in config and validated by scripts and pytest; live-verified on the
hosted backend:

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

## 5. Backend / API inventory

**Read-only (GET) surface already available** (no secrets required):

- Broker: `/broker/health`, `/broker/account`; `/brokers`, `/brokers/{id}/status`, `/brokers/{id}/account`, `/brokers/{id}/positions`
- Alpaca Paper (demo): `/alpaca-paper/status`, `/alpaca-paper/account-preview`, `/alpaca-paper/market-clock`
- Paper: `/paper/...` sandbox and run-preview GET routes
- Account / risk / safety: `/account/overview`, `/risk/status`, `/risk/violations`, `/safety/status`
- Trading data: `/orders` (GET list, read-only), `/positions/open`, `/positions/history`
- Terminal: `/terminal/summary`, `/terminal/events`, `/terminal/trading-plan`

**Mutating routes present — audited, none execute live orders:**

| Route | Verb | Assessment |
|---|---|---|
| `/broker/dry-run-report` | POST | Builds a **dry-run** execution report (`dry_run=True` hardcoded); no broker call |
| `/paper/tickets/draft` | POST | Paper-only ticket **draft** for human review; docstring: "never calls any broker, network service, or database" |
| `/risk/config` | PUT | Updates in-memory risk config; not execution |
| `/risk/emergency-stop` | POST | Safety control (kill-switch), not execution |
| `/mobile-ai/...` | POST | Mobile AI screenshot upload; not execution |

**No live broker SDK** is imported in `app/` (only a guarded optional
`import MetaTrader5` in `app/core/dependencies.py`). The Alpaca/paper surfaces
are served by demo/preview services:
`app/services/alpaca_paper_demo.py` ("static demo data only. No network calls,
no credentials"), `alpaca_paper_order_preview_service.py`,
`paper_run_preview_service.py`, `paper_sandbox.py`, `paper_sandbox_history.py`.

## 6. Frontend / UI inventory

- Pages: `TerminalPage.tsx`, `PaperRunPreviewPage.tsx`, `MobileAppPage.tsx`.
- Components: `BrokerCard.tsx` (display only — e.g. a "Buying power" label),
  safety badges across surfaces.
- API clients: `lib/brokerApi.ts` explicitly documents that it "exposes no
  `placeOrder` / `submitOrder` / `cancelOrder` / `modifyOrder` / `executeTrade`
  / `enableAutotrade`". The only POST clients are `paperTicketApi.ts` (paper
  draft) and `screenshotPreviewApi.ts` (mobile AI).
- **No Buy / Sell / Execute / Place Order controls, no broker-credential UI, no
  connect-live UX.**

## 7. Docs / evidence inventory

- Broker design: [../BROKER_ADAPTER_PLAN.md](../BROKER_ADAPTER_PLAN.md), [../IBKR_PAPER_ADAPTER.md](../IBKR_PAPER_ADAPTER.md), [../architecture/BROKER_SUPPORT_MATRIX.md](../architecture/BROKER_SUPPORT_MATRIX.md), [../architecture/broker_abstraction_implementation_plan.md](../architecture/broker_abstraction_implementation_plan.md), [../roadmap/ibkr_read_only_phase_plan.md](../roadmap/ibkr_read_only_phase_plan.md)
- Paper-trading contracts: [../paper_trading/paper_sandbox_safety_contract.md](../paper_trading/paper_sandbox_safety_contract.md), [../paper_trading/pds_001_trade_ticket_contract.md](../paper_trading/pds_001_trade_ticket_contract.md), [../paper_trading/pds_002_ticket_draft_service.md](../paper_trading/pds_002_ticket_draft_service.md), [../paper_trading/pds_003_paper_ticket_draft_endpoint.md](../paper_trading/pds_003_paper_ticket_draft_endpoint.md), [../paper_trading/pds_004_ai_workspace_ticket_preview.md](../paper_trading/pds_004_ai_workspace_ticket_preview.md)
- Demo: [../demo/paper_sandbox_local_demo.md](../demo/paper_sandbox_local_demo.md), [../demo/paper_sandbox_readonly_smoke.md](../demo/paper_sandbox_readonly_smoke.md), [../demo/ibkr_paper_readonly_demo.md](../demo/ibkr_paper_readonly_demo.md), [../demo/terminal_v1_local_demo.md](../demo/terminal_v1_local_demo.md), [../demo/mobile_pwa_evidence_refresh_001.md](../demo/mobile_pwa_evidence_refresh_001.md)
- Tests: `tests/app/test_safety_invariants.py` (15 tests), `tests/app/test_safety_status.py` (10), `tests/app/test_validate_safety_config_script.py`, `tests/app/test_supabase_schema_safety.py`, `tests/test_claude_ai_safety.py`.

## 8. Readiness classification

**B — READY FOR INTERNAL SIMULATED BROKER PREVIEW.**

The repository can already safely show broker/account/position/ticket
information from local/demo/fallback data, with no secrets and no execution.
It clears classification A (read-only paper status) outright, and the demo
services + paper-ticket-draft flow place it at B. It is **not** C (the
foundation — schemas, services, routes, tests, contracts — already exists) and
**not** D (no secret exposure or live-execution surface: the only mutating
routes are dry-run/paper-draft/risk-config/emergency-stop, and the frontend
exposes no order controls).

## 9. Missing pieces (to fully exercise simulated broker testing)

1. A single consolidated **simulated-broker walkthrough** tying together
   `/brokers` status → `/alpaca-paper/account-preview` → `/positions` →
   `/paper/tickets/draft` as one demo narrative (pieces exist; the end-to-end
   story is scattered).
2. A **read-only end-to-end smoke** that drives the GET surface + a paper
   ticket *draft* (not execution) and records results as evidence.
3. Optional: a clearly-labelled **"Simulated / demo data"** banner on the
   broker/account preview surfaces so no viewer mistakes demo balances for real
   ones (verify current labelling; add only if a later approved task allows UI).

## 10. Task breakdown to broker-sim testing

### 10.1 Audit / docs
- **BROKER-SIM-WALKTHROUGH-DOC-001** — Goal: write one demo walkthrough doc tying the existing GET surface + paper-draft flow into a single narrative. Allowed: `docs/demo/`, `docs/paper_trading/`. Forbidden: any `app/`, `frontend/`, config, workflows. Safety: docs-only; cite endpoints, never credentials. Validation: `validate_safety_config.py` PASS, link check. **Required before testing: recommended, not blocking.**

### 10.2 Backend (read-only)
- **BROKER-SIM-READONLY-SMOKE-SCRIPT-001** — Goal: a GET-only smoke checklist/script that hits `/safety/status`, `/brokers`, `/alpaca-paper/account-preview`, `/positions/open`, `/orders` and records status + key fields. Allowed: `docs/` + (only if approved) a read-only `scripts/` helper that performs GET only. Forbidden: new routes, mutating verbs, broker SDKs, env/secrets. Safety: GET-only, no credentials. Validation: validator PASS; script makes no POST/PUT/PATCH/DELETE. **Required before testing: yes (evidence).**
- *(No new execution routes. The dry-run report and paper-ticket-draft endpoints already cover the safe mutating surface and must remain dry-run/paper-only.)*

### 10.3 Frontend (display-only)
- **BROKER-SIM-DEMO-LABEL-AUDIT-001** — Goal: confirm broker/account preview surfaces visibly label data as simulated/demo and show safety badges; document findings. Allowed: `docs/`; UI edits only in a separate explicitly-approved task. Forbidden: adding order controls, broker-credential UI. Safety: no Buy/Sell/Execute added. Validation: manual UI checklist. **Required before testing: recommended.**

### 10.4 Test / validation
- **BROKER-SIM-INVARIANT-TEST-REVIEW-001** — Goal: confirm `test_safety_invariants.py` / `test_safety_status.py` cover the simulated-broker surfaces (read-only, dry-run, no execution); document any gap as a follow-up. Allowed: `docs/`; test additions only in a separate approved task. Forbidden: weakening any safety assertion. Validation: `pytest -q` (read-only review). **Required before testing: yes.**

### 10.5 Evidence / smoke
- **BROKER-SIM-EVIDENCE-PACK-001** — Goal: capture GET-only smoke results (and optionally existing screenshots `brokers-readonly.png`, `terminal-home.png`) into an evidence doc. Allowed: `docs/demo/`. Forbidden: new binaries unless an approved screenshot task. Safety: docs-only. Validation: validator PASS, link check. **Required before a confident demo: yes.**

## 11. Demo navigation plan

- **First route:** `/terminal` — show the safety banner + terminal summary so the read-only / dry-run posture is obvious within seconds.
- **Second route:** `/brokers` (read-only broker status, safe-disconnected/demo) and `/terminal/paper-run-preview`.
- **What to show:** simulated account overview, open/closed positions (demo data), a paper **ticket draft** (human-review, never executed), and the visible `READ ONLY` / `DRY RUN` / `LIVE ORDERS BLOCKED` / `EXECUTION OFF` chips.
- **What not to show / claim:** no live balances, no real broker connection, no order placement, no "it trades", no profit/ROI/win-rate.

## 12. What not to build yet

- No live broker API connection or credential handling.
- No POST/PUT/PATCH/DELETE order routes; no `placeOrder` / `submitOrder` /
  `executeTrade` / `enableAutotrade`.
- No Buy / Sell / Order / Execute UI controls.
- No changes to safety or risk config.
- No real money, no live execution path of any kind.

## 13. What not to claim

- No live trading, broker execution, or autonomous order placement.
- No production trading readiness; no regulated financial product status.
- No real users / adoption.
- No profit, returns, ROI, win-rate, or passive income.
- No financial advice. Simulated/demo data must never be presented as real.

## 14. Recommended next task

**BROKER-SIM-READONLY-SMOKE-SCRIPT-001** (read-only GET smoke + evidence) is the
highest-value next step: it exercises the already-safe surface, produces demo
evidence, and requires no new execution surface. Pair it with
**BROKER-SIM-WALKTHROUGH-DOC-001** for the demo narrative. Net: roughly **1–2
required tasks** before basic simulated broker testing, and **2–3 tasks** before
a demo user can navigate confidently — all docs/read-only, no new execution.

---

*MellyTrade is a read-only, dry-run, paper-only portfolio project. It is not a
commercial platform, not a live trading system, and not financial advice.*
