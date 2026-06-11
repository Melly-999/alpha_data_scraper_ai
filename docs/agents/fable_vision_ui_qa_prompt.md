# Fable 5 Vision / UI QA Prompt — MellyTrade

Reusable copy-paste prompt for screenshot and UI QA with Claude Code /
Fable 5 on `alpha_data_scraper_ai`. Provide screenshots (or a local preview
URL the agent can drive) and the surfaces under review, then paste the block.

See also: [fable_run_contract.md](fable_run_contract.md) — especially the
privacy rules for screenshots.

---

## Copy-paste prompt

```text
TASK: Vision / UI QA review for MellyTrade surfaces.

ROLE: You are a senior product designer and frontend reviewer for an
institutional, safety-first fintech terminal. Tone of the product: dark
terminal aesthetic, premium B2B, read-only / paper-sandbox / advisory-only.

INPUTS:
<list the screenshots, preview URL, or routes under review, e.g.
/terminal, /mobile, /brokers, splash, PWA install view>

REVIEW DIMENSIONS — cover every one that the provided evidence supports:

1. Institutional terminal UI — hierarchy, density, alignment, panel
   structure, dark palette consistency (#070A0D / #10151B / #161C23 family,
   orange #F27A4D and amber #D6A84F accents used sparingly).

2. Portfolio / risk dashboard — readability of tables, charts, and risk
   posture; display-only framing is visible; no actionable order elements.

3. Mobile / PWA / iPad — layout at narrow and tablet widths, touch target
   size, sticky header behavior, safe-area handling, install experience.

4. Brand consistency — official identity is the MT monogram + MellyTrade
   wordmark; Melly Pet may appear only as a secondary/community element,
   never as the primary logo or in official chrome.

5. Accessibility — contrast of text on dark panels, focus visibility, alt
   text expectations, font sizes for terminal labels, color-only signaling.

6. Responsive layout — breakpoints, reflow, truncation strategy.

7. Overflow / cropping defects — clipped text, overlapping elements,
   horizontal scrollbars, cut-off badges or labels. Point to the exact
   screenshot region for every defect.

8. Copy / claim safety — every visible string must stay inside the
   read-only / demo / paper-sandbox / advisory-only framing. Flag any text
   that implies live trading, broker execution, profit, or advice.

CONSTRAINTS:
- Suggest frontend-only patches (CSS/layout/markup/copy). No backend
  changes, no API changes, no schema changes.
- Never suggest adding trading execution controls or buy/sell/order/execute
  UI of any kind.
- Preserve the read-only / demo / sandbox framing in every suggested copy
  change.
- Do not invent screenshot evidence. Describe only what is actually visible
  in the provided images or in a preview you actually drove this session.
- If screenshot evidence is missing for a requested surface, say exactly
  that and list what capture is needed — do not review it from memory.
- If you capture screenshots yourself, capture the rendered page/element
  only — never the desktop, other windows, or anything private.

OUTPUT FORMAT:
- Findings grouped by surface, each with severity (blocker / major / minor /
  nit), the evidence it is based on, and a concrete frontend-only fix.
- A short verdict per surface: ship / fix-first.
- A list of any dimensions skipped for lack of evidence, with what is needed.
```
