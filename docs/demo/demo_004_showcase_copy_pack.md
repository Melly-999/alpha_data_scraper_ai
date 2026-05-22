# DEMO-004 Showcase Copy Pack

## Project One-Liner
MellyTrade Terminal is a read-only, safety-first AI trading workstation that combines an institutional terminal UI, paper sandbox visibility, and explicit risk gating without exposing live execution controls.

## Short Product Description
This terminal is designed for supervised market analysis and audit-first decision support. It presents market context, AI workspace status, paper sandbox evidence, and broker posture in a dark institutional shell while preserving a strict no-live-trading posture.

## What the Terminal Demonstrates
- Red-black institutional terminal frame
- AI Workspace with advisory-only analysis
- Paper Sandbox Preview and Activity/Audit Rail
- Signal Quality Summary card verified after SIG-004B: read-only, dry-run-only, risk-blocked, human-review-required quality snapshot with no execution controls.
- Read-only broker and risk posture
- GET-only paper sandbox smoke flow
- Clear safety badges for read-only, dry-run, and live-orders-blocked states

## Safety-First Architecture Summary
- Backend and frontend both communicate a strict read-only posture
- Paper sandbox endpoints are consumed as GET-only status surfaces
- No order placement, execution, or connect-live UX is exposed
- Risk policy remains visible and conservative
- Degraded and fallback states are explicit so users can see when services are unavailable without losing safety context

## Key Screenshots and What Each Shows
- `01_dashboard_home_1366x768.png` - dashboard home, safety shell, and terminal entry context
- `02_terminal_ai_workspace_1366x768.png` - AI Workspace hero shot and advisory-only cockpit
- `03_terminal_paper_sandbox_activity_1366x768.png` - Paper Sandbox Preview plus Activity/Audit Rail
- `04_signals_readonly_1366x768.png` - read-only signals view and decision support context
- `05_brokers_readonly_1366x768.png` - broker posture snapshot with execution denied
- `06_portfolio_readonly_1366x768.png` - portfolio read-only presentation for recruiters and portfolio pages

## Suggested Ordering for Portfolio Presentation
1. `02_terminal_ai_workspace_1366x768.png`
2. `03_terminal_paper_sandbox_activity_1366x768.png`
3. `05_brokers_readonly_1366x768.png`
4. `04_signals_readonly_1366x768.png`
5. `06_portfolio_readonly_1366x768.png`
6. `01_dashboard_home_1366x768.png`

## What Not to Claim
- Do not claim live trading
- Do not claim automated execution
- Do not claim broker connectivity that enables orders
- Do not claim guaranteed profits or alpha
- Do not claim that safety controls replace human review
- Do not show or mention secrets, account IDs, or credentials

