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

## JOBSCAN-001 — Docs-Only Foundation

**Scope:** Create the docs-only foundation for the Job Scanner Agent: README, public-safe candidate profile example, job posting example, and scoring rules document. No runtime code. No scraping. No auto-apply. No private data.

**Branch:** `docs/jobscan-001-foundation`

**Files created:**
- `job_scanner/README.md` — purpose, scope, non-goals, advisory-only safety model, manual review requirement, scoring overview, bridge-role strategy, target roles, input/output examples, planned files, future phases
- `job_scanner/examples/candidate_profile.example.json` — public-safe placeholder candidate profile with no private contact data
- `job_scanner/examples/job_posting.example.json` — synthetic job posting schema example
- `job_scanner/scoring_rules.md` — 0–100 score model, category weights, penalties, red flags, hard skip criteria, no-fabrication rule, manual review rule

**Validation:**
- No runtime code added.
- No scraping or job board calls.
- No auto-apply path.
- No private contact details committed.
- No DOCX/PDF/media files committed.
- Privacy scan: no phone, email, address, API keys, broker IDs, fake claims found.
- Safety scan: no auto-apply, no fabricated experience, no live trading claims.

**Safety constraints:**
- No real address, phone number, private email, or broker credentials in any committed file.
- All contact fields use `[PLACEHOLDER]` format in example files.
- Salary expectation stays in private career notes only.

**Acceptance criteria:**
- README clearly states advisory-only, no auto-apply, no fabrication, no financial advice.
- Candidate profile example is versionable with no secrets.
- Scoring rules are understandable without reading code.
- No runtime code, workflow YAML, config.json, or trading safety settings modified.

**Status:** Complete (branch docs/jobscan-001-foundation)

---

## JOBSCAN-002 — Scoring Prototype

**Scope:** Build the deterministic 0–100 scoring engine. Advisory output only. No auto-apply.

**Files expected:**
- `job_scanner/scorer.py`
- `job_scanner/scoring_rules.json` (machine-readable weights)
- `job_scanner/tests/test_scorer.py`

**Validation:**
- Score components match `scoring_rules.md`: role fit (25), skill fit (25), project evidence fit (20), bridge-role fit (10), location/work mode fit (10), language/seniority/education fit (10).
- Penalties applied correctly: senior-only (−30), mandatory degree (−25), mandatory matura (−20), live trading (−50), financial advisor licence (−50), commercial IT required (−20).
- Deterministic: same input → same score on repeat runs.
- Role tags: `apply_now` (65–100), `stretch` (45–64), `learn_first` (25–44), `skip` (0–24).
- Bridge-role detection: any 2 of 6 criteria → `bridge_role_detected=true`.
- Skill gap detection: blocking vs. improvement gaps.

**Acceptance criteria:**
- `test_scorer.py` has at least 10 test cases.
- Senior-only job scores < 40.
- Portfolio-relevant junior FinTech job without degree requirement scores > 60.
- Jobs requiring live trading execution score < 25 (skip tag).
- Score is unchanged on 5 consecutive calls with same input.

**Safety constraints:**
- No auto-apply path introduced.
- No fabricated claims in any scoring output.
- No real personal data in test fixtures.

**Status:** Not started

---

## JOBSCAN-003 — No-Fabrication and Seniority Mismatch Tests

**Scope:** Build a dedicated test suite asserting that no generated output fabricates qualifications or misrepresents seniority. Tests run without live API calls (mock responses).

**Files expected:**
- `job_scanner/tests/test_no_fabrication.py`
- `job_scanner/tests/test_seniority_mismatch.py`

**Validation:**
- `test_no_fabrication.py` asserts generated cover letter drafts do NOT contain:
  - "commercial IT experience" (fabricated)
  - "I have a degree" or "university" (fabricated)
  - "matura completed" (fabricated)
  - "live trading" as a candidate capability
  - MellyTrade described as "commercial product" or "live system"
- `test_no_fabrication.py` asserts every cover letter draft contains `DRAFT — requires human review and approval before sending`.
- `test_seniority_mismatch.py` asserts senior-only jobs (3+ years IT required) are tagged `skip` or `learn_first`.
- All tests use mocked API responses — no real OpenAI calls in CI.

**Acceptance criteria:**
- All tests pass with 0 failures on mocked data.
- Tests are runnable without OPENAI_API_KEY set (mock only).

**Status:** Not started

---

## JOBSCAN-004 — Weekly Report Template

**Scope:** Create a weekly review report template. Advisory output only. No auto-apply.

**Files expected:**
- `job_scanner/weekly_report_template.md`

**Validation:**
- Template groups results into: apply-now, stretch, skip sections.
- Template includes: most common skill gaps, next portfolio task, suggested course, bridge-role highlights.
- Template includes advisory disclaimer at top.
- Template includes manual action checklist (not automated).

**Acceptance criteria:**
- Template is human-readable without running any code.
- All sections clearly marked advisory only.
- No auto-apply or auto-submit language.

**Status:** Not started

---

## JOBSCAN-005 — Optional Local CLI

**Scope:** Build a local CLI for pasting job descriptions and getting scores. Advisory output only. No HTTP POST to job boards. No auto-apply.

**Files expected:**
- `job_scanner/cli.py` (Click-based)
- `job_scanner/extractor.py` (OpenAI Responses API extraction)
- `job_scanner/prompts/extraction_system_prompt.txt`
- `job_scanner/prompts/scoring_explanation_prompt.txt`
- `job_scanner/prompts/cover_letter_draft_prompt.txt`
- `.env.example` (API key template — real key never committed)

**Validation:**
- CLI command: `python job_scanner/cli.py ingest --paste` → prompts for job text → returns score + tag + gap list.
- Extractor falls back gracefully if `OPENAI_API_KEY` is not set.
- No auto-apply path in CLI.
- Cover letter draft generation requires explicit user confirmation step before saving.
- All prompts include no-fabrication MANDATORY instructions.

**Acceptance criteria:**
- CLI runnable locally without live API key using mock adapter.
- No HTTP POST to any job board from CLI.
- Cover letter saved only after explicit APPROVE input.

**Status:** Not started

---

## JOBSCAN-006 — Optional Dashboard Integration

**Scope:** Optional: integrate Job Scanner Agent read-only view into the MellyTrade React dashboard. Deferred — implement after CLI is stable.

**Files expected (future):**
- `frontend/src/pages/JobScanner.tsx` (read-only job list)
- `frontend/src/components/ScoreBadge.tsx`
- `frontend/src/components/DraftWarning.tsx`
- FastAPI GET routes for job scanner data

**Validation (future):**
- Dashboard is GET-only for job data.
- No apply button or form submission to external services.
- All draft content clearly marked `DRAFT — review before use`.
- MellyTrade safety posture (autotrade=false, dry_run=true, live_orders_blocked=true) is not affected.

**Safety constraints:**
- No order buttons, no trade execution, no broker connection UX added.
- Dashboard integration must not modify any existing trading safety settings.

**Status:** Deferred (implement after JOBSCAN-005 is stable)

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
