# Career Execution Board

## P0 - Apply Fast

| ID | Goal | Expected files | Estimated time | Dependencies | Acceptance criteria | Recommended tool |
|---|---|---|---:|---|---|---|
| P0-01 | Verify private career notes | `C:\AI\MellyTrade_Workspace\_career\cv\career_notes.md` | 30 min | None | All private fields reviewed; TODOs confirmed or filled | User |
| P0-02 | Fill missing KPIs | `career_notes.md`, final CV outside repo | 45-90 min | P0-01 | Average calls/day, QA score, sales conversion, trained people, CRM tools marked with real values or left TODO | User |
| P0-03 | Create final DOCX/PDF outside repo | Private `_career/cv` folder only | 60-120 min | P0-01, P0-02 | Final CV exists outside repo; no private CV copied into repo | User / Claude Code |
| P0-04 | Review PL CV | Final PL CV outside repo, `docs/career/cv_mateusz_ozimkiewicz_pl.md` as draft | 45 min | P0-03 | One selected PL version is concise, honest, ATS-readable | User / Codex |
| P0-05 | Review EN CV | Final EN CV outside repo, `docs/career/cv_mateusz_ozimkiewicz_en.md` as draft | 45 min | P0-03 | One selected EN version is concise, honest, ATS-readable | User / Codex |
| P0-06 | Update LinkedIn | LinkedIn profile | 60-90 min | P0-01 | Headline, about, experience, project and GitHub link match source truth | User |
| P0-07 | Add GitHub screenshots | `docs/assets/screenshots/`, README links | 60-120 min | Working local demo | 5-7 public-safe screenshots show terminal, risk, audit, broker read-only states | Claude Code / Codex |
| P0-08 | Create For Recruiters README section | `README.md` | 45-60 min | P0-07 preferred | README has short recruiter section linking case study, screenshots and safety validation | Codex |

## P1 - Portfolio Credibility

| ID | Goal | Expected files | Estimated time | Dependencies | Acceptance criteria | Recommended tool |
|---|---|---|---:|---|---|---|
| P1-01 | Loom demo script | `docs/career/loom_demo_script.md` | 45 min | P0-07 | 2-3 minute script explains project, safety and candidate ownership | Codex |
| P1-02 | Recruiter case study short version | `docs/career/recruiter_case_study_short.md` | 30-45 min | Existing case study | One-page version suitable for GitHub/LinkedIn | Codex |
| P1-03 | GitHub profile README | GitHub profile repo README outside this repo | 60 min | P0-06 | Profile shows target roles, MellyTrade, AI-assisted workflow and contact placeholder | User / Claude Code |
| P1-04 | Course/certification roadmap final review | `docs/career/course_certification_roadmap.md` | 45 min | Target role selection | Roadmap is reduced to high-ROI courses only; no certificate collecting | Codex |
| P1-05 | First application templates | Private `_career/applications/` folder | 60-90 min | Final CV | Templates for support, AI automation, fintech support and junior backend | User / Codex |
| CAREER-005 | GitHub + LinkedIn profile copy pack | `docs/career/github_profile_readme_draft.md`, `docs/career/github_pinned_repo_descriptions.md`, `docs/career/linkedin_copy_pack.md` | 60-90 min | P0-06, P1-03 | Public-safe copy exists with placeholders, no private contact data, no overclaims, and read-only/dry-run project positioning | Codex |
| CAREER-006 | Final CV DOCX/PDF generation checklist | `docs/career/final_cv_generation_checklist.md` | 45-60 min | P0-01, P0-02, P0-03 | Draft-ready checklist exists for private final CV exports outside repo; no DOCX/PDF or private contact data committed | Codex |

## P2 - Job Scanner MVP

| ID | Goal | Expected files | Estimated time | Dependencies | Acceptance criteria | Status | Recommended tool |
|---|---|---|---:|---|---|---|---|
| JOBSCAN-001 | Docs-only foundation | `job_scanner/README.md`, `job_scanner/examples/candidate_profile.example.json`, `job_scanner/examples/job_posting.example.json`, `job_scanner/scoring_rules.md` | 120 min | P0-01 | Advisory-only disclaimer, no auto-apply, no fabricated claims, no private data, privacy scan passed, validation script passed | Complete (branch: docs/jobscan-001-foundation) | OpenCode |
| JOBSCAN-002 | Scoring prototype | `job_scanner/scorer.py`, `job_scanner/scoring_rules.json`, `job_scanner/tests/test_scorer.py` | 90-180 min | JOBSCAN-001 | Manual pasted job scored 0-100 locally; no auto-apply; 10+ test cases | Not started | OpenCode |
| JOBSCAN-003 | No-fabrication and seniority mismatch tests | `job_scanner/tests/test_no_fabrication.py`, `job_scanner/tests/test_seniority_mismatch.py` | 60-120 min | JOBSCAN-002 | All tests pass with mocked API; no fabrication phrases in generated drafts; senior-only jobs tagged skip | Not started | OpenCode |
| JOBSCAN-004 | Weekly report template | `job_scanner/weekly_report_template.md` | 45 min | JOBSCAN-001 | Report groups apply-now, stretch, skip; includes missing skills and next portfolio tasks; advisory disclaimer at top | Not started | OpenCode |
| JOBSCAN-005 | Optional local CLI | `job_scanner/cli.py`, `job_scanner/extractor.py`, `job_scanner/prompts/` | 90-180 min | JOBSCAN-002, JOBSCAN-003 | CLI runnable locally without live API key; no HTTP POST to job boards; APPROVE step required for cover letter save | Not started | OpenCode |
| JOBSCAN-006 | Optional dashboard integration | `frontend/src/pages/JobScanner.tsx`, FastAPI GET routes | Deferred | JOBSCAN-005 | GET-only; no apply button; no form submission; MellyTrade safety posture unchanged | Deferred | OpenCode |
