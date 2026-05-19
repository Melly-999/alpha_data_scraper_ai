# DEMO-004 LinkedIn Copy

## Short Post
Built a read-only AI trading terminal that looks like an institutional console and stays explicit about safety. It combines an advisory AI Workspace, Paper Sandbox visibility, and a live audit trail of read-only signals and broker posture. No live execution, no order buttons, no connect-live flow.

## Medium Post
I have been shaping MellyTrade into a safety-first AI trading workstation rather than a retail trading app.

The current terminal demo combines:
- an institutional dark UI
- a red-black terminal frame
- an AI Workspace for advisory-only analysis
- Paper Sandbox Preview and Activity/Audit Rail visibility
- broker posture and risk state shown as read-only status

The important part is not just the visual polish. The product is designed to be explicit about what it cannot do:
- no live trading
- no order placement
- no broker execution controls
- no connect-live UX
- no hidden automation

This is the kind of UX I want for serious market tooling: clear, audited, conservative, and impossible to confuse with a live trading screen.

## Technical Post
Shipped a read-only terminal demo with a safety-first architecture:
- React + Vite terminal shell
- FastAPI backend
- GET-only paper sandbox preview/history surfaces
- Paper Sandbox Activity/Audit Rail
- conservative risk posture surfaced in the UI
- local smoke validation for terminal demo flows

The demo is intentionally not a trading automation claim. It is a supervised, read-only workstation with explicit degraded states, audit-first messaging, and no live execution path.

