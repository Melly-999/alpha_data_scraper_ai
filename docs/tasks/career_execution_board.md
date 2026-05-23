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

## P2 - Job Scanner MVP

| ID | Goal | Expected files | Estimated time | Dependencies | Acceptance criteria | Recommended tool |
|---|---|---|---:|---|---|---|
| P2-01 | Job Scanner README | `job_scanner/README.md` | 45 min | P0-01 | Scope states advisory-only, no auto-apply, no fabricated claims | Codex |
| P2-02 | Candidate profile example | `job_scanner/candidate_profile.example.json` | 45 min | P0-01 | Public-safe profile schema with no private contact data | Codex |
| P2-03 | Job posting example | `job_scanner/job_posting.example.json` | 30 min | P2-01 | Schema covers title, requirements, remote, seniority, degree requirement and source | Codex |
| P2-04 | Scoring rules doc | `job_scanner/scoring_rules.md` | 60 min | P2-02, P2-03 | 0-100 score with weights, red flags and bridge-role logic | Codex |
| P2-05 | Scoring prototype | `job_scanner/score_job.py` or notebook | 90-180 min | P2-04 | Manual pasted job can be scored locally without auto-apply | Codex / OpenCode |
| P2-06 | Tests | `job_scanner/tests/` | 60-120 min | P2-05 | Tests cover no-fabrication flags, senior-only penalty and degree-gated roles | Codex / OpenCode |
| P2-07 | Weekly report format | `job_scanner/weekly_report_template.md` | 45 min | P2-04 | Report groups apply-now, stretch, skip, missing skills and next portfolio tasks | Codex |
