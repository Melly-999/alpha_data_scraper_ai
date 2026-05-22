# Job Scanner Agent — Design Document

**Project:** AI Job Scanner Agent  
**Candidate:** Mateusz Ozimkiewicz  
**Status:** Design phase — MVP not yet built  
**Safety level:** No auto-apply, no fabricated qualifications, no scraping against ToS, no secret storage in repo  
**AI direction:** OpenAI Responses API / Agents SDK + optional local Ollama fallback  
**Storage:** SQLite (MVP) → PostgreSQL + FastAPI (future)  
**UI:** CLI first → Streamlit or React dashboard (future)

---

## Purpose

The Job Scanner Agent is a local AI-assisted tool that:

1. Accepts job descriptions (pasted or from permitted sources).
2. Extracts structured fields from raw job text using an LLM.
3. Scores each job 0–100 against the candidate's actual profile.
4. Detects bridge roles (customer service + tech overlap) as high-priority opportunities.
5. Identifies skill gaps between the candidate's current state and the job requirements.
6. Recommends the highest-ROI courses and portfolio tasks to close the gap.
7. Generates tailored application strategy, CV bullet suggestions, and cover letter drafts.
8. Produces a daily and weekly review workflow.
9. Never auto-applies, never fabricates qualifications, never bypasses access controls.

---

## MVP Scope

The MVP covers the minimum viable loop: paste a job → get a score, a gap list, and a strategy brief.

| Phase | Scope |
|---|---|
| Phase 0 | Candidate profile schema + scoring rules |
| Phase 1 | Job ingestion CLI (paste job text → structured JSON) |
| Phase 2 | Fit scoring engine (0–100, with human-readable explanation) |
| Phase 3 | Application strategy drafts (CV bullets, cover letter, interview prep) |
| Phase 4 | Source adapters (RSS/public APIs only, no scraping) |
| Phase 5 | Portfolio gap recommendations |
| Future | FastAPI + React dashboard |

---

## Architecture

```
INPUT LAYER
    ├── CLI: paste job description → extract_job()
    ├── RSS/public API adapters → normalise_job()
    └── Manual JSON import

EXTRACTION LAYER (LLM)
    ├── OpenAI Responses API or Agents SDK
    ├── Extracts: title, company, location, remote, skills, seniority, education, red_flags
    └── Optional: local Ollama fallback for non-sensitive text

CANDIDATE PROFILE
    ├── candidate_profile.json — skills, projects, experience, constraints, target roles
    └── scoring_rules.json — weights, penalties, hard filters

SCORING ENGINE
    ├── score_job(job, candidate_profile) → score 0–100
    ├── detect_bridge_role(job) → bool
    ├── detect_skill_gap(job, candidate_profile) → gap_list
    └── tag_role(job, score) → apply_now | stretch | learn_first | skip

STRATEGY GENERATOR (LLM)
    ├── generate_recruiter_notes(job, candidate_profile) → positioning brief
    ├── generate_cv_bullets(job, candidate_profile) → bullet suggestions
    ├── generate_cover_letter_draft(job, candidate_profile) → draft + DRAFT watermark
    ├── generate_interview_prep(job) → likely questions
    └── generate_missing_proof_checklist(job, gap_list) → artifact checklist

STORAGE
    ├── SQLite (MVP): jobs.db — jobs, scores, strategy_drafts, applications
    └── PostgreSQL (future): same schema, Supabase-compatible

REPORT LAYER
    ├── daily_report() → top 5 jobs, score summary, action list
    └── weekly_review() → skill gap trends, best bridge roles, portfolio tasks

SAFETY LAYER
    ├── No auto-apply path
    ├── No fake-claim validator (LLM prompt guardrails + post-processing)
    ├── Ethics flag: skip jobs requiring fabricated claims
    └── Privacy: no personal data sent to LLM without explicit review step
```

---

## Candidate Profile Schema

```json
{
  "version": "1.0",
  "candidate": {
    "name": "Mateusz Ozimkiewicz",
    "location": "Toruń, Poland",
    "timezone": "Europe/Warsaw",
    "languages": ["Polish (native)", "English (B2+)"],
    "work_authorisation": "Poland / EU"
  },
  "education": {
    "current": "Liceum Ogólnokształcące dla Dorosłych Cosinus, Toruń",
    "status": "in_progress",
    "matura": "in_progress",
    "notes": "Self-taught programmer. No completed formal IT degree."
  },
  "experience": {
    "it_commercial": 0,
    "customer_service_years": 3,
    "sales_years": 2,
    "portfolio_projects": ["MellyTrade", "Job Scanner Agent (in progress)"],
    "ai_workflow_experience": true,
    "notes": "No paid IT employment. Portfolio evidence only for technical skills."
  },
  "skills": {
    "languages": ["Python 3.11"],
    "frameworks": ["FastAPI", "Pydantic", "React 18", "TypeScript", "Vite"],
    "testing": ["pytest"],
    "tooling": ["Git", "GitHub", "Docker basics", "PowerShell"],
    "ai_tools": ["Claude Code", "OpenAI Codex", "GitHub Copilot", "Ollama", "LM Studio"],
    "databases": ["SQLite basics", "Supabase/PostgreSQL basics"],
    "monitoring": ["Prometheus basics", "Grafana basics"],
    "infrastructure": ["Docker Compose", "Kubernetes manifests (awareness level)"],
    "concepts": ["REST APIs", "broker adapters", "risk guardrails", "audit trails", "dry-run patterns"]
  },
  "target_roles": [
    "AI Automation Specialist",
    "AI Workflow Engineer",
    "Technical Support Engineer (FinTech / SaaS)",
    "FinTech Support Specialist",
    "Junior Python Backend Developer",
    "Junior Full-Stack Developer",
    "Trading Operations Support"
  ],
  "constraints": {
    "min_seniority": "junior",
    "max_seniority": "mid",
    "degree_required_ok": false,
    "matura_required_ok": false,
    "prefer_remote_or_hybrid": true,
    "location_ok": ["Poland", "remote EU", "remote global"],
    "no_live_trading_execution_roles": true,
    "no_financial_advisor_roles": true,
    "no_senior_only_roles": true
  },
  "hard_no_flags": [
    "requires_completed_degree",
    "requires_matura_proof_for_application",
    "requires_commercial_IT_experience",
    "requires_live_trading_execution",
    "requires_financial_advice_licence"
  ]
}
```

---

## Job Posting Schema

```json
{
  "job_id": "uuid",
  "source": "manual | rss | api | csv_export",
  "source_url": "https://...",
  "retrieved_at": "2026-05-22T00:00:00Z",
  "raw_text": "Full original job description",
  "extracted": {
    "title": "Junior Python Developer",
    "company": "Example FinTech Sp. z o.o.",
    "location": "Warsaw / Remote",
    "remote_policy": "hybrid | remote | onsite | unknown",
    "employment_type": "full_time | part_time | contract | internship",
    "seniority": "junior | mid | senior | unknown",
    "required_skills": ["Python", "FastAPI", "REST APIs"],
    "nice_to_have_skills": ["Docker", "TypeScript", "LLM experience"],
    "education_requirement": "none | matura | degree | specific_degree",
    "experience_years_required": 0,
    "languages_required": ["Polish", "English"],
    "salary_range": {"min": null, "max": null, "currency": "PLN"},
    "red_flags": ["senior experience required", "mandatory degree"],
    "ai_tools_mentioned": true,
    "fintech_domain": true
  },
  "scoring": {
    "score": 78,
    "tag": "apply_now",
    "score_breakdown": {
      "core_skill_match": 24,
      "entry_level_realism": 18,
      "degree_matura_tolerance": 15,
      "portfolio_relevance": 12,
      "remote_poland_friendly": 9
    },
    "skill_gap": ["SQL / PostgreSQL", "Docker advanced", "CI/CD pipeline ownership"],
    "bridge_role_detected": true,
    "explanation": "Strong Python/FastAPI match. No degree required. Remote-friendly. FinTech domain aligns with MellyTrade. Gap: SQL depth."
  },
  "strategy": {
    "recruiter_notes": "...",
    "cv_bullets": ["..."],
    "cover_letter_draft": "DRAFT — requires human review before sending\n...",
    "interview_prep": ["..."],
    "missing_proof_checklist": ["Add FastAPI test coverage screenshot to README", "Publish demo GIF"]
  },
  "application_status": "saved | drafting | applied | response | closed",
  "applied_at": null,
  "notes": ""
}
```

---

## Scoring Logic (0–100)

The scoring engine produces a deterministic 0–100 score per job against the candidate profile.

### Score Components

| Component | Max Points | Description |
|---|---:|---|
| Core skill match | 30 | Required skills vs. candidate's actual skills |
| Entry-level realism | 20 | Is this role genuinely accessible without 2+ years IT experience? |
| Degree / matura tolerance | 15 | Does the job not require a completed degree or matura? |
| Portfolio relevance | 15 | Does MellyTrade evidence reduce the experience gap for this role? |
| Remote or Poland-friendly | 10 | Is the role accessible from Toruń, Poland or remote? |
| Customer-service bridge value | 10 | Does the role value customer operations experience? |
| **Total** | **100** | |

### Penalties

| Condition | Penalty |
|---|---:|
| "Senior only" or "3+ years IT experience required" | −30 |
| "Mandatory degree (BA/BS/etc.)" | −25 |
| "Mandatory matura proof for application" | −20 |
| "Live trading execution required" | −50 (likely skip) |
| "Heavy production ML experience required" | −20 |
| "Financial advisor licence required" | −50 (skip) |
| "Commercial IT employment required" | −20 |

### Role Tags

| Tag | Score Range | Meaning |
|---|---|---|
| `apply_now` | 65–100 | Strong fit, apply with current portfolio |
| `stretch` | 45–64 | Possible with a strong cover letter, highlight bridge angle |
| `learn_first` | 25–44 | Missing 1–2 key skills — earn them first, then apply |
| `skip` | 0–24 | Not accessible without fabrication or ineligible |

---

## Bridge-Role Detection

A bridge role is one where customer service or support experience combines with technical skills to create a genuine competitive advantage over pure CS graduates with no operations background.

Detection criteria (any 2 of the following):

- Job mentions customer support, client communication, or stakeholder management.
- Job is in FinTech, SaaS, or trading operations.
- Job title contains: Support, Operations, Technical Account, Customer Success, Helpdesk, Tier 1/2.
- Job mentions CRM, ticketing systems, or escalation workflows.
- Job does not require a CS degree.
- Job mentions AI tools, automation, or process improvement.

---

## Skill Gap Detection

```python
def detect_skill_gap(job: JobPosting, candidate: CandidateProfile) -> list[str]:
    required = set(job.extracted.required_skills)
    nice_to_have = set(job.extracted.nice_to_have_skills)
    candidate_skills = set(candidate.skills.all_skills_flat())
    
    hard_gaps = required - candidate_skills      # blocking gaps
    soft_gaps = nice_to_have - candidate_skills  # improvement areas
    
    return {
        "blocking": list(hard_gaps),
        "improvement": list(soft_gaps),
        "portfolio_covers": [s for s in required if is_evidenced_by_portfolio(s, candidate)]
    }
```

Each gap item is mapped to:
- A course recommendation from the course roadmap.
- A portfolio task (e.g., "add SQLite persistence to Job Scanner Agent").
- A timeline estimate.

---

## Course Recommendation Logic

```python
def recommend_courses(skill_gaps: list[str]) -> list[CourseRecommendation]:
    # Map gaps to courses from docs/career/course_certification_roadmap.md
    GAP_TO_COURSE = {
        "SQL": ["PostgreSQL fundamentals (pgExercises, free)"],
        "Docker": ["Docker foundations (KodeKloud or official)"],
        "CI/CD": ["GitHub Actions Learning Lab (free)"],
        "LLM / AI Agents": ["DeepLearning.AI LangGraph course (free)"],
        "LangChain": ["LangChain Academy (free)"],
        "OpenAI API": ["DeepLearning.AI OpenAI Agents SDK course (free)"],
        "AWS": ["AWS Cloud Practitioner (P3 — defer until first role)"],
        "React": ["Scrimba React course (free tier)"],
        "Python fundamentals": ["Google IT Automation with Python (P0)"],
    }
    return [GAP_TO_COURSE[gap] for gap in skill_gaps if gap in GAP_TO_COURSE]
```

---

## Application Strategy Generator

For each `apply_now` or `stretch` job, the agent generates:

### Recruiter Notes
- Why this role fits the candidate's actual background.
- What to emphasise in the cover letter and conversation.
- What to avoid or not over-claim.
- The bridge-role angle if applicable.

### CV Bullet Suggestions
- Bullets based only on verified portfolio evidence from MellyTrade and other actual projects.
- No fabrication. Each bullet must map to a real file, test, or documented feature.
- Format: action verb + what + technology + outcome.

### Cover Letter Draft
- Marked `DRAFT — requires human review and approval before sending`.
- Positioned to target bridge-role overlap.
- Honest about education, portfolio status, and learning path.
- No fabricated employer, title, or employment dates.

### Interview Prep
- 5–8 likely questions extracted from the job description.
- Suggested answers based on actual portfolio evidence.
- "What I can't answer yet" section for honest gap acknowledgement.

### Missing Proof Checklist
- Screenshot needed: X
- README section needed: Y
- Test coverage needed: Z
- Certificate needed: W

---

## Daily Workflow

```
08:00  Check job alert emails (manually forwarded to agent CLI or pasted)
08:15  Run: job_scanner ingest --paste  → paste 1-3 new job descriptions
08:30  Review scores and tags for today's batch
08:45  For any apply_now job: review strategy draft, edit cover letter, save
09:00  For any learn_first job: check skill gap → add to weekly study plan
09:15  Mark applied jobs → update application_status
```

---

## Weekly Review Workflow

```
Monday morning (15 minutes):
    Run: job_scanner weekly_review
    → Top bridge roles seen this week
    → Most common skill gaps across saved jobs
    → Highest-priority portfolio task (from gap recommendations)
    → Suggested course to complete this week
    → Application status summary
```

---

## Safety and Privacy Rules

| Rule | Enforcement |
|---|---|
| No auto-apply | No HTTP POST or form submission to any job board from the tool |
| No fake experience | LLM system prompt guardrails + post-processing assertion |
| No scraping against ToS | Only RSS feeds, public APIs, manual paste, CSV export |
| No secret storage in repo | All API keys via `.env` (git-ignored) |
| No personal data to LLM without review | User confirms before any PII (name, email, address) is sent |
| No fake certificate or degree claims | Hard-coded check: no claim of completed degree or matura |
| Drafts are drafts | All generated cover letters marked `DRAFT — human review required` |
| Application status is manual | No automatic status updates — user updates manually |

---

## Low-Cost MVP Stack (Local JSON / SQLite First)

```
job_scanner/
├── candidate_profile.json      # candidate data (no secrets)
├── scoring_rules.json          # scoring weights and penalties
├── jobs.db                     # SQLite database
├── cli.py                      # click-based CLI
├── extractor.py                # LLM job extraction (OpenAI Responses API)
├── scorer.py                   # scoring engine
├── strategy.py                 # strategy generator (LLM drafts)
├── report.py                   # daily and weekly report generators
├── sources/
│   ├── rss_adapter.py          # RSS feed reader (no scraping)
│   └── manual_adapter.py       # paste job text
├── tests/
│   ├── test_scorer.py          # deterministic scoring tests
│   ├── test_no_fabrication.py  # guardrail compliance tests
│   └── test_strategy.py        # draft format tests (DRAFT watermark present)
├── .env.example                # API key template (not committed)
└── README.md                   # advisory-only disclaimer
```

**LLM usage cost estimate (MVP):**  
- 5 jobs/day × 1,000 tokens each = ~5,000 tokens/day
- GPT-4o-mini at $0.15/million input tokens = ~$0.01/day
- Monthly cost: ~$0.30 for extraction + scoring explanation
- Feasible at zero income level

---

## Future Version: FastAPI + React Dashboard

```
job_scanner_api/
├── app/
│   ├── routes/
│   │   ├── jobs.py             # GET /api/jobs, GET /api/jobs/{id}
│   │   ├── scoring.py          # GET /api/jobs/{id}/score
│   │   ├── strategy.py         # GET /api/jobs/{id}/strategy (draft only, no submit)
│   │   └── reports.py          # GET /api/reports/daily, GET /api/reports/weekly
│   ├── services/
│   │   ├── extractor_service.py
│   │   ├── scorer_service.py
│   │   └── strategy_service.py
│   └── db/                     # PostgreSQL / Supabase
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── JobList.tsx     # saved jobs with score badges
│   │   │   ├── JobDetail.tsx   # score breakdown, strategy, gap list
│   │   │   └── WeeklyReport.tsx
│   │   └── components/
│   │       ├── ScoreBadge.tsx
│   │       ├── GapList.tsx
│   │       └── DraftWarning.tsx # always visible on generated drafts
└── docker-compose.yml
```

The dashboard is GET-only for job data. No apply button. No form submission to external services. All draft content is read-only and clearly watermarked.

---

## OpenAI Responses API / Agents SDK Direction

### Extraction Agent

```python
client = openai.OpenAI()

response = client.responses.create(
    model="gpt-4o-mini",
    instructions="""
    You are a job posting parser. Extract structured fields from the raw job text.
    Return JSON only. Do not add information not present in the job text.
    Flag any red_flags (degree requirements, senior-only, live trading execution).
    """,
    input=raw_job_text,
    text={"format": {"type": "json_schema", "json_schema": JOB_SCHEMA}}
)
```

### Scoring Explanation Agent

```python
response = client.responses.create(
    model="gpt-4o-mini",
    instructions="""
    You are a career advisor for a self-taught junior developer in Poland.
    Explain the job fit score in plain language.
    Be honest about gaps. Do not invent qualifications.
    Do not claim the candidate has experience they do not have.
    """,
    input=f"Job: {job_json}\nScore: {score}\nGaps: {gaps}"
)
```

### Cover Letter Draft Agent

```python
response = client.responses.create(
    model="gpt-4o",
    instructions="""
    You are a career writing assistant.
    Write a cover letter draft for a self-taught junior developer.
    MANDATORY: Start the output with "DRAFT — requires human review and approval before sending."
    MANDATORY: Do not claim completed matura or university degree.
    MANDATORY: Do not claim commercial IT employment history.
    MANDATORY: Present MellyTrade as a portfolio project, not a commercial product.
    MANDATORY: Be honest about being self-taught.
    Use bridge-role framing: customer service + technical automation skills.
    """,
    input=f"Job: {job_json}\nProfile: {profile_json}"
)
```

---

## Acceptance Criteria for MVP

- A pasted job description produces a structured JSON record in `jobs.db`.
- The score is deterministic: same input → same score.
- Each score includes a human-readable explanation.
- No generated draft claims commercial IT employment.
- No generated draft claims a completed degree or matura.
- No generated draft claims MellyTrade is a commercial product.
- The `DRAFT — human review required` watermark is present on every cover letter.
- The tool has no HTTP POST path to any job board.
- All API keys are in `.env`, not in code or JSON.
- `test_no_fabrication.py` passes before any feature is merged.
