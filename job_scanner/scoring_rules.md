# Job Scanner Agent — Scoring Rules

**ADVISORY ONLY. Scores are guidance for human decision-making. No auto-apply. No fabricated claims. Manual review required.**

Design doc: [docs/career/job_scanner_agent_design.md](../docs/career/job_scanner_agent_design.md)

---

## Score Model Overview

Every job is scored on a 0–100 scale against the candidate profile. The score is deterministic: the same job and the same profile always produce the same score.

The score answers one question: *How accessible is this role to this specific candidate, honestly, without fabricating any claim?*

Higher is better. A score of 65+ means the candidate can apply today with their current portfolio. A score below 25 means the role is not accessible without misrepresenting qualifications.

---

## Scoring Categories and Weights

| Category | Max Points | Description |
|---|---:|---|
| Role fit | 25 | Job title, responsibilities, and domain match to target roles and candidate background |
| Skill fit | 25 | Required and nice-to-have skills vs. candidate's actual verified skills |
| Project evidence fit | 20 | How much of the job's requirements is covered by MellyTrade and documented portfolio work |
| Bridge-role fit | 10 | Customer service + tech overlap bonus — only awarded if bridge-role criteria are met |
| Location / work mode fit | 10 | Role accessible from Poland; remote or hybrid available |
| Language, seniority, and education fit | 10 | Language requirements met; seniority accessible; degree/matura conditions acceptable |
| **Total** | **100** | |

---

## Category Scoring Details

### Role Fit (0–25)

| Condition | Points |
|---|---:|
| Job title matches a primary target role exactly | 20–25 |
| Job title is a close variant of a target role | 12–19 |
| Responsibilities heavily overlap with candidate background | +3–5 bonus (within cap) |
| Domain is FinTech, SaaS, AI, or technical support | +3–5 bonus (within cap) |
| Job title has no overlap with target roles | 0–5 |

### Skill Fit (0–25)

Measured as: (matched_required_skills / total_required_skills) × 20 + (matched_nice_to_have / total_nice_to_have) × 5.

- Required skills matched: up to 20 points.
- Nice-to-have skills matched: up to 5 points.
- If the candidate has no match on any required skill: score for this category is capped at 5.

Skills are matched against the candidate profile `skills` field. AI tool mentions in the job description are matched against the candidate's `ai_tools` list.

### Project Evidence Fit (0–20)

MellyTrade evidence reduces the experience gap for specific requirement types:

| Job requirement type | MellyTrade evidence | Points |
|---|---|---:|
| Python backend development | FastAPI routes, scripts, pytest | 18–20 |
| REST API design / consumption | FastAPI backend, Pydantic schemas | 15–18 |
| React / TypeScript frontend | MellyTrade terminal UI | 12–16 |
| AI tooling or automation workflows | Claude Code, Codex, Copilot, Ollama | 14–18 |
| Read-only FinTech / broker systems | MellyTrade read-only surfaces | 12–16 |
| Risk management concepts | Safety posture, guardrails | 10–14 |
| Documentation and process | Recruiter docs, task queues, checklists | 10–14 |
| Database (SQLite basics) | Project storage | 8–12 |
| Docker basics | Docker Compose awareness | 6–10 |
| No relevant portfolio evidence | 0–5 |

### Bridge-Role Fit (0–10)

A bridge role bonus of up to 10 points is added when the role qualifies as a bridge role.

**Bridge-role detection**: the role must meet **any 2** of the following 6 criteria:

1. Job mentions customer support, client communication, or stakeholder management.
2. Job is in FinTech, SaaS, or trading operations domain.
3. Job title contains any of: Support, Operations, Technical Account, Customer Success, Helpdesk, Tier 1, Tier 2.
4. Job mentions CRM, ticketing systems, or escalation workflows.
5. Job does not require a CS degree.
6. Job mentions AI tools, automation, or process improvement.

If bridge-role criteria are met: +10 points.  
If not met: +0 points.

Bridge roles are also given priority rank in daily and weekly reports independent of raw score.

### Location / Work Mode Fit (0–10)

| Condition | Points |
|---|---:|
| Fully remote, Poland eligible | 10 |
| Hybrid (Poland / remote combination) | 8–10 |
| On-site in Poland, Torun or nearby | 7–9 |
| On-site in major Polish city (Warsaw, Krakow, Gdansk, Wroclaw, Poznan) | 5–8 |
| On-site elsewhere in EU with relocation support | 4–6 |
| On-site outside EU or unclear remote eligibility | 0–3 |

### Language, Seniority, and Education Fit (0–10)

| Condition | Points |
|---|---:|
| Polish required only (candidate is native) | 4 |
| English B1–B2+ required (candidate is B2+) | 3 |
| Both Polish and English required (candidate qualifies) | 4 |
| Seniority is junior or internship | 3 |
| Seniority is mid or unspecified (accessible with portfolio) | 1–2 |
| No degree required | 3 |
| Matura not required as application condition | 3 |
| Total available in category | 10 (capped) |

---

## Penalties

Penalties are applied after the base score is calculated. Penalties can reduce the score below zero (floored at 0).

| Condition | Penalty |
|---|---:|
| "Senior only" or "3+ years commercial IT experience required" | −30 |
| "Mandatory BA/BS/MA degree or equivalent required" | −25 |
| "Mandatory matura proof required at application stage" | −20 |
| "Live trading execution authority required" | −50 |
| "Heavy production ML/AI system experience required (2+ years)" | −20 |
| "Financial advisor licence or CFA required" | −50 |
| "Commercial IT employment history required (no portfolio accepted)" | −20 |
| "Clearance or compliance that requires verified employment history" | −15 |

Multiple penalties stack. A role requiring senior experience AND a degree AND live trading execution will score near 0 regardless of skill fit.

---

## Score Tags

| Tag | Score Range | Meaning | Action |
|---|---|---|---|
| `apply_now` | 65–100 | Strong fit; current portfolio is sufficient to apply | Apply with reviewed and edited cover letter |
| `stretch` | 45–64 | Possible fit; strong cover letter + bridge angle can help | Consider applying; be honest about gaps in cover letter |
| `learn_first` | 25–44 | Missing 1–2 key skills; worth addressing before applying | Close the gap first; set a timeline and revisit |
| `skip` | 0–24 | Not accessible without fabrication or ineligible | Do not apply; flag reason in review log |

---

## Bridge-Role Bonus (Detail)

When `bridge_role_detected = true`, the role receives:

1. +10 points to base score (within the bridge-role fit category).
2. Priority flag in daily and weekly reports.
3. Strategy note: "Lead with customer service + technical automation angle in cover letter."

Bridge roles are ranked before non-bridge roles of the same score tier in the priority output.

---

## Project Evidence Fit Bonus

When MellyTrade portfolio evidence directly covers a required skill:

- The skill is not counted as a blocking gap.
- The strategy brief notes: "MellyTrade provides direct evidence for this requirement."
- A CV bullet suggestion referencing the specific MellyTrade feature is included.

---

## Degree Requirement Penalty (Detail)

| Degree condition | Penalty |
|---|---:|
| "Degree required" or "BA/BS required" | −25 |
| "Degree preferred but not required" | 0 (no penalty) |
| "Degree or equivalent portfolio experience accepted" | 0 (no penalty) |
| "No degree required" | 0 (standard) |

If the degree penalty reduces the score to or below the `skip` threshold (24), the role is automatically tagged `skip` regardless of other scores.

---

## Seniority Mismatch Penalty (Detail)

| Seniority condition | Penalty |
|---|---:|
| "Senior" with "5+ years IT experience" | −30 |
| "Mid" with "2–3+ years commercial IT experience required" | −20 |
| "Junior" or "Entry-level" | 0 |
| "Internship" | 0 |
| "Unspecified" (assess from responsibilities) | 0 to −10 depending on wording |

---

## Red Flags

The following conditions are flagged as red flags in the job record. A red flag does not always cause a skip, but it does lower the score and is highlighted in the output.

| Red flag | Effect |
|---|---|
| "Live trading execution required" | −50 penalty; likely `skip` |
| "Financial advisor licence (KNF, CFA, etc.) required" | −50 penalty; likely `skip` |
| "Commercial IT employment required (no exceptions)" | −20 penalty |
| "Mandatory degree with no exceptions" | −25 penalty |
| "Mandatory matura proof at application stage" | −20 penalty |
| "Senior-only position" | −30 penalty |
| "Heavy production ML ownership 2+ years" | −20 penalty |
| "Multiple required skills with zero candidate coverage" | Lower skill_fit score; note in gap list |
| "Role involves autonomous financial decisions" | Flag only; user reviews |
| "Outside EU with no remote eligibility" | Lower location/work mode score |

---

## Hard Skip Criteria

The following conditions result in an automatic `skip` tag regardless of other scores:

- Role explicitly requires live trading execution authority.
- Role requires a financial advisor licence (KNF, FCA, CFA, or equivalent).
- Role requires commercial IT employment as a non-negotiable condition.
- Score after all penalties is below 25.
- Role involves autonomous financial decision-making without human oversight.

Hard skips are logged with the reason. The user can override a hard skip manually — the agent does not prevent the user from applying to any role.

---

## Apply-Now Criteria (65–100)

A role tagged `apply_now` means:

- The candidate can apply today with the current portfolio and honest claims.
- No fabrication is needed.
- The cover letter draft can be generated and reviewed.
- The strategy brief includes: CV bullets, cover letter draft, interview prep, missing proof checklist.

Apply-now roles must be reviewed by the user before any action. The agent does not submit anything.

---

## Stretch Criteria (45–64)

A role tagged `stretch` means:

- The candidate can apply but should expect a harder sell.
- The cover letter should address gaps honestly and lead with the bridge-role angle.
- 1–2 key skills are missing but are learnable in 2–8 weeks.
- The strategy brief includes a recommended action before applying (e.g., "Complete Docker basics course first").

---

## Missing Skill Gap Output

For every scored job, the scoring engine outputs:

```json
{
  "skill_gap": {
    "blocking": ["SQL basics", "Docker intermediate"],
    "improvement": ["LangChain / LangGraph", "CI/CD pipeline ownership"],
    "portfolio_covers": ["Python backend", "FastAPI", "REST APIs", "AI tooling", "TypeScript / React"]
  },
  "recommended_course": {
    "SQL basics": "pgExercises (free, ~2 weeks)",
    "Docker intermediate": "KodeKloud Docker Foundations (free tier, ~1 week)"
  }
}
```

Blocking gaps are skills the job lists as required that the candidate does not have. Improvement gaps are nice-to-have skills not yet evidenced.

---

## Suggested Next Portfolio Task Output

For every scored job, the engine maps each blocking gap to a concrete portfolio task:

| Blocking gap | Suggested portfolio task | Estimated effort |
|---|---|---|
| SQL basics | Add SQLite persistence to Job Scanner Agent | 1–2 days |
| Docker intermediate | Containerise Job Scanner Agent with a Dockerfile | 1 day |
| CI/CD pipeline | Add a GitHub Actions workflow to Job Scanner Agent | 1 day |
| LangGraph / LangChain | Build a minimal LangGraph agent example | 2–4 days |
| PostgreSQL | Migrate Job Scanner Agent storage from SQLite to PostgreSQL | 2–3 days |
| OpenAI API | Build a job description extractor using OpenAI Responses API | 1–2 days |
| AWS basics | Complete AWS Cloud Practitioner (P3 — defer until first role) | 2–4 weeks |

Portfolio tasks are advisory only. The user decides what to build.

---

## No-Fabrication Rule (Mandatory)

The scoring engine and strategy generator must never produce output that:

- Claims commercial IT employment not held by the candidate.
- Claims a completed matura or university degree.
- Claims MellyTrade is a commercial product, live system, or production deployment.
- Claims live trading, broker order execution, or autonomous trading capability.
- Claims senior or mid-level developer experience beyond the candidate's actual level.
- States or implies AI wrote the code without supervised human review.
- Provides financial advice, investment recommendations, or profit guarantees.

This rule is enforced by:
1. LLM system prompt with MANDATORY guardrail instructions.
2. Post-processing assertion in `tests/test_no_fabrication.py`.
3. Human review requirement on every generated draft.

If a generated output violates any of these conditions, it must be rejected and flagged. The tool must not save or surface a draft that contains fabricated claims.

---

## Manual Review Rule (Mandatory)

Every output of the scoring engine is advisory. The user must:

- Review the score breakdown before deciding to apply.
- Edit every generated draft (CV bullets, cover letter, interview prep) before any use.
- Approve cover letters with an explicit APPROVE step.
- Update application status manually.

No automated submission. No bypass of the review step.

---

## Score Example

**Job:** Junior Python Developer — FinTech Support / Automation  
**Company:** Synthetic Example Co. (no degree, hybrid remote, junior, customer service valued)

| Category | Score |
|---|---:|
| Role fit (FinTech support, Python dev — strong match) | 22 |
| Skill fit (Python ✓, FastAPI ✓, REST ✓; SQL ✗) | 20 |
| Project evidence fit (MellyTrade covers Python, FastAPI, REST, AI tools) | 18 |
| Bridge-role fit (2+ bridge criteria: SaaS/FinTech + customer service valued) | 10 |
| Location / work mode fit (hybrid, Poland eligible) | 9 |
| Language / seniority / education fit (PL native, EN B2+, junior, no degree) | 9 |
| **Subtotal** | **88** |
| Penalties (none applicable) | 0 |
| **Final score** | **88 → `apply_now`** |

**Skill gap:** SQL basics (blocking), Docker (improvement).  
**Recommended course:** pgExercises (free, ~2 weeks).  
**Recommended portfolio task:** Add SQLite/PostgreSQL persistence to Job Scanner Agent.  
**Bridge-role note:** Lead with customer service + Python + FinTech support angle.
