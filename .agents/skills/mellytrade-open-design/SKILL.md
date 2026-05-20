# mellytrade-open-design

Use this skill for Open Design, terminal UI, dashboard, AI Workspace, paper sandbox, audit rail, demo screenshots, frontend polish, or design system work for MellyTrade.

## Operating Rules

- Inspect the existing frontend before coding.
- Reuse existing components, layouts, tokens, and utility patterns.
- Keep all trading UI read-only and display-only.
- Use GET-only clients for read paths.
- Preserve the safety badges and audit-first language.
- Do not add order controls, trade execution controls, or live trading entry points.
- Do not add POST, PUT, PATCH, or DELETE trading clients.
- Do not expose secrets, credentials, or account IDs.

## Open Design Workflow

- Treat Open Design as the source for prototype exploration and HTML review.
- External Open Design workspace: `C:\AI\MellyTrade_Workspace\04_Tools\open-design`
- MellyTrade design system: `C:\AI\MellyTrade_Workspace\04_Tools\open-design\design-systems\mellytrade-terminal`
- Review generated screens before porting ideas into the frontend.
- Port only approved visual patterns, not execution behavior.

## Safety Constraints

- `autotrade` stays false.
- `dry_run` stays true.
- live orders remain blocked.
- max risk per trade stays `<= 1%`.
- no live execution UX.
- no broker connect-live call to action.
- no Buy/Sell/Execute/Place Order controls.

## Preferred Output Shape

- For design work, produce reviewable HTML, screenshots, or documentation first.
- For frontend implementation work, keep changes narrow and preserve existing terminal shell behavior.
- When in doubt, choose the safer display-only interpretation.
