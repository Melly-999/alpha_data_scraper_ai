# MellyTrade Public Launch Pack

SOURCE STATUS: Public-safe. Reusable copy for LinkedIn, GitHub profile, CV, recruiter messages and feedback communities. No private data, no secrets, no account IDs.

**Project:** MellyTrade / Alpha AI — read-only, safety-first AI trading terminal demo
**Repository:** `github.com/Melly-999/alpha_data_scraper_ai`
**Primary case study:** [docs/career/recruiter_case_study.md](recruiter_case_study.md)

**Safety posture (applies to every piece of copy in this pack):**

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
execution_enabled=false
paper_only=true
requires_human_review=true
max_risk_per_trade <= 1%
no live trading
no broker execution
no order buttons
no financial advice
no profit guarantees
```

---

## 1. Positioning Summary

### One sentence

MellyTrade is a read-only, dry-run AI trading terminal demo — web, mobile/PWA and desktop — built by a self-taught developer with FastAPI, React/TypeScript and Tauri, using AI-assisted development under strict human review, with no live trading and no broker execution by design.

### 30-second pitch

MellyTrade is my portfolio project: a financial terminal demo that looks and behaves like a real trading workstation, but is intentionally read-only and paper-only. The backend is Python/FastAPI hosted on Render; the frontend is React/TypeScript/Vite hosted on Vercel, with a mobile/PWA view and a local Tauri v2 desktop shell. There are no buy/sell buttons, no broker write paths and no live trading — the point of the project is to show safety-first engineering, not trading results. I built it with AI coding assistants (Claude Code, Codex, Copilot) under a supervised workflow: every diff reviewed, every PR through CI and review gates, safety config validated on every change.

### 2-minute pitch

Most AI trading demos in portfolios overpromise: they imply live execution, hide their risk posture, or claim results they cannot prove. MellyTrade does the opposite. It is a read-only fintech workstation that demonstrates how a system like this *should* be built: safety constraints first, features second.

The stack: a Python/FastAPI backend (Pydantic models, REST, pytest, safety validation scripts) hosted on Render, and a React/TypeScript/Vite terminal-style frontend hosted on Vercel, with a mobile/PWA route and a Tauri v2 desktop shell built locally. The broker surface is Alpaca Paper, status only — there is no write path to any broker, anywhere in the codebase.

The safety posture is enforced in config, validated by scripts, smoke-tested against the hosted demo, and rendered as visible badges on every public surface: `READ ONLY`, `DRY RUN`, `LIVE ORDERS BLOCKED`, `EXECUTION OFF`. The config is `autotrade=false`, `dry_run=true`, `read_only=true`, `paper_only=true`, with max risk per trade capped at 1% and human review required for everything. No live trading. No broker execution. Not financial advice.

The second thing the project demonstrates is an AI-assisted development workflow done honestly. I used Claude Code, OpenAI Codex, GitHub Copilot and local models as supervised assistants — for planning, drafts, tests and documentation — while I owned the scope, reviewed every diff, and gated every merge through CI plus CodeRabbit and Sourcery review. The project reached a documented demo-freeze milestone with a hosted smoke test (PASS WITH NOTES) and a full recruiter-facing case study. It is a portfolio project, not a commercial product — and it says so on every surface.

---

## 2. LinkedIn Post — English

```text
I just finished the demo-freeze milestone for MellyTrade, my portfolio project: a safety-first AI trading terminal demo.

What it is:
- A financial terminal demo with web, mobile/PWA and desktop surfaces
- Backend: Python + FastAPI (hosted on Render)
- Frontend: React + TypeScript + Vite (hosted on Vercel)
- Desktop shell: Tauri v2 (local build)
- Broker surface: Alpaca Paper, status only — read-only

What it deliberately is NOT:
- No live trading. autotrade=false, dry_run=true, read_only=true, paper_only=true
- No broker execution and no order buttons anywhere
- No financial advice and no profit claims — it is a portfolio demo, not a product

The part I am most proud of is the process. I built this with AI coding assistants (Claude Code, OpenAI Codex, GitHub Copilot) used as supervised tools, not as the author: I owned the scope, reviewed every diff, and every PR went through CI plus CodeRabbit and Sourcery review gates before merge. Safety config is validated by scripts and smoke-tested against the live demo.

Live demo: https://alpha-data-scraper-ai.vercel.app
Repo + case study: https://github.com/Melly-999/alpha_data_scraper_ai

I would genuinely appreciate feedback — on the UI, the README, the safety posture, or anything you would want to see improved before I show this to recruiters. Honest critique welcome.
```

---

## 3. LinkedIn Post — Polish

```text
Wlasnie domknalem etap "demo freeze" w moim projekcie portfolio: MellyTrade — demo terminala tradingowego AI zaprojektowane w duchu safety-first.

Co to jest:
- Demo terminala finansowego: wersja web, mobile/PWA i desktop
- Backend: Python + FastAPI (hosting na Render)
- Frontend: React + TypeScript + Vite (hosting na Vercel)
- Wersja desktop: Tauri v2 (build lokalny)
- Warstwa brokera: Alpaca Paper, tylko status konta — wylacznie odczyt

Czym to celowo NIE jest:
- Zero live tradingu. autotrade=false, dry_run=true, read_only=true, paper_only=true
- Zero realnych zlecen brokerskich i zero przyciskow kup/sprzedaj
- To nie jest porada inwestycyjna ani obietnica zysku — to projekt portfolio, nie produkt

Najbardziej cenie sobie sam proces. Projekt powstal z pomoca asystentow AI (Claude Code, OpenAI Codex, GitHub Copilot), ale uzywanych jako nadzorowane narzedzia, nie jako autor kodu: zakres zadan, review kazdego diffa i decyzje o merge byly po mojej stronie. Kazdy PR przechodzil przez CI oraz bramki review (CodeRabbit, Sourcery), a konfiguracja bezpieczenstwa jest walidowana skryptami i testowana smoke testem na dzialajacym demo.

Demo na zywo: https://alpha-data-scraper-ai.vercel.app
Repo + case study: https://github.com/Melly-999/alpha_data_scraper_ai

Bede wdzieczny za feedback — UI, README, czytelnosc zalozen bezpieczenstwa, cokolwiek co warto poprawic zanim pokaze to rekruterom. Szczera krytyka mile widziana.
```

---

## 4. GitHub Profile README Snippet

```markdown
### MellyTrade — safety-first AI trading terminal demo

Read-only financial terminal demo with web, mobile/PWA and desktop (Tauri v2) surfaces.
**Stack:** Python/FastAPI · React/TypeScript/Vite · Tauri v2 · pytest · GitHub Actions
**Posture:** `READ ONLY` · `DRY RUN` · `PAPER ONLY` · no live trading, no broker execution, not financial advice
**Process:** AI-assisted development under human review — every PR through CI + CodeRabbit + Sourcery gates

[Live demo](https://alpha-data-scraper-ai.vercel.app) · [Repo](https://github.com/Melly-999/alpha_data_scraper_ai) · [Case study](https://github.com/Melly-999/alpha_data_scraper_ai/blob/main/docs/career/recruiter_case_study.md)
```

---

## 5. CV / Portfolio Bullets

Pick 3–5 per application; tailor to the role. All bullets are honest and verifiable against the repo.

**Junior Python Developer:**

- Built and deployed a Python/FastAPI REST backend (Pydantic models, pytest, safety validation scripts) hosted on Render, serving a hosted React frontend
- Enforced a config-driven safety posture (`autotrade=false`, `dry_run=true`, `read_only=true`) validated by automated scripts and post-deploy smoke tests

**Junior Frontend/React Developer:**

- Built a terminal-style financial dashboard in React + TypeScript + Vite, deployed on Vercel, with a dedicated mobile/PWA route and consistent safety badges across all surfaces
- Shipped a Tauri v2 desktop shell mirroring the web terminal layout, including custom branding and icon pipeline

**AI Automation / AI-assisted development:**

- Ran a supervised AI-assisted development workflow (Claude Code, OpenAI Codex, GitHub Copilot): human-owned task scope, per-diff review, and CI + CodeRabbit + Sourcery review gates on every PR
- Authored agent workflow rules and task queues that kept AI-generated changes small, reviewable and safety-compliant

**FinTech product/support role:**

- Designed a read-only broker integration (Alpaca Paper, account status only — no write path) demonstrating fintech vocabulary: paper trading, order preview, risk guardrails, audit posture
- Wrote recruiter-facing documentation (case study, demo-freeze report, honest-limitations section) that explains the system's capabilities without overclaiming
- Defined and validated a demo-freeze milestone: hosted smoke test against live Vercel/Render surfaces with documented PASS WITH NOTES result
- Maintained strict honesty constraints in all public materials: no live trading, no broker execution, no profit claims, not financial advice

---

## 6. Recruiter Message

```text
Hi [Name],

I'm a self-taught developer transitioning from customer operations into technical/junior development roles. Rather than describing my skills, I'd like to show them: MellyTrade is my portfolio project — a read-only AI trading terminal demo (Python/FastAPI backend, React/TypeScript frontend, Tauri desktop shell) with a live hosted demo and a full case study.

It is deliberately paper-only and read-only — no live trading, no broker execution — because the point is to demonstrate safety-first engineering and a disciplined AI-assisted development workflow (every change human-reviewed, CI + review gates on every PR).

Live demo: https://alpha-data-scraper-ai.vercel.app
Case study: https://github.com/Melly-999/alpha_data_scraper_ai/blob/main/docs/career/recruiter_case_study.md

If you have roles where a candidate with strong customer-operations background plus demonstrated Python/React/AI-workflow skills could fit (technical support, junior developer, AI automation, fintech support), I'd appreciate a conversation.

Best regards,
Mateusz Ozimkiewicz
```

---

## 7. Community Feedback Post

For Discord / Reddit / Skool / indie hacker communities. Adjust the opener to each community's norms; read the rules before posting.

```text
I built a safety-first AI trading terminal DEMO and I'd love product/UI feedback (not trading advice)

I'm a self-taught dev and this is my main portfolio project: MellyTrade, a financial terminal demo with web, mobile/PWA and desktop surfaces.

Important framing: it does NOT trade. It's intentionally read-only, dry-run, paper-only — no live trading, no broker execution, no order buttons. The project is about demonstrating safety-first engineering and an honest AI-assisted dev workflow (human review on every change), not about making money. Not financial advice.

Stack: FastAPI (Render) + React/TypeScript/Vite (Vercel) + Tauri v2 desktop shell.

Live demo: https://alpha-data-scraper-ai.vercel.app
Repo: https://github.com/Melly-999/alpha_data_scraper_ai

What I'd love feedback on:
- Is the safety posture (read-only / dry-run badges) clear within 10 seconds?
- Does the README explain what this is quickly enough?
- Does the mobile route feel credible or like an afterthought?
- What would you fix before showing this to a recruiter?

I'm NOT looking for trading strategy advice — just product, UI, docs and credibility feedback. Thanks!
```

---

## 8. Feedback Questions

Use these when asking anyone to review the demo:

1. Is the safety posture (read-only, dry-run, paper-only) clear within the first 10 seconds of opening the demo?
2. Does the README explain what the product is — and is not — quickly enough?
3. Does the terminal view look like a credible financial workstation, or like a generic dashboard?
4. Does the mobile/PWA route feel credible, or like an afterthought?
5. Which feature or surface looks strongest, and which looks weakest?
6. Is anything on the public surfaces confusing about whether real money or live trading is involved? (It is not — does the UI make that obvious?)
7. Does the case study read as honest, or does any part feel like overclaiming?
8. Is the AI-assisted development framing ("supervised tools, human review") convincing and clearly explained?
9. What would you improve before showing this to a recruiter?
10. If you were a hiring manager, what single change would most increase your confidence in this candidate?

---

## 9. What Not To Claim

Never claim any of the following, in any post, message or conversation:

- Do not claim production trading readiness — this is a portfolio demo
- Do not claim profit, returns, or trading performance of any kind
- Do not claim live trading — `autotrade=false` and `dry_run=true` by design
- Do not claim autonomous execution — `execution_enabled=false`; human review is required
- Do not claim financial advice — all surfaces carry "Analysis only. Not financial advice."
- Do not claim broker integration beyond read-only status and paper preview — there is no write path to any broker
- Do not claim "AI built everything" — use "AI-assisted development under human review" honestly
- Do not claim commercial IT employment or credentials not yet earned

---

## 10. Where to Post

**LinkedIn**

- Personal post (Section 2 EN, Section 3 PL) — the primary channel
- Featured section: pin the repo and the case study link

**GitHub profile**

- Add the project card (Section 4) to the profile README
- Pin the repository

**Portfolio website**

- Embed the 30-second pitch plus one screenshot and the live demo link

**Discord / Skool communities**

- Indie hacker, learn-to-code, Python and React communities — use Section 7
- Read each server's self-promo rules first; post in showcase/feedback channels only

**Reddit — with caution**

- Subreddits that explicitly allow project feedback posts (e.g. webdev/Python showcase threads)
- Never post in trading/investing subreddits as if it were a trading tool; the framing must stay "portfolio demo, feedback wanted"
- Follow each subreddit's self-promotion rules strictly; one post, no cross-post spam

**Polish tech/job groups**

- Polish IT communities and junior-developer groups (Facebook/Discord) — use Section 3
- Local Toruń/kujawsko-pomorskie tech groups where appropriate

**Recruiter messages**

- Direct messages using Section 6, personalized per recruiter; never bulk-send identical copy

---

## 11. Launch Checklist

Before posting anything:

- [ ] Check live links: main app, `/terminal`, `/mobile`, `/brokers` on Vercel; `/api/health` and `/api/safety/status` on Render
- [ ] Check the README renders correctly on GitHub (badges, screenshots, links)
- [ ] Check screenshots are current and show safety badges
- [ ] Check the case study link resolves on `main`
- [ ] Prepare one strong screenshot (terminal view with visible safety badges) for posts
- [ ] Run `python scripts/validate_safety_config.py` one final time — must PASS

Posting discipline:

- [ ] Post once per channel; do not repost the same content across many channels on the same day
- [ ] Track feedback in one place (issues or a notes doc) and respond to every substantive comment
- [ ] Do not spam: no bulk DMs, no repeated bumps, no cross-post flooding
- [ ] If a hosted surface goes down (free-tier cold start or outage), pause promotion until it recovers

---

## Safety Confirmation

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
execution_enabled=false
paper_only=true
requires_human_review=true
max_risk_per_trade <= 1%
no live trading
no broker execution
no order buttons
no connect-live UX
no financial advice
no profit guarantees
no secrets in repo
```

*MellyTrade is a read-only, dry-run, paper-only portfolio project with human review required for all changes. It is not a commercial platform, not a live trading system, and not financial advice.*
