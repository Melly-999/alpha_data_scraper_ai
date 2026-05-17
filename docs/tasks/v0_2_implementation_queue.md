# MellyTrade v0.2 Implementation Queue

> Planning and tracking reference for v0.2 tasks after the Closed Beta Demo v0.1
> pre-release. Docs-only — does not change any runtime behaviour or safety posture.

---

## Status

v0.1-beta is released as a GitHub pre-release (Closed Beta Demo v0.1 — Candidate PASS).

v0.2 must remain read-only, dry-run, and advisory-only:

```text
autotrade      = false
dry_run        = true
read_only      = true
live_orders_blocked = true
max risk       <= 1%
```

---

## Primary v0.2 goals

1. More useful scanner/watchlist universes (SIG-UNIVERSE-001 — in progress)
2. Windows local launcher EXE plan (DESKTOP-001 — planned)
3. IBKR Paper read-only dashboard plan (IBKR-READ-002 — planned)
4. Better beta feedback loop
5. Hosted deployment plan (later — DEPLOY-001)

---

## Task queue

---

### SIG-UNIVERSE-001 — Scanner universe presets

**Goal:** Add deterministic read-only symbol universes for scanner/watchlist demos.

**Status:** In progress — `feature/sig-universe-presets-v1`

**Universes:**

- AI Mega Caps (US stocks)
- XTB CFDs / macro instruments
- Core FX / commodities / crypto
- Polish/EU optional watchlist
- Default demo (combined subset)

**Scope:**

- `app/services/signal_universe.py` — offline symbol universe definitions
- `tests/app/test_signal_universe.py` — full safety and correctness tests
- No route changes
- No frontend changes
- No broker calls
- No network calls

**Safety:**

- no trading instructions
- no orders
- no broker calls
- no network calls
- advisory labels only
- all outputs immutable tuples

---

### SIG-UNIVERSE-002 — Universe selector endpoint / frontend

**Goal:** Expose universe presets via a safe GET endpoint and add a read-only
universe selector to the scanner UI.

**Depends on:** SIG-UNIVERSE-001

**Scope:**

- `app/schemas/signal_scanner.py` — `SignalUniversePreset`, `SignalUniverseListResponse` Pydantic models
- `app/api/routes/signals.py` — `GET /signals/scanner/universes` (read-only), `universe` query param on preview
- `frontend/src/lib/scannerPreviewApi.ts` — `getScannerUniverses()`, updated `getScannerPreview({ symbols?, universe? })`
- `frontend/src/components/terminal/AIWorkspacePanel.tsx` — local universe state, `<select>` dropdown, local re-fetch
- `frontend/src/components/terminal/terminal.css` — universe selector row/select/loading styles
- `tests/app/test_signal_universe_endpoint.py` — 31 endpoint tests
- No POST/PUT/PATCH/DELETE routes
- No execution controls
- No broker calls

**Status:** In progress — `feature/sig-universe-selector-v1`

---

### DESKTOP-001 — Windows local launcher EXE plan

**Goal:** Plan a Windows `.exe` launcher for local MellyTrade demo usage.

**Scope:** Docs only in this queue. See `docs/tasks/desktop_launcher_exe_plan.md`.

**Status:** Planned

---

### IBKR-READ-002 — IBKR Paper read-only dashboard plan

**Goal:** Plan a safe IBKR Paper read-only positions/account dashboard.

**Scope:** Docs only in this queue. See `docs/tasks/ibkr_readonly_dashboard_plan.md`.

**Status:** Planned

---

### DEPLOY-001 — Hosted staging plan

**Goal:** Define safe hosted staging, auth model, smoke checklist, secrets policy,
and staging vs. production environment separation.

**Safety:**

- no public live trading
- no broker credentials in hosted app
- no execution routes
- auth before any public access

**Status:** Deferred — after beta feedback reviewed

---

## v0.2 non-goals

The following must NOT be introduced in v0.2:

- live trading
- broker execution
- order buttons (Buy / Sell / Execute / Place Order)
- production billing
- investment advice language
- guaranteed profit claims
- autotrade=true
- dry_run=false
- read_only=false

---

## v0.2 gates before hosted deployment

| Gate | Status |
|---|---|
| Auth model defined | Pending |
| Privacy/data handling documented | Pending |
| Hosted deployment smoke test | Pending |
| Security review (secrets, logs, data) | Pending |
| Beta tester feedback reviewed | Pending |
| Safety validator green on deployment target | Required |

---

## Related docs

- `docs/tasks/desktop_launcher_exe_plan.md` — DESKTOP-001 launcher plan
- `docs/tasks/ibkr_readonly_dashboard_plan.md` — IBKR-READ-002 dashboard plan
- `docs/release/closed_beta_demo_v0_1_next_steps.md` — v0.1 next steps
- `docs/product/closed_beta_readiness.md` — readiness gates
- `docs/beta/first_tester_feedback_plan.md` — feedback priorities

---

*MellyTrade v0.2 Implementation Queue — planning reference*
