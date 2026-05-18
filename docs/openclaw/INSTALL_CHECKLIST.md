# OpenClaw Install Checklist — MellyTrade Read-Only Operator

> **Primary path:** WSL2 on Windows  
> **Alternative:** Windows PowerShell (noted where different)  
> **Primary channel:** Discord (phone / Discord mobile app)

---

## Prerequisites

- [ ] Windows 11 with WSL2 enabled (`wsl --version` shows WSL 2)
- [ ] Python 3.10+ available in WSL2 (`python3 --version`)
- [ ] Git configured in WSL2 (`git config --global user.name` returns your name)
- [ ] Docker Desktop running and accessible from WSL2 (`docker ps`)
- [ ] Discord account with access to your private server/category

---

## 1. Install OpenClaw

> Verify against [OpenClaw's official documentation](https://github.com/openclawai/openclaw)
> before running — these steps are generic and may need to be adjusted for the current
> release.

### WSL2 (recommended)

```bash
# Clone or install OpenClaw per its official docs
# Example — replace with the actual install command from OpenClaw docs:
pip install openclaw   # or: pipx install openclaw
```

### Windows PowerShell (alternative)

```powershell
# If not using WSL2:
pip install openclaw
# Or follow the Windows-native install from OpenClaw docs
```

- [ ] OpenClaw binary is on PATH (`openclaw --version`)

---

## 2. Configure OpenClaw

```bash
# Initialise a local config (do not commit this file)
openclaw init

# Edit ~/.openclaw/config.yaml (or the path OpenClaw uses)
# Set:
#   gateway.bind = 127.0.0.1   ← local only, never 0.0.0.0
#   skill_path = /path/to/alpha_data_scraper_ai/skills/mellytrade-operator
```

> **Never** set `gateway.bind = 0.0.0.0` without an auth layer + VPN.

- [ ] Config file created
- [ ] Gateway is bound to `127.0.0.1` (local only)
- [ ] Skill path points to `skills/mellytrade-operator/SKILL.md`

---

## 3. Validate Installation

```bash
openclaw doctor
```

Expected: all checks green. If any check fails, resolve before continuing.

```bash
openclaw gateway status
```

Verify:
- [ ] Gateway binds to `127.0.0.1` only (not `0.0.0.0` or a public IP)
- [ ] No secrets are printed in the status output
- [ ] No trading execution tools are listed as available
- [ ] Skill `mellytrade-operator` is loaded

---

## 4. Discord Mobile Setup (Primary Channel)

### 4a. Create your private Discord server or private category

- [ ] Create a **private Discord server** (or a private category in an existing server)
- [ ] Name it something not publicly discoverable (e.g. `mellytrade-private`)

### 4b. Create private channels

- [ ] `#mellytrade-ops` — status cockpit (daily driver from phone)
- [ ] `#mellytrade-alerts` — safety/CI/advisory signal alerts
- [ ] `#mellytrade-dev` — PRs, validation, Codex/Claude Code prompts
- [ ] `#mellytrade-reports` — daily/weekly summaries

### 4c. Create and configure the Discord bot

- [ ] Create a Discord application and bot at [discord.com/developers](https://discord.com/developers/applications)
- [ ] Generate bot token — **store it only in a local environment variable or secure
      secrets manager, never in docs, repo, chat, issues, logs, or screenshots**
- [ ] Set bot permissions: Read Messages, Send Messages, Embed Links only
- [ ] Do **not** grant Administrator permission
- [ ] Restrict bot to the private server/channels only
- [ ] Configure OpenClaw to use this bot according to OpenClaw's Discord integration docs
- [ ] Set the Discord token in your local environment (example only — adapt to OpenClaw):

```bash
export OPENCLAW_DISCORD_TOKEN="<your-token>"   # set in shell profile, not in code
```

```powershell
# PowerShell alternative:
$env:OPENCLAW_DISCORD_TOKEN = "<your-token>"
```

### 4d. Test from phone (Discord mobile app)

- [ ] Open Discord mobile app on phone
- [ ] Navigate to `#mellytrade-ops`
- [ ] Send: `@bot /status`  — verify a read-only status reply arrives
- [ ] Send: `@bot /safety` — verify safety validation result arrives
- [ ] Confirm the bot does **not** respond to write or execution commands
- [ ] Confirm no secrets, tokens, or account IDs appear in any reply

---

## 5. Optional: Tailscale / VPN for Remote Access

If the OpenClaw Gateway needs to be reachable outside localhost (e.g. from mobile data):

- [ ] Install Tailscale: `sudo apt install tailscale` (WSL2) or from [tailscale.com](https://tailscale.com)
- [ ] Connect: `sudo tailscale up`
- [ ] Bind OpenClaw Gateway to the Tailscale IP only — never to a public interface without auth

> **Warning:** Do not expose OpenClaw Gateway publicly without auth + VPN protection.
> Exposing the gateway to the open internet creates an unauthenticated AI execution surface.

---

## 6. Optional: Slack (Future Team Workflow)

Slack integration is optional and intended for future team workflow only. Configure per
OpenClaw's Slack connector docs when needed. All safety rules in this document apply
equally to Slack.

---

## 7. Optional: Telegram (Fallback Only)

Telegram may be used as a fallback notification channel if Discord is unavailable.
It is not the recommended default for this project. All safety rules apply.

---

## 8. Security Warnings

> **Do not expose OpenClaw Gateway publicly without authentication and VPN.**
>
> **Never paste Discord bot tokens, webhook URLs, guild IDs, or channel IDs into docs,
> repo, issues, chat messages, logs, or screenshots.**
>
> **Store tokens only in local environment variables or a secure secrets manager.**
> (e.g. system keychain, HashiCorp Vault, or OS-level credential manager)

---

## 9. Before Enabling Any Automation

Complete this checklist before scheduling any automated OpenClaw task:

- [ ] Repository is clean (`git status --short` returns nothing unexpected)
- [ ] Safety validation is green (`python scripts/validate_safety_config.py` → PASS)
- [ ] OpenClaw skill `mellytrade-operator` is installed and loaded
- [ ] Command allowlist has been reviewed (see `SECURITY_MODEL.md`)
- [ ] Discord bot permissions have been reviewed (no admin, no write)
- [ ] Bot has no write permissions to any trading runtime file
- [ ] Bot has no access to `.env` or any secrets store
- [ ] No execution or order tools are exposed
- [ ] No direct `main` push permission is granted via OpenClaw
- [ ] No force-push permission is granted via OpenClaw

---

## 10. Rollback / Uninstall

```bash
# Stop the gateway
openclaw gateway stop

# Remove the skill
rm -rf skills/mellytrade-operator   # repo-level only; does not affect runtime

# Uninstall OpenClaw
pip uninstall openclaw

# Revoke Discord bot token
# → Go to discord.com/developers → your application → Bot → Regenerate Token
# → Remove the old token from all environments immediately

# Remove local OpenClaw config
rm -rf ~/.openclaw
```

- [ ] Gateway stopped
- [ ] Discord bot token revoked and removed from all environments
- [ ] Local config removed
- [ ] Repository skill directory removed (docs-only, no runtime impact)

---

## Related Files

- [`docs/openclaw/README.md`](README.md) — architecture overview
- [`docs/openclaw/DAILY_USAGE.md`](DAILY_USAGE.md) — daily command examples
- [`docs/openclaw/SECURITY_MODEL.md`](SECURITY_MODEL.md) — threat model
- [`skills/mellytrade-operator/SKILL.md`](../../skills/mellytrade-operator/SKILL.md) — operator skill
