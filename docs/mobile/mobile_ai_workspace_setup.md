# Mobile AI Workspace Setup

**Task:** MOBILE-AI-000
**Type:** Workspace setup guide (docs-only)

This guide helps configure the MellyTrade Mobile AI project as if starting from
zero: ClickUp structure, OpenAI Platform project conventions, Claude Console
workspace conventions, recommended apps, and a starter workflow.

This is documentation only. Nothing here adds a runtime dependency, env var,
provider key, or config change. In particular:

- **No** OpenAI or Anthropic env vars are added to runtime for MOBILE-AI-000.
- **No** AI provider keys in frontend, ever.
- **No** broker credentials, MT5/IBKR secrets, or wallet keys anywhere.

Safety posture for everything below:

- Analysis only. Not financial advice.
- Paper plan only. No live orders.
- Human review required.
- Max simulated risk 1%.
- Wait for confirmation. Do not chase.
- No broker execution.
- No guaranteed profit.
- No wallet/private keys.
- No AI provider keys in frontend.

---

## A. ClickUp setup

Recommended ClickUp structure.

**Space:**

- MellyTrade

**Folder:**

- Mobile AI App

**Lists:**

- MOBILE-AI Roadmap
- Mobile UX / Screens
- AI Chart Review
- Safety + Compliance
- App Store / Native Future
- Evidence / Smoke Tests

**Statuses:**

- Backlog
- Ready
- In Progress
- Review Gate
- Blocked
- Done
- Archived

**Custom fields:**

- Task ID
- Implementation Type
- Safety Risk
- Repo Scope
- Validation Required
- PR URL
- Commit SHA
- Device Target
- Platform

**Views:**

- Board by Status
- List by Phase
- Calendar for Review Gates
- Docs view for product notes
- Table view for PR tracking

**ClickUp task templates:**

- **Template 1 — Mobile AI docs-only task**
  - Implementation Type: docs-only
  - Safety Risk: Low
  - Validation Required: safety config validation + static scan
  - Definition of done: docs-only diff, no runtime files touched.

- **Template 2 — Frontend-only mock task**
  - Implementation Type: frontend-only
  - Safety Risk: Low
  - Validation Required: frontend build/lint, no new endpoints, mock data only
  - Definition of done: static/mock UI only, no backend, no execution controls.

- **Template 3 — Safety review gate**
  - Implementation Type: review gate
  - Safety Risk: gate
  - Validation Required: confirm safety posture unchanged (autotrade=false,
    dry_run=true, read_only=true, live_orders_blocked=true, max risk ≤ 1%)
  - Definition of done: reviewer signs off that no execution surface exists.

- **Template 4 — Mobile smoke test evidence**
  - Implementation Type: evidence
  - Safety Risk: Low
  - Validation Required: device smoke checklist + screenshots/evidence pack
  - Definition of done: evidence captured, no runtime change.

---

## B. OpenAI Platform setup

**Recommended project name:**

- `mellytrade-mobile-ai-dev`

**Purpose:**

- Future **backend-only** AI analysis experiments for MellyTrade Mobile.
- No frontend API keys.
- No live trading.
- No broker execution.

**Rules:**

- Create a project-scoped key **only when backend integration starts**.
- Prefer restricted permissions.
- Set a low monthly budget alert.
- Do not put OpenAI keys in the frontend.
- Do not commit keys to the repo.
- Use environment variables only.
- The first run does **not** need an OpenAI key.

**Suggested future env var names** (for a later backend phase only):

- `OPENAI_API_KEY`
- `OPENAI_PROJECT_ID`
- `OPENAI_MOBILE_AI_MODEL`

> Do not add these env vars, or docs requiring them, into runtime for
> MOBILE-AI-000. They are reference notes for a future backend phase only.

---

## C. Claude Console setup

**Recommended workspace / project name:**

- `mellytrade-mobile-ai`

**Use cases:**

- prompt testing
- mobile AI chart review prompt design
- safety copy
- risk coach wording
- journal summary prompts
- weekly report prompt prototypes

**Rules:**

- No broker credentials.
- No MT5/IBKR secrets.
- No wallet keys.
- No live order prompts.
- No frontend provider keys.
- The first run does **not** need a Claude API key.

**Suggested future env var names** (for a later backend phase only):

- `ANTHROPIC_API_KEY`
- `CLAUDE_MOBILE_AI_MODEL`

> Do not add these env vars, or docs requiring them, into runtime for
> MOBILE-AI-000. They are reference notes for a future backend phase only.

---

## D. Recommended apps if starting from zero

**PC / Windows:**

- VS Code or Cursor
- Git
- GitHub Desktop
- Docker Desktop
- Node.js LTS
- Python 3.11 / 3.12
- PowerShell 7
- Windows Terminal
- Tailscale
- Postman or Bruno
- Figma
- Obsidian or Notion
- ClickUp Desktop/Web
- Discord
- NVIDIA App for graphics/performance management
- 1Password or Bitwarden for secret storage

**Tablet / iPad:**

- ChatGPT
- Claude
- ClickUp
- GitHub
- Figma
- Notion or Obsidian
- Freeform / Concepts
- Procreate or Canva
- TestFlight
- Working Copy
- Termius
- Documents by Readdle

**Phone / iOS or Android:**

- ChatGPT
- Claude
- ClickUp
- GitHub
- Discord
- Google Drive
- Bitwarden or 1Password
- TestFlight / Play Console app if available
- Expo Go for future native tests
- Termius
- TradingView / XTB only for manual market reference, **not** execution
  automation

---

## E. Starter workflow

**Daily:**

1. Check the ClickUp Today view.
2. Pick one small task.
3. Paste the task prompt into Claude Code.
4. Let Claude create the branch and PR.
5. Review the diff.
6. Run validation.
7. Move the ClickUp task to Review Gate.
8. Save the PR URL and commit SHA.

**Weekly:**

1. Review the roadmap.
2. Review the safety posture.
3. Review mobile screenshots / evidence.
4. Plan the next 1–3 PRs only.
