# OpenClaw Security Model — MellyTrade

## Threat Model

| Threat | Description | Mitigation |
|---|---|---|
| Compromised Discord account | Attacker gains access to `#mellytrade-ops` and issues commands | Private server, 2FA on Discord account, minimal bot permissions |
| Leaked Discord bot token | Token exposed in logs, screenshots, docs, or repo | Store token only in local env vars; rotate immediately on exposure |
| Public Discord channel command injection | Commands sent from public channel reach the bot | Restrict bot to private server/channels only |
| Prompt injection | Malicious text in a Discord message tricks the agent into unsafe action | Command allowlist enforced at Gateway level; agent must refuse forbidden commands |
| Malicious prompt inside Discord message | User or attacker pastes a crafted message to unlock execution | Agent refuses any command that matches forbidden patterns; no execution tools loaded |
| Accidental log/screenshot exposure | Logs shown in Discord contain secrets or account IDs | Agent must never output secrets, tokens, .env values, account IDs, or broker credentials |
| Leaked token | Bot token or API key committed to repo or pasted in chat | Pre-commit hook (`.gitleaks` or similar); rotate on exposure |
| Accidental command execution | User sends an ambiguous message that the agent interprets as an execution command | Command allowlist; no execution tools registered in the skill |
| Public gateway exposure | OpenClaw Gateway bound to `0.0.0.0` and accessible from the internet | Bind to `127.0.0.1` only; use Tailscale/VPN for remote access |
| Unsafe repo writes | Agent modifies runtime files, config, or workflow YAML | Skill explicitly forbids all writes outside `docs/` and `skills/` |

---

## Permission Tiers

| Tier | Allowed | Examples |
|---|---|---|
| **Tier 0** | Read-only status and reporting | `git status`, `git log`, docker log tail, safety validation read |
| **Tier 1** | Local validation commands only | `validate_safety_config.py`, `pytest tests/app -q` |
| **Tier 2** | Draft GitHub issues/comments only | Prepare text for a GitHub issue — no automatic post without human confirmation |
| **Tier 3** | Docs-only file creation | New files under `docs/` only — never under app, backend, frontend, broker modules |
| **Forbidden** | All execution, broker mutation, secrets access, risk policy mutation | See forbidden list below |

---

## Recommended Command Allowlist

Only these commands (or functionally equivalent read-only variants) should be available
to the OpenClaw operator skill:

```bash
git status --short
git log --oneline -n 20
git diff --name-only
git diff --stat

python scripts/validate_safety_config.py
python -m pytest tests/app -q

docker compose logs --tail=200 trading-bot
```

No other shell commands should be executable via the OpenClaw operator skill.

---

## Forbidden Commands and Patterns

The following must never be executed or suggested as executable via OpenClaw:

```
# Git — write operations
git push origin main
git push --force
git push --force-with-lease
git commit --amend
git reset --hard
git rebase -i

# Secrets / environment
cat .env
type .env
Get-Content .env
echo $env:...
printenv
env | grep ...
python -c "import os; print(os.environ)"

# Config mutation
# (any script or command that sets autotrade.enabled=true)
# (any command that sets dry_run=false)
# (any modification to config.json, profiles/, risk policy)

# Broker / execution
# (any MT5, IBKR, or broker API call that places, modifies, or cancels orders)
# (any route that writes to execution endpoints)

# Secrets scanning output
# (any tool output that contains actual secret values, not just secret names)

# Docker mutation
docker exec ... (write operations)
docker restart trading-bot  # (without explicit human confirmation)
```

---

## Discord-Specific Mitigations

- Use a **private Discord server** or private category — never a public server.
- Grant bot **minimal permissions** only: Read Messages, Send Messages, Embed Links.
- **Never grant Administrator** permission to the bot.
- **Never paste bot tokens, webhook URLs, guild IDs, or channel IDs** into repo, docs,
  chat, issues, logs, or screenshots.
- Enforce the **command allowlist** at the OpenClaw Gateway level.
- **Register no execution tools** in the mellytrade-operator skill.
- Set **rate limits** on the bot to prevent alert spam from runaway triggers.
- If a security incident occurs, **disable the bot immediately** in Discord Developer
  Portal before investigating.
- **Rotate the Discord bot token** if it is ever exposed in any medium.

---

## Incident Response

If a security incident is detected (unexpected command execution, exposed token, suspected
prompt injection, bot responding to commands from wrong channels):

1. **Disable the Discord bot** immediately in Discord Developer Portal (disable application or revoke token).
2. **Stop OpenClaw Gateway**: `openclaw gateway stop`.
3. **Rotate all exposed tokens** (Discord bot token, any API keys that may have been in scope).
4. **Inspect OpenClaw logs** for the sequence of commands that were executed.
5. **Inspect Discord audit log** and channel history for the suspicious message context.
6. **Run `git status` and `git diff`** to confirm no repo files were modified.
7. **Run safety validation**: `python scripts/validate_safety_config.py`.
8. **Open a postmortem issue** in the repository documenting: what happened, what was
   affected, what was rotated, and what mitigations are being added.

---

## Final Principle

> Discord is only a **control surface for read-only operations**, not an execution terminal.
>
> No command received via Discord should ever result in a broker order, a config mutation,
> a secret being exposed, or a runtime file being modified.
>
> If there is any doubt about whether a requested action is safe, the agent must stop,
> refuse, and provide a read-only alternative for human review.

---

## Related Files

- [`docs/openclaw/README.md`](README.md) — architecture and safety contract
- [`docs/openclaw/INSTALL_CHECKLIST.md`](INSTALL_CHECKLIST.md) — installation
- [`docs/openclaw/DAILY_USAGE.md`](DAILY_USAGE.md) — daily usage examples
- [`skills/mellytrade-operator/SKILL.md`](../../skills/mellytrade-operator/SKILL.md) — operator skill
