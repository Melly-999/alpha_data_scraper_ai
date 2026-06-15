# Alpaca Paper Read-Only Adapter 001

SOURCE STATUS: Public-safe. No secrets, no credentials, no account IDs. This
task adds a GET/read-only Alpaca Paper adapter foundation. It implements **no**
order placement, cancellation, or replacement, and no live broker execution.

> **Read-only only.** This is the foundation for later paper order *testing* —
> but this task does not submit, cancel, or replace any order, and never
> connects to a live broker.

## 1. Purpose

Add a safety-first **read-only** Alpaca Paper adapter so MellyTrade can later
read Alpaca **paper** account/positions data and expose a sanitized preview —
without order placement, without live execution, and without committing or
exposing credentials.

## 2. Scope

- New read-only adapter service + sanitized schema + one GET-only route + tests.
- No mutating routes, no order logic, no live endpoint, no secrets, no frontend
  changes.

## 3. Existing Alpaca surfaces reviewed

- Routes: `app/api/routes/alpaca_paper.py` — existing GET-only `/status`,
  `/account-preview`, `/market-clock`, `/watchlist-preview`, `/order-preview`
  (all demo/preview, no execution).
- Demo service: `app/services/alpaca_paper_demo.py` (static demo data; no
  network, no credentials, no SDK).
- Schemas: `app/schemas/alpaca_paper.py` (locked `Literal` safety flags,
  `extra="forbid"`), `app/schemas/alpaca_paper_order_preview.py`.
- Order preview service: `app/services/alpaca_paper_order_preview_service.py`
  (deterministic local preview; `submitted=false`).
- Legacy: `brokers/alpaca_adapter.py` — a live-order adapter (`place_order` /
  `submit_order`). **Left untouched and intentionally NOT wired into the app.**
- Tests: `tests/app/test_alpaca_paper_demo_endpoint.py`,
  `tests/app/test_alpaca_paper_order_preview_endpoint.py`,
  `tests/app/test_openapi_forbidden_paths.py`, `test_safety_invariants.py`,
  `test_safety_status.py`, `test_validate_safety_config_script.py`.

The existing demo schemas are locked (`Literal` + `extra="forbid"`), so rather
than mutate them, a dedicated read-only adapter + a new sanitized schema + a new
GET route were added.

## 4. Implementation summary

- **Adapter:** `app/services/alpaca_paper_readonly_adapter.py` —
  `AlpacaPaperReadOnlyAdapter`. Accepts an optional injected client
  (duck-typed `get_all_positions`) and an `env_reader` (defaults to
  `os.getenv`). Resolves a client only when explicitly enabled
  (`ALPACA_PAPER_READONLY_ENABLED=true`, `ALPACA_ENV=paper`, credentials
  present) **or** when a client is injected; otherwise returns a safe
  `degraded_demo` preview. The default client factory lazy-imports the Alpaca
  SDK with `paper=True` (paper endpoint only) and degrades on any failure.
- **Schema:** `app/schemas/alpaca_paper_readonly.py` —
  `AlpacaPaperPositionsPreview` (extends the existing `AlpacaPaperSafetyFlags`)
  and `AlpacaPaperReadOnlyPosition`. Adds `mode`, `connected`,
  `order_placement_enabled=False`, `paper_simulated=True`, `redacted=True`,
  `source`, `count`, `positions`, `last_updated`.
- **Route:** `GET /api/alpaca-paper/positions-preview` (added to the existing
  `alpaca_paper` router) → `readonly_adapter.get_positions_preview()`.
- **Fallback/degraded:** no credentials / not enabled / unsafe env / client
  error → `mode=degraded_demo`, `connected=false`, `source=fallback`, empty
  positions. Never raises.
- **Fake client support:** an injected client is treated as an explicit,
  trusted read-only client (used by tests; no env required, no network).

## 5. Read-only boundary

- GET-only; the only client method referenced is `get_all_positions`.
- No `place_order` / `submit_order` / `cancel_order` / `replace_order` / market
  or limit order construction anywhere in the new code.
- No POST/PUT/PATCH/DELETE routes added.
- No live broker endpoint (`paper=True` only).
- No credential UI, no connect-live flow.
- Safety flags always: `read_only=true`, `dry_run=true`,
  `live_orders_blocked=true`, `execution_enabled=false`,
  `order_placement_enabled=false`.

## 6. Sanitization and redaction

Each raw position is reduced to display-safe fields only: `symbol` (upper-cased),
`qty`, `market_value`, `unrealized_pl`, `side` (coerced to `long`/`short`/
`unknown`). The schema uses `extra="forbid"`, so broker-internal fields on the
raw objects (e.g. `account_id`, `asset_id`, `exchange`) are dropped and can
never appear. No `account_id` / `broker_order_id` / `execution_id` / `api_key` /
`secret` / `token` is ever represented. Credentials are read locally only to
check presence and to construct the paper client; they are never stored on the
adapter, logged, or returned.

## 7. Tests

`tests/app/test_alpaca_paper_readonly_adapter.py` (13 tests):

- default adapter (no env) → `degraded_demo`, `connected=false`, empty.
- injected client → sanitized positions (symbol upper-cased, side coerced).
- no forbidden fields leak even when raw objects carry `account_id`/`asset_id`.
- raising client → degrades safely.
- malformed positions (non-iterable; dict missing `symbol`) → degrade/skip.
- unsafe config (`ALPACA_ENV=live`) and disabled config → no client resolved.
- route: GET 200 + safety flags; no forbidden keys; POST/PUT/PATCH/DELETE → 405;
  OpenAPI shows GET-only.

No test requires real Alpaca credentials or performs real network calls.

## 8. Validation

- `python -m pytest tests/app/test_alpaca_paper_readonly_adapter.py
  tests/app/test_alpaca_paper_demo_endpoint.py
  tests/app/test_alpaca_paper_order_preview_endpoint.py` → **100 passed**
- `pytest tests/app/test_safety_invariants.py test_safety_status.py
  test_validate_safety_config_script.py` → **62 passed**
- `pytest tests/app/test_openapi_forbidden_paths.py` → **21 passed**
- `python scripts/validate_safety_config.py` → **OVERALL: PASS** (no forbidden
  execution segments across route files)
- `black` clean, `flake8` clean, `mypy` clean (new files), `git diff --check`
  clean.

## 9. Static scan

No secrets / token-shaped strings / DB URLs / API keys / broker credentials /
account IDs / emails / phones / Neon identifiers. No safety-flip values. No
`place_order` / `submit_order` / `execute_order` / `cancel_order` /
`replace_order` / `MarketOrderRequest` / `OrderSide` in the new code (the legacy
`brokers/alpaca_adapter.py` was not touched). Order/execution terms appear only
in denylist, prohibition docs/comments, and tests asserting their absence.

## 10. What remains out of scope

- Paper order submission.
- Paper order cancellation / replacement.
- Live broker connection.
- Live credentials / storing credentials.
- Live trading.
- Frontend Buy/Sell/Order/Execute UI.
- Profit / ROI / win-rate claims.

## 11. Safety confirmation

- no frontend Buy/Sell/Order/Execute UI ✅
- no live trading ✅
- no live credentials / no stored or printed credentials ✅
- no broker execution ✅
- no secrets ✅
- no profit/ROI/win-rate claims ✅
- no financial-advice claims ✅
- autotrade=false ✅
- dry_run=true ✅
- read_only=true ✅
- live_orders_blocked=true ✅
- max risk ≤ 1% (unchanged; safety config validator PASS) ✅

## 12. Recommended next step

- **ALPACA-PAPER-READONLY-ADAPTER-001-PUBLISH** — push + Draft PR.
- Later (separate, explicitly-approved): **ALPACA-PAPER-ORDER-DRAFT-001**
  (draft-only, still no submission). **ALPACA-PAPER-ORDER-SUBMIT-SANDBOX-001**
  only after explicit approval — it introduces a mutating surface and is out of
  scope here.

---

*MellyTrade is a read-only, dry-run, paper-only portfolio project. It is not a
commercial platform, not a live trading system, and not financial advice.*
