# MellyTrade Public Launch Pack

SOURCE STATUS: Public-safe. A launch and feedback playbook for sharing the
MellyTrade portfolio demo on LinkedIn, GitHub, CV channels and feedback
communities. No private data, no secrets, no account IDs.

**Project:** MellyTrade / Alpha AI — read-only, safety-first AI trading terminal demo
**Repository:** <https://github.com/Melly-999/alpha_data_scraper_ai>
**Live demo:** <https://alpha-data-scraper-ai.vercel.app>

**Safety posture (applies to every piece of copy you share):**

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

## 1. Purpose

This pack is the **distribution layer** for the MellyTrade portfolio project: a
practical playbook for *where* and *how* to share the demo and gather honest
feedback before approaching recruiters. It does not restate the full marketing
copy — that lives in the canonical portfolio docs (see §2). It focuses on the
launch-and-feedback work those docs do not cover: community posting, feedback
questions, channel strategy, a pre-launch checklist, and the honesty guardrails
to apply everywhere.

## 2. Current source of truth

Reuse the existing, maintained copy instead of duplicating it. This pack links
to it rather than copying, so nothing drifts out of sync:

- **Full pitch + recruiter narrative:** [../portfolio/mellytrade_recruiter_portfolio_pack.md](../portfolio/mellytrade_recruiter_portfolio_pack.md)
- **Case study (capabilities + honest limitations):** [recruiter_case_study.md](recruiter_case_study.md)
- **LinkedIn copy (EN/PL posts):** [linkedin_copy_pack.md](linkedin_copy_pack.md) and [../portfolio/mellytrade_linkedin_summary.md](../portfolio/mellytrade_linkedin_summary.md)
- **CV / portfolio bullets:** [../portfolio/mellytrade_cv_project_entry.md](../portfolio/mellytrade_cv_project_entry.md)
- **Demo evidence + freeze:** [../demo/demo_freeze_001_recruiter_script.md](../demo/demo_freeze_001_recruiter_script.md), [../demo/demo_evidence_pack_001.md](../demo/demo_evidence_pack_001.md)

If a piece of copy here and in those docs disagree, **the canonical doc wins** —
update it there, not only here.

## 3. Launch positioning

One sentence to anchor every post:

> MellyTrade is a read-only, dry-run AI trading terminal demo — web, mobile/PWA
> and desktop — built by a self-taught developer with FastAPI, React/TypeScript
> and Tauri, using AI-assisted development under strict human review, with no
> live trading and no broker execution by design.

For the 30-second and 2-minute versions, use the pitches in the
[recruiter portfolio pack](../portfolio/mellytrade_recruiter_portfolio_pack.md).
The point of the project is to demonstrate **safety-first engineering and an
honest AI-assisted workflow**, not trading results.

## 4. Public surfaces to share

| Surface | URL |
|---|---|
| Live web demo (Vercel) | <https://alpha-data-scraper-ai.vercel.app> |
| Live API health (Render) | <https://alpha-data-scraper-ai.onrender.com> |
| GitHub repository | <https://github.com/Melly-999/alpha_data_scraper_ai> |
| Recruiter case study | [recruiter_case_study.md](recruiter_case_study.md) |

Check each surface is live before sharing (see the checklist in §8).

## 5. Community feedback post

For Discord / Reddit / Skool / indie-hacker communities. Adjust the opener to
each community's norms and read the rules before posting.

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

## 6. Feedback questions

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

## 7. Where to post / channel strategy

**LinkedIn** — the primary channel.
- Personal post using the EN/PL copy in [linkedin_copy_pack.md](linkedin_copy_pack.md).
- Featured section: pin the repo and the case study link.

**GitHub profile.**
- Add the project card from [github_profile_readme_draft.md](github_profile_readme_draft.md) to the profile README; pin the repository.

**Portfolio website.**
- Embed the 30-second pitch plus one screenshot and the live demo link.

**Discord / Skool communities.**
- Indie-hacker, learn-to-code, Python and React communities — use the post in §5.
- Read each server's self-promo rules first; post in showcase/feedback channels only.

**Reddit — with caution.**
- Only subreddits that explicitly allow project-feedback posts (e.g. webdev/Python showcase threads).
- Never post in trading/investing subreddits as if it were a trading tool; the framing must stay "portfolio demo, feedback wanted."
- Follow each subreddit's self-promotion rules strictly; one post, no cross-post spam.

**Polish tech / job groups.**
- Polish IT communities and junior-developer groups — use the PL copy from [linkedin_copy_pack.md](linkedin_copy_pack.md).

**Recruiter messages.**
- Direct messages personalized per recruiter; never bulk-send identical copy. Use the template in the [recruiter portfolio pack](../portfolio/mellytrade_recruiter_portfolio_pack.md).

## 8. Launch checklist

Before posting anything:

- [ ] Check live links: the web demo and its key routes on Vercel, and the backend health endpoint (`/api/health`) on Render
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

## 9. What not to claim

Never claim any of the following, in any post, message or conversation:

- Do not claim production trading readiness — this is a portfolio demo
- Do not claim profit, returns, ROI, win-rate or trading performance of any kind
- Do not claim live trading — `autotrade=false` and `dry_run=true` by design
- Do not claim autonomous execution — `execution_enabled=false`; human review is required
- Do not claim financial advice — all surfaces carry "Analysis only. Not financial advice."
- Do not claim broker integration beyond read-only status and paper preview — there is no write path to any broker
- Do not claim "AI built everything" — use "AI-assisted development under human review" honestly
- Do not claim commercial IT employment or credentials not yet earned
- Do not claim it is a regulated or investment product — it is not

## 10. Next steps

1. Run the §8 checklist and capture one strong screenshot.
2. Post the LinkedIn EN/PL copy (canonical source: [linkedin_copy_pack.md](linkedin_copy_pack.md)).
3. Share the §5 community post in 1–2 feedback communities; collect answers to the §6 questions.
4. Fold substantive feedback back into the README, case study and portfolio pack.
5. Begin personalized recruiter outreach once the surfaces and copy are validated.

---

## PR #300 Milestone

PR #300 marks the public-launch readiness checkpoint for MellyTrade. It connects
the completed demo freeze, evidence pack, recruiter portfolio pack, stale PR
cleanup, and public feedback plan into one coherent public-facing launch layer.

This milestone does not represent live trading, broker execution, production
trading readiness, investment advice, or profit claims. It represents a
portfolio-ready public launch package for a read-only, safety-first fintech
tools project.

---

## Safety confirmation

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

*MellyTrade is a read-only, dry-run, paper-only portfolio project with human
review required for all changes. It is not a commercial platform, not a live
trading system, and not financial advice.*
