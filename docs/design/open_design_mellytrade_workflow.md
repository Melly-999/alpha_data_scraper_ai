# Open Design + MellyTrade Workflow

This repository uses Open Design for safe prototype exploration and Codex for controlled implementation.

## External Open Design Location

Open Design is installed outside this repo:

`C:\AI\MellyTrade_Workspace\04_Tools\open-design`

## Active MellyTrade Design System

The active design system is:

`C:\AI\MellyTrade_Workspace\04_Tools\open-design\design-systems\mellytrade-terminal`

It defines the MellyTrade Institutional Terminal visual direction: premium red-black, read-only, dry-run, advisory-only, and audit-first.

## Start Open Design

Use these commands from PowerShell:

```powershell
cd C:\AI\MellyTrade_Workspace\04_Tools\open-design
pnpm tools-dev start web
```

If the web process is already running, use `pnpm tools-dev status web` to inspect it.

## Generate Prototype Screens

1. Open the MellyTrade design system prompt file:
   `C:\AI\MellyTrade_Workspace\04_Tools\open-design\design-systems\mellytrade-terminal\PROMPT_TERMINAL_SCREEN.md`
2. Use it to generate a 1366x768 terminal screen prototype.
3. Keep the output as a single HTML artifact with realistic placeholder data.
4. Ensure the screen contains the required safety badges and no execution controls.

## Review Before Porting

Before moving anything into the frontend:

1. Inspect the generated HTML or screenshot.
2. Verify that the screen is read-only.
3. Verify that no live trading, execution, or order placement controls exist.
4. Confirm that the safety badges are visible.
5. Check that accessibility labels and focus states are present.

## Manual Porting Rules

- Port only approved UI ideas into the frontend.
- Do not copy the generated artifact wholesale.
- Reuse existing React components and styling primitives where possible.
- Preserve the terminal shell, audit-first UX, and display-only broker cards.
- Keep the frontend GET-only for trading reads.

## Validation Checklist

- Safety posture still holds: `autotrade=false`, `dry_run=true`, live orders blocked, max risk `<= 1%`.
- No order buttons or execution controls were added.
- No POST, PUT, PATCH, or DELETE trading clients were introduced.
- No secrets or account IDs were added.
- Existing frontend behavior remains stable.

## Forbidden Changes Checklist

- No backend runtime changes.
- No workflow changes.
- No broker execution code.
- No MT5 or IBKR execution code.
- No trading config changes.
- No secrets or credentials.
- No live trading UX.
- No new order-entry controls.

## Exact Next Prompt for Frontend Porting

Use this prompt after reviewing an Open Design prototype:

> Port only the approved visual patterns from the reviewed Open Design prototype into the existing MellyTrade frontend. Keep the trading UI read-only and display-only, preserve safety badges, preserve audit-first structure, reuse existing components, and do not add any live trading, order placement, broker execution, or POST/PUT/PATCH/DELETE trading clients.
