# Mobile AI Screenshot Preview — Demo Evidence (DEMO-MOBILE-AI-EVIDENCE-001)

**Type:** docs-only evidence pack
**Covers:** MOBILE-AI-007B (backend endpoint, #256) + MOBILE-AI-007C (frontend UI, #257)

This pack documents how to demo the analysis-only screenshot preview feature
and records the safety posture and validation. It is documentation only — no
runtime code, no deploy, no secrets.

---

## 1. Routes

**Frontend (PWA):**

- `/mobile` — MellyTrade Mobile command center. The **AI Screenshot Review**
  card appears after the AI Chart Review section.

**Backend (read/analysis API):**

- `POST /api/mobile/ai/screenshot/preview` — analysis-only screenshot preview.
  Accepts raw image bytes (`image/png`, `image/jpeg`, `image/webp`), max 5 MB.
  Returns a paper-only `ScreenshotAnalysisPreview`. The image is validated and
  discarded — never stored, never logged, never sent to an AI provider.

Local dev base URLs (typical):

- Frontend: `http://localhost:5173/mobile`
- Backend: `http://localhost:8000/api/...` (frontend uses `VITE_API_BASE_URL`,
  default `/api`).

---

## 2. Screenshot / smoke checklist

Capture on a 375px-wide mobile viewport and on iPad width. See the companion
checklist: `docs/demo/mobile_ai_screenshot_preview_checklist.md`.

- [ ] `/mobile` loads without errors.
- [ ] "AI Screenshot Review" card is visible.
- [ ] Safety copy visible: "Analysis only. Not financial advice.",
      "Paper plan only. No live orders.", "Human review required.".
- [ ] File picker accepts only PNG / JPEG / WebP.
- [ ] Valid image → paper-only preview (instrument, bias, pattern, paper plan,
      max simulated risk ≤ 1%, safety score) with chips "No live orders",
      "Human review required", "Not stored".
- [ ] No order controls (no Buy / Sell / Execute / Place Order / Live Trade).
- [ ] No broker controls / "Connect Broker".
- [ ] No AI provider key inputs.
- [ ] No account IDs shown.
- [ ] Backend rejection cases surface a readable message:
  - [ ] unsupported type (e.g. SVG/PDF) → 415
  - [ ] file > 5 MB → 413
  - [ ] empty file → 400
- [ ] Offline/demo state: with backend unavailable, a clearly-labelled offline
      demo preview is shown.
- [ ] Mobile layout is clean at 375px and on iPad.

---

## 3. Validation commands and results

Backend safety (run from repo root):

```
python scripts/validate_safety_config.py
# → OVERALL: PASS (5 passed, 0 failed, 1 note)

python -m pytest tests/app/test_mobile_ai_screenshot_endpoint.py \
  tests/app/test_openapi_forbidden_paths.py \
  tests/app/test_safety_invariants.py -q
# → all passed (endpoint contract + OpenAPI forbidden-paths + safety invariants)
```

Frontend build (from `frontend/`):

```
npm run build
# → success (tsc clean, Vite build)
```

OpenAPI forbidden-path scan: the path `mobile/ai/screenshot/preview` contains
no forbidden execution segments; `test_openapi_forbidden_paths.py` passes.

---

## 4. Safety posture confirmation

- autotrade = false · dry_run = true · read_only = true ·
  live_orders_blocked = true · max risk ≤ 1%.
- Analysis only. Not financial advice. Paper plan only. Human review required.
- No broker execution, no order placement, no buy/sell/order/execute controls.
- No wallet/private keys, no broker/account fields, no secrets.
- No AI provider keys in frontend; no AI provider call from the endpoint.
- No image storage, no image logging (image validated then discarded).
- Response flags are Literal-locked: `analysis_only`, `paper_only`,
  `live_orders_blocked`, `broker_execution=false`, `requires_human_review`,
  `stored=false`, `provider_used=false`.

---

## 5. Still future (not in this pack)

- MOBILE-AI-008 — backend-only AI provider integration (analysis-only
  responses; provider data-use + privacy review; no frontend provider keys).
- MOBILE-AI-009 — smart alerts (reminders only, never execution).
- MOBILE-AI-011 — Capacitor/Expo/native wrapper research.
- MOBILE-AI-012 — App Store / Google Play readiness checklist.
