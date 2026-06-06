# Mobile AI Screenshot Preview — Smoke Checklist (DEMO-MOBILE-AI-EVIDENCE-001)

**Type:** docs-only smoke checklist (TEMPLATE — fill in when executed)
**Covers:** MOBILE-AI-007B endpoint + MOBILE-AI-007C `/mobile` UI

Use this checklist to smoke-test and capture evidence for the analysis-only
screenshot preview. Paper/simulation only — never live trading.

---

## Preconditions

- [ ] Backend running (`/api` reachable) OR offline demo path being tested.
- [ ] Frontend running and `/mobile` reachable.
- [ ] Use synthetic / demo chart screenshots only — **no real broker account
      screenshots, no secrets, no account IDs** (per the image privacy policy).

## Viewports

- [ ] iPhone width (375px)
- [ ] iPad width

## Load + layout

- [ ] `/mobile` loads without console errors.
- [ ] "AI Screenshot Review" card renders after AI Chart Review.
- [ ] Cards stack cleanly; text is readable (no tiny text); chips have spacing.

## Safety copy visible

- [ ] "Analysis only. Not financial advice."
- [ ] "Paper plan only. No live orders."
- [ ] "Human review required."
- [ ] Card note: "The image is not stored."

## Happy path (valid upload)

- [ ] Pick a valid PNG → preview renders.
- [ ] Pick a valid JPEG → preview renders.
- [ ] Pick a valid WebP → preview renders.
- [ ] Preview shows instrument/timeframe, market bias, pattern, paper plan,
      "Max simulated risk … % · PAPER_ONLY", safety score.
- [ ] Safety chips show: "No live orders", "Human review required", "Not stored".

## Rejection cases

- [ ] SVG or PDF → error message (backend 415) shown, no preview.
- [ ] File > 5 MB → "too large" message (backend 413 / client guard).
- [ ] Empty file → error (400 / client guard).
- [ ] Mismatched type (PNG bytes labelled JPEG) → 415 (if testable).

## Offline / fallback

- [ ] With backend unavailable, the card shows "Analysis service unavailable —
      showing an offline demo preview." with a demo preview.

## Forbidden-surface confirmation (must all be ABSENT)

- [ ] No Buy / Sell / Execute / Place Order / Live Trade buttons.
- [ ] No "Connect Broker" control.
- [ ] No API key / provider key input field.
- [ ] No account ID / broker account fields.
- [ ] No wallet/private key inputs.

## Evidence to capture

- [ ] Screenshot: `/mobile` card idle state.
- [ ] Screenshot: valid-upload preview.
- [ ] Screenshot: a rejection message.
- [ ] Screenshot: offline demo state.
- [ ] Note the commit SHA / branch under test.

## Result (fill in)

- Date executed: ______
- Commit SHA: ______
- Device(s): ______
- Outcome: PASS / FAIL — notes: ______
