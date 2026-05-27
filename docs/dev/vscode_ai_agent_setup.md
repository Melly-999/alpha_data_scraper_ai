# VS Code and AI Agent Setup for MellyTrade

## 1. VS Code Profiles
- **MellyTrade Safe Dev**: Strict safe development profile with no runtime or trading code modifications, focused on safety and compliance.
- **AI Agent Lab**: Profile configured for experimenting with AI coding agents, includes relevant AI extensions.
- **Open Design Lab**: Profile for open design and code exploration with more flexible agent usage.
- **Docs/Demo Lab**: Profile for documentation and demonstrations.
- **Security Lab**: Profile focusing on security tools and audits.

## 2. What Each VS Code Extension Does
- **Core Python:** Python language support, linting, type checking, formatting (black, ruff, flake8, mypy).
- **Frontend:** ESLint, Prettier, Tailwind CSS support, auto rename tag for HTML/XML.
- **Git/GitHub:** GitLens, GitHub Pull Requests, GitHub Actions, Copilot extensions.
- **API/Test/DevOps:** REST client, Thunder Client, Playwright for testing, Docker, Remote Dev.
- **Docs:** Markdown All in One, Markdownlint, Mermaid diagrams, YAML support.
- **Productivity:** ErrorLens, TODO tree, path intellisense, dotenv, Peacock for color coding workspaces, Project Manager.
- **Optional:** Continue extension for AI continuation workflows.

## 3. Recommended Keyboard/Workflow
- PLAN → DIFF → TEST → SAFETY SCAN → DRAFT PR
- Use format on save to keep code consistent.
- Use ESLint/Prettier for consistent frontend styling.
- Use GitLens for commit history and changes.
- Use TODO tree for tracking tasks.
- Use Peacock for workspace color coding.

## 4. How to Run Backend
```powershell
py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

## 5. How to Run Dashboard
```powershell
cd mellytrade_v3/mellytrade/dashboard
npm run dev
```

## 6. How to Run Safety Checks
```powershell
py -3.11 scripts/validate_safety_config.py
py -3.11 -m pytest tests/app/test_openapi_forbidden_paths.py tests/app/test_safety_invariants.py -q
```

## 7. How to Use AI Agents Safely
- Workspace settings must never contain tokens or secrets.
- Copilot-chat appears built-in/installed; github.copilot install had conflict; manual check recommended in VS Code Accounts/Extensions.
- Plan your changes carefully and review diffs before applying.
- Never allow agents to touch trading or risk critical files without explicit prompt.

## 8. Workspace Secrets Policy
- Do not store tokens in `.vscode/settings.json`.
- Use VS Code User Settings, environment variables, or official secret stores for credentials.
- Sourcery tokens must be configured outside the repo.
- If a token appears in a chat, log, or repo file, rotate or revoke it.
- Never commit API keys, broker credentials, GitHub tokens, Claude/OpenAI keys, or MT5 credentials.
- Sourcery token removed; rotate/revoke the exposed token manually.

## 9. Agent Permissions
- Plan first, inspect diffs, never touch critical code, config or secrets without explicit prompt.
- Use separate branches/worktrees per task.

## 10. iPad Workflow
- iPad as dashboard/control panel.
- PC runs code.
- Use Tailscale, LAN for secure connect.

## 11. Safety Reminder
- Do not modify trading code or risk policy.
- autotrade=false
- dry_run=true
- read_only=true
- live_orders_blocked=true
- max_risk_per_trade<=1%

---

This document helps maintain a safe, consistent, and secure development environment when using AI-powered coding tools.
