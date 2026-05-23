# Job Scanner Agent

**ADVISORY TOOL ONLY. No auto-apply. No fabricated claims. No financial advice. Manual review required for every decision.**

---

## Purpose

The Job Scanner Agent is a local advisory tool for analysing job postings and matching them against public-safe candidate facts and verified project evidence. It produces a fit score (0–100), a gap list, and a strategy brief for human review.

The agent assists the user in identifying realistic entry-point roles, understanding skill gaps, and planning portfolio work — it does not apply to jobs, contact employers, send messages, or make decisions on the user's behalf.

---

## Scope

- Accept job descriptions via manual paste or structured JSON input.
- Extract structured fields from raw job text (title, company, seniority, requirements, remote policy, degree requirement).
- Score each job 0–100 against the candidate profile using deterministic rules.
- Detect bridge roles where customer service experience gives a genuine advantage.
- Identify skill gaps (blocking and improvement gaps) and map them to courses and portfolio tasks.
- Produce application strategy briefs (CV bullet suggestions, cover letter drafts) that require human review before any use.
- Generate daily and weekly advisory reports.

---

## Non-Goals

The Job Scanner Agent must **never**:

- Auto-apply to any job posting.
- Submit any form, HTTP POST, or automated request to a job board.
- Fabricate experience, qualifications, or employment history.
- Claim a completed matura or university degree unless confirmed by the user.
- Claim MellyTrade is a commercial product or live trading system.
- Store real private contact details (phone, home address, private email) in the repository.
- Send personal data to any LLM without explicit user confirmation.
- Perform aggressive scraping or bypass access controls on any website.
- Execute broker trades, place orders, or perform any financial transaction.
- Provide financial advice or profit guarantees.
- State or imply autonomous operation without human oversight.

---

## Advisory-Only Safety Model

Every output of the Job Scanner Agent is advisory. The agent:

1. Scores jobs and explains the reasoning — but does not decide whether to apply.
2. Generates cover letter drafts marked `DRAFT — requires human review and approval before sending` — but never sends them.
3. Recommends courses and portfolio tasks — but does not enrol or execute autonomously.
4. Flags red flags (senior-only, mandatory degree, live trading execution) — but does not filter the user's options.

The user reviews every output before acting. No path exists in the tool for submitting an application or sending a message without an explicit human step.

---

## Manual Review Requirement

All generated content — scores, strategy briefs, CV bullets, cover letter drafts — is for human review only. The user must:

- Read and verify every score breakdown.
- Edit every generated draft before use.
- Approve cover letters with an explicit APPROVE step before saving the final version.
- Update application status manually after applying.

No automated status updates. No automated submission. The tool is a research and drafting assistant, not an autonomous agent.

---

## No Auto-Apply Rule

There is no auto-apply path in the Job Scanner Agent. Specifically:

- No HTTP POST to any job board.
- No browser automation (Playwright, Selenium).
- No pre-filled application forms.
- No email sending.
- No LinkedIn or Indeed API submission.

If such a feature is ever proposed, it must be rejected unless the user explicitly designs a human-gated approval step with no bypass.

---

## No Fabricated Claims Rule

The scoring engine and strategy generator must never produce output that claims:

- Commercial IT employment the user has not had.
- A completed matura or university degree.
- Live trading experience.
- MellyTrade as a commercial or production system.
- Senior or mid-level developer experience beyond the user's actual level.
- AI-written code without supervised human review.
- Financial advice, guaranteed returns, or trading signals as reliable profit indicators.

Every generated draft must be grounded in verified portfolio evidence from MellyTrade and documented project work. The no-fabrication rule is enforced by LLM system prompt guardrails and post-processing assertions in `tests/test_no_fabrication.py`.

---

## Candidate Fit Scoring Overview

Scoring is deterministic: the same job + same candidate profile always produces the same score.

Score range: 0–100. Score components and weights:

| Component | Max Points |
|---|---:|
| Role fit (title, responsibilities, domain) | 25 |
| Skill fit (required and nice-to-have skills) | 25 |
| Project evidence fit (MellyTrade coverage) | 20 |
| Bridge-role fit (customer service + tech overlap) | 10 |
| Location / work mode fit | 10 |
| Language, seniority, education fit | 10 |
| **Total** | **100** |

Score tags:

| Tag | Range | Meaning |
|---|---|---|
| `apply_now` | 65–100 | Strong fit, apply with current portfolio |
| `stretch` | 45–64 | Possible with a strong cover letter |
| `learn_first` | 25–44 | Missing 1–2 key skills |
| `skip` | 0–24 | Not accessible without fabrication |

Full scoring rules: [scoring_rules.md](scoring_rules.md).

---

## Bridge-Role Strategy

A bridge role is one where customer service or support experience combines with technical skills to create a genuine advantage over candidates with no operations background. The Job Scanner Agent detects bridge roles as high-priority opportunities.

Bridge-role indicators (any 2 of the following qualify):

- Job mentions customer support, client communication, or stakeholder management.
- Job is in FinTech, SaaS, or trading operations.
- Job title contains: Support, Operations, Technical Account, Customer Success, Helpdesk, Tier 1/2.
- Job mentions CRM, ticketing systems, or escalation workflows.
- Job does not require a CS degree.
- Job mentions AI tools, automation, or process improvement.

Bridge roles receive a scoring bonus and are ranked above non-bridge roles with the same raw score.

---

## Target Roles

Primary targets for this candidate profile:

- AI Automation Specialist
- AI Workflow Engineer
- Technical Support Engineer (FinTech / SaaS)
- FinTech Support Specialist
- Customer Success Technical Specialist
- Junior Python Backend Developer
- Junior Full-Stack Developer
- Backend Developer Intern
- Trading Operations Support

Explicitly excluded:

- Senior developer roles (3+ years commercial IT required)
- Roles requiring a completed university degree
- Roles requiring live trading execution authority
- Roles requiring a financial advisor licence
- Roles requiring completed matura as a mandatory application condition

---

## Input / Output Examples

### Input: pasted job description

```text
Junior Python Developer - FinTech Support
Company: Example Fintech Sp. z o.o.
Location: Warsaw / Remote Poland
Requirements: Python, REST APIs, basic SQL. Customer service experience a plus.
Education: No degree required.
Seniority: Junior
```

### Output: score record (advisory)

```json
{
  "score": 82,
  "tag": "apply_now",
  "bridge_role_detected": true,
  "skill_gap": {
    "blocking": ["SQL basics"],
    "improvement": ["Docker"]
  },
  "recommended_course": "pgExercises (free, ~2 weeks)",
  "recommended_portfolio_task": "Add SQLite persistence to Job Scanner Agent",
  "explanation": "Strong Python/FastAPI match. Customer service bridge angle is an advantage here. No degree required. Gap: SQL depth needs a quick fix.",
  "draft_status": "ADVISORY ONLY — human review required"
}
```

### Input: candidate profile (public-safe example)

See [examples/candidate_profile.example.json](examples/candidate_profile.example.json).

### Input: job posting (example schema)

See [examples/job_posting.example.json](examples/job_posting.example.json).

---

## Planned Files

```
job_scanner/
├── README.md                          # This file
├── scoring_rules.md                   # Scoring weights, penalties, red flags
├── examples/
│   ├── candidate_profile.example.json # Public-safe candidate profile example
│   └── job_posting.example.json       # Job posting schema example
├── candidate_profile.json             # Runtime profile (no secrets — future)
├── scoring_rules.json                 # Machine-readable scoring weights (future)
├── cli.py                             # Click-based CLI entry point (future)
├── extractor.py                       # LLM job extraction (future)
├── scorer.py                          # Scoring engine (future)
├── strategy.py                        # Strategy/draft generator (future)
├── report.py                          # Daily and weekly report generators (future)
├── weekly_report_template.md          # Weekly report format (future)
├── sources/
│   ├── manual_adapter.py              # Paste job text (future)
│   ├── mock_adapter.py                # Synthetic test data (future)
│   └── rss_adapter.py                 # Public RSS feeds only (future)
├── prompts/
│   ├── extraction_system_prompt.txt   # LLM extraction instructions (future)
│   ├── scoring_explanation_prompt.txt # LLM score explanation (future)
│   └── cover_letter_draft_prompt.txt  # Draft prompt with no-fabrication guards (future)
├── tests/
│   ├── test_scorer.py                 # Deterministic scoring tests (future)
│   ├── test_no_fabrication.py         # No-fabrication guardrail tests (future)
│   └── test_strategy.py              # Draft format / DRAFT watermark tests (future)
└── .env.example                       # API key template — never commit real keys
```

---

## Future Implementation Phases

| Phase | ID | Scope | Status |
|---|---|---|---|
| 0 | JOBSCAN-001 | Docs-only foundation: README, examples, scoring rules | In progress |
| 1 | JOBSCAN-002 | Scoring prototype: `scorer.py`, `scoring_rules.json`, basic tests | Planned |
| 2 | JOBSCAN-003 | No-fabrication and seniority mismatch tests | Planned |
| 3 | JOBSCAN-004 | Weekly report template | Planned |
| 4 | JOBSCAN-005 | Optional local CLI: `cli.py`, `extractor.py` (OpenAI Responses API) | Planned |
| 5 | JOBSCAN-006 | Optional dashboard integration: FastAPI routes + React panel | Deferred |

All phases are advisory-only and local/manual-review-first. No auto-apply path will be introduced at any phase.

---

## Privacy and Data Handling

- No real phone number, home address, or private email committed to this repository.
- Contact details in the candidate profile use `[PLACEHOLDER]` format.
- API keys loaded from `.env` (git-ignored) only.
- No personal data sent to any LLM without explicit user confirmation step.
- All output stored locally only — no cloud sync, no external submission.

---

## Safety Confirmation

```text
advisory_only=true
auto_apply=false
fabricated_claims=forbidden
manual_review_required=true
no_live_trading=true
no_financial_advice=true
no_broker_execution=true
```

Design doc: [docs/career/job_scanner_agent_design.md](../docs/career/job_scanner_agent_design.md)  
Scoring rules: [scoring_rules.md](scoring_rules.md)  
Implementation queue: [docs/tasks/job_scanner_agent_implementation_queue.md](../docs/tasks/job_scanner_agent_implementation_queue.md)
