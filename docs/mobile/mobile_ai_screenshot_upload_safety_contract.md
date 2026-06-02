# Mobile AI Screenshot Upload Safety Contract (MOBILE-AI-007A)

**Type:** docs-only safety/privacy contract (no runtime code, no endpoint)

This document defines the safety requirements that must be satisfied **before**
any screenshot upload analysis endpoint is implemented (MOBILE-AI-007B). It is
documentation only: no backend route, no frontend upload UI, no AI provider
integration, no image-processing dependency, and no storage are added here.

Standing posture (unchanged): `autotrade=false`, `dry_run=true`,
`read_only=true`, `live_orders_blocked=true`, max risk ≤ 1%, paper/simulation
only, human review required, analysis only — not financial advice.

---

## A. Purpose

- Define safety requirements before implementing screenshot upload.
- The future endpoint is **analysis-only**, not trading execution.
- Screenshots may contain sensitive information and must be handled carefully.

---

## B. Explicit scope for future MOBILE-AI-007B

The future endpoint **may only**:

- accept an image upload for chart analysis,
- validate file type,
- validate file size,
- return a structured analysis preview,
- return a paper-only plan preview,
- require human review,
- avoid storing images by default.

The future endpoint **must NOT**:

- place orders,
- execute trades,
- call broker APIs,
- expose broker account IDs,
- accept wallet/private keys,
- accept MT5/IBKR credentials,
- accept AI provider keys from the frontend,
- store images without an explicit, approved policy,
- claim financial advice,
- claim guaranteed profit.

---

## C. Required upload constraints for future implementation

Proposed constraints for MOBILE-AI-007B:

- **Allowed MIME types:** `image/png`, `image/jpeg`, `image/webp`.
- **Max file size:** conservative proposal — **5 MB**.
- Reject **SVG** by default (script/XML risk).
- Reject **PDF** by default.
- Reject **archives** (zip/tar/etc.) by default.
- Strip / ignore **EXIF** metadata where applicable.
- **Never trust the client filename.**
- Generate **server-side safe IDs** if storage is later approved.
- **Rate limit** the future endpoint.
- Require **authentication** later if the app becomes public.
- If OCR is ever added, **scan/redact sensitive text** before any further use.

---

## D. Privacy / safety warnings

Screenshots may include:

- account balances,
- broker names,
- user names,
- order IDs,
- account IDs,
- API keys accidentally visible,
- open positions,
- chat messages,
- personal data.

The future system must warn users:

> “Do not upload screenshots containing account numbers, API keys, passwords,
> broker credentials, or personal data.”

---

## E. Response constraints for future endpoint

The future analysis response must include (and lock):

- `analysis_only = true`
- `not_financial_advice = true`
- `paper_only = true`
- `live_orders_blocked = true`
- `broker_execution = false`
- `requires_human_review = true`
- `max_risk_per_trade_pct <= 1.0`
- **no** buy/sell/order/execute instruction wording.

These align with the existing `app/schemas/mobile_ai.py` Literal-locked
schemas (`ChartAnalysisResult`, `PaperGamePlan`, `RiskAssessment`).

---

## F. App copy examples

Safe copy for future UI:

- “Analysis only. Not financial advice.”
- “Paper plan only. No live orders.”
- “Human review required.”
- “Do not upload screenshots with account numbers or API keys.”
- “MellyTrade never places orders from uploaded screenshots.”

---

## G. Stop conditions

Future implementation (MOBILE-AI-007B) must **stop and escalate** if:

- provider keys would be needed in the frontend,
- image storage is required before a retention policy is approved,
- the endpoint would create a trading action,
- the endpoint would expose user account / broker data,
- the endpoint would add live execution,
- the endpoint would require package changes that are not approved.

See also: `docs/mobile/mobile_ai_image_privacy_retention_policy.md`.
