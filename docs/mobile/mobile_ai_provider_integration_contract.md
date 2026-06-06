# Mobile AI Provider Integration Contract (MOBILE-AI-008A)

**Type:** docs-only contract (no runtime code, no provider calls, no keys)

This document defines the contract for backend-only AI provider integration
behind the existing analysis-only screenshot endpoint
(`POST /api/mobile/ai/screenshot/preview`, MOBILE-AI-007B). It is the
prerequisite for MOBILE-AI-008B (provider service, mock default) and
MOBILE-AI-008C (optional real provider behind an env flag).

It extends — and must not weaken — the MOBILE-AI-007A safety contract and the
image privacy/retention policy.

Standing posture (unchanged): `autotrade=false`, `dry_run=true`,
`read_only=true`, `live_orders_blocked=true`, max risk ≤ 1%, paper/simulation
only, human review required, analysis only — not financial advice.

---

## A. Goals and non-goals

**Goal:** allow the screenshot preview to be produced by a pluggable analysis
**provider**, while keeping the response analysis-only / paper-only and the
default behavior fully offline and deterministic.

**Non-goals (forbidden in this track):**

- No AI provider keys in the frontend — ever.
- No image storage / persistence; no image bytes in logs.
- No broker execution, order placement, or buy/sell/order/execute controls.
- No live trading; no wallet/private keys; no account IDs in responses.
- No new runtime dependency without explicit approval (see Section F).

---

## B. Provider abstraction

A single backend interface selects the analysis implementation:

```
analyze(image_bytes, mime) -> ScreenshotAnalysisPreview
```

Implementations:

| Provider | Network? | New dependency? | Role |
|---|---|---|---|
| `mock` | No | No | **Default.** Deterministic preview (current 007B output). |
| `stub` | No | No | Internal fallback used on disable / missing key / error. |
| `claude` | Yes (backend) | **No** — `anthropic` is already a dependency | Optional, 008C only, behind env flag. |
| `openai` | Yes (backend) | **Yes** (`openai` not present) | **Deferred** — needs explicit dependency approval. |

The returned object is always the existing Literal-locked
`ScreenshotAnalysisPreview` (`app/schemas/mobile_ai.py`). Providers cannot add
fields or weaken safety flags.

## C. Backend-only configuration

Backend env vars (server-side only; never read in `frontend/`):

- `MOBILE_AI_PROVIDER` — `mock` (default) | `claude`.
- `MOBILE_AI_PROVIDER_ENABLED` — `false` (default) | `true`.
- Claude path reuses the existing `ANTHROPIC_API_KEY` (already used by the
  legacy `claude_ai.py`); no new key name is introduced.

**Degraded fallback (must hold):** if the provider is disabled, the key is
missing, or the provider raises any error/timeout, the service returns the
deterministic `stub`/`mock` preview with `provider_used=false`. No 500 leak,
no key/provider error surfaced to the client.

## D. Endpoint integration

- Reuse the existing route `POST /api/mobile/ai/screenshot/preview` — no new
  route, so the OpenAPI surface is unchanged.
- Validation (MIME allowlist, 5 MB cap, magic-signature) stays in front of the
  provider call, exactly as in 007B.
- Response stays `ScreenshotAnalysisPreview`: `analysis_only=true`,
  `paper_only=true`, `live_orders_blocked=true`, `broker_execution=false`,
  `requires_human_review=true`, `stored=false`, `max_risk_per_trade_pct ≤ 1.0`.
  `provider_used` is `true` only when a real provider actually produced the
  result; `mock`/`stub`/fallback keep it `false`.

## E. Privacy alignment (007A retention policy)

- Image processed in memory only; never persisted; never logged.
- If a real provider is enabled (008C), it is **backend-only**; document
  explicitly that images are sent to that provider and review its data-use
  policy first (per `mobile_ai_image_privacy_retention_policy.md` §C).
- Redact/strip metadata before any provider send; never send an image believed
  to contain secrets or account IDs.

## F. PR slicing

- **008A** (this doc) — contract, docs-only.
- **008B** — `app/services/mobile_ai_provider.py` (abstraction + `mock` +
  `stub`), endpoint delegates to it, **mock default**, tests. No real calls, no
  key required, no dependency change.
- **008C** — optional `claude` implementation behind `MOBILE_AI_PROVIDER_ENABLED`,
  mocked in tests; explicit "images sent to provider" privacy note.

## G. Stop conditions

Stop and escalate if any of the following becomes necessary:

- a provider key would be exposed in the frontend,
- image storage is required,
- a package/dependency change is needed without approval (e.g. adding `openai`),
- any execution / broker / order path is introduced,
- live-trading wording appears,
- account IDs or secrets would be handled or returned.

## Next

MOBILE-AI-008B — backend AI provider service (mock default), then optionally
MOBILE-AI-008C (real Claude provider behind an env flag).
