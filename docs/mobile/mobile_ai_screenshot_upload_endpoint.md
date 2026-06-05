# Mobile AI Screenshot Upload Endpoint (MOBILE-AI-007B)

**Type:** backend endpoint (analysis-only, paper-only) — high safety review

Implements the future endpoint defined by the MOBILE-AI-007A safety contract
(`docs/mobile/mobile_ai_screenshot_upload_safety_contract.md`) and image
privacy/retention policy (`docs/mobile/mobile_ai_image_privacy_retention_policy.md`).

## Endpoint

`POST /api/mobile/ai/screenshot/preview`

- **Request:** raw image bytes in the request body (no multipart — avoids a
  `python-multipart` dependency). `Content-Type` must be `image/png`,
  `image/jpeg`, or `image/webp`. Max **5 MB**.
- **Response:** `ScreenshotAnalysisPreview` (HTTP 200) — a deterministic,
  analysis-only preview wrapping `ChartAnalysisResult`, `PaperGamePlan`, and
  `RiskAssessment`, with Literal-locked flags `analysis_only=true`,
  `paper_only=true`, `live_orders_blocked=true`, `broker_execution=false`,
  `requires_human_review=true`, `stored=false`, `provider_used=false`.
- **Errors:** `400` empty body / bad Content-Length, `413` over 5 MB,
  `415` disallowed MIME or magic-signature mismatch.

## Validation

- MIME allowlist + **magic-signature** check (PNG / JPEG / WebP), pure stdlib —
  no Pillow / python-magic.
- SVG, PDF, and archive signatures are rejected.
- Body is size-capped while streaming, so an oversized upload is rejected
  without being fully buffered.
- Client filename is never read or trusted.

## Files

- `app/api/routes/mobile_ai.py` — route (raw-body read + cap)
- `app/services/screenshot_analysis.py` — validation + deterministic preview
- `app/schemas/mobile_ai.py` — adds `ScreenshotAnalysisPreview` (additive)
- `app/main.py` — registers the router under `/api`
- `tests/app/test_mobile_ai_screenshot_endpoint.py` — contract + safety tests
- `tests/app/test_safety_invariants.py` — adds the route to the admin
  non-GET allowlist with justification

## Safety

- No image storage / persistence; bytes are validated then discarded.
- No image logging, no training use.
- No AI provider call, no network call, no database write.
- No broker execution, no order placement, no buy/sell/order/execute controls.
- No live trading. Analysis only — not financial advice. Paper plan only.
  Human review required. Max simulated risk ≤ 1%.

## Next recommended task

MOBILE-AI-008 — AI provider integration (backend-only keys, analysis-only
responses; prerequisite: provider data-use + privacy review).
