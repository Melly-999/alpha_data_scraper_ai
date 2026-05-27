# DEMO-MASCOT-001 — Melly Pet Workspace Companion Evidence

## Status

Documentation and screenshot-capture checklist.
Text-only. No binary assets committed.

## Feature Source

| Field | Value |
|---|---|
| Task ID | UI-MASCOT-001 |
| PR | #224 |
| Branch merged | `feature/ui-mascot-001-ai-pet-workspace` |
| Merge SHA | `b7868ed` |
| Component | `frontend/src/components/branding/MellyPetMascot.tsx` |
| Placement | AI Workspace right rail — after Today's Action Queue |
| Section header | Workspace Companion / branding |
| CSS | `frontend/src/components/terminal/terminal.css` (mascot block, lines 2756+) |

## What Melly Pet Is

Melly Pet is a lightweight inline-SVG brand mascot that appears in the AI Workspace right rail.
It is a pure presentational React component:

- no hooks, no state, no API calls, no side effects
- inline SVG only — no external image files, no binary assets
- no trading controls, no order buttons, no broker execution UX
- no new npm dependencies
- original MellyTrade styling — no third-party brand assets

Its purpose is visual branding and safety-posture storytelling during demos.

## Required Capture Set

- [ ] `/workspace` full-page desktop screenshot (default viewport)
- [ ] AI Workspace right rail close-up — Melly Pet card visible
- [ ] Melly Pet card close-up — name, subtitle, copy, and all four chips legible
- [ ] Amber idle-glow animation frame (if screen recording is available)
- [ ] Responsive / narrow viewport screenshot (≤ 900px) — figure shrinks to 60px

## Expected Visible Copy

| Element | Expected text |
|---|---|
| Micro-label | `DEMO COMPANION` |
| Name | `Melly Pet` |
| Subtitle | `Your read-only AI workspace companion.` |
| Description | `Guides the demo, explains safety posture, and keeps the workspace focused on paper-only previews.` |
| Chip 1 | `READ ONLY` |
| Chip 2 | `DRY RUN` |
| Chip 3 | `LIVE ORDERS BLOCKED` |
| Chip 4 | `EXECUTION OFF` |

## Accessibility Checks

- [ ] Card has `aria-label="Melly Pet — MellyTrade AI workspace companion"`
- [ ] SVG figure has `aria-hidden="true"` and `focusable="false"`
- [ ] Safety chips region has `aria-label="Active safety constraints"`
- [ ] Section has `aria-label="Melly Pet — workspace companion"`
- [ ] Text contrast is readable against dark terminal surface (`#10141a`)
- [ ] No horizontal overflow at any tested viewport
- [ ] Reduced-motion: animations absent when `prefers-reduced-motion: reduce` is active

## Safety Checks

- [ ] No order buttons visible
- [ ] No Buy / Sell / Execute / Place Order controls
- [ ] No live trading UX elements
- [ ] No broker execution UX elements
- [ ] No account, credential, or balance data shown
- [ ] Safety chips all render: READ ONLY · DRY RUN · LIVE ORDERS BLOCKED · EXECUTION OFF

## Browser Smoke Evidence (DOM-verified, 2026-05-27)

Performed against `alpha-frontend` server (port 5173), route `/workspace`.

| Check | Result |
|---|---|
| `path` | `/workspace` |
| `mainLabel` | `Terminal view: workspace` |
| `mellyPresent` | `true` |
| `.melly-pet-name` | `Melly Pet` |
| `.melly-pet-micro` | `DEMO COMPANION` |
| `.melly-pet-subtitle` | `Your read-only AI workspace companion.` |
| `.melly-pet-copy` | `Guides the demo, explains safety posture…` |
| `.melly-pet-chip` count | 4 |
| chips | `READ ONLY`, `DRY RUN`, `LIVE ORDERS BLOCKED`, `EXECUTION OFF` |
| `.melly-pet-figure` (SVG) | present |
| `aria-label` on card | `Melly Pet — MellyTrade AI workspace companion` |
| `aria-label` on section | `Melly Pet — workspace companion` |
| `aria-label` on chips region | `Active safety constraints` |
| no horizontal overflow | `true` |

## Artifact Policy

Screenshots must be saved **outside the repository**. Do not commit PNG, JPG, WebP, MP4, or Playwright trace files.

Recommended local path for captures:

```text
C:\AI\MellyTrade_Workspace\screenshots\demo-mascot-001-melly-pet\
```

Recommended filename pattern:

```text
demo_mascot_001_01_workspace_fullpage.png
demo_mascot_001_02_right_rail_closeup.png
demo_mascot_001_03_melly_pet_card_closeup.png
demo_mascot_001_04_chips_legible.png
demo_mascot_001_05_narrow_viewport.png
```

## Safety Note

This document does not claim:

- live trading capability
- broker execution capability
- real-money order placement
- guaranteed trading profit
- investment or financial advice

Melly Pet is a demo companion. It reinforces the read-only, dry-run, paper-only posture.
It does not add trading features, execution routes, or broker connectivity.

## Related Docs

- [iPad PWA Paper Run Preview Showcase](../showcase/ipad_pwa_paper_run_preview.md)
- [DEMO-009 iPad PWA screenshot checklist](demo_009_ipad_pwa_screenshot_checklist.md)
- [DEMO-009 iPad PWA smoke evidence](demo_009_ipad_pwa_smoke_evidence.md)
- [Recruiter screenshot checklist](recruiter_screenshot_checklist.md)
