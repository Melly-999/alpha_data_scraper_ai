# Higgsfield Cinematic Prompt Pack 001

**Task:** MELLY-HIGGSFIELD-CINEMATIC-PROMPT-PACK-001
**Status:** Approved plan — docs-only. No media generated yet. No implementation.
**Date:** 2026-07-11
**Scope:** Portfolio website hero + MellyCore AIOS `/aios` cinematic showcase (W1 static slice) + MellyTrade Market Orbit.

**Source patterns studied:** The One-Prompt Website Pack / Fable5-Higgsfield Website Prompt Pack (hero-image-first reference chain, std 1080p 16:9 no-audio ~8s, frame-chaining for scroll journeys, 2–3 takes on hero only, compress for web) and the Ultimate Prompting Guide for Video Generation Models (scene setup → camera path → environment → one style → motion tone; continuous motion, no cuts).
**Patterns deliberately rejected:** fake stats counters, fake logo strips, fake pricing, "award-winning" claims in copy, humans as the central element.

---

## 1. Recommended generation order

| # | Asset | Type | Why this order |
|---|---|---|---|
| G1 | **Master hero image** — "MellyCore Command Core" | 1 image | The single visual anchor. Everything references it. Nothing else is generated until this is approved. |
| G2 | Portfolio hero poster (crop/regrade of G1) | 1 image | Immediately usable on the portfolio site with zero extra credits. |
| G3 | Scene 02 — Obsidian galaxy | poster → clip | Signature AIOS visual; maps to existing `#architecture` section. |
| G4 | Scene 06 — MellyTrade Market Orbit | poster → clip | The product-layer showpiece and the riskiest one to get right (safety exclusions). |
| G5 | Scene 04 — Context Gateway flow | poster → clip | Completes the core process→platform→product triad. |
| G6 | Scenes 01, 03 | posters only | Boot + Model Hub read fine as stills. |
| G7 | Scenes 05, 07 | posters only | Dashboard layer and PWA surface are compositional, not motion-dependent. |
| G8 | Optional clip upgrades for 01/03/05/07 | clips | Only after the site works poster-first and credits allow. |

**Rule:** no clip is generated for a scene whose poster hasn't been approved. The poster *is* the clip's reference image (start frame), so a bad poster wastes every downstream credit.

## 2. Master visual style block

Append this block to **every** image and video prompt, verbatim:

```
STYLE — Cinematic, minimal, high-end technology aesthetic. Abstract data
visualization, not a real software screenshot. Deep obsidian background
(#0A0E14 range), never pure black. Two accent families only: warm amber
(safety, guardrails, MellyTrade) and cool cyan-teal (knowledge, context,
graph). Soft volumetric glow, thin luminous lines, fine particle fields,
subtle film grain. Physically plausible studio lighting with gentle rim
light. No humans. No readable text, numbers, words, or UI labels anywhere
in frame — all interface elements are abstract glowing shapes and blurred
glyph suggestions. Composition holds a clear focal center and generous
negative space, framed 16:9, safe for a dark website hero.
MOTION TONE (video only) — slow, smooth, elegant; one continuous camera
move; no cuts; loop-friendly ending that settles into stillness.
FORMAT — Seedance / Higgsfield std mode, 1080p, 16:9, no audio, ~8 s.
```

The "no readable text" rule is load-bearing: video models garble text, and garbled fake UI numbers on a trading-adjacent visual would read as fake data — the one thing this portfolio must never do.

## 3. Strict exclusions block (negative prompt)

Append to every generation, verbatim:

```
NEGATIVE / STRICT EXCLUSIONS — absolutely no: Buy buttons, Sell buttons,
Order or Execute buttons or any trading execution UI; broker screens,
order tickets, position tables; profit-and-loss numbers, PnL curves,
percentage returns, dollar or currency amounts, account balances; any
implication of live trading; candlestick or OHLC trading charts as a main
visual; account IDs, usernames, e-mail addresses, API keys, tokens,
passwords, QR codes; real or readable note titles, real Notion pages or
databases, real Obsidian vault content, real file names; company logos or
trademarks of any kind (no Apple, Notion, Obsidian, OpenAI, Anthropic,
GitHub, ClickUp marks); app store badges; human faces, hands, bodies, or
silhouettes; watermarks; readable text of any language; screenshots of
real software.
```

Two notes beyond the required list: **no currency symbols/percentages** (a stray "+34%" in a generated frame is a fake return), and **no real-brand device chrome** — Scene 07 uses a *generic* glass slab phone, never an identifiable iPhone with Apple branding.

## 4. The 7 MellyCore AIOS scene prompts

Every prompt below implicitly ends with the STYLE block (§2) and EXCLUSIONS block (§3). Poster prompt = image generation; clip prompt = video generation using that scene's approved poster as start-image reference plus the G1 hero image as style reference. Scenes 02→03→04 are frame-chained (each clip's final frame = next clip's start image) to form one continuous scroll journey through the "platform layer"; the other scenes are standalone sections, so chaining is not used there.

### Scene 01 — Boot sequence *(poster-first; clip optional)*

```
POSTER — A dormant obsidian command core at the exact center of a dark
void: a faceted dark sphere wrapped in three thin concentric orbit rings,
all unlit except a single amber ember waking at its heart. Faint cyan
circuitry traces spread outward across the floor plane like frost,
suggesting a system about to come online. Low-key lighting, deep shadows,
quiet anticipation.

CLIP — Same scene. The camera starts wide and slowly dollies in toward
the core. As it approaches, the amber ember brightens, the three orbit
rings light up one by one, and cyan circuit traces ripple outward in a
single calm wave. The move ends in a stable medium shot of the fully lit
core, holding still. Slow and ceremonial, like a machine taking its
first breath.
```

### Scene 02 — Obsidian galaxy *(poster + clip; signature scene)*

```
POSTER — A vast knowledge galaxy inside a dark void: hundreds of small
luminous cyan-teal nodes connected by hair-thin glowing threads, forming
organic clusters like constellations of linked notes. A brighter amber
core cluster sits slightly off-center as the gravitational heart. Depth
of field makes near nodes soft and distant clusters faint, giving real
parallax depth. Feels like standing inside a living second brain.

CLIP — The camera drifts laterally through the node field in one slow,
weightless glide, passing between clusters so threads slide past with
parallax. Nodes gently pulse as connections light up along their threads
toward the amber core cluster. The move ends framing the amber core with
the galaxy receding behind it. Calm, deep, meditative motion.
```

### Scene 03 — Model Hub constellation *(poster-first; clip optional, chained after 02)*

```
POSTER — Starting from a bright amber core cluster in the foreground
(matching the end of the galaxy scene): a ring of five distinct larger
orbs orbits the core at equal spacing, each orb a different cool hue of
the same glass-and-light material, connected to the core by clean curved
light conduits. The orbs represent interchangeable AI models — abstract
spheres only, no logos, no text. Symmetrical, calm, engineered.

CLIP — One slow 120° orbital camera move around the constellation. As
the camera circles, light pulses travel along the conduits from the
amber core to each orb and back, one at a time, like requests being
routed. Ends with the constellation centered and settled. Smooth
mechanical elegance, clockwork calm.
```

### Scene 04 — Context Gateway flow *(poster + clip, chained after 03)*

```
POSTER — A luminous gateway structure: two tall thin amber light pillars
forming a portal frame in the void, with a horizontal stream of soft
cyan light-packets flowing through it in a disciplined line. Before the
gate the stream is loose and scattered; after passing through it emerges
ordered, evenly spaced, and gently color-shifted toward warm white —
context entering, structured knowledge leaving. Strong central
one-point perspective.

CLIP — The camera tracks slowly alongside the packet stream toward the
gate, passes through the portal frame together with the packets in one
continuous move, and eases to a stop on the far side, watching the
ordered stream continue into the distance. A single amber scan-line
sweeps each packet as it crosses the threshold. Precise, calm,
processional motion.
```

### Scene 05 — Notion dashboard layer *(poster only in v1)*

```
POSTER — An abstract planning surface floating in the void at a gentle
isometric angle: translucent frosted-glass panels arranged in a tidy
grid, some panels holding blurred glyph-like shapes suggesting lists and
boards — deliberately unreadable. Thin cyan connector lines run between
panels; one amber panel sits at the top as the focal anchor. Everything
is clearly an abstract homage to a workspace, not a real product
screenshot. Soft even lighting, shallow depth of field.
```

*(Optional later clip: slow top-down crane descent as panels assemble into the grid one by one.)*

### Scene 06 — MellyTrade Market Orbit

See §6 below — the product-layer showpiece.

### Scene 07 — iOS/PWA command surface *(poster only in v1)*

```
POSTER — A generic matte-glass smartphone slab (no brand, no buttons, no
notch detail) standing upright in the void at a slight three-quarter
angle, its screen showing only abstract light: the miniature amber
command core from the hero image glowing at the screen's center with two
thin orbit rings. Soft reflections of cyan node-light on the glass body.
The composition is vertical-friendly: the phone occupies the center
third, so a 9:16 crop from this 16:9 frame works for mobile posters.
Quiet, premium, minimal.
```

*(Optional later clip: 15° slow parallax turn of the slab while the mini-core pulses once.)*

## 5. Portfolio website hero prompt

```
HERO IMAGE (generate FIRST — this is G1, the master reference for the
entire pack) — "The MellyCore Command Core": a dark, cinematic wide shot
of a faceted obsidian sphere hovering at the center of a quiet void,
wrapped in three thin concentric luminous orbit rings tilted at
different angles. The innermost ring glows warm amber — the guardrail.
The outer rings glow cool cyan-teal, carrying tiny bright nodes like
satellites of knowledge. Below the core, a faint reflective floor plane
catches the glow. Fine particles drift in the light. The image reads as
"an AI command center, calm and under control" — engineered, safe,
precise. Nothing playful, nothing chaotic. Composition leaves the right
third of the frame calmer/darker so a website headline can sit over it.

HERO CLIP (only after the image is approved; use the hero image as the
start frame) — One slow, perfectly smooth 30° orbital drift around the
command core. The rings rotate at slightly different speeds; node lights
pulse gently; particles drift. No dramatic events, no flares, no
build-up — the motion should be ignorable behind headline text. The
final frame closely resembles the start frame so the clip loops cleanly.
```

Honesty guard for this asset: it decorates the hero **behind** the copy approved in `homepage_copy_001.md` — it must never be presented as a screenshot of a real product, and no generated frame may be captioned as MellyCore "running."

## 6. MellyTrade Market Orbit prompt (Scene 06)

```
POSTER — "Market Orbit": an abstract market-intelligence observatory in
a dark void. At the center, a cluster of neutral cool-white asset nodes
— plain glowing spheres of varying sizes, deliberately generic, no
symbols, no tickers. Enclosing the entire cluster: one continuous,
unbroken warm AMBER GUARDRAIL RING, clearly a boundary that nothing
crosses — the visual statement that this system observes and never
executes. Around and between the nodes: soft translucent VOLATILITY
CLOUDS like slow nebulae, and thin cyan LIQUIDITY STREAMS flowing in
smooth laminar arcs between node groups. Far outside the guardrail, a
faint, huge MACRO TIMELINE RING circles the whole scene like an orrery's
outermost track, marked only by dim evenly spaced tick-glows — no
numbers, no dates. Mood: a calm observatory, watching, simulated,
advisory — never a trading floor. No charts, no candles, no prices.

CLIP — The camera begins outside the macro timeline ring and performs
one slow, continuous push-in that crosses the timeline ring, drifts
through a volatility cloud (which parts softly around the lens), and
settles just OUTSIDE the amber guardrail ring, looking in at the asset
nodes — the camera itself respects the boundary and never crosses it.
Liquidity streams flow steadily; nodes drift in slow orbital motion;
the guardrail ring stays constant and unbroken throughout. Ends holding
on the composed observatory view. Slow, weightless, observational.
```

The camera stopping *at* the guardrail and never crossing it is the whole story of MellyTrade told in one move: intelligence, not execution.

## 7. Credit-saving strategy

1. **One master image funds everything.** G1 is the only asset that justifies 2–3 attempts by default. Every scene poster inherits its palette/material via image reference, so consistency comes free (the packs' "consistency beats quality" rule).
2. **Poster-first is the release gate, not a fallback.** The `/aios` slice ships fully working on 7 static posters + 1 portfolio poster ≈ 8 image generations total. Clips are progressive enhancement.
3. **Takes budget:** 2–3 takes — G1 hero image, portfolio hero clip, Scene 02 clip, Scene 06 clip (the four "wow carriers"). **One take only** — Scenes 01, 03, 04 clips and all remaining posters; accept the first usable result. **Zero takes now** — clips for 05 and 07.
4. **Reuse before regenerate.** Portfolio hero poster = regrade/crop of G1. Scene 07's phone screen = miniature of G1. Scene 03's core = Scene 02's final-frame amber cluster. Three assets, one generation.
5. **Never 4K, never audio, never >8s.** Std mode 1080p throughout; the site serves compressed ~720p webm/mp4 anyway. Compress everything for web after generation (~90% size cut per the pack).
6. **Kill criteria per attempt:** discard immediately (don't iterate) if a frame contains readable text, anything resembling a candlestick chart, a broken guardrail ring, or logo-like marks — those violate §3 and no amount of regrading fixes them.

## 8. What to generate now vs later

**Now (on explicit go-ahead — nothing has been generated):**
- G1 master hero image (up to 3 attempts, keeper picked by Mateusz)
- Portfolio hero poster derived from G1
- Posters for Scenes 02, 06, 04 (one attempt each)

That is ≤ 6 image generations and it makes both the portfolio hero and the three core `/aios` sections shippable poster-first.

**Later, wave 2 (after posters are live in the W1 slice):** portfolio hero clip; Scene 02 and 06 clips (2 takes each); Scene 04 clip (1 take); posters for 01, 03, 05, 07.

**Later, wave 3 (optional polish, only if credits are comfortable):** clips for 01 and 03 with frame-chaining 02→03→04; parallax clips for 05/07; a single 9:16 mobile-hero variant.

## 9. Implementation notes (for the future task — no code touched in this task)

- **Mapping to the W1 slice:** posters/clips drop into the existing `mellycore-visual-card panel-glass` slots in `MellyCorePage.tsx` — Scene 02 replaces the CSS `mellycore-galaxy-grid`, the hero asset sits behind/replaces the CSS `mellycore-command-core` orbits, Scene 06 anchors the `#safety` section. Route architecture (`/aios` → `MellyCorePage`) unchanged.
- **Poster-first loading:** `<video poster="…" preload="none" muted playsinline loop>` with the poster as an eagerly-loaded optimized image; video lazy-loads on intersection. First paint never waits on video.
- **Reduced motion:** `prefers-reduced-motion: reduce` → posters only, videos never mount.
- **Mobile-first (iPhone 13, 390×844):** posters exported with a 9:16-safe center crop (Scene 07 is composed for this); consider serving posters only below ~768px to protect data and battery.
- **No WebGL/Three.js, no new dependencies** — plain `<video>`/`<img>` and existing CSS. Scroll-scrub canvas sequencing from the source packs is explicitly *not* adopted for W1; it is a heavy-dependency pattern and the static slice does not need it.

---

## Related documents

- [portfolio_hub_spec_001.md](portfolio_hub_spec_001.md) — portfolio site master spec
- [homepage_copy_001.md](homepage_copy_001.md) — approved homepage copy (hero visual sits behind this copy)
- [case_study_structure_001.md](case_study_structure_001.md) — case study template (image slots)
- [implementation_backlog_001.md](implementation_backlog_001.md) — build backlog (asset work = PF-030/PF-031)
