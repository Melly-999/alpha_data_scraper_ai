# MellyTrade Media Integration 001

> **Frontend-only integration.** No media generated in this run, no Higgsfield
> MCP connected, no credits spent, no external APIs called. No backend/
> runtime/broker/config/package/deployment files changed. No push, merge, or
> deploy.
> **Run:** `MELLYTRADE-MEDIA-INTEGRATION-001` · **Date:** 2026-07-05 · **Model:** Sonnet 5

## Outcome

**Integrated, with one deliberate scope reduction.** The 4 accepted Higgsfield
assets from `MELLYTRADE-MEDIA-GENERATION-001` are copied into the repo,
manifested, and wired into both public pages. The hero image now replaces the
CSS placeholder on both `/` and `/case-study`. After viewing the accepted C1
clip (`aios-assembly.mp4`) in its actual page context — full-bleed behind the
landing hero headline — the previously-flagged "rising trendline" caveat read
as a real risk rather than a minor imperfection: on a page for a company
literally named "MellyTrade," a smooth continuous line rising from
lower-left to upper-right is strong "line go up" trading shorthand, even
without any chart furniture. Both hero bands now use **the static hero image
only** (poster, no autoplay video); C1 is copied into the repo, manifested,
and documented as available for a future non-hero section, but is not
rendered anywhere in this run.

## Assets Integrated

| Asset | Repo path | Wired into |
|---|---|---|
| H0 hero image | `frontend/public/media/mellytrade/hero-command-core.png` | `/` and `/case-study` hero bands (as poster/static image) |
| Hero poster (copy of H0) | `frontend/public/media/mellytrade/hero-command-core-poster.png` | `/` and `/case-study` hero bands |
| C1 — AIOS Assembly | `frontend/public/media/mellytrade/aios-assembly.mp4` | Copied + manifested only. **Not rendered** — see Outcome. |
| C2 — Risk Layer Activation | `frontend/public/media/mellytrade/risk-layer-activation.mp4` | Copied + manifested only, per the design pack's "available media" allowance. Not rendered anywhere yet. |
| C3 — Product Showcase Finale | `frontend/public/media/mellytrade/product-showcase-finale.mp4` | Copied + manifested only. Not rendered anywhere yet. |

No rejected or `review_crops` assets were copied into the repo.

## Asset Paths

Live paths (served by Vite from `frontend/public/`):

```
/media/mellytrade/hero-command-core.png
/media/mellytrade/hero-command-core-poster.png
/media/mellytrade/aios-assembly.mp4
/media/mellytrade/risk-layer-activation.mp4
/media/mellytrade/product-showcase-finale.mp4
/media/mellytrade/manifest.json
```

Exposed in code via `frontend/src/fixtures/mediaAssets.ts` →
`MELLYTRADE_PUBLIC_MEDIA` (replaces the prior `FUTURE_MEDIA_ASSETS`
placeholder constant, which pointed at `.webp`/`.webm` filenames that were
never generated — the accepted assets are `.png`/`.mp4`).

Checksums (MD5) were verified identical between the local export folder and
the copied repo files for all 4 accepted assets before proceeding.

## Manifest

`frontend/public/media/mellytrade/manifest.json` documents, per asset: role,
source prompt, model/settings, dimensions/duration, credits spent, safety
sweep result and notes, and the rising-trendline caveat. It also records a
high-level (path-free) summary of the 4 rejected/failed takes for
traceability, and the overall credit budget (110 → 61.64, 48.36 spent). No
secrets, account info, or rejected asset file paths are included.

## Routes Verified

| Route | Result |
|---|---|
| `/` | Hero renders `hero-command-core-poster.png` as a static `<img>` (not `<video>`) at both desktop and mobile widths. No console errors. |
| `/case-study` | Hero band renders the same poster image inside `.public-case-hero`. No console errors. |
| `/terminal` | Unchanged, renders `.terminal-root` normally. No console errors. |

## Visual Safety Review

- Grepped all changed frontend files (`PublicLandingPage.tsx`,
  `CaseStudyPage.tsx`, `mediaAssets.ts`) and the new `manifest.json` for
  buy/sell/execute/order/place-trade/PnL/account/broker-logo/API-key/secret
  — every match is descriptive safety copy or a manifest safety note
  confirming an *absence* of that content; no interactive control or
  exposed secret exists.
- Confirmed via network panel: zero `/api/*` requests and zero 404s on
  either public page; the poster image and (when wired) video both resolved
  with `200`/`206` responses.
- Re-reviewed the hero image and C1 clip specifically for: price-chart
  resemblance, casino red/green cues, and any forbidden control. The hero
  image and C1 both remain free of literal chart furniture (no axis, no
  gridlines, no price labels, no candles) and contain no red/green casino
  styling anywhere — consistently amber/cyan/black. The C3 accepted take
  (2nd take) was re-confirmed to contain no chart panel of any kind, unlike
  its rejected 1st take.
- Decision recorded above: despite passing the literal absolute-exclusion
  checklist, C1's rising-line motif was judged too close to a "line go up"
  finance visual for full-bleed hero autoplay use on this specific brand
  and was withheld from the hero in this run.

## Responsive / Reduced Motion Review

- Desktop (1280×900) and mobile (375×812): no horizontal overflow on either
  `/` or `/case-study` after the poster image was wired in.
- Because both hero bands now render a static `<img>` (no `videoSrc` is
  passed anywhere in this run), `CinematicHeroMedia`'s existing mobile
  (`max-width: 768px`) and `prefers-reduced-motion: reduce` autoplay guards
  are currently not exercised in production — they remain in place,
  type-checked, and ready for the moment a future run passes a `videoSrc`
  into either page (e.g. if C2 or C3 is later approved for a non-hero
  section with autoplay).

## Validation Commands

```powershell
git diff --check     # clean
npx tsc -b            # clean
npm run build           # clean; confirmed frontend/public/media/mellytrade/*
                         # copied through to dist/media/mellytrade/* including
                         # manifest.json
```

Not run: Playwright e2e suite (no test file targets the public routes) and
the Python safety validator (no backend/Python files touched in this run).

## Known Caveats

- The hero image and the (unrendered) C1 clip both carry the flowing
  amber/cyan line with a rising-trendline visual quality. It is judged safe
  as a static hero image (calmer, easier to read as an abstract "signal"
  motif when not moving), but was withheld as an autoplaying hero video.
- Video files remain MP4-only (no WebM). `CinematicHeroMedia`'s `<video>`
  element still wires a single `<source type="video/mp4">` — unchanged,
  since no video is currently rendered in production anyway.
- C2 and C3 are present in the repo and manifested but not linked from any
  page yet. A future run could add a lower, non-hero, non-autoplay preview
  section for one or both, per the design pack's "Cinematic Motion Plan."

## Retake Notes, If Any

No retake is being requested in this run (media generation is out of scope
here). For a future `MELLYTRADE-MEDIA-GENERATION-001`-style run that wants a
hero-safe version of C1, notes for the prompt author (using the "Ultimate
Prompting Guide" principles — one core idea, explicit start/motion/end,
one visual style, continuous motion, no conflicting moods):

- **Core idea:** the AIOS interface assembling from particles into the
  hero's still frame — keep this singular idea; do not also ask for a
  "flowing signal line" as a co-equal visual element.
- **Start:** a field of scattered amber/cyan particles in the dark void,
  no line, no monogram.
- **Motion path:** particles converge and coalesce directly into panels and
  the MT monogram — a single continuous convergence, not a line-plus-particle
  combination.
- **End frame:** the accepted hero still (badges + monogram), unchanged.
- **Explicit exclusion to add next time:** "no continuous rising or falling
  line of any kind, no trend line, no waveform" — stronger and more specific
  than this run's "no line chart, no price chart," which still allowed a
  smooth ambient line to pass the literal safety sweep.

## Next Recommended Run

`MELLYTRADE-PUBLIC-SHOWCASE-FINAL-QA-001`

## Safety Confirmation

```text
Safety confirmation:
- No broker execution or live trading enabled.
- No Buy/Sell/Execute/Order controls added.
- No secrets printed or exposed.
- No backend/runtime/broker/config/package/deployment files changed.
- No package or lock files changed.
- No external APIs called.
- No Higgsfield MCP/media generation performed.
- No rejected media assets integrated.
- No push, merge, deploy, reset, clean, delete, or force operation performed.
```
