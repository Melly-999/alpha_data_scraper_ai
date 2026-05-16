# MERGE #100 — MellyTrade Read-Only AI Operations Layer (Architecture)

This document describes the **observability + AI operations** layer that
ships with MERGE #100. It captures the flow of data from external sources
through FastAPI, Supabase, and the React frontend, and explicitly enumerates
the safety barriers at every layer.

> **Hard contract.** Nothing in this milestone changes the existing
> read-only posture. The architecture below is *additive observability*,
> not new execution capability.
>
> `autotrade=false`, `dry_run=true`, `read_only=true`,
> `live_orders_blocked=true`, `max_risk_per_trade ≤ 1%`.

---

## 0. Component map

```
                      ┌──────────────────────────────┐
                      │   External signal generation │
                      │   (MT5 fetcher, Claude AI,   │
                      │   NewsAPI, scanner heuristics)│
                      └──────────────┬───────────────┘
                                     │  in-process, no broker calls
                                     ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │                       FastAPI backend (GET-only)                │
   │                                                                 │
   │   /api/signals/scanner/preview   ─ advisory scanner             │
   │   /api/signals                   ─ list                         │
   │   /api/signals/{id}              ─ detail                       │
   │   /api/signals/{id}/reasoning    ─ reasoning                    │
   │   /api/signals/decisions         ─ dry-run decision history     │
   │   /api/signals/lifecycle         ─ lifecycle view (steps)       │
   │   /api/audit/events              ─ audit feed                   │
   │   /api/risk/config               ─ risk policy (read)           │
   │   /api/local-checklist           ─ safety checklist              │
   │                                                                 │
   │   Every route registered above is GET. No POST/PUT/PATCH/DELETE. │
   └──────────────┬────────────────────────────┬──────────────────────┘
                  │ service_role (server-side)│  
                  ▼                            ▼
   ┌────────────────────────┐    ┌─────────────────────────────┐
   │  Supabase observability│    │  In-memory seed fixtures    │
   │  - signal_decisions    │    │  - _SEED_DECISIONS          │
   │  - audit_events        │    │  - prototype_activity_feed  │
   │  RLS deny-all default  │    │  - audit event builders     │
   └────────────────────────┘    └─────────────────────────────┘
                  │                            │
                  └──────────────┬─────────────┘
                                 ▼
              ┌──────────────────────────────────────┐
              │   React + Vite frontend (poll-only)  │
              │   usePollingResource → apiGet (GET)  │
              │   useStaleDetector (display-only)    │
              └──────────────────────────────────────┘
```

---

## 1. Backend flow

For each user-facing read:

```
HTTP GET → FastAPI route → service layer → reader/seed → response
                                  │
                                  └── audit/persist (fire-and-forget,
                                      cannot block the response)
```

Key invariants enforced in `app/services/`:

- **Safety re-enforcement** in `signal_decision_reader._row_to_record()` —
  the DB cannot return a record with `dry_run=false`, `auto_trade=true`,
  `read_only=false`, or `max_risk_per_trade > 0.01`. These values are
  forced server-side regardless of stored data.
- **Graceful degradation** — every service that talks to Supabase wraps the
  call in `try/except` and falls back to in-memory seed fixtures. The
  client never sees an error or a missing response.
- **Persistence is fire-and-forget** — even the scanner-preview audit
  insert is wrapped so that an audit-table failure cannot block the read.

---

## 2. Scanner flow (advisory only)

```
GET /api/signals/scanner/preview?symbols=...
    │
    ├── scan_symbols(symbols)         ─ pure-Python scoring, no IO
    │
    ├── For each result:
    │     write_signal_decision(record)  ─ fire-and-forget; decision=watch_only
    │
    └── emit_scanner_preview_event()     ─ fire-and-forget audit row
```

The scanner **never** produces a record with `decision=dry_run_allowed` —
its hardcoded output is `decision=watch_only`, `risk_status=blocked`,
`order_placed=False`.

---

## 3. Supabase observability flow

```
Frontend  →  FastAPI  →  service_role  →  Supabase RLS  →  table
   ▲           │
   │           └── (NEVER) direct browser-side Supabase reads
   │
   └── decisions / audit rows arrive *only* through FastAPI
```

RLS posture (`supabase/migrations/20260516_signal_decisions_rls.sql`):
- `signal_decisions`: `ENABLE ROW LEVEL SECURITY`
- No public/anon SELECT policy
- service_role bypasses RLS by Supabase design
- All other roles are denied by default

The frontend has zero knowledge of Supabase. The Supabase client lives
only in `app/services/supabase_client.py` and is wrapped in
`get_safe_supabase_client()` which returns `None` if the env vars are
missing — degrading every consumer to the seed fixture path.

---

## 4. Frontend polling flow

```
React component
    │
    └── usePollingResource(loader, intervalMs)
            │
            ├── apiGet<T>('/...')              ─ pure GET, no auth tokens
            ├── lastUpdatedAt (Date | null)    ─ feeds useStaleDetector
            ├── data | loading | error         ─ standard hook surface
            └── re-polls every intervalMs       ─ no WebSocket, no SSE
```

Display-only freshness:
```
useStaleDetector(lastUpdatedAt) → "initializing" | "fresh" | "stale"
                                              │
                                              └── 90s threshold
                                                  15s re-check
                                                  pure computation
```

No data-fetching hook in this milestone writes to localStorage,
sessionStorage, IndexedDB, cookies, or any browser persistence
mechanism. The session is genuinely stateless across page reloads.

---

## 5. Reasoning layer (DATA-002)

```
GET /api/signals/{id}                ─ SignalDetail (reasoning string)
GET /api/signals/{id}/reasoning      ─ SignalReasoning (factors + gates)
        │
        ▼
SignalReasoningPanel (React, frontend/src/components/signals/)
    │
    ├── "Why this signal?"   — narrative + technical_factors
    ├── Confidence breakdown — value, band, vs 70% threshold
    ├── "Why blocked?"       — only when detail.blocked
    ├── Risk gates triggered — failed expanded, passed collapsed
    ├── "Human review required" — explicit non-autonomy framing
    ├── Optional Claude validation block
    │
    └── Safety badges: DRY RUN ONLY · READ ONLY · HUMAN REVIEW REQUIRED · RISK BLOCKED
```

The panel has exactly one interactive control: a collapse/expand toggle.
That toggle calls `setExpanded` — pure React state, no network, no DOM
mutation outside the panel itself.

---

## 6. Safety barriers (defense in depth)

Listed in order from outermost to innermost:

1. **No execution routes registered.** `validate_safety_config.py` scans
   every route file for forbidden segments (`execute`, `live-trade`).
2. **No mutating HTTP verbs on signal surfaces.** OpenAPI tests
   (`tests/app/test_openapi_forbidden_paths.py`) assert this.
3. **Pydantic response models default to safety values.**
   `SignalDecisionRecord.dry_run=True`, `.auto_trade=False`,
   `.read_only=True` cannot be overridden by stored data.
4. **Reader-level safety re-enforcement.** Even if a DB row had
   `dry_run=False`, `_row_to_record()` overrides it.
5. **RLS deny-all on `signal_decisions`.** Without service_role, no read
   succeeds.
6. **Frontend cannot construct an order.** No `TradingPlanItem` field
   ever contained quantity/lot/sl/tp/order_id. The reasoning panel
   has no order-shaped affordances.
7. **CI gates.** `validate_local.ps1` runs the full safety battery
   (config, openapi, invariants, unit tests, frontend build).

Any single layer above failing would still leave the others intact. The
combined posture is **safe by construction**.

---

## 7. Feature ladder for this milestone

| Item | Layer | Sub-task |
|---|---|---|
| `from_date`/`to_date` filters | backend reader + service + route | SUPA-014 |
| Date range UI (chips + pickers) | frontend hook + page + CSS | SUPA-015 |
| Realistic seed (15 records) | backend `_SEED_DECISIONS` | DATA-001 |
| Operational audit events | `audit_event_service.build_operational_events()` | DATA-001 |
| Activity feed realism | `fixture_data.prototype_activity_feed()` | DATA-001 |
| AI reasoning panel | `SignalReasoningPanel.tsx` | DATA-002 |
| Demo runbook + screenshot plan | `docs/demo/*.md` | DEMO-001 |
| This architecture doc | `docs/architecture/milestone_100_*.md` | DEMO-001 |
