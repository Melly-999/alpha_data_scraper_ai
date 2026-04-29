# Portfolio Summary — MellyTrade

MellyTrade is an AI-assisted trading workstation built with FastAPI, React and TypeScript, broker adapter architecture, and paper-trading focused execution workflows.

Highlights:
- Implemented IBKR Paper Adapter support with safe disconnected mode and dry-run reporting
- Added broker health and account visibility to the dashboard
- Built local Windows run tooling and smoke-test workflows
- Preserved strict safety defaults with live trading blocked
- Kept MT5 integration paths available without exposing live execution controls

Tech stack:
Python, FastAPI, React, TypeScript, pytest, mypy, flake8, IBKR Paper, MT5 integration path.

Safety-first note:
The current project posture is research and paper-trading only. Live trading remains blocked by default.
