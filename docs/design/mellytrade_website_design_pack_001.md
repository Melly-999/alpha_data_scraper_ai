# MellyTrade Website Design Pack 001

> **Design/planning document only.** No frontend, backend, runtime, config, package, or
> deployment files were changed to produce this document. No push, merge, or deploy.
> **Run:** `MELLYTRADE-WEBSITE-DESIGN-PACK-001` · **Date:** 2026-07-05 · **Model:** Fable 5

## Goal

Produce an implementation-ready design pack for the public MellyTrade website layer —
`/` (landing) and `/case-study` (portfolio/recruiter page) — inside the existing
React/Vite SPA, adapting the cinematic website prompt-pack patterns to the locked
MellyTrade AIOS identity: institutional dark/amber, read-only, paper-first, safety as the
product story. This document is the direct input for the Sonnet 5 implementation run
`MELLYTRADE-FRONTEND-READONLY-PROTOTYPE-001`.

## Inputs Read

1. `docs/design/mellytrade_aios_platform_scope_001.md` — platform scope, asset inventory,
   route plan, milestones (primary input).
2. `docs/design/mellytrade_cinematic_showcase_concept.md` — approved scroll-narrative
   sections, hard constraints, copy guardrails.
3. `The One-Prompt Website Pack.pdf` (Fable 5 + Higgsfield MCP prompt pack, 10 prompts) —
   used as a **pattern library only**; mechanics extracted, no prompts copied verbatim.

No repo frontend code was read in this run; component facts come from the scope document.

## Existing Platform Assets To Reuse

From the scope audit — the platform is substantially built; this pack composes, it does
not rebuild:

- **Shell/preview surfaces:** `TerminalShell`, `TerminalPage`, `MarketOverviewGrid`,
  `AgentStatusBar`, `TopTickerBar`
- **Safety:** `SafetyBanner`, `SafetyBadges`, `AccessStatusBanner` patterns
- **Portfolio/risk:** `PortfolioRiskSummaryCard`, `RiskGuardrailsCard`, `WatchlistPage`
- **Paper sandbox:** `PaperRunPreviewPage`, `PaperSandboxPreviewPanel`,
  `PaperSandboxActivityRail`, `AlpacaPaperReadOnlyCard`
- **Audit:** `AuditEventsPreview`, `AuditTrailPage`, `AuditRailFilters`
- **AI workspace:** `AIWorkspacePanel`, `AISignalFeedPreview`, `SignalReasoningPanel`
- **Mobile:** `MobileAppPage`, `ScreenshotPreviewCard`
- **Primitives/theme:** `Badge`, `Button`, `Card`, `GaugeBar`, `MiniChart`, `Table`,
  `design/terminalTheme.ts`
- **Brand:** MT pixel monogram + MellyTrade wordmark (primary), `MellyPetMascot.tsx`
  (secondary/community only)
- **Narrative/evidence copy:** README sections (`Safety Contract`, `Architecture`,
  `Validation & Evidence`, `What This Project Demonstrates`, `Roadmap`), `docs/demo/`
  and `docs/showcase/` evidence docs, screenshot inventories

## Product Positioning

**"An AIOS-style read-only trading intelligence and engineering showcase platform."**

MellyTrade **is**: advisory · read-only · paper/simulation-first · safety-first ·
recruiter/client-facing · engineering-evidence-backed · institutional dark/amber ·
premium but calm.

MellyTrade **is not**: a live trading bot, a broker, a signal-selling product, an
execution platform, a casino-like finance app, a get-rich product, or a fake performance
dashboard.

The core narrative inversion: *the safety posture is the flex.* The site should read as
"this builder can ship a production-grade trading-adjacent platform and deliberately
engineered it to be incapable of trading."

## Safety Contract

Non-negotiable on every public surface, visible from the first frame:

- `autotrade=false` · `dry_run=true` · `read_only=true` · `live_orders_blocked=true` ·
  max risk ≤ 1%
- No broker execution, no live trading, no Buy/Sell/Execute/Order/Place-trade controls
- No real or realistic-looking account IDs, order IDs, credentials, API keys, secrets
- No fake or implied performance claims — no invented returns, win-rates, or PnL
- All preview data labeled **DEMO / PAPER / SIMULATED** — never presented as live
- AI output always carries "advisory only · not financial advice"
- No push, merge, deploy, or destructive git actions without explicit approval

## Source PDF Pattern Adaptation

Only the mechanics were extracted; every adapted pattern is re-grounded in the
institutional/no-hype constraints.

| PDF Prompt | Pattern taken | MellyTrade adaptation |
|---|---|---|
| **08 — SaaS/App (PULSE)** | Dark product hero where the UI "assembles itself" on scroll; feature blocks pinned over media; proof/metrics strip; FAQ; final CTA | **Landing page backbone.** Hero = AIOS command core assembling from amber/cyan particles. Feature blocks = Signal Intake / Risk Layer / Paper Sandbox. Metrics strip replaced with **engineering-evidence counters** (tests passing, CI runs, audit events, docs) — never trading metrics. FAQ becomes "Project Notes / What this is not." |
| **03 — Personal Portfolio** | Massive display type identity; stats strip; three-pillars section; work cards; strong recruiter CTA | **/case-study backbone.** Identity element is the **MT monogram + project**, not a personal likeness (no portrait required or generated). Stats = engineering facts. Three pillars = Platform Engineering / Safety Engineering / AI Workflow. Work cards = milestone/evidence cards. |
| **02 — Journey/Descent (ABYSSAL)** | Chained scroll-scrub journey with a fixed HUD meter and zone labels; scrolling *is* the narrative | **AIOS scroll narrative** on the landing page: Signal Intake → Risk Layer → Paper Sandbox → Audit Rail → GitHub Evidence → Safety Contract. Fixed HUD shows a **safety-status meter** (badges accumulating: READ ONLY → PAPER → AUDITED), not depth or speed. Implemented with pinned sections + CSS/JS reveals; full five-clip chaining is out of MVP scope. |
| **09 — Agency/Studio (NOIR&CO)** | Selected-work grid with hover reveals; kinetic one-word manifesto; disciplined accent budget | **Proof grid**: GitHub/CI cards, milestone cards, evidence-doc cards with quiet hover states. Kinetic manifesto adapted to a restrained three-beat: `READ-ONLY. PAPER-FIRST. AUDITED.` Accent-budget rule adopted: cyan used at most three times per page. |
| **01 — Luxury Product (AURUM & NOIR)** | One hero object, macro detail passes, "quiet, expensive, very few words" copy; spec callouts | **Terminal-as-object.** The read-only terminal is treated like a luxury product: black-glass panel reveal, macro passes over the safety badges and audit rail, spec callouts drawn from real config (`autotrade=false`, `max risk ≤ 1%`). Copy tone imported wholesale: sparse, confident, no exclamation marks. |
| **07 — Hypercar/HUD (VANTA)** | Corner HUD synced to scroll; performance-like responsiveness | **Used lightly.** A small fixed HUD chip showing section name + safety badges. No speed counters, no 0–250 metaphors, no fake performance numbers of any kind. |

Pack-wide mechanics adopted: **one hero image referenced by every clip** (consistency
beats quality), **spend generation budget on the hero only**, **std/1080p/~8s/no-audio
defaults**, **compress videos for web**, **launch on localhost and verify before done**.

## Visual System

Inherits the locked identity (`mellytrade_visual_identity_board_summary.md`,
`terminalTheme.ts`) — no re-litigation:

- **Base:** institutional near-black (`#0A0A0C`-family), black-glass panels
  (subtle translucency + 1px amber-tinted borders), terminal grid texture at very low
  opacity, optional faint scanlines in hero only
- **Primary accent:** amber/gold — signal lines, active states, monogram glow
- **Secondary accent:** cyan/blue — data-flow lines only, budgeted (≤3 uses per page)
- **Type:** condensed display face for headlines (large, tracked-in), clean sans for
  body, monospace for badges/spec callouts/config values
- **Brand:** MT pixel monogram = primary symbol; MellyTrade wordmark = product name;
  Melly Pet = one small optional community/footer detail only
- **Never:** green/red gambling cues, blinking tickers, neon-casino gradients, fake
  candlestick walls, urgency/FOMO patterns

## Hero Concept

**"The Institutional AI Command Core."**

One hero concept powers the whole site and all media: a black-glass terminal shell
floating in a dark institutional void. Amber risk/signal lines trace through it; a subtle
cyan data flow enters from the left (signal intake) and terminates in a paper-sandbox
panel — never in an order button. Floating read-only safety badges (`READ ONLY`,
`PAPER SANDBOX`, `LIVE ORDERS BLOCKED`) orbit slowly. An audit rail glows along the right
edge. At the center, the **MT pixel monogram glows quietly** — steady, not pulsing.
No prices, no PnL, no candles implying live fills.

This single image is: the landing hero, the reference frame for all clips, the
`/case-study` header (cropped), and the social/OG share image.

## Cinematic Motion Plan

Low-cost, web-practical. **1 hero image + max 3 clips** for the MVP, all reusing the same
hero image as reference. Defaults: std mode, 1080p, 16:9, no audio, ~8s, no 4K, max 2–3
takes on the hero clip only, compress all video for web (~90% size cut), lazy-load
below-the-fold media, poster frames from the hero image.

1. **Clip 1 — AIOS Assembly** *(hero)*: the command interface assembles from amber/cyan
   signal particles in the dark void; safety badges are the **last elements to lock into
   place**, ending on the hero frame. Used as the scroll-scrubbed or autoplay hero.
2. **Clip 2 — Risk Layer Activation**: macro glide across the shell as safety toggles,
   read-only badges, paper-sandbox markers, and audit events slide in and settle.
   Backs the Safety Contract / Risk Layer sections.
3. **Clip 3 — Product Showcase Finale**: terminal, dashboard, paper sandbox, audit rail,
   mobile preview, and a GitHub evidence card align into one premium composed product
   view. Backs the final CTA.

Fallback rule: every clip position must degrade gracefully to the static hero image —
the site must ship and look premium with **zero** clips.

## Route Plan

| Route | Status | Purpose |
|---|---|---|
| `/` | **New** | Public landing — hero, AIOS narrative, previews, safety contract, GitHub evidence, CTA |
| `/case-study` | **New** | Portfolio/recruiter/client case study |
| `/terminal` (+ sub-routes) | Unchanged | Internal terminal; linked as "Open the terminal preview" |
| `/watchlist` | Unchanged | Portfolio dashboard; linked from landing preview card |
| `/mobile` | Unchanged | Mobile/PWA demo; linked from PWA section |
| `/paper-run-preview` (existing path) | Unchanged | Paper sandbox preview; linked from sandbox section |

Public routes are additive inside the existing SPA. `App.tsx`'s current `/ → /terminal`
redirect is replaced by the new landing page; a persistent "Enter terminal" nav link
preserves the old behavior for returning users. No internal route is redesigned.

## Landing Page Structure

Single scroll narrative (Prompt 02 spine + Prompt 08 sections). A fixed slim HUD chip
(top-right) shows the current section name and the safety badges throughout.

### Hero
Full-viewport. Hero media (Clip 1 or static hero image), `MellyTrade` wordmark tracking
in over the MT monogram, headline + subheadline (see Copy Blocks), `READ-ONLY · ADVISORY`
badge visible from frame one. Two buttons: `View the case study` (primary, amber) and
`Explore the terminal preview` (ghost). Scroll cue: a thin amber line, not a bouncing
arrow.

### Product Snapshot
Three-beat kinetic statement pinned on scroll — `READ-ONLY. PAPER-FIRST. AUDITED.` —
followed by one calm paragraph stating what the platform is, and one stating what it
refuses to be.

### AIOS Preview
The journey section. Pinned steps over subtle amber/cyan line animation:
**Signal Intake → Risk Layer → Paper Sandbox → Audit Rail**, one line of copy per step,
each step lighting its badge in the HUD chip. This is reveal choreography over static
panels, not a video chain.

### Safety Contract
Black-glass panel rendering the contract as monospace config lines
(`autotrade = false`, `dry_run = true`, `read_only = true`,
`live_orders_blocked = true`, `max_risk ≤ 1%`) with a plain-language line beneath each.
Reuses `SafetyBanner`/`SafetyBadges`. Framed as a feature, headline per Copy Blocks.

### Terminal Preview
Wide black-glass card embedding a **demo-mode** `TerminalShell` composition (static or
sample-data render, watermarked `DEMO DATA`). Macro spec callouts (Prompt 01 style):
market intelligence grid, AI advisory panel, agent status — and the explicit callout
"no execution controls exist in this interface." Link: `Open the terminal preview →
/terminal`.

### Portfolio Dashboard Preview
`PortfolioRiskSummaryCard` + `RiskGuardrailsCard` composition with illustrative,
labeled sample data. Copy leads with risk discipline (exposure, drawdown guard, ≤1% cap),
never returns. Link to `/watchlist`.

### Paper Sandbox Preview
`PaperSandboxPreviewPanel` / `PaperRunPreviewPage` composition. Permanent
`PAPER · SIMULATED` labels. Copy states there is no path from sandbox to a live account.
Link to the existing paper-run preview route.

### Audit / Event Rail
Vertical rail (reusing `AuditEventsPreview`) scrolling a feed of real, safe event types:
analyses run, validations passed, safety checks, config assertions. Copy: evidence over
claims.

### GitHub Evidence
Proof grid (Prompt 09 mechanics): repo card, CI/test cards (pytest suite, Playwright
e2e, static safety scan), evidence-doc cards from `docs/demo/`, milestone cards from the
roadmap. Links only — no tokens, no secrets, no private URLs. Engineering counters
(tests, workflows, audit docs) may count up on scroll; trading numbers may not exist.

### Mobile / iPad PWA
Split panel: device-frame screenshot(s) from the existing iPad PWA evidence + copy on
the responsive, installable read-only surface. Link to `/mobile`.

### CTA
Final band over Clip 3 (or hero image). Recruiter/client CTA copy (see Copy Blocks),
buttons: `Read the case study`, `View the repository on GitHub`. Footer: MT monogram,
one-line disclaimer, optional small Melly Pet mark with "community mascot" microcopy,
no social-proof inflation.

## Case Study Page Structure

Prompt 03 skeleton, identity = the project. Shares the hero image (cropped band) and HUD
chip. Sections are `CaseStudyLayout` wrappers over `Card`/`Badge` primitives; content is
ported from README + `docs/demo/` narrative docs rather than rewritten from scratch.

### Project Story
One-screen intro: what MellyTrade is, why it exists (engineering showcase), and the
deliberate decision to make it read-only. Three-pillar strip: **Platform Engineering ·
Safety Engineering · AI Workflow**.

### Problem
Trading-adjacent software is the hardest place to prove engineering judgment: high
stakes, regulatory sensitivity, hype-saturated. The problem framed: *demonstrate
production-grade capability without creating execution risk.*

### Solution
An AIOS-style read-only intelligence platform: signal analysis, risk framing, paper
simulation, and audit evidence — with execution structurally removed, not merely
disabled.

### Architecture
Rendered architecture diagram (data flow: intake → indicators → LSTM/AI advisory →
risk gates → paper sandbox → audit), plus the stack list (Python pipeline, React/Vite/TS
terminal, CI). Sourced from README's Architecture section.

### Safety Engineering
The strongest section. Config-level contract, orchestrator deny-list + static safety
scan, pytest safety-regression suite, "what is intentionally blocked" list, and the
UI-level guarantee: no execution control exists anywhere in the component tree.

### UI System
The locked visual identity: terminal theme, black-glass panels, badge language, MT
monogram system, component library overview with 2–3 screenshots.

### Validation / Evidence
Cards for: pytest suite, Playwright e2e (incl. iPad/mobile viewports), static safety
scan, demo/evidence docs, session logs. Each links to the artifact in the repo.

### Roadmap
Rendered from the existing roadmap: shipped milestones as completed cards, next steps as
open cards. Honest, dated, no vaporware.

### Recruiter / Client Summary
Short closing block: what this project demonstrates (full-stack + AI product + safety
engineering), what a collaboration looks like, links: GitHub, case-study PDF (optional
later), contact. No likeness required.

## Copy Blocks

Tone: calm, direct, premium, technical. No hype, no exclamation marks, no promises.

- **Hero headline:** `Intelligence, not execution.`
- **Hero subheadline:** `MellyTrade is a read-only AI market-analysis platform. It studies, simulates, and explains — and is engineered so it cannot trade.`
- **Product snapshot:** `An AIOS-style command center for market intelligence: signal analysis, risk framing, paper simulation, and a full audit trail. Built as engineering evidence, not as a trading product.`
- **Safety contract:** `Safety is the architecture, not the disclaimer. Autotrade is off. Orders are blocked. Risk is capped at one percent. Every surface is read-only — by construction, and verified by tests.`
- **Terminal preview:** `A production-grade terminal with everything except an order button. Market intelligence, AI advisory, agent status — rendered on demo data, labeled as such.`
- **Portfolio dashboard preview:** `Risk first, always. Exposure, drawdown guards, and allocation views on illustrative data. Performance is deliberately understated — because it is simulated.`
- **Paper sandbox preview:** `Every position here is paper. The sandbox has no path to a live account — not hidden, not gated. Absent.`
- **Audit / event rail:** `Every analysis, validation, and safety check leaves a record. The platform argues from evidence, and so does this site.`
- **GitHub evidence:** `Don't take the website's word for it. The tests, the safety scans, the CI runs, and the commit history are public.`
- **Case-study intro:** `A production-quality trading platform that refuses to trade. This case study covers the architecture, the safety engineering, and the AI-assisted workflow behind it.`
- **Recruiter/client CTA:** `If you're evaluating whether this team can build safe, auditable, AI-assisted tooling — the evidence is one click away.`
- **Final CTA:** `Read the case study. Inspect the code. Everything is on the record.`
- **Persistent disclaimer (footer):** `Advisory and educational software. Read-only. All data shown is demo or simulated. Not financial advice. No live trading capability exists.`

## Component Reuse Plan

| Public section | Reused asset | Mode |
|---|---|---|
| Safety Contract | `SafetyBanner`, `SafetyBadges` | as-is |
| Terminal Preview | `TerminalShell` + `MarketOverviewGrid` + `AgentStatusBar` | demo-data/preview mode wrapper |
| Dashboard Preview | `PortfolioRiskSummaryCard`, `RiskGuardrailsCard` | sample-data wrapper |
| Paper Sandbox | `PaperSandboxPreviewPanel`, `PaperTicketPreviewPanel` | as-is (already preview-shaped) |
| Audit Rail | `AuditEventsPreview` | sample-event fixture |
| Mobile/PWA | `ScreenshotPreviewCard`, existing PWA screenshots | as-is |
| Layout primitives | `Card`, `Badge`, `Button`, `GaugeBar`, `MiniChart`, `Table` | as-is |
| Theme | `design/terminalTheme.ts` | extend with landing tokens only if needed |

Rule: if an internal component can't render safely on sample data without modification,
wrap it in a lightweight public-preview wrapper — **do not change internal app
behavior.**

## New Components Needed

Minimum set, all presentational, no new data/state plumbing:

1. `PublicLandingPage` — route component for `/`
2. `CaseStudyPage` — route component for `/case-study`
3. `HeroAIOSShowcase` — hero media band (image/clip + wordmark + badges + CTAs)
4. `PublicSafetyContract` — monospace contract panel wrapping `SafetyBadges`
5. `ProductPreviewGrid` — layout for the terminal/dashboard/sandbox/audit preview cards
6. `GitHubEvidenceSection` — repo/CI/evidence/milestone proof grid
7. `CinematicHeroMedia` — video-with-poster-fallback media primitive (lazy, compressed)
8. `RecruiterCTA` — final CTA band (links only, no PII forms)
9. `SectionHUDChip` — small fixed section-name + safety-badge indicator (optional; cut
   first if scope pressure)

## Animation / Media Notes

- Motion is **restrained and deliberate**: fades, 200–400ms translates, pinned reveals.
  One kinetic-type moment (Product Snapshot) per page, maximum.
- Prefer CSS/IntersectionObserver reveals; add Lenis-style smooth scroll only if it
  costs nothing on mobile. Full canvas frame-scrubbing is a nice-to-have, not MVP.
- `prefers-reduced-motion`: all pinned/kinetic sections collapse to static stacked
  layout; videos replaced by poster images.
- All media compressed for web (target: hero clip < 4–6 MB), lazy-loaded below the fold,
  poster frames everywhere. Site must be fully presentable with zero videos.
- Engineering counters may animate up on scroll; no number that could be mistaken for a
  trading result may appear, animated or static.

## Higgsfield Clip Plan

**Status: prompts prepared only.** Higgsfield MCP was **not** connected in this run; no
images or videos were generated and no credits were spent. The prompts below are
copy-paste-ready for a later, separate media-generation run
(`MELLYTRADE-MEDIA-GENERATION-001`, proposed). That run generates at most: **1 hero image
+ 3 clips**, std mode, 1080p, 16:9, no audio, ~8s each, all referencing the same hero
image. No 4K. Budget rule: 2–3 takes on the hero image and Clip 1 only; first acceptable
take for Clips 2–3.

### Prompt H0 — Hero image (generate FIRST; reference in every clip)

> Cinematic hero image of an institutional AI command core: a black glass trading-terminal
> shell floating in a dark, empty institutional void. Thin amber signal lines trace across
> its panels; a subtle cyan data stream flows in from the left and terminates inside a
> panel labeled PAPER SANDBOX. Small floating holographic badges read READ ONLY, PAPER
> SANDBOX, LIVE ORDERS BLOCKED. A quiet vertical audit-log rail glows faintly along the
> right edge. At the center, a pixel-art "MT" monogram glows softly in amber — steady, not
> pulsing. Mood: institutional, premium, calm, expensive; matte blacks, restrained amber
> accent, faint cyan secondary. High-end product photography lighting, shallow depth,
> subtle film grain. STRICTLY EXCLUDE: buy or sell buttons, order tickets, candlestick
> charts, price numbers, PnL or percentage figures, account numbers, broker logos, red/
> green trading colors, neon casino glow, human faces.

### Prompt C1 — Clip 1 "AIOS Assembly" (hero clip; std, 1080p, 16:9, ~8s, no audio)

> Using the attached hero image as the strict visual reference: thousands of amber and
> cyan light particles drift in a dark institutional void, then slowly assemble into the
> black glass command interface from the reference image. Panels form first, then the
> amber signal lines connect, and LAST the three safety badges — READ ONLY, PAPER
> SANDBOX, LIVE ORDERS BLOCKED — lock into place with a quiet settle. End exactly on the
> reference hero frame, motionless. Slow, deliberate, premium motion; no camera shake.
> Same exclusions as the reference: no trading controls, prices, charts, or figures.

### Prompt C2 — Clip 2 "Risk Layer Activation" (std, 1080p, 16:9, ~8s, no audio)

> Using the attached hero image as the strict visual reference: a slow macro camera glide
> across the black glass terminal surface. As the camera passes, safety elements activate
> one by one: a toggle labeled AUTOTRADE settles into OFF, a READ ONLY badge illuminates,
> PAPER SANDBOX markers fade in over a simulation panel, and small audit-log entries
> slide into the rail on the right, each with a soft amber tick. Calm, mechanical
> precision, watchmaking-macro feel. End on a composed wide of the activated safety
> layer. Same exclusions as the reference.

### Prompt C3 — Clip 3 "Product Showcase Finale" (std, 1080p, 16:9, ~8s, no audio)

> Using the attached hero image as the strict visual reference: six floating black glass
> panels — terminal, portfolio risk dashboard, paper sandbox, audit event rail, a mobile/
> tablet preview, and a GitHub evidence card — drift in from the darkness and align into
> one balanced, premium product composition around the glowing amber MT pixel monogram.
> Slow convergence, gentle parallax, everything settling into stillness on a final
> poster-ready frame. Institutional, calm, expensive. Same exclusions as the reference.

### Post-generation steps (same later run)

1. Compress all clips for web (target < 4–6 MB each; H.264/H.265 + WebM).
2. Export a poster frame per clip (Clip 1's poster = the hero image itself).
3. Deliver to `frontend/public/media/` (or the path the frontend run designates) with a
   short manifest listing file, section, and poster mapping.
4. Verify no generated frame contains excluded content (order controls, prices, PnL,
   account numbers) before the files enter the repo.

## Mobile Rules

- Both public pages meet the same responsive bar as `MobileAppPage` and the documented
  iPad PWA evidence.
- Hero: static image on small viewports (no autoplay video), headline scales down, CTAs
  stack full-width.
- Pinned scroll sections degrade to plain stacked sections under ~768px.
- Preview cards become a single column; the proof grid becomes swipeable or stacked
  cards.
- HUD chip hidden on mobile; safety badges instead render inline at the top of each
  section.
- Touch targets ≥ 44px; no hover-only reveals without a tap equivalent.

## Accessibility Notes

- Semantic landmarks and heading order (`h1` once, per-section `h2`).
- Contrast: amber-on-near-black and body text meet WCAG AA; verify amber link text
  against glass panels specifically.
- All media: descriptive alt text; videos are decorative (`aria-hidden`) with content
  duplicated in text; no autoplay with sound (there is no audio at all).
- Full keyboard navigability; visible focus states in amber; skip-to-content link.
- `prefers-reduced-motion` honored globally (see Animation notes).
- Safety badges rendered as text, not images — screen readers must hear "read only,
  paper sandbox, live orders blocked."

## Explicitly Out of Scope

- Any frontend/backend/runtime/config/package/deployment change in **this** run
- Live trading, broker execution, order placement, or any Buy/Sell/Execute/Order control
- Live data feeds to anonymous visitors; auth; payments; PII-collecting forms
- Redesign of internal routes (`/terminal`, `/watchlist`, `/mobile`, paper previews)
- Melly Pet as primary identity; personal portrait generation
- OmniRoute/GLM routing/RTK/hooks/extra-skills work
- Video generation (deferred to a separate media run)
- Separate marketing-site stack (SSR/Astro/Next) — revisit only if SEO demands it later

## Sonnet Implementation Handoff

**Next run ID:** `MELLYTRADE-FRONTEND-READONLY-PROTOTYPE-001` · **Model:** Sonnet 5

Instructions for the implementation run:

1. **Scope:** implement only the public `/` and `/case-study` routes per this pack.
   Frontend-only. Docs updates allowed. Nothing else.
2. **Reuse first:** compose the existing components listed in the Component Reuse Plan;
   build only the New Components listed above. If an internal component can't render on
   sample data unmodified, wrap it — do not change internal app behavior.
3. **Routing:** add the two routes additively in `App.tsx`; replace the `/ → /terminal`
   redirect with `PublicLandingPage`; keep every existing route working unchanged; add a
   persistent "Enter terminal" nav link.
4. **Data:** static sample fixtures only, all labeled DEMO/PAPER/SIMULATED. No new
   backend endpoints, no live feeds.
5. **Media:** build against the static hero image with `CinematicHeroMedia`
   poster-fallback slots; do not block on video clips (separate media run).
6. **Hard blocks:** no broker execution, no live trading, no Buy/Sell/Execute/Order/
   Place-trade controls or copy, no secrets, no account/order IDs, no fake performance
   claims, no backend/runtime/config/package/deployment changes unless explicitly
   approved (a minimal route addition in `App.tsx` is the approved exception).
7. **Verification:** local only — `npm run dev`/preview, verify both routes render,
   responsive pass at mobile/iPad/desktop widths, `prefers-reduced-motion` check, and a
   manual safety-copy sweep (grep the new code for buy/sell/execute/order strings). Run
   the existing safety validator and test suite; do not push, merge, or deploy.
8. **Keep it reviewable:** small commits on a task branch, docs-first notes, PR only —
   never direct to `main`.

## Next Recommended Run

`MELLYTRADE-FRONTEND-READONLY-PROTOTYPE-001` — implement the public `/` and
`/case-study` routes per this pack (frontend/docs-only, local verification, no push or
deploy without approval).

## Implementation Note (MELLYTRADE-FRONTEND-READONLY-PROTOTYPE-001, Sonnet 5)

Implemented on branch `feature/public-landing-case-study-001` (frontend/docs-only,
not pushed). Routes, components, and copy match this pack. Two deviations, both
safety-motivated:

- **`SafetyBadges` used instead of `SafetyBanner`.** `SafetyBanner` polls the live
  `/health` and `/risk/config` endpoints via `useMellyHealth`/`useMellyRiskConfig`.
  Calling those from an anonymous public page would be a live backend feed to
  anonymous visitors, which the scope doc rules out. `SafetyBadges` is static and
  network-free, so `PublicSafetyContract` reuses that instead.
- **Terminal/Portfolio/Paper-sandbox previews are static wrappers, not live
  embeds.** `TerminalShell`'s dashboard view renders `AIWorkspacePanel`,
  `SupabaseStatusCard`, and `AlpacaPaperReadOnlyCard`, all of which fetch live data
  internally regardless of the `data` prop passed in; the paper-sandbox panels
  (`PaperSandboxPreviewPanel`, `PaperRunPreviewPanel`, `PaperSandboxActivityRail`)
  and `PortfolioRiskSummaryCard` do the same. Per this pack's own fallback rule
  ("if an internal component can't render safely on sample data without
  modification, wrap it"), `ProductPreviewGrid` instead composes the confirmed
  pure, props-only components (`MarketOverviewGrid`, `RiskGuardrailsCard`,
  `IBKRBrokerCard`, `AgentStatusBar`, `AISignalFeedPreview`, `AuditEventsPreview`)
  over a static fixture, plus small static cards for the portfolio and
  paper-sandbox previews.

Fixture data lives in `frontend/src/fixtures/publicShowcaseFixtures.ts` (not
`src/data/` — the repo's root `.gitignore` has a blanket `data/` rule that would
have silently excluded it from version control).

Files added: `frontend/src/pages/PublicLandingPage.tsx`,
`frontend/src/pages/CaseStudyPage.tsx`, `frontend/src/pages/public-site.css`,
`frontend/src/components/public/*` (`PublicSiteNav`, `PublicSiteFooter`,
`HeroAIOSShowcase`, `CinematicHeroMedia`, `SectionHUDChip`,
`PublicSafetyContract`, `ProductPreviewGrid`, `GitHubEvidenceSection`,
`RecruiterCTA`), `frontend/src/fixtures/publicShowcaseFixtures.ts`. Modified:
`frontend/src/App.tsx` (added `/` and `/case-study` routes; all other routes
unchanged).

Verified locally: `tsc -b` clean, `npm run build` clean, both routes and all
pre-existing routes (`/terminal`, `/watchlist`, `/mobile`) render with no console
errors, no horizontal overflow at mobile/tablet/desktop widths, and a grep sweep
of the new code found no Buy/Sell/Execute/Order strings outside of copy that
explicitly describes what is forbidden. Not run: Playwright e2e suite (existing
specs only target `/terminal/paper-run-preview`, unaffected by this change) and
the Python safety validator (no backend/Python files changed in this run).
