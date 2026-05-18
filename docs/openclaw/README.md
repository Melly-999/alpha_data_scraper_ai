# OpenClaw — MellyTrade Read-Only Operator Layer

## What Is OpenClaw in This Context?

OpenClaw is an open-source local AI agent gateway. In the MellyTrade project it is used
exclusively as a **read-only operator layer** — a mobile-accessible control surface that
lets the project owner monitor the system, summarise logs and PRs, preview scanner
signals, and receive daily reports, all from a **phone via Discord**.

OpenClaw is **not** a trading executor. It cannot and must not place, modify, cancel, or
simulate real broker orders beyond the existing dry-run documentation already present in
this repository.

---

## Architecture

```
Phone / Discord mobile app
    ↓
Discord (private server / #mellytrade-ops channel)
    ↓
OpenClaw Gateway  (runs locally or over Tailscale/VPN — never exposed publicly)
    ↓
MellyTrade Operator Agent  (skills/mellytrade-operator/SKILL.md)
    ↓
Read-only tools only
    ├── git status / git log
    ├── docker compose logs (read-only tail)
    ├── python scripts/validate_safety_config.py
    ├── python -m pytest tests/app -q
    └── GitHub PR / issue read-only queries
    ↓
Reports, summaries, safety checks, scanner previews
    ↓
Discord response (phone-readable, compact blocks)
```

**Primary channel:** Discord  
**Primary device:** Phone / Discord mobile app  
**Secondary channels:** Slack (optional, future team workflow), Telegram (optional fallback only — not the recommended default)

---

## Safe Use Cases

| Command | What it does |
|---|---|
| `/status` | Repo state, branch, last commit, safety flags |
| `/safety` | Run `validate_safety_config.py`, report pass/fail |
| `/logs` | Tail last 200 lines of trading-bot container logs |
| `/signals` | Advisory-only scanner preview — no execution |
| `/prs` | Open PRs with status and review readiness |
| `/daily-report` | Summary: PRs, tests, signals, errors, next 3 tasks |
| `/next-task` | Suggest the safest next action from open tasks |
| `/validate` | Full local safety suite: config + pytest -q |

All of these operations are **read-only**. No command listed here modifies any runtime
file, config, or trading state.

---

## Forbidden Use Cases

The following are strictly prohibited via OpenClaw or any agent connected through it:

- Live trading or order execution of any kind
- Changing `autotrade.enabled` to `true`
- Setting `dry_run` to `false`
- Disabling `live_orders_blocked`
- Touching `.env`, secrets, credentials, or account IDs
- Reading or printing environment variables
- Modifying `config.json`, risk policy, or profiles
- Modifying backend routes, frontend runtime UI, or broker/MT5/IBKR modules
- Modifying workflow YAML or Docker runtime config
- Pushing directly to `main` or force-pushing
- Placing, modifying, cancelling, or simulating real broker orders beyond existing dry-run
  documentation

---

## Recommended Discord Setup

### Server / Channel Structure

Use a **private Discord server** or a **private category** inside an existing server.
Never use a public server or public channel for operational commands.

| Channel | Purpose |
|---|---|
| `#mellytrade-ops` | Status cockpit — `/status`, `/safety`, `/validate` |
| `#mellytrade-alerts` | Safety alerts, CI failures, advisory signal alerts |
| `#mellytrade-dev` | PR summaries, validation, Codex/Claude Code prompts |
| `#mellytrade-reports` | Daily/weekly summaries, scanner previews |

### Bot Permissions

- Grant **minimal permissions** only — read messages, send messages, embed links.
- Do **not** grant Administrator permission.
- Restrict channel access so only the project owner can invoke commands.
- Never paste bot tokens, webhook URLs, guild IDs, or channel IDs into chat, docs, issues,
  or screenshots.
- Rotate the bot token immediately if it is ever exposed.

### Notifications

Configure OpenClaw to push to Discord for:
- Daily reports (scheduled)
- Safety validation failures
- CI pipeline failures
- Advisory scanner signals above confidence threshold
- New PRs ready for review

---

## Recommended Milestone Roadmap

### Phase 1 — Local Read-Only Cockpit
Set up OpenClaw Gateway locally. Connect to Discord. Validate `/status` and `/safety`
from phone. Confirm no execution tools are active.

### Phase 2 — Scheduled Discord Reports
Configure daily `#mellytrade-reports` posts: repo state, open PRs, last test run, scanner
preview summary.

### Phase 3 — GitHub / PR Summaries
Add read-only GitHub integration. `/prs` returns open PRs with review status and CI badge.
`/next-task` pulls from open issues or task board.

### Phase 4 — Advisory Signal Alerts
Connect scanner preview output to `#mellytrade-alerts`. Alerts are advisory only — no
auto-execution path is ever created.

### Phase 5 — Supabase / Audit Read-Only Summaries
Add read-only Supabase query for audit log tail. Surface recent signal decisions and
safety events in `#mellytrade-reports`.

---

## Safety Contract

```
autotrade            = false
dry_run              = true
read_only            = true
live_orders_blocked  = true
risk_allowed         = false  # unless explicitly reviewed by a human
execution_mode       = dry_run_only
requires_human_review = true
max_risk_per_trade_pct <= 1
```

This contract is enforced by `scripts/validate_safety_config.py` and
`tests/app/test_safety_invariants.py`. OpenClaw must never be used to modify any of these
values.

---

## Related Files

- [`docs/openclaw/INSTALL_CHECKLIST.md`](INSTALL_CHECKLIST.md) — step-by-step setup
- [`docs/openclaw/DAILY_USAGE.md`](DAILY_USAGE.md) — practical daily commands (Polish)
- [`docs/openclaw/SECURITY_MODEL.md`](SECURITY_MODEL.md) — threat model and mitigations
- [`docs/openclaw/DISCORD_LOCAL_SMOKE_CHECKLIST.md`](DISCORD_LOCAL_SMOKE_CHECKLIST.md) — OPENCLAW-002 phone/Discord smoke tests
- [`docs/openclaw/DISCORD_BOT_SETUP_GUIDE.md`](DISCORD_BOT_SETUP_GUIDE.md) — OPENCLAW-003 Discord bot creation and permissions
- [`docs/openclaw/OPENCLAW_LOCAL_CONFIG_TEMPLATE.md`](OPENCLAW_LOCAL_CONFIG_TEMPLATE.md) — OPENCLAW-003 local config shape reference
- [`skills/mellytrade-operator/SKILL.md`](../../skills/mellytrade-operator/SKILL.md) — operator skill definition
