# MellyTrade Pre-Media Snapshot 001

> **Docs-only snapshot.** No media generated, no Higgsfield/MCP connected, no
> credits spent, no external APIs called. No backend/runtime/broker/config/
> package/deployment files changed. No push, merge, or deploy.
> **Run:** `MELLYTRADE-PRE-MEDIA-SNAPSHOT-001` · **Date:** 2026-07-05 · **Model:** Sonnet 5

## Outcome

**Ready, with 4 small wiring gaps to close in the media-integration run.**
The landing/case-study layout itself is stable (clean build, no console
errors, no overflow, zero live API calls, confirmed in prior QA). The gaps
below are about the *media plumbing* — where assets plug in — not the layout:
`HeroAIOSShowcase` doesn't yet pass any path into `CinematicHeroMedia`,
`CaseStudyPage` has no media slot at all yet, `.public-hero__media` is
missing `object-fit`/sizing rules needed once a real `<img>`/`<video>`
replaces the placeholder `<div>`, and there is no mobile/reduced-motion
autoplay guard on the future `<video>`. None of these block generating the
assets — they only need to be wired up when the assets land.

## Branch / Commit Reviewed

- Branch: `feature/public-landing-case-study-001`
- Latest local commit: `99bde92` (fix(frontend): QA fixes for public
  landing/case-study a11y and touch targets)
- Previous commit: `da74565` (feat(frontend): add public landing and
  case-study routes)
- Upstream: none configured (`no upstream configured for branch
  'feature/public-landing-case-study-001'`) — not pushed
- Working tree: clean for everything under `frontend/` and the design/QA
  docs touched by this branch; only pre-existing, unrelated untracked files
  remain elsewhere in the repo (not part of this branch's scope)

## Layout Readiness

- `npx tsc -b` — clean
- `npm run build` — clean (`dist/index.html`, one CSS bundle, one JS bundle)
- `git diff --check` — clean
- Live preview: `/` and `/case-study` render with zero console errors and
  zero `/api/*` network calls (re-confirmed in this run)
- No horizontal overflow at 1280×900 (desktop) or 375×812 (mobile)
- **Conclusion: layout is stable enough to receive media.** The remaining
  work is prop/CSS wiring, not structural risk.

## Media Slots Reviewed

**`frontend/src/components/public/CinematicHeroMedia.tsx`** — accepts
optional `posterSrc` / `videoSrc` props:
- `videoSrc` set → renders `<video muted loop playsInline autoPlay poster={posterSrc}>` with a single `<source type="video/mp4">`
- no `videoSrc`, `posterSrc` set → renders `<img src={posterSrc} alt="" aria-hidden>`
- neither set (today's state) → renders a static CSS gradient `<div>`

**`frontend/src/components/public/HeroAIOSShowcase.tsx`** — calls
`<CinematicHeroMedia />` with **no props today**. This is gap #1: even once
assets exist, this call site needs `posterSrc="/media/mellytrade/hero-command-core.webp"` (etc.) added — a one-line change, not a redesign.

**`frontend/src/pages/CaseStudyPage.tsx`** — gap #2: does **not** import or
render `CinematicHeroMedia` at all. `.public-case-hero` (line 49) is
text-only today. The design pack calls for the case-study page to "share the
hero image (cropped band)" — this will need a small addition (either reuse
`CinematicHeroMedia` in a shorter fixed-height band, or a plain `<img>`)
before the case-study page gets its hero visual.

**`frontend/src/pages/public-site.css`** — `.public-hero__media` (line 184):
```css
.public-hero__media {
  position: absolute;
  inset: 0;
  z-index: 0;
}
```
Gap #3: no `width`, `height`, or `object-fit` declared. This is harmless for
today's `<div>` placeholder (which has no intrinsic size), but a real
`<img>`/`<video>` defaults to `object-fit: fill`, which will **stretch and
distort** the asset to match the box instead of cropping it proportionally.
Required addition before real assets land:
```css
.public-hero__media {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}
```

Gap #4: the existing global rule
```css
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
}
```
does not stop a `<video autoPlay>` element from playing (autoplay is not a
CSS animation/transition). The design pack's accessibility notes and mobile
rules both require "no autoplay video on mobile" and implicitly no forced
motion under reduced-motion. Today, `CinematicHeroMedia` has no
`matchMedia('(prefers-reduced-motion: reduce)')` check and no viewport check
— when `videoSrc` is wired in, this component needs a small addition (JS
`matchMedia` check, or a `<picture>`-style conditional render) to fall back
to the poster image on mobile and under reduced-motion.

Measured hero container box (via live preview, `getBoundingClientRect`):

| Viewport | Hero box (w × h) | Aspect ratio |
|---|---|---|
| Desktop 1280×900 | 1265 × 774 | ≈1.63:1 (close to 16:9, driven by `min-height: 86vh`) |
| Mobile 375×812 | 375 × 572 | ≈0.66:1 (portrait — `min-height: auto` collapses to content height) |

This confirms the design pack's own instruction is correct and sufficient:
one landscape hero image/clip with `object-fit: cover` can serve every
breakpoint — but the crop on mobile will be aggressive (portrait window
cropping a landscape frame), so the hero composition should keep its focal
point (MT monogram) dead-center with no critical detail near the left/right
edges.

## Recommended Asset Paths

Recommend **`frontend/public/media/mellytrade/`** (matches the task's own
example paths, and matches the existing repo convention already used for
`frontend/public/brand/mellypet/*.png` — a category folder plus a
subject-named subdirectory). Confirmed this path is **not** excluded by any
`.gitignore` rule (checked root `.gitignore` for `media`, `webm`, `webp`,
`mp4`, `public` patterns — no matches; unlike `frontend/src/data/`, which a
prior run discovered *was* silently ignored by a root `data/` rule).

```
frontend/public/media/mellytrade/hero-command-core.webp        (H0 poster / fallback image)
frontend/public/media/mellytrade/hero-command-core-poster.webp (explicit poster frame, if distinct from H0 — likely identical to H0 per the pack's "Clip 1's poster = the hero image itself" rule; keep both names for clarity even if same file)
frontend/public/media/mellytrade/aios-assembly.webm            (C1, VP9/WebM primary)
frontend/public/media/mellytrade/aios-assembly.mp4             (C1, H.264 fallback — CinematicHeroMedia currently only wires one <source type="video/mp4">, see Issues)
frontend/public/media/mellytrade/risk-layer-activation.webm    (C2)
frontend/public/media/mellytrade/risk-layer-activation.mp4     (C2 fallback)
frontend/public/media/mellytrade/product-showcase-finale.webm  (C3)
frontend/public/media/mellytrade/product-showcase-finale.mp4   (C3 fallback)
frontend/public/media/mellytrade/manifest.json                 (per the design pack's own "post-generation steps": file/section/poster mapping)
```

Vite serves everything under `frontend/public/` at the site root, so these
resolve at runtime as `/media/mellytrade/<file>` — that is the exact string
to pass into `posterSrc`/`videoSrc` props.

## Recommended Media Specs

| Asset | Spec |
|---|---|
| Hero image (H0) | 16:9, ≥2400×1350 (allows retina desktop crop + safe mobile center-crop), WebP primary (JPEG fallback optional), target < 500 KB |
| Clips (C1–C3) | 1080p, 16:9, ~8s, no audio, WebM (VP9) primary + MP4 (H.264) fallback, target < 4–6 MB each per the design pack's own compression budget |
| Poster frames | Same 16:9 crop as the hero image; Clip 1's poster = the H0 hero image itself (per design pack) |
| `object-fit` | `cover`, `object-position: center` — needed in CSS (see gap #3) so one asset serves desktop/tablet/mobile without a separate crop file |
| Mobile | No autoplay video (design pack rule) — poster/static image only below ~768px; needs the reduced-motion/viewport guard described in gap #4 |
| Format fallback | `CinematicHeroMedia` currently renders a single `<source type="video/mp4">` — if a WebM is generated as primary, either add a second `<source type="video/webm">` before the MP4 `<source>`, or generate MP4 only, to avoid a silent no-op `<video>` tag in browsers that don't get a matching source |

## Higgsfield Prompt Readiness

Confirmed present in `docs/design/mellytrade_website_design_pack_001.md`:

- ✅ Prompt H0 — Hero image (line 351)
- ✅ Prompt C1 — "AIOS Assembly" (line 365)
- ✅ Prompt C2 — "Risk Layer Activation" (line 375)
- ✅ Prompt C3 — "Product Showcase Finale" (line 385)
- ✅ Budget rule (line 348): "2–3 takes on the hero image and Clip 1 only;
  first acceptable take for Clips 2–3", std mode/1080p/16:9/~8s/no audio,
  max 1 hero image + 3 clips
- ✅ Post-generation steps (line 394): compress for web, export poster
  frames, deliver to `frontend/public/media/` with a manifest, verify no
  excluded content before the files enter the repo

**Nothing is missing.** The design pack is fully ready to hand to a
Higgsfield generation run as-is; no prompt text needs to be added or
amended.

## Frame-Level Safety Checklist

To be checked on every generated frame **before it enters the repo**
(per the design pack's own H0 prompt exclusions and this run's brief):

**Must NOT appear in any generated frame:**
- [ ] Buy button / Sell button / Execute button / Order button / "place a trade" affordance
- [ ] Prices or price numbers
- [ ] Candlestick charts
- [ ] PnL figures or percentage-gain figures
- [ ] Account numbers or account IDs
- [ ] Order IDs
- [ ] Broker logos (real or implied)
- [ ] API keys, tokens, or any secret-shaped string
- [ ] Red/green casino-style trading cues or neon-casino glow
- [ ] Guaranteed-return or "live account" claims (text or implied UI state)
- [ ] Human faces (per the H0 prompt's own exclusion list)

**May appear (per design pack + this run's brief):**
- Abstract/stylized terminal UI panels
- READ ONLY / PAPER SANDBOX / LIVE ORDERS BLOCKED badges
- Paper/simulated/demo labels
- Audit-rail visual motif
- GitHub-evidence card motif
- MT pixel monogram (glowing amber, steady — not pulsing)
- Amber primary / cyan secondary signal lines (cyan budgeted, per the pack's
  "≤3 uses per page" rule — applies to on-site chrome, not literally to a
  single generated frame, but keep cyan secondary/minor in any frame too)

This checklist should be applied as a manual visual review pass on the
hero image and all three clips (and their poster frames) immediately after
generation, before any file is copied into `frontend/public/media/`.

## Mobile / Responsive Notes

- Hero container becomes content-height (not viewport-height) below 768px
  (`min-height: auto`), producing a portrait-oriented box (measured
  375×572, aspect ≈0.66:1) versus a landscape box on desktop (measured
  1265×774, aspect ≈1.63:1).
- A single landscape hero asset with `object-fit: cover` (once added) can
  serve all breakpoints — no separate mobile-crop file is required — but the
  composition should keep the MT monogram/focal point centered with no
  critical detail near the left/right thirds, since mobile will center-crop
  a narrow vertical slice.
- Design pack's own mobile rule ("static image on small viewports, no
  autoplay video") is not yet enforced in code — see gap #4. This must be
  implemented in the same run that wires in real video, not deferred
  further.

## Validation Commands

```powershell
git diff --check     # clean
npx tsc -b            # clean
npm run build          # clean
```

Also re-confirmed live in preview: `/` and `/case-study` render with 0
console errors and 0 `/api/*` network requests; no horizontal overflow at
1280×900 or 375×812.

Not run (out of scope for this docs-only snapshot): Playwright e2e suite,
Python safety validator — no frontend behavior or backend files changed in
this run to warrant re-running them.

## Issues / Blockers

No blockers to generating the media itself. Four small **wiring** gaps to
close in the integration step of the next run (all one-line-to-small CSS/JSX
changes, not redesigns):

1. `HeroAIOSShowcase.tsx` — `<CinematicHeroMedia />` call needs
   `posterSrc`/`videoSrc` props added once asset paths exist.
2. `CaseStudyPage.tsx` — no hero media slot exists yet; the design pack
   calls for a cropped hero band here too.
3. `.public-hero__media` (public-site.css) — needs `width: 100%; height:
   100%; object-fit: cover; object-position: center;` added before a real
   `<img>`/`<video>` replaces the placeholder `<div>`.
4. `CinematicHeroMedia.tsx` — no mobile/`prefers-reduced-motion` guard on
   the future `<video autoPlay>`; needs a viewport/matchMedia check to fall
   back to the poster image, per the design pack's own mobile rule.

None of these require backend, package, or config changes — all are
contained to the three files already touched by the public-site work.

## Next Recommended Run

`MELLYTRADE-MEDIA-GENERATION-001` — generate the H0 hero image and the C1–C3
clips per the existing, complete prompt plan in
`docs/design/mellytrade_website_design_pack_001.md`, deliver to
`frontend/public/media/mellytrade/` with a manifest, run the frame-level
safety checklist above on every asset before it enters the repo, then wire
the four gaps listed above in the same or an immediately following run.

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
- No push, merge, deploy, reset, clean, delete, or force operation performed.
```

## Addendum: Wiring Completed (MELLYTRADE-MEDIA-WIRING-PREP-001)

All four gaps listed above are now closed, with default (no-props) behavior
unchanged and zero media 404s introduced:

1. **`HeroAIOSShowcase.tsx`** now accepts optional `posterSrc`/`videoSrc`
   props and forwards them to `CinematicHeroMedia`. `PublicLandingPage.tsx`
   still calls it with no props, so the CSS placeholder keeps rendering
   until real paths are passed in a future run.
2. **`CaseStudyPage.tsx`** now accepts optional `heroPosterSrc`/
   `heroVideoSrc` props and renders `<CinematicHeroMedia>` inside
   `.public-case-hero`, sharing the same media primitive as the landing
   hero (cropped band, per the design pack). Hero text content was wrapped
   in a new `.public-case-hero__content` element so it layers above the
   media.
3. **`.public-hero__media`** (in `public-site.css`, reused by both hero
   bands) now sets `width: 100%; height: 100%; object-fit: cover;
   object-position: center;` in addition to the existing `position:
   absolute; inset: 0;` — a real `<img>`/`<video>` will now crop correctly
   instead of stretching.
4. **`CinematicHeroMedia.tsx`** now uses a small `useMatchMedia` hook (no
   new dependency) to check `(max-width: 768px)` and
   `(prefers-reduced-motion: reduce)`. An autoplaying `<video>` is only
   rendered when a `videoSrc` is provided **and** neither condition is
   true; otherwise it falls back to the poster image, or the static
   placeholder if no poster is provided either.

Also added `frontend/src/fixtures/mediaAssets.ts`, documenting the exact
future asset paths under `frontend/public/media/mellytrade/` (unused by any
component today — importing/passing these before the files exist would
404, so nothing references them yet).

Verified: `git diff --check`, `tsc -b`, and `npm run build` all clean;
live preview confirmed `/`, `/case-study`, and `/terminal` render with no
console errors, zero `/api/*` calls, zero media-asset requests, and no
horizontal overflow at mobile width (375px) — and confirmed the
`(max-width: 768px)` / `(prefers-reduced-motion: reduce)` media queries
resolve correctly at both desktop and mobile viewport widths (the same
queries the new hook uses).
