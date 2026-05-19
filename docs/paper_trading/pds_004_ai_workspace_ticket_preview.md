# PDS-004 — AI Workspace Paper Ticket Preview

## Purpose

Adds a read-only, advisory-only UI panel inside the **AI Workspace** area of
the MellyTrade Terminal that lets an analyst validate a paper-only trade ticket
draft directly from the browser.  The panel POSTs to the PDS-003 endpoint
(`POST /api/paper/tickets/draft`) and displays the validation result — with no
order placement, no broker execution, and no live trading of any kind.

---

## What PDS-004 is NOT

| Capability | Status |
|---|---|
| Live order placement | **NEVER** |
| Broker execution (MT5 / IBKR) | **NEVER** |
| Autotrade enablement | **NEVER** |
| `dry_run=false` path | **NEVER** |
| `live_orders_blocked=false` | **NEVER** |
| Paper fill / paper position creation | Not yet — planned for PAPER-001+ |

---

## Files added / modified

| File | Change |
|---|---|
| `frontend/src/lib/paperTicketApi.ts` | New — typed POST client for `/api/paper/tickets/draft` |
| `frontend/src/components/terminal/PaperTicketPreviewPanel.tsx` | New — advisory-only preview panel |
| `frontend/src/components/terminal/AIWorkspacePanel.tsx` | Modified — imports and renders `PaperTicketPreviewPanel` |
| `frontend/src/components/terminal/index.ts` | Modified — exports `PaperTicketPreviewPanel` |
| `frontend/src/components/terminal/terminal.css` | Modified — PDS-004 panel styles (advisory, no execution semantics) |
| `docs/paper_trading/pds_004_ai_workspace_ticket_preview.md` | New — this document |

---

## API client (`paperTicketApi.ts`)

Wraps `POST /api/paper/tickets/draft` with:

- Typed input (`PaperTicketInput`) mirroring `TradeTicketDraftInput`
- Typed result (`PaperTicketDraftResult`) mirroring `TradeTicketDraftResult`
- Explicit `PaperTicketSafetyContract` type with literal `true`/`false` fields
- 15-second abort timeout
- Graceful error handling — returns `{ ok: false, error }` on network/timeout/server errors
- `createFallbackSafetyContract()` — always returns the locked safety contract for display
- Never calls broker adapters, MT5, IBKR, or any live execution surface

---

## Panel component (`PaperTicketPreviewPanel.tsx`)

Located in: `frontend/src/components/terminal/PaperTicketPreviewPanel.tsx`

- Mounted inside `AIWorkspacePanel` after the Scanner Preview section
- Pre-populated with a default EURUSD long setup for quick validation preview
- Form fields: symbol, side, entry type, timeframe, entry price, stop loss,
  take profit 1, risk %, confidence, reason
- Submit button label: **"Validate draft"** — never "Place Order", "Execute Trade",
  or any order-placement language
- On submit: calls `createPaperTicketDraft()`, shows spinner during request
- On success: displays accepted/rejected verdict, rejection reasons, warnings,
  draft summary (if accepted), and the full safety contract
- Safety badges always visible: `PAPER ONLY`, `DRY RUN`, `HUMAN REVIEW`, `NO EXECUTION`
- No `apiPost`/`apiPut`/`apiDelete`/`apiPatch` helpers — only `paperTicketApi.ts`

---

## Safety invariants

Every safety field is enforced server-side by the PDS-003 endpoint and the
PDS-002 `TradeTicketDraftService`.  The UI simply displays them.

| Invariant | Value | Enforced by |
|---|---|---|
| `paper_only` | `true` | `Literal[True]` schema, backend service |
| `dry_run` | `true` | `Literal[True]` schema, backend service |
| `read_only` | `true` | `Literal[True]` schema, backend service |
| `live_orders_blocked` | `true` | `Literal[True]` schema, backend service |
| `requires_human_review` | `true` | `Literal[True]` schema, backend service |
| `risk_allowed` | `false` | `Literal[False]` schema, backend service |
| `broker_execution_allowed` | `false` | `Literal[False]` schema, backend service |
| `max_risk_pct` | `<= 1.0` | Schema `le=1.0`, validator runtime check |
| `execution_mode` | `"paper_only_draft"` | Backend constant |

---

## Frontend static safety check

`tests/app/test_safety_invariants.py` scans `TERMINAL_V1_FRONTEND_GLOBS` for
mutating API helpers.  `PaperTicketPreviewPanel.tsx` is **not** in that list
(it is correctly excluded as it uses a POST helper for the paper sandbox, not
the read-only terminal surface).  `AIWorkspacePanel.tsx` is also not in the
scanned list.

`paperTicketApi.ts` does NOT export any symbol named `apiPost`, `apiPut`,
`apiDelete`, or `apiPatch` — it exports only `createPaperTicketDraft` and
type/utility helpers.

---

## Roadmap relation

| ID | Title | Status |
|---|---|---|
| **PDS-001** | Paper-only TradeTicket schema & validator | ✅ Merged |
| **PDS-002** | Ticket Draft Service | ✅ Merged |
| **PAPER-GUARD-001** | Guardrail tests + safety contract | ✅ Merged |
| **PDS-003** | Draft endpoint (`POST /api/paper/tickets/draft`) | ✅ Merged |
| **PDS-004** | AI Workspace ticket preview | ✅ This PR |
| **PAPER-001** | In-memory paper broker sandbox | ⬜ Planned |
| **PAPER-002** | PaperOrder / PaperFill / PaperPosition schemas | ⬜ Planned |
| **PAPER-003** | Paper-only execute endpoint behind human approval | ⬜ Planned |
| **PAPER-004** | Paper portfolio state and sandbox reset | ⬜ Planned |
| **SUPA-003** | Audit writer service | ⬜ Planned |
