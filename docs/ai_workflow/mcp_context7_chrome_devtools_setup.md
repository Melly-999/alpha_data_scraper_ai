# MCP, Context7, and Chrome DevTools Setup

This repository uses MCP tooling as **development-time assistance**, not as a
trading or execution path.

## What MCP means here

MCP lets coding agents connect to approved tools for documentation lookup and
browser verification. In MellyTrade, MCP is limited to:

- current library and framework docs lookup
- browser/UI smoke checks
- console, network, layout, and performance inspection

It does **not** grant permission to trade, place orders, connect live, or
weaken safety rules.

## Why Context7 is used

Use Context7 before coding against external libraries or framework APIs. It is
the source for current docs when working with:

- FastAPI
- Pydantic v2
- React
- Vite
- Supabase
- Playwright and browser tooling

This reduces guesswork and avoids relying on stale memory when APIs change.

## Why Chrome DevTools MCP is used

Use Chrome DevTools MCP for browser verification when frontend files change.
It helps inspect:

- console errors
- failed network calls
- layout and rendering issues
- basic performance traces

It is a smoke-check tool, not a replacement for tests.

## Windows PowerShell setup examples

### Claude Code

```powershell
npx ctx7 setup --claude
claude mcp add chrome-devtools --scope user npx chrome-devtools-mcp@latest
```

### Codex CLI

```powershell
npx ctx7 setup --opencode
codex mcp add chrome-devtools -- npx chrome-devtools-mcp@latest
```

### VS Code

```powershell
npx ctx7 setup --cursor
```

Use the generated MCP configuration with the VS Code workflow in this repo.
Keep the setup in your local environment and do not hard-code private paths.

### OpenCode

```powershell
npx ctx7 setup --opencode
```

## Context7 examples

```powershell
npx ctx7 setup --claude
npx ctx7 setup --opencode
npx ctx7 setup --cursor
```

## Chrome DevTools MCP examples

```powershell
claude mcp add chrome-devtools --scope user npx chrome-devtools-mcp@latest
codex mcp add chrome-devtools -- npx chrome-devtools-mcp@latest
```

## Secrets and API keys

Store API keys outside git. Use local environment variables, secret managers, or
other non-committed local configuration.

### Do not commit secrets

- no API keys
- no tokens
- no passwords
- no account IDs
- no credentials
- no private local paths

## Troubleshooting

- `npx not found`: install Node.js/npm, then reopen PowerShell so `npx` is on
  `PATH`.
- `MCP server unavailable`: confirm the command runs locally and that the
  package name is correct.
- `browser not launching`: verify Chrome is installed and that the MCP server
  is allowed to open a browser window.
- `stale docs`: rerun Context7 setup before changing code that depends on an
  external API.
- `agent using memory instead of docs`: stop and look up the current docs before
  patching code.

## Safety reminder

This setup is for documentation lookup and browser verification only. It must
never be used to enable trading, execution, or live broker access.
