# Free Claude Code Setup (Local AI Coding Worker)

This document describes how to run **Claude Code** against a free / self-hosted
LLM backend (OpenRouter free tier or a local Ollama model) as an AI coding
worker for the `alpha_data_scraper_ai` repository.

> ⚠️ **Safety first.** This setup is for **code editing and review only**. It
> must never be used to enable live trading, change risk caps, expose secrets,
> or modify execution behavior. See [Safe Usage Rules](#safe-usage-rules).

---

## What is `free-claude-code`?

`free-claude-code` (community project, typically cloned to
`C:\AI\free-claude-code`) is a small **local FastAPI proxy** that speaks the
Anthropic Messages API on one side and forwards requests to a backend of your
choice on the other (OpenRouter, Ollama, or any OpenAI-compatible gateway).

The official Claude Code CLI is then pointed at the proxy via the
`ANTHROPIC_BASE_URL` env variable. Claude Code believes it is talking to
Anthropic; in reality it is talking to your local proxy, which routes the
request to a free or local model.

---

## Recommended use in MellyTrade

Use the free Claude Code worker for:

- Read-only **code review** and static analysis
- Drafting **frontend-only** patches (Terminal V1, charts, layout)
- Drafting **GET-only / read-only** backend endpoints
- Generating **unit tests**
- Producing **documentation updates**
- **PR readiness** checklists and **safety audits**

Do **not** use it for:

- Anything that changes `autotrade`, `dry_run`, `read_only`, or risk caps
- Anything that adds order-execution routes or buttons
- Anything that touches MT5 / IBKR / Alpaca trading code paths
- Anything that handles real secrets

---

## Windows setup

### 1. Prerequisites

- Windows 10/11
- Python 3.11 or 3.12 (`python --version`)
- Node.js LTS (for the official Claude Code CLI)
- Git
- The proxy repo cloned to `C:\AI\free-claude-code`

```powershell
git clone https://github.com/<your-fork>/free-claude-code C:\AI\free-claude-code
cd C:\AI\free-claude-code
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Install Claude Code CLI

```powershell
npm install -g @anthropic-ai/claude-code
claude --version
```

---

## OpenRouter setup (recommended free path)

1. Create a free account at https://openrouter.ai/.
2. Generate an API key (`sk-or-...`).
3. Pick a free model, e.g. `deepseek/deepseek-r1-0528:free`.
4. Configure the proxy via environment variables (see
   `docs/dev/free_claude_code.env.example`).

OpenRouter is the simplest path: no GPU needed, decent free quotas, many
models to choose from.

---

## Ollama setup (fully local)

1. Install Ollama: https://ollama.com/download (Windows installer).
2. Pull a coding model:

   ```powershell
   ollama pull qwen2.5-coder:7b
   # or
   ollama pull deepseek-coder-v2:16b
   ```

3. Confirm the local API is reachable:

   ```powershell
   curl http://127.0.0.1:11434/api/tags
   ```

4. Point the proxy at the Ollama base URL (`http://127.0.0.1:11434`) and
   pick a model name like `ollama/qwen2.5-coder:7b`.

Fully local. No data leaves the machine. Slower than OpenRouter unless you
have a strong GPU.

---

## Claude Code env variables

Claude Code reads these from the environment when it starts. Set them in the
PowerShell session **before** launching `claude`:

| Variable | Purpose |
|---|---|
| `ANTHROPIC_AUTH_TOKEN` | Any non-empty placeholder token (e.g. `freecc`). The proxy ignores it. |
| `ANTHROPIC_BASE_URL` | `http://127.0.0.1:8082` — the local proxy. |
| `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY` | `1` — lets Claude Code list models from the gateway. |
| `OPENROUTER_API_KEY` | Your OpenRouter key (only if using OpenRouter). |
| `MODEL` | Routed model id, e.g. `open_router/deepseek/deepseek-r1-0528:free`. |
| `LOG_RAW_API_PAYLOADS` | `false` — keep request bodies out of disk logs. |
| `LOG_RAW_SSE_EVENTS` | `false` — keep streamed tokens out of disk logs. |
| `ALLOWED_DIR` | Restrict file edits to this absolute path. |
| `CLAUDE_WORKSPACE` | Sandbox folder Claude Code may write to. |

A copy-pastable starter is in
[`free_claude_code.env.example`](./free_claude_code.env.example). It contains
no real secrets.

---

## Safe usage rules

These rules apply **every** time you run the free Claude Code worker against
this repo:

1. **No live trading.** `config.json -> autotrade.enabled` must remain `false`.
2. **Dry run on.** `config.json -> autotrade.dry_run` must remain `true`.
3. **Read-only where present.** Do not flip `read_only` to `false`.
4. **No execution routes.** Do not add new `/orders`, `/trade`, `/execute`,
   or broker-write endpoints.
5. **No order buttons.** Do not add UI controls that submit live orders.
6. **No secrets in code.** API keys live in `.env` (git-ignored) only.
7. **Risk cap stays ≤ 1%.** Do not raise `max_risk` / per-trade risk above 1%.
8. **No MT5/IBKR execution changes.** Treat `mt5_trader.py`, `brokers/`,
   `execution/`, and `execution_service.py` as read-only.
9. **No pushes without approval.** Local commits are fine; never `git push`
   unless the human operator says so.
10. **Prefer docs / scripts / config templates** over invasive code changes.

The model **does not** override these rules — you do. Reject any patch that
violates them, no matter how confidently it was suggested.

---

## Example prompts

Pre-baked, safety-aware prompts live in
[`ai_worker_prompt_pack.md`](./ai_worker_prompt_pack.md). Quick taste:

- *Safe code review of changed files since `main`*
- *Frontend-only Terminal V1 patch (no backend writes)*
- *Backend GET-only endpoint patch (read-only)*
- *Test generation for a single module*
- *PR readiness checklist*
- *Security & safety audit of the diff*
- *Documentation update for an existing module*

Always paste the **Safety preamble** from the prompt pack at the top of every
session.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ECONNREFUSED 127.0.0.1:8082` | Proxy not running | Run `scripts/start_free_claude_code_proxy.ps1` |
| `401 invalid_api_key` | Empty / wrong token | Set `ANTHROPIC_AUTH_TOKEN=freecc` |
| `model not found` | Bad `MODEL` id | Use the exact id printed by `/models` in the proxy |
| Claude Code edits files outside the repo | `ALLOWED_DIR` not set | Export `ALLOWED_DIR` before launching `claude` |
| OpenRouter `429` | Free quota exhausted | Switch model, slow down, or move to Ollama |
| Streaming hangs in PowerShell | Antivirus interfering | Whitelist `python.exe` and the proxy port |
| Logs contain prompts/keys | Raw logging enabled | Set `LOG_RAW_API_PAYLOADS=false` and `LOG_RAW_SSE_EVENTS=false` |

---

## Security notes (secrets and logs)

- **Never commit `.env` files.** `.env` is git-ignored; keep it that way.
- **Never paste API keys into prompts.** The proxy already has them.
- **Keep raw logging disabled.** `LOG_RAW_API_PAYLOADS=false` and
  `LOG_RAW_SSE_EVENTS=false` prevent prompt + key leakage to disk.
- **Rotate keys** if you ever suspect a leak (OpenRouter, Anthropic, MT5,
  NewsAPI). `secrets_manager.py` reloads from env on next run.
- **Treat third-party model outputs as untrusted.** Always read the diff
  before applying.
- **No real broker credentials in prompts.** If a model asks for MT5 login,
  refuse — production code already loads them from `secrets_manager.py`.

---

**Last updated**: 2026-05-08
