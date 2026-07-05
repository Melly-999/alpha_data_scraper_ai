# MellyTrade Public Showcase Final QA 001

> **QA/audit document.** No media generated, no Higgsfield MCP connected, no
> credits spent, no external APIs called. No backend/runtime/broker/config/
> package/deployment files changed. No frontend fixes were needed. No push,
> merge, or deploy.
> **Run:** `MELLYTRADE-PUBLIC-SHOWCASE-FINAL-QA-001` · **Date:** 2026-07-05 · **Model:** Sonnet 5

## Outcome

**PASS — clean.** The public website, including the integrated hero media,
holds up under a full final QA pass. All 6 routes render correctly, the
hero image loads on both public pages with no autoplay video anywhere, zero
`/api/*` calls fire from either public page, no forbidden trading controls
or chart imagery exist, and the full validation suite is clean. No frontend
or docs fixes were required in this run.

## Branch / Commit Reviewed

- Branch: `feature/public-landing-case-study-001`
- Latest local commit: `ba6fc80` (feat(frontend): integrate public website
  media pack)
- Prior commits: `bb8aa69`, `5d2ecaa`, `99bde92`, `da74565`
- Upstream: none configured (`no upstream configured for branch
  'feature/public-landing-case-study-001'`) — not pushed
- Working tree: clean for everything under `frontend/` and the design/QA
  docs touched across this branch's history; only pre-existing, unrelated
  untracked/modified files remain elsewhere in the repo (same set observed
  in every prior QA pass on this branch — `docs/architecture/*`,
  `docs/design/*` design-pack inputs, `frontend/public/brand/`, etc.),
  confirming no overlap with this run's target files.

## Routes Verified

| Route | Result |
|---|---|
| `/` | Renders `PublicLandingPage`; hero shows the static poster image (`<img>`, not `<video>`); "Enter terminal" CTA confirmed `href="/terminal"`. |
| `/case-study` | Renders `CaseStudyPage`; hero band shows the same static poster image inside `.public-case-hero`. |
| `/terminal` | Unchanged, renders `.terminal-root`. |
| `/watchlist` | Unchanged. Shows its own pre-existing "no backend running" fallback state in this local session — not a regression (file untouched, same behavior observed in every prior QA pass on this branch). |
| `/mobile` | Unchanged, renders fully. |
| `/terminal/paper-run-preview` | Unchanged, renders `.terminal-root`. |

No console errors on any route.

## Media Verified

- `frontend/public/media/mellytrade/` contains exactly the 6 expected files:
  `hero-command-core.png`, `hero-command-core-poster.png`,
  `aios-assembly.mp4`, `risk-layer-activation.mp4`,
  `product-showcase-finale.mp4`, `manifest.json`. No `rejected/` or
  `review_crops/` content is present anywhere in the repo.
- `manifest.json` is valid, well-formed JSON (parsed successfully with
  Python's `json` module); 5 asset entries, each with `safety_sweep: PASS`
  (one marked `PASS (2nd take)` for C3, one `PASS (identical to H0)` for the
  poster duplicate).
- Both `hero-command-core.png` and `hero-command-core-poster.png` load with
  `200`/`304` responses in the live preview; no 404s anywhere.
- `/` uses `hero-command-core-poster.png` as a static `<img>` — confirmed via
  DOM inspection (`mediaTag: "IMG"`), not a `<video>` element.
- `/case-study` uses the same poster image, same confirmation method.
- `aios-assembly.mp4`, `risk-layer-activation.mp4`, and
  `product-showcase-finale.mp4` all exist in the public media directory and
  are referenced in `mediaAssets.ts` and `manifest.json`, but **no network
  request for any of the three `.mp4` files occurred** while browsing `/` or
  `/case-study` in this session — confirming they are not rendered or
  autoplayed on either public page.

## Visual Safety Review

- Confirmed via `git grep` across all public-facing frontend files (pages,
  `components/public/`, fixtures, and the media manifest) for
  buy/sell/execute/order/place-trade/PnL/account/broker-logo/API-key/secret:
  every match is descriptive safety copy, a manifest safety note affirming
  an *absence* of that content, or the one previously-reviewed non-issue
  (`direction: "BUY"` — a plain-text, non-interactive signal-direction value
  in the demo fixture, rendered as inert text under a "no execution
  controls" panel header, unchanged since the original implementation QA).
  No interactive control, secret, or credential exists anywhere.
- Hero image / C1 line re-review: as documented in
  `docs/showcase/media_integration_001.md`, the amber/cyan flowing line
  reads as an abstract signal-flow motif when static (current production
  state) — no axis, gridlines, price labels, or candles are present in
  either asset. The integration run already made the conservative call to
  keep this as a **static image only** (no autoplay), specifically because
  the line felt too close to a "line go up" trading visual once seen moving
  full-bleed behind the headline. That decision remains correct and is
  preserved unchanged in this QA pass — no reason was found in this run to
  revisit it.
- C3's accepted take (2nd take) re-confirmed to contain no chart panel,
  consistent with the integration run's finding.
- No red/green casino-style trading cues found anywhere; the palette is
  consistently amber/cyan/black across all UI and media.

## Public Data / Copy Review

- All demo metrics on `/` and `/case-study` carry explicit DEMO / PAPER /
  SIMULATED / READ-ONLY labels (chip badges on every `ProductPreviewGrid`
  card, "DEMO DATA" watermark on the terminal-preview frame, "PAPER" tag on
  the sandbox card).
- No fake trading performance or real-account claims: copy explicitly states
  "no path from sandbox to a live account," "nothing here calls a live
  account," and the persistent footer disclaimer ("Read-only... All data
  shown is demo or simulated. Not financial advice. No live trading
  capability exists.").
- GitHub/evidence claims (real repo link, real PR/test/CI references) are
  phrased strictly as engineering proof — test counts, CI workflow names,
  safety-validator results — never as trading performance.
- Copy tone remains calm, technical, and premium throughout; no exclamation
  marks, no hype language, no urgency/FOMO patterns.

## Network / Backend Call Review

Confirmed via live network panel on both `/` and `/case-study`: zero
requests to `/api/*` or to the FastAPI proxy target. All traffic is Vite
dev-server module transforms, the static media files, and one pre-existing,
unrelated Google Fonts load declared in `index.html` (not part of the public
website work, present on every route in the app). No broker or backend call
of any kind originates from either public page.

## Responsive Review

| Width | Hero | Overflow | Notes |
|---|---|---|---|
| Desktop (1280×900) | Poster image, full hero band | None | — |
| Tablet (768×1024) | Poster image, `753×516` (`/`) / `753×586` (`/case-study`) | None | Moderate vertical crop via `object-fit: cover`, image remains centered and legible |
| Mobile (375×812) | Poster image | None | Confirmed in the media-integration run; re-verified here |

Nav collapses correctly on mobile (links hidden, CTA remains visible and
full touch-target size per the earlier QA fix). No layout shift observed
switching from the CSS placeholder to the real poster image (both fill the
same `position: absolute; inset: 0` box).

## Accessibility / Reduced Motion Review

- Single `h1` per page confirmed on both `/` and `/case-study`.
- Hero `<img>` carries `alt=""` and `aria-hidden="true"` (correct treatment
  for a decorative image whose content is duplicated as real text
  elsewhere on the page — unchanged pattern from the original component
  design).
- No `outline: none` or other focus-suppressing CSS found; default browser
  focus rings remain intact.
- `CinematicHeroMedia`'s mobile (`max-width: 768px`) and
  `prefers-reduced-motion: reduce`) autoplay guards remain in the code,
  type-checked and unchanged — currently unexercised in production only
  because no page passes a `videoSrc` prop, which is itself the safety-first
  choice under review here.
- Confirmed no video is autoplaying on either public page at any viewport
  size in this session.

## Validation Commands

```powershell
git diff --check     # clean
npx tsc -b            # clean
npm run build           # clean
```

Not run: Playwright e2e suite (existing specs only target
`/terminal/paper-run-preview`, unaffected by any change on this branch) and
the Python safety validator (no backend/Python files touched anywhere in
this branch's history).

## Issues Found

None. No forbidden controls, no chart imagery, no secrets, no 404s, no
console errors, no layout regressions were found.

## Fixes Applied, If Any

None required in this run.

## Known Limitations

- `/watchlist` shows its own pre-existing "backend unavailable" fallback
  state when QA'd without a running backend — expected local-session
  behavior, not a defect, and outside this branch's scope (file untouched).
- C1/C2/C3 video clips remain unused on any page; still available for a
  future non-hero, non-autoplay preview section per the design pack, per
  `docs/showcase/media_integration_001.md`'s retake/reuse notes.
- Video assets are MP4-only (no WebM source) — irrelevant to current
  production behavior since no video is rendered, but noted for any future
  run that does wire one in.

## Next Recommended Run

`MELLYTRADE-BRANCH-SCOPE-AUDIT-001`

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
