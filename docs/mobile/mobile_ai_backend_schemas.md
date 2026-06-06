# Mobile AI Backend Schemas (MOBILE-AI-006)

**Type:** backend schema-only (no endpoints, no AI provider calls, no DB writes)

This note records the typed Pydantic schemas added for the Mobile AI
workstream. They define the data contract behind the frontend-only `/mobile`
mock surface (MOBILE-AI-003 chart review, MOBILE-AI-004 setup journal,
MOBILE-AI-005 FOMO guard + risk coach). They are **schemas only** — no routes,
no services, no persistence, no provider integration.

## Scope

Added files only:

- `app/schemas/mobile_ai.py` — typed schemas
- `tests/app/test_mobile_ai_schemas.py` — schema unit tests

## Schemas

| Schema | Purpose |
|---|---|
| `ChartAnalysisResult` | AI chart review output (analysis only) |
| `PaperGamePlan` | Paper/simulation game plan (cannot place an order) |
| `RiskAssessment` | Behavior/risk summary for a reviewed setup |
| `JournalEntry` | Saved setup journal entry (review/learning record) |
| `FomoGuardState` | FOMO guard behavior feedback (does not execute trades) |
| `WeeklyReview` | Weekly learning / coach summary |

Supporting enums: `MarketBias`, `RiskLevel`, `OutcomeStatus`.

## Safety design

- Every model uses `ConfigDict(extra="forbid")` — unknown fields are rejected.
- Safety flags are `Literal`-locked and cannot be weakened by callers:
  - `analysis_only = True`, `not_financial_advice = True`
  - `paper_only = True`, `live_orders_blocked = True`
  - `broker_execution = False`, `requires_human_review = True`
  - `FomoGuardState.executes_trades = False`
- Risk fields enforce `max_risk_per_trade_pct <= 1.0` (and `risk_pct <= 1.0`)
  via field validators.
- No model can represent a live order, broker routing, or execution intent.

## Safety constraints

- No API routes / endpoints added (OpenAPI surface unchanged).
- No AI provider calls or keys.
- No database / persistence writes.
- No `fetch`/network calls.
- No broker execution, no wallet/private keys.
- Analysis only. Not financial advice. Paper/simulation only. Human review
  required. No guaranteed profit.

## Next recommended task

The screenshot upload work was split into MOBILE-AI-007A (safety contract +
retention policy, merged) and MOBILE-AI-007B (the analysis-only upload
endpoint, merged in #256):

- MOBILE-AI-007A — Screenshot upload safety contract and image
  privacy/retention policy (docs-only).
- MOBILE-AI-007B — Screenshot upload analysis endpoint
  (`POST /api/mobile/ai/screenshot/preview`): analysis-only, paper-only,
  no image storage, no provider keys in frontend, no trading execution.

Next: MOBILE-AI-008 — backend-only AI provider integration (analysis-only
responses; prerequisite: provider data-use + privacy review; no frontend
provider keys).
