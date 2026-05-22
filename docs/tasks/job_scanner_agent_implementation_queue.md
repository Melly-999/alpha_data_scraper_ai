# Job Scanner Agent — Implementation Queue

**Goal:** Build a local AI-assisted job scanner that finds realistic entry roles, scores fit, identifies skill gaps, and generates application strategy — without auto-applying or fabricating qualifications.  
**Design doc:** [docs/career/job_scanner_agent_design.md](../career/job_scanner_agent_design.md)  
**Safety:** No auto-apply. No fake claims. No scraping against ToS. No secrets in repo.

---

## Safety Constraints (all tasks)

These apply to every task in this queue:

- Do not build any HTTP POST path to a job board.
- Do not generate content that claims commercial IT employment.
- Do not generate content that claims a completed degree or matura.
- Do not generate content that presents MellyTrade as a commercial product.
- Every generated cover letter must include `DRAFT — requires human review and approval before sending`.
- All API keys via `.env` (git-ignored, never committed).
- No personal data (name, email, address) sent to LLM without explicit user confirmation step.

---

## CAREER-001 — Recruiter Case Study Doc

**Scope:** Create or update `docs/career/recruiter_case_study.md` as a comprehensive portfolio case study explaining MellyTrade to technical recruiters.

**Files expected:**
- `docs/career/recruiter_case_study.md`

**Validation:**
- Document covers: what the project is, why it matters, architecture overview, frontend/backend stack, AI-assisted workflow, safety posture, broker adapter concept, audit/event systems, risk guardrails.
- Includes "For Recruiters" section.
- Includes "What this project proves" table.
- Includes "Limitations / Honesty" section with explicit statements about no commercial IT experience, education in progress, portfolio-only status.
- Includes target role fit table.

**Acceptance criteria:**
- No false claims about commercial employment.
- No false claims about completed education.
- Safety posture block (`autotrade=false, dry_run=true, read_only=true`) is present at the end.
- Document is recruiter-readable without prior knowledge of the codebase.

**Status:** Complete (this session)

---

## CAREER-002 — CV Positioning Notes

**Scope:** Create or update `docs/career/cv_positioning_notes.md` with detailed guidance for writing CVs across all four target role versions.

**Files expected:**
- `docs/career/cv_positioning_notes.md`

**Validation:**
- Covers: headline options for A/B/C/D versions, profile summaries, AI-assisted workflow wording, MellyTrade project description, technical skills ordering.
- Includes customer service → tech reframing guidance.
- Includes education/matura handling instructions with EN and PL wording.
- Includes PL and EN examples for summary, project, and AI workflow lines.
- Includes version-specific guidance for: a) AI Automation/Python, b) Technical Support/FinTech, c) Junior Backend/Internship, d) Freelance AI automation.
- Includes recruiter risk mitigation table.

**Acceptance criteria:**
- No false claims.
- Education handled honestly throughout.
- Four distinct versions clearly differentiated.

**Status:** Complete (this session)

---

## CAREER-003 — Course / Certification Roadmap

**Scope:** Create `docs/career/course_certification_roadmap.md` with a ranked, prioritised list of courses and certifications.

**Files expected:**
- `docs/career/course_certification_roadmap.md`

**Validation:**
- Contains P0, P1, P2, P3 priority tiers.
- Each entry includes: priority, duration, cost, certificate yes/no, market value, recruiter value, startup value, put on CV flag, when to do, portfolio project link.
- Covers: Google IT Automation, Claude Code, DeepLearning.AI LangGraph, OpenAI Agents SDK, LangChain, FastAPI, Docker, PostgreSQL, GitHub Actions, React/TypeScript, RAG, AWS Cloud Practitioner.
- Includes study schedule recommendation.
- Includes ATS keywords added per certificate.

**Acceptance criteria:**
- P0 certificates are free or very low cost.
- No certificate is recommended without a matching portfolio project.
- AWS is correctly listed as P3 (defer).

**Status:** Complete (this session)

---

## CAREER-004 — CV Drafts (EN + PL)

**Scope:** Create or update full ATS-friendly CV markdown drafts for EN and PL versions, each with three embedded versions (AI Automation, Technical Support, Junior Backend).

**Files expected:**
- `docs/career/cv_mateusz_ozimkiewicz_en.md`
- `docs/career/cv_mateusz_ozimkiewicz_pl.md`

**Validation:**
- Each file contains three clearly labelled version sections (A, B, C).
- Education listed as in progress.
- No commercial IT experience claimed.
- MellyTrade described as portfolio project.
- AI-assisted workflow described with supervised framing.
- ATS-friendly formatting: sections with clear headers, bullet points, no tables or special characters in main content.
- Contact details use placeholder format except for email.

**Acceptance criteria:**
- No false claims.
- Both EN and PL versions are complete.
- Each version has a distinct headline, summary, and skills ordering.

**Status:** Complete (this session)

---

## JOBSCAN-001 — Candidate Profile Schema

**Scope:** Create the local candidate profile JSON file that the scoring engine uses.

**Files expected:**
- `job_scanner/candidate_profile.json`
- `job_scanner/README.md` (advisory-only disclaimer)

**Validation:**
- JSON is valid and matches the schema in `job_scanner_agent_design.md`.
- Contains: personal context (no sensitive data committed), education status, experience, skills, target roles, constraints, hard_no_flags.
- `hard_no_flags` includes: `requires_completed_degree`, `requires_matura_proof_for_application`, `requires_commercial_IT_experience`, `requires_live_trading_execution`.
- README states: advisory tool only, no auto-apply, no fabrication, no financial advice.

**Safety constraints:**
- No real address, phone number, or broker credentials in the committed file.
- Email in `.env.example` only.

**Acceptance criteria:**
- Profile JSON is versionable with no secrets.
- Scoring rules are understandable without reading code.
- README advisory disclaimer is present.

**Status:** Not started

---

## JOBSCAN-002 — Job Posting Schema and Storage

**Scope:** Define the job posting JSON schema and SQLite storage layer.

**Files expected:**
- `job_scanner/schemas/job_schema.py` (Pydantic model)
- `job_scanner/db/models.py` (SQLite via sqlalchemy or sqlite3)
- `job_scanner/db/migrations/001_initial.sql`
- `job_scanner/tests/test_job_schema.py`

**Validation:**
- Schema matches `job_scanner_agent_design.md` Job Posting Schema.
- Includes: `job_id`, `source`, `source_url`, `retrieved_at`, `raw_text`, `extracted`, `scoring`, `strategy`, `application_status`.
- SQLite migration creates `jobs` table and `strategy_drafts` table.
- Round-trip test: create a job record, save to SQLite, retrieve, assert fields intact.
- Duplicate detection test: same company + title + URL → duplicate flag.

**Safety constraints:**
- No actual personal data in test fixtures.
- Test fixtures use synthetic company names and job descriptions.

**Acceptance criteria:**
- pytest passes with 0 failures.
- Schema and DB layer are importable without external API keys.

**Status:** Not started

---

## JOBSCAN-003 — Scoring Engine

**Scope:** Build the deterministic 0–100 scoring engine.

**Files expected:**
- `job_scanner/scorer.py`
- `job_scanner/scoring_rules.json`
- `job_scanner/tests/test_scorer.py`

**Validation:**
- Score components match design doc: core skill match (30), entry-level realism (20), degree/matura tolerance (15), portfolio relevance (15), remote/Poland-friendly (10), customer-service bridge value (10).
- Penalties applied: senior-only (-30), mandatory degree (-25), mandatory matura (-20), live trading (-50), heavy production ML (-20), financial advisor licence (-50).
- Deterministic: same input → same score on repeat runs.
- Role tags: `apply_now` (65–100), `stretch` (45–64), `learn_first` (25–44), `skip` (0–24).
- Bridge-role detection: any 2 of the 6 criteria → bridge_role_detected=True.
- Skill gap detection: blocking vs. improvement gaps.

**Acceptance criteria:**
- `test_scorer.py` includes at least 10 test cases.
- Senior-only job scores < 40.
- Portfolio-relevant junior FinTech job without degree requirement scores > 60.
- Jobs requiring live trading execution score < 25 (skip tag).
- Score is unchanged on 5 consecutive calls with same input.

**Status:** Not started

---

## JOBSCAN-004 — OpenAI Prompt / System Design

**Scope:** Design and implement the LLM extraction and explanation prompts. No auto-apply, no fabrication guardrails enforced by prompt design and post-processing.

**Files expected:**
- `job_scanner/extractor.py`
- `job_scanner/prompts/extraction_system_prompt.txt`
- `job_scanner/prompts/scoring_explanation_prompt.txt`
- `job_scanner/prompts/cover_letter_draft_prompt.txt`
- `job_scanner/tests/test_no_fabrication.py`

**Validation:**
- Extraction system prompt instructs LLM to return JSON only, not add information not in the job text, and flag red_flags.
- Cover letter prompt includes MANDATORY instructions: DRAFT watermark, no degree claim, no commercial IT claim, no MellyTrade as commercial claim.
- `test_no_fabrication.py` asserts that generated cover letters contain `DRAFT — requires human review`.
- `test_no_fabrication.py` asserts generated cover letters do not contain phrases like "commercial experience", "I have a degree", "university", "matura completed".
- Extractor falls back gracefully if `OPENAI_API_KEY` is not set (raises `ConfigError`, not crashes).

**Safety constraints:**
- No real job description from a real company in committed test fixtures.
- No personal name/email/address in committed test fixtures.
- API key loaded from `.env` via `python-dotenv`.

**Acceptance criteria:**
- `test_no_fabrication.py` passes with 0 failures (can mock the API response in tests).
- Extraction prompt produces valid JSON that passes `job_schema.py` validation.
- Cover letter prompt output always includes the DRAFT watermark.

**Status:** Not started

---

## JOBSCAN-005 — Source Adapters (Mock / No Scraping)

**Scope:** Build controlled job discovery adapters. Phase 1: manual paste + mock adapter. Phase 2: RSS feed adapter (no scraping).

**Files expected:**
- `job_scanner/sources/__init__.py`
- `job_scanner/sources/manual_adapter.py` (paste raw text → job record)
- `job_scanner/sources/mock_adapter.py` (returns 5 synthetic jobs for testing)
- `job_scanner/sources/rss_adapter.py` (reads RSS feeds, normalises to job schema)
- `job_scanner/tests/test_sources.py`

**Validation:**
- Manual adapter: paste text → returns normalised job dict.
- Mock adapter: returns 5 deterministic synthetic job records for offline testing.
- RSS adapter: reads a real RSS URL (with rate limiting), normalises 3 fields (title, company, link) minimum.
- RSS adapter: respects `RATE_LIMIT_SECONDS` env var.
- RSS adapter: stores source URL and retrieved_at timestamp.
- All adapters produce output that passes `job_schema.py` validation.

**Safety constraints:**
- RSS adapter must not POST to any URL.
- RSS adapter only fetches permitted public feeds.
- No browser automation (Playwright, Selenium) in any adapter.

**Acceptance criteria:**
- `test_sources.py` passes with 0 failures using mock adapter (no real network in CI).
- Manual adapter is usable from CLI without any API key.
- RSS adapter is gated behind an explicit `--source rss` flag.

**Status:** Not started

---

## JOBSCAN-006 — Report Output

**Scope:** Build the daily and weekly report generators.

**Files expected:**
- `job_scanner/report.py`
- `job_scanner/templates/daily_report.md.jinja`
- `job_scanner/templates/weekly_report.md.jinja`
- `job_scanner/tests/test_report.py`

**Validation:**
- Daily report: top 5 jobs by score, score + tag per job, action list (apply / learn / skip).
- Weekly report: skill gap trends across saved jobs, top bridge roles, highest-priority portfolio task, suggested course from roadmap, application status summary.
- Reports render to clean markdown.
- Reports do not contain any fabricated content or claims.
- Report output is saved to `output/reports/YYYY-MM-DD_daily.md` or `YYYY-WW_weekly.md`.

**Safety constraints:**
- Reports marked as advisory only at the top.
- No report includes auto-generated application submission confirmation.

**Acceptance criteria:**
- `test_report.py` passes with 0 failures using mock job data.
- Daily report renders in under 2 seconds.
- Report files are saved and retrievable without overwriting previous reports.

**Status:** Not started

---

## JOBSCAN-007 — Dashboard MVP

**Scope:** Build a minimal Streamlit or FastAPI + React read-only dashboard for saved jobs and reports.

**Files expected (Streamlit MVP):**
- `job_scanner/dashboard.py` (Streamlit)
- or `job_scanner_api/app/routes/jobs.py` (FastAPI GET routes)

**Validation (Streamlit):**
- Displays saved jobs from SQLite with score badges and tags.
- Clicking a job shows: score breakdown, gap list, recruiter notes.
- Draft cover letter is visible but clearly marked `DRAFT — review before use`.
- No apply button, no POST to external sites.
- No delete or edit actions on job records (read-only view only).

**Safety constraints:**
- Dashboard is read-only.
- No form submission to job boards.
- No storage of API keys in dashboard code.

**Acceptance criteria:**
- Dashboard launches with `streamlit run dashboard.py` or `uvicorn`.
- All displayed drafts show DRAFT watermark.
- No HTTP POST to external services from the dashboard.

**Status:** Not started

---

## JOBSCAN-008 — Tailored CV / Cover Letter Draft Generator

**Scope:** Build the per-job CV bullet and cover letter draft generator with mandatory human approval step before saving final draft.

**Files expected:**
- `job_scanner/strategy.py`
- `job_scanner/tests/test_strategy.py`
- `job_scanner/tests/test_no_fabrication.py` (extended)

**Validation:**
- `generate_cv_bullets(job, profile)` returns bullets based only on verified portfolio evidence.
- `generate_cover_letter_draft(job, profile)` returns draft with DRAFT watermark on first line.
- Human approval step: CLI prompts `Review draft and type APPROVE to save, or SKIP to discard`.
- Saved drafts go to `output/drafts/YYYY-MM-DD_{job_id}_cover_letter.md`.
- All drafts include: target role, candidate name, DRAFT watermark, revision date.

**Safety constraints:**
- No draft is automatically sent or submitted.
- `test_no_fabrication.py` asserts the following are NEVER present in generated output:
  - "I have completed my matura"
  - "I have a university degree"
  - "years of commercial IT experience"
  - "my production system"
  - MellyTrade described as "commercial product" or "live system"

**Acceptance criteria:**
- `test_no_fabrication.py` passes with 0 failures (mocked API responses).
- Human approval step cannot be bypassed programmatically.
- Drafts are saved only after explicit APPROVE input.

**Status:** Not started

---

## JOBSCAN-009 — Weekly Opportunity Review

**Scope:** Build the weekly review workflow: aggregate skill gaps, rank bridge roles, generate weekly action plan.

**Files expected:**
- `job_scanner/weekly_review.py`
- `job_scanner/tests/test_weekly_review.py`
- `output/reports/` (output directory, gitignored)

**Validation:**
- Aggregates skill gaps across all jobs saved in the past 7 days.
- Ranks top 3 most common missing skills.
- Maps each gap to a course from `docs/career/course_certification_roadmap.md`.
- Maps each gap to a portfolio task (new feature to add to MellyTrade or Job Scanner Agent).
- Generates 7-day action plan: apply (N jobs), learn (skill), build (portfolio task), document.
- Weekly review is saved to `output/reports/YYYY-WW_weekly_review.md`.

**Safety constraints:**
- No auto-apply actions in the action plan.
- Action plan items are advisory.
- Output includes advisory disclaimer.

**Acceptance criteria:**
- `test_weekly_review.py` passes with 0 failures using synthetic job data.
- Action plan contains at least one apply, one learn, and one build item.
- Weekly report is saved without overwriting previous weeks.

**Status:** Not started

---

## Implementation Order

```
Now (this session):    CAREER-001, CAREER-002, CAREER-003, CAREER-004 — Complete
Next sprint:           JOBSCAN-001 (candidate profile + README)
                       JOBSCAN-002 (schema + SQLite)
Then:                  JOBSCAN-003 (scoring engine)
                       JOBSCAN-004 (LLM prompts + no-fabrication tests)
Then:                  JOBSCAN-005 (source adapters)
                       JOBSCAN-006 (report output)
Then:                  JOBSCAN-007 (dashboard MVP)
                       JOBSCAN-008 (cover letter generator)
                       JOBSCAN-009 (weekly review)
```

---

## Acceptance Criteria Summary (Whole Project)

- A pasted job description produces a structured JSON record.
- Scoring is deterministic.
- No generated content claims commercial IT employment.
- No generated content claims completed degree or matura.
- No generated content presents MellyTrade as a commercial product.
- Every cover letter draft has the DRAFT watermark on line 1.
- The tool has no HTTP POST path to any job board.
- All API keys are in `.env`, not in source code.
- `test_no_fabrication.py` passes before any feature merges.
- `test_scorer.py` has at least 10 test cases covering edge cases.
