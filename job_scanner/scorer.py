"""
job_scanner/scorer.py
Deterministic advisory scoring engine for the Job Scanner Agent.

ADVISORY TOOL ONLY.
- No auto-apply. No LLM calls. No network calls. No file writes by default.
- No fabricated claims. No private contact data required.
- Manual review required for every output.

Usage:
    from job_scanner.scorer import score_job, load_rules

    rules = load_rules()                          # optional
    result = score_job(candidate_profile, job)    # always returns advisory dict

Output always includes:
    manual_review_required = True
    auto_apply_allowed     = False
    advisory_only          = True
    no_fabrication_required = True
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_DEFAULT_RULES_PATH = Path(__file__).parent / "scoring_rules.json"

# ---------------------------------------------------------------------------
# Target role titles (normalized) — from scoring_rules.md
# ---------------------------------------------------------------------------
_TARGET_TITLES: list[str] = [
    "ai automation specialist",
    "ai workflow engineer",
    "technical support engineer",
    "fintech support specialist",
    "saas support specialist",
    "customer success technical specialist",
    "customer success specialist",
    "junior python backend developer",
    "junior python developer",
    "junior full-stack developer",
    "junior full stack developer",
    "junior backend developer",
    "junior software developer",
    "junior developer",
    "backend developer intern",
    "trading operations support",
    "automation specialist",
    "python developer",
    "support engineer",
    "technical support specialist",
]

# ---------------------------------------------------------------------------
# Domain keywords — give a role-fit bonus
# ---------------------------------------------------------------------------
_DOMAIN_KEYWORDS: list[str] = [
    "fintech",
    "saas",
    "artificial intelligence",
    "automation",
    "technical support",
    "customer success",
    "operations",
]

# ---------------------------------------------------------------------------
# Bridge-role detection buckets
# ---------------------------------------------------------------------------
_BRIDGE_BUCKETS: dict[str, list[str]] = {
    "support_communication": [
        "customer support",
        "client communication",
        "stakeholder management",
        "customer service",
        "client relations",
        "end user support",
        "tier 1",
        "tier 2",
        "level 1",
        "level 2",
        "helpdesk",
        "help desk",
        "user support",
    ],
    "fintech_saas_domain": [
        "fintech",
        "financial technology",
        "saas",
        "trading",
        "financial services",
        "brokerage",
        "payments",
        "banking",
        "investment",
        "capital markets",
    ],
    "support_titles": [
        "support",
        "operations",
        "technical account",
        "customer success",
        "helpdesk",
        "help desk",
        "service desk",
    ],
    "crm_ticketing": [
        "crm",
        "ticketing",
        "zendesk",
        "jira",
        "salesforce",
        "escalation",
        "intercom",
        "freshdesk",
        "hubspot",
        "servicenow",
        "customer relationship",
    ],
    "ai_automation": [
        "ai tools",
        "automation",
        "llm",
        "artificial intelligence",
        "machine learning",
        "process improvement",
        "workflow automation",
        "ai-assisted",
        "chatgpt",
        "copilot",
        "claude",
    ],
    # Criterion 5 ("no degree required") is checked via degree_requirement field
}

# ---------------------------------------------------------------------------
# Project evidence map: (job_keyword, evidence_label, max_contribution)
# MellyTrade covers all of these.
# ---------------------------------------------------------------------------
_EVIDENCE_MAP: list[tuple[str, str, int]] = [
    ("python", "Python backend — FastAPI routes, scripts, pytest", 20),
    ("fastapi", "FastAPI — MellyTrade API routes and typed schemas", 18),
    ("rest api", "REST API — FastAPI backend with Pydantic schemas", 18),
    ("pydantic", "Pydantic schema validation — MellyTrade schemas", 16),
    ("react", "React frontend — MellyTrade terminal UI", 15),
    ("typescript", "TypeScript frontend — MellyTrade terminal UI", 14),
    ("vite", "Vite build tooling — MellyTrade frontend", 10),
    ("pytest", "pytest — MellyTrade safety validation and signal tests", 14),
    ("testing", "Testing with pytest — MellyTrade signal and safety tests", 12),
    ("ai tool", "AI tooling — Claude Code, Codex, Copilot, Ollama", 17),
    ("ai automation", "AI automation — MellyTrade + Job Scanner Agent workflow", 17),
    ("llm", "LLM tooling — Claude Code, Codex, Ollama, LM Studio", 16),
    ("automation", "Process automation — MellyTrade + Job Scanner Agent", 14),
    ("fintech", "FinTech domain — MellyTrade read-only fintech workstation", 15),
    ("trading", "Trading domain awareness — MellyTrade read-only surfaces", 13),
    ("broker", "Broker adapter knowledge — MellyTrade read-only broker surfaces", 13),
    ("risk management", "Risk management — safety posture and guardrails", 14),
    ("risk", "Risk awareness — max-risk <=1%, safety guardrails", 12),
    ("audit", "Audit trail — MellyTrade audit/event feed", 11),
    ("documentation", "Documentation — recruiter docs, task queues, checklists", 12),
    ("process", "Process docs — task queues and runbooks", 11),
    ("sqlite", "SQLite basics — project storage", 10),
    ("sql", "SQL basics — SQLite project usage", 9),
    ("database", "Database basics — SQLite usage in projects", 9),
    ("docker", "Docker basics — Compose awareness in MellyTrade", 8),
    ("git", "Git/GitHub workflow — daily repo usage, branching, PRs", 12),
    ("github", "GitHub workflow — PRs, branches, Actions awareness", 12),
    ("monitoring", "Monitoring basics — Prometheus/Grafana awareness", 9),
    ("api", "REST API exposure — FastAPI backend and Pydantic schemas", 14),
    ("rest", "REST API exposure — FastAPI backend", 14),
    ("powershell", "PowerShell scripting — local dev scripts and automation", 9),
    ("script", "Python scripting — automation scripts in MellyTrade", 11),
]

# ---------------------------------------------------------------------------
# Skill gap → suggested portfolio task
# ---------------------------------------------------------------------------
_GAP_TO_TASK: dict[str, str] = {
    "sql": "Add SQLite persistence to Job Scanner Agent (1-2 days)",
    "sqlite": "Add SQLite persistence to Job Scanner Agent (1-2 days)",
    "postgresql": "Migrate Job Scanner Agent storage from SQLite to PostgreSQL (2-3 days)",
    "postgres": "Migrate Job Scanner Agent storage from SQLite to PostgreSQL (2-3 days)",
    "docker": "Containerise Job Scanner Agent with a Dockerfile (1 day)",
    "ci/cd": "Add a GitHub Actions workflow to Job Scanner Agent (1 day)",
    "github actions": "Add a GitHub Actions workflow to Job Scanner Agent (1 day)",
    "cicd": "Add a GitHub Actions workflow to Job Scanner Agent (1 day)",
    "langchain": "Build a minimal LangGraph agent example (2-4 days)",
    "langgraph": "Build a minimal LangGraph agent example (2-4 days)",
    "openai api": "Build a job description extractor using OpenAI Responses API (1-2 days)",
    "openai": "Build a job description extractor using OpenAI Responses API (1-2 days)",
    "aws": "Complete AWS Cloud Practitioner (P3 — defer until first role) (2-4 weeks)",
    "kubernetes": "Add a Kubernetes manifest to Job Scanner Agent — defer (1-2 days)",
    "machine learning": "Complete DeepLearning.AI LangGraph course (free) (1-2 weeks)",
    "ml": "Complete DeepLearning.AI LangGraph course (free) (1-2 weeks)",
    "react": "Extend MellyTrade dashboard with a new React component (1-2 days)",
    "typescript": "Add a TypeScript utility to MellyTrade frontend (1 day)",
    "java": "Java is not on the current roadmap — defer",
    "c#": "C# is not on the current roadmap — defer",
}

_POLAND_CITIES: frozenset[str] = frozenset(
    {
        "warsaw",
        "krakow",
        "gdansk",
        "wroclaw",
        "poznan",
        "lodz",
        "katowice",
        "szczecin",
        "bydgoszcz",
        "lublin",
        "torun",
        "poland",
    }
)

_EU_TERMS: frozenset[str] = frozenset(
    {
        "eu",
        "europe",
        "european union",
        "germany",
        "france",
        "netherlands",
        "ireland",
        "sweden",
        "denmark",
        "finland",
        "spain",
        "italy",
        "portugal",
        "belgium",
        "austria",
        "czech republic",
        "slovakia",
    }
)


# ===========================================================================
# Public API
# ===========================================================================


def load_rules(path: str | Path | None = None) -> dict:
    """Load scoring rules from JSON. Falls back to built-in defaults."""
    p = Path(path) if path else _DEFAULT_RULES_PATH
    if p.exists():
        with p.open(encoding="utf-8") as f:
            return json.load(f)
    return _default_rules()


def score_job(
    candidate_profile: dict,
    job_posting: dict,
    rules: dict | None = None,
) -> dict:
    """
    Score a job posting against a candidate profile.

    Deterministic: same inputs always produce the same output.
    Advisory only: does not apply, submit, send, or call any external service.
    No private contact data is required.

    Returns a dict with score, tag, category breakdown, penalties, skill gaps,
    bridge-role signals, suggested portfolio tasks, and safety invariants.
    """
    if rules is None:
        rules = load_rules()

    weights = rules.get("category_weights", _default_rules()["category_weights"])
    candidate_skills = _flatten_candidate_skills(candidate_profile)

    role_score, role_notes = _score_role_fit(candidate_profile, job_posting, weights)
    skill_score, matched, blocking, improvement = _score_skill_fit(
        candidate_skills, job_posting, weights
    )
    evidence_score, evidence_labels = _score_project_evidence(job_posting, weights)
    bridge_score, bridge_signals = _score_bridge_role(job_posting, weights)
    location_score = _score_location(job_posting, weights)
    lang_score = _score_language_seniority_education(
        candidate_profile, job_posting, weights
    )

    base = (
        role_score
        + skill_score
        + evidence_score
        + bridge_score
        + location_score
        + lang_score
    )

    penalty_total, penalty_breakdown, red_flags = _compute_penalties(
        candidate_profile, job_posting, rules
    )
    hard_skip, hard_skip_reasons = _check_hard_skips(job_posting, rules)

    raw = max(0, min(100, base + penalty_total))
    if hard_skip:
        raw = min(raw, 24)

    tag = _assign_tag(raw, rules)

    suggested_tasks = {gap: task for gap in blocking if (task := _gap_to_task(gap))}

    return {
        "score": raw,
        "max_score": 100,
        "tag": tag,
        "categories": {
            "role_fit": role_score,
            "skill_fit": skill_score,
            "project_evidence_fit": evidence_score,
            "bridge_role_fit": bridge_score,
            "location_work_mode_fit": location_score,
            "language_seniority_education_fit": lang_score,
            "base_before_penalties": base,
        },
        "penalties": penalty_breakdown,
        "penalty_total": penalty_total,
        "hard_skip": hard_skip,
        "hard_skip_reasons": hard_skip_reasons,
        "missing_skills": {
            "blocking": blocking,
            "improvement": improvement,
            "portfolio_covers": evidence_labels,
        },
        "matched_skills": matched,
        "matched_project_evidence": evidence_labels,
        "bridge_role_signals": bridge_signals,
        "red_flags": red_flags,
        "role_fit_notes": role_notes,
        "suggested_next_portfolio_tasks": suggested_tasks,
        # Safety invariants — these must never change
        "manual_review_required": True,
        "auto_apply_allowed": False,
        "advisory_only": True,
        "no_fabrication_required": True,
    }


# ===========================================================================
# Candidate skill extraction
# ===========================================================================


def _flatten_candidate_skills(profile: dict) -> set[str]:
    """Return a flat set of normalised skill names from the candidate profile."""
    skills: set[str] = set()
    skill_sections = profile.get("skills", {})

    for section in (
        "programming_languages",
        "frameworks",
        "testing",
        "tooling",
        "ai_tools",
        "databases",
        "monitoring",
    ):
        for item in skill_sections.get(section, []):
            if isinstance(item, dict):
                name = item.get("name", "")
            else:
                name = str(item)
            n = _norm(name)
            if n:
                skills.add(n)
                # Also add the root word (e.g. "python 3.11" → "python")
                root = n.split()[0]
                if len(root) > 1:
                    skills.add(root)

    for concept in skill_sections.get("concepts", []):
        if isinstance(concept, str):
            skills.add(_norm(concept))

    return skills


# ===========================================================================
# Category scorers
# ===========================================================================


def _score_role_fit(profile: dict, job: dict, weights: dict) -> tuple[int, list[str]]:
    max_pts = weights.get("role_fit", 25)
    title = _norm(job.get("title", ""))
    all_text = _norm(_all_job_text(job))
    resp_text = _norm(" ".join(job.get("responsibilities", [])))
    notes: list[str] = []

    title_score = 0
    for target in _TARGET_TITLES:
        if target in title or title in target:
            title_score = 20
            notes.append(f"Title match: '{title}' ≈ '{target}'")
            break
        target_words = set(target.split())
        title_words = set(title.split())
        common = target_words & title_words
        if len(common) >= 2:
            candidate = max(title_score, 14)
            if candidate > title_score:
                title_score = candidate
                notes.append(
                    f"Partial title overlap ({len(common)} words): {sorted(common)}"
                )
        elif len(common) == 1 and any(len(w) > 4 for w in common):
            candidate = max(title_score, 8)
            if candidate > title_score:
                title_score = candidate

    domain_bonus = 0
    for kw in _DOMAIN_KEYWORDS:
        if kw in all_text:
            domain_bonus = 4
            notes.append(f"Domain keyword: '{kw}'")
            break

    resp_bonus = 0
    candidate_concepts = {
        _norm(c)
        for c in profile.get("skills", {}).get("concepts", [])
        if isinstance(c, str)
    }
    candidate_concepts.update(
        {
            "customer service",
            "technical support",
            "documentation",
            "process",
            "python",
            "api",
            "fastapi",
        }
    )
    for concept in sorted(candidate_concepts):
        if len(concept) > 3 and concept in resp_text:
            resp_bonus = 3
            notes.append(f"Responsibility overlap: '{concept}'")
            break

    return min(title_score + domain_bonus + resp_bonus, max_pts), notes


def _score_skill_fit(
    candidate_skills: set[str],
    job: dict,
    weights: dict,
) -> tuple[int, list[str], list[str], list[str]]:
    max_pts = weights.get("skill_fit", 25)
    required = [_norm(s) for s in job.get("must_have_requirements", [])]
    nice = [_norm(s) for s in job.get("nice_to_have_requirements", [])]

    matched_req: list[str] = []
    blocking: list[str] = []
    matched_nice: list[str] = []
    improvement: list[str] = []

    for req in required:
        if _skill_matches(req, candidate_skills):
            matched_req.append(req)
        else:
            blocking.append(req)

    for n in nice:
        if _skill_matches(n, candidate_skills):
            matched_nice.append(n)
        else:
            improvement.append(n)

    if not required:
        req_score = 10
    elif not matched_req:
        req_score = 3
    else:
        req_score = round((len(matched_req) / len(required)) * 20)

    nice_score = 0
    if nice and matched_nice:
        nice_score = round((len(matched_nice) / len(nice)) * 5)

    return (
        min(req_score + nice_score, max_pts),
        matched_req + matched_nice,
        blocking,
        improvement,
    )


def _skill_matches(requirement: str, candidate_skills: set[str]) -> bool:
    """True if any candidate skill covers this requirement phrase."""
    for skill in candidate_skills:
        if skill in requirement or requirement in skill:
            return True
        skill_words = set(skill.split())
        req_words = set(requirement.split())
        overlap = skill_words & req_words
        if overlap and any(len(w) > 3 for w in overlap):
            return True
    return False


def _score_project_evidence(job: dict, weights: dict) -> tuple[int, list[str]]:
    """Score based on how much MellyTrade portfolio evidence covers job requirements."""
    max_pts = weights.get("project_evidence_fit", 20)
    all_text = _norm(_all_job_text(job))
    labels: list[str] = []
    seen: set[str] = set()
    pts_list: list[int] = []

    for kw, label, pts in _EVIDENCE_MAP:
        nkw = _norm(kw)
        if nkw in all_text and nkw not in seen:
            seen.add(nkw)
            labels.append(label)
            pts_list.append(pts)

    if not pts_list:
        return 0, []

    pts_list.sort(reverse=True)
    # Weighted average of top 3 evidence contributions
    w = [0.50, 0.30, 0.20]
    score = sum(pts_list[i] * w[i] for i in range(min(len(pts_list), 3)))
    return min(round(score), max_pts), labels


def _score_bridge_role(job: dict, weights: dict) -> tuple[int, list[str]]:
    """Award bridge-role bonus if >= 2 bridge criteria are met."""
    max_pts = weights.get("bridge_role_fit", 10)
    all_text = _norm(_all_job_text(job))
    title = _norm(job.get("title", ""))
    degree_req = _norm(job.get("degree_requirement", "required"))
    signals: list[str] = []
    criteria_met = 0

    for kw in _BRIDGE_BUCKETS["support_communication"]:
        if _norm(kw) in all_text:
            signals.append(f"Support/communication keyword: '{kw}'")
            criteria_met += 1
            break

    for kw in _BRIDGE_BUCKETS["fintech_saas_domain"]:
        if _norm(kw) in all_text:
            signals.append(f"FinTech/SaaS domain keyword: '{kw}'")
            criteria_met += 1
            break

    for kw in _BRIDGE_BUCKETS["support_titles"]:
        if _norm(kw) in title:
            signals.append(f"Support-type title keyword: '{kw}'")
            criteria_met += 1
            break

    for kw in _BRIDGE_BUCKETS["crm_ticketing"]:
        if _norm(kw) in all_text:
            signals.append(f"CRM/ticketing keyword: '{kw}'")
            criteria_met += 1
            break

    if degree_req in ("none", "no", "not required", ""):
        signals.append("No degree requirement — portfolio accepted")
        criteria_met += 1

    for kw in _BRIDGE_BUCKETS["ai_automation"]:
        if _norm(kw) in all_text:
            signals.append(f"AI/automation keyword: '{kw}'")
            criteria_met += 1
            break

    if criteria_met >= 2:
        return max_pts, signals
    return 0, signals


def _score_location(job: dict, weights: dict) -> int:
    max_pts = weights.get("location_work_mode_fit", 10)
    remote_policy = _norm(job.get("remote_policy", ""))
    location = _norm(job.get("location", ""))
    combined = remote_policy + " " + location

    if "remote" in remote_policy:
        return max_pts
    if "hybrid" in remote_policy:
        return min(max_pts, 9)
    for city in _POLAND_CITIES:
        if city in combined:
            return min(max_pts, 8)
    for term in _EU_TERMS:
        if term in combined:
            return min(max_pts, 6)
    return min(max_pts, 3)


def _score_language_seniority_education(profile: dict, job: dict, weights: dict) -> int:
    max_pts = weights.get("language_seniority_education_fit", 10)
    score = 0

    lang_req = job.get("language_requirement", {})
    required_langs = [_norm(lng) for lng in lang_req.get("required", [])]
    candidate_langs = [
        _norm(lng.get("language", "")) for lng in profile.get("languages", [])
    ]
    has_polish = any("polish" in lng for lng in candidate_langs)
    has_english = any("english" in lng for lng in candidate_langs)

    if any("polish" in lng for lng in required_langs) and has_polish:
        score += 4
    if any("english" in lng for lng in required_langs) and has_english:
        score += 3

    seniority = _norm(job.get("seniority", ""))
    if seniority in ("junior", "entry", "entry-level", "intern", "internship"):
        score += 3
    elif seniority in ("mid", "mid-level", "unspecified", ""):
        score += 1

    degree_req = _norm(job.get("degree_requirement", "required"))
    if degree_req in ("none", "no", "not required", ""):
        score += 3
    elif degree_req in ("preferred", "preferred but not required"):
        score += 1

    return min(score, max_pts)


# ===========================================================================
# Penalties and hard-skip detection
# ===========================================================================


def _compute_penalties(
    candidate_profile: dict,
    job: dict,
    rules: dict,
) -> tuple[int, dict[str, int], list[str]]:
    penalty_rules = rules.get("penalties", _default_rules()["penalties"])
    breakdown: dict[str, int] = {}
    red_flags: list[str] = []
    all_text = _norm(_all_job_text(job))
    seniority = _norm(job.get("seniority", ""))
    degree_req = _norm(job.get("degree_requirement", ""))
    matura_req = _norm(job.get("matura_requirement", ""))
    job_flags: list[str] = job.get("hard_skip_flags", [])

    # Senior-only
    senior_signals = [
        "senior",
        "5+ years",
        "5 years experience",
        "lead developer",
        "staff engineer",
        "principal engineer",
    ]
    if seniority == "senior" or any(s in all_text for s in senior_signals):
        pts = penalty_rules.get("senior_only_role", -30)
        breakdown["senior_only_role"] = pts
        red_flags.append("Senior-only or 5+ years IT experience required")

    # Mandatory degree
    degree_required_terms = {"required", "mandatory", "ba", "bs", "ma", "msc"}
    degree_text_signals = [
        "bachelor",
        "master degree",
        "university degree",
        "ba/bs",
        "bs/ms",
        "tertiary education required",
    ]
    if degree_req in degree_required_terms or any(
        kw in all_text for kw in degree_text_signals
    ):
        pts = penalty_rules.get("mandatory_degree_if_not_confirmed", -25)
        breakdown["mandatory_degree_if_not_confirmed"] = pts
        red_flags.append("Mandatory degree required — candidate has none confirmed")

    # Mandatory matura at application stage
    if matura_req in ("required", "mandatory"):
        pts = penalty_rules.get("mandatory_matura_if_not_confirmed", -20)
        breakdown["mandatory_matura_if_not_confirmed"] = pts
        red_flags.append("Mandatory matura proof required at application stage")

    # Live trading / financial advice
    live_kws = [
        "live trading",
        "live order",
        "trade execution",
        "financial advisor licence",
        "cfa required",
        "knf required",
        "broker execution",
        "autonomous trading",
        "financial advice required",
        "financial advice licence",
    ]
    if (
        any(kw in all_text for kw in live_kws)
        or "live_trading_or_financial_advice_required" in job_flags
    ):
        pts = penalty_rules.get("live_trading_or_financial_advice_required", -50)
        breakdown["live_trading_or_financial_advice_required"] = pts
        red_flags.append(
            "Live trading execution or financial advice licence required — hard skip"
        )

    # Commercial IT required (no portfolio accepted)
    commercial_kws = [
        "commercial it experience required",
        "paid it experience required",
        "professional it experience required",
        "no portfolio accepted",
        "commercial employment required",
    ]
    if (
        any(kw in all_text for kw in commercial_kws)
        or "commercial_it_required_if_missing" in job_flags
    ):
        pts = penalty_rules.get("commercial_it_required_if_missing", -20)
        breakdown["commercial_it_required_if_missing"] = pts
        red_flags.append(
            "Commercial IT employment required — candidate has portfolio only"
        )

    # Auto-apply / spam
    if "auto_apply_or_spam_requirement" in job_flags:
        pts = penalty_rules.get("auto_apply_or_spam_requirement", -100)
        breakdown["auto_apply_or_spam_requirement"] = pts
        red_flags.append("Auto-apply or bulk spam submission requirement — hard skip")

    # Sensitive data requested too early
    if "requests_sensitive_data_too_early" in job_flags:
        pts = penalty_rules.get("requests_sensitive_data_too_early", -50)
        breakdown["requests_sensitive_data_too_early"] = pts
        red_flags.append("Requests sensitive personal data before screening step")

    return sum(breakdown.values()), breakdown, red_flags


def _check_hard_skips(job: dict, rules: dict) -> tuple[bool, list[str]]:
    hard_skip_flags = rules.get("hard_skip_flags", _default_rules()["hard_skip_flags"])
    job_flags: list[str] = job.get("hard_skip_flags", [])
    reasons: list[str] = []

    for flag in hard_skip_flags:
        if flag in job_flags:
            reasons.append(flag)

    # Text-based detection for live trading (catches cases without explicit flags)
    all_text = _norm(_all_job_text(job))
    live_kws = [
        "live trading",
        "trade execution",
        "broker execution",
        "financial advisor licence",
        "autonomous trading",
        "cfa required",
        "financial advice required",
    ]
    if any(kw in all_text for kw in live_kws):
        flag = "live_trading_or_financial_advice_required"
        if flag not in reasons:
            reasons.append(flag)

    return bool(reasons), reasons


# ===========================================================================
# Tag assignment
# ===========================================================================


def _assign_tag(score: int, rules: dict) -> str:
    tags = rules.get("score_tags", _default_rules()["score_tags"])
    if score >= tags.get("apply_now", 65):
        return "apply_now"
    if score >= tags.get("stretch", 45):
        return "stretch"
    if score >= tags.get("learn_first", 25):
        return "learn_first"
    return "skip"


# ===========================================================================
# Portfolio task suggestion
# ===========================================================================


def _gap_to_task(gap: str) -> str | None:
    g = _norm(gap)
    for kw, task in _GAP_TO_TASK.items():
        if kw in g or g in kw:
            return task
    return None


# ===========================================================================
# Helpers
# ===========================================================================


def _all_job_text(job: dict) -> str:
    parts = [
        job.get("title", ""),
        job.get("company", ""),
        job.get("location", ""),
        job.get("remote_policy", ""),
        " ".join(job.get("must_have_requirements", [])),
        " ".join(job.get("nice_to_have_requirements", [])),
        " ".join(job.get("responsibilities", [])),
        job.get("degree_requirement", ""),
        job.get("matura_requirement", ""),
        job.get("notes", ""),
        " ".join(job.get("positive_signals", [])),
    ]
    return " ".join(str(p) for p in parts)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def _default_rules() -> dict:
    return {
        "schema_version": "1.0",
        "max_score": 100,
        "category_weights": {
            "role_fit": 25,
            "skill_fit": 25,
            "project_evidence_fit": 20,
            "bridge_role_fit": 10,
            "location_work_mode_fit": 10,
            "language_seniority_education_fit": 10,
        },
        "penalties": {
            "senior_only_role": -30,
            "mandatory_degree_if_not_confirmed": -25,
            "mandatory_matura_if_not_confirmed": -20,
            "live_trading_or_financial_advice_required": -50,
            "commercial_it_required_if_missing": -20,
            "auto_apply_or_spam_requirement": -100,
            "requests_sensitive_data_too_early": -50,
        },
        "score_tags": {
            "apply_now": 65,
            "stretch": 45,
            "learn_first": 25,
            "skip": 0,
        },
        "hard_skip_flags": [
            "live_trading_or_financial_advice_required",
            "auto_apply_or_spam_requirement",
            "requires_false_claims",
            "requests_sensitive_data_too_early",
        ],
    }
