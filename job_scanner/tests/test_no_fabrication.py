"""
job_scanner/tests/test_no_fabrication.py

Hardening tests asserting the scoring engine NEVER produces fabricated claims.

Every output must be advisory only. The scorer must:
- Never claim the candidate has a degree they do not hold.
- Never claim matura is completed when it is in_progress.
- Never claim commercial IT employment the candidate does not have.
- Never claim senior experience or production ownership beyond the portfolio.
- Hard-skip all live trading, financial advice, and guaranteed-returns roles.
- Always carry the four safety invariants in every result.
- Suggest only learning / portfolio-building tasks, never fabrication prompts.

All tests use inline dict fixtures — no network, no API, no env vars, no secrets.

ADVISORY TOOL ONLY. No auto-apply. No fabricated claims. Manual review required.
"""

from __future__ import annotations

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parents[3]))

from job_scanner.scorer import score_job, load_rules

# ---------------------------------------------------------------------------
# Candidate profile — honest, no private contact data
# ---------------------------------------------------------------------------

CANDIDATE = {
    "languages": [
        {"language": "Polish", "level": "native"},
        {"language": "English", "level": "B2+"},
    ],
    "education_status": {
        "matura": "in_progress",    # NOT completed — penalty must fire if required
        "formal_it_degree": False,  # NO degree — penalty must fire if required
    },
    "experience_summary": {
        "commercial_it_years": 0,   # NO commercial IT employment
        "customer_service_years": 3,
    },
    "skills": {
        "programming_languages": [{"name": "Python 3.11", "level": 3}],
        "frameworks": [
            {"name": "FastAPI", "level": 2},
            {"name": "React 18", "level": 2},
            {"name": "TypeScript", "level": 2},
        ],
        "testing": [{"name": "pytest", "level": 2}],
        "tooling": [
            {"name": "Git", "level": 3},
            {"name": "Docker", "level": 1},
        ],
        "ai_tools": [{"name": "Claude Code", "level": 3}],
        "databases": [{"name": "SQLite", "level": 2}],
        "monitoring": [],
        "concepts": [
            "REST APIs",
            "risk guardrails",
            "CRM/KPI/SLA processes",
            "technical support and escalation workflows",
        ],
    },
}

# ---------------------------------------------------------------------------
# Job fixtures
# ---------------------------------------------------------------------------

DEGREE_REQUIRED_JOB = {
    "title": "Junior Python Developer",
    "seniority": "junior",
    "remote_policy": "remote",
    "location": "Remote EU",
    "degree_requirement": "required",   # candidate has NO degree
    "matura_requirement": "none",
    "must_have_requirements": ["Python", "Git", "REST API"],
    "nice_to_have_requirements": ["FastAPI"],
    "responsibilities": ["Build backend services"],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

MATURA_REQUIRED_JOB = {
    "title": "Junior Support Specialist",
    "seniority": "junior",
    "remote_policy": "hybrid",
    "location": "Warsaw, Poland",
    "degree_requirement": "none",
    "matura_requirement": "required",   # candidate's matura is in_progress (not confirmed)
    "must_have_requirements": ["customer service", "Polish"],
    "nice_to_have_requirements": ["CRM"],
    "responsibilities": ["Handle customer tickets", "escalation support"],
    "language_requirement": {"required": ["Polish"]},
    "positive_signals": [],
}

COMMERCIAL_IT_JOB = {
    "title": "Backend Developer",
    "seniority": "mid",
    "remote_policy": "remote",
    "location": "Remote EU",
    "degree_requirement": "none",
    "matura_requirement": "none",
    # The phrase "commercial IT experience required" triggers the penalty via text detection
    "must_have_requirements": ["Python", "commercial IT experience required", "PostgreSQL"],
    "nice_to_have_requirements": ["Docker"],
    "responsibilities": ["Build production microservices"],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

SENIOR_DEV_JOB = {
    "title": "Senior Python Engineer",
    "seniority": "senior",              # candidate is junior/entry level — hard mismatch
    "remote_policy": "remote",
    "location": "Remote EU",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": ["Python", "FastAPI", "Docker", "5+ years experience"],
    "nice_to_have_requirements": ["Kubernetes"],
    "responsibilities": ["Lead backend development", "mentor junior developers"],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

PRODUCTION_FINTECH_JOB = {
    "title": "FinTech Platform Engineer",
    "seniority": "mid",
    "remote_policy": "remote",
    "location": "Remote EU",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": [
        "Python",
        "production fintech platform experience",
        "2 years commercial deployment",
    ],
    "nice_to_have_requirements": ["FastAPI", "PostgreSQL"],
    "responsibilities": [
        "Own production fintech systems",
        "deploy to production environments",
    ],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

LIVE_TRADING_JOB = {
    "title": "Trading Operations Specialist",
    "seniority": "mid",
    "remote_policy": "onsite",
    "location": "London",
    "degree_requirement": "required",
    "matura_requirement": "none",
    "hard_skip_flags": ["live_trading_or_financial_advice_required"],
    "must_have_requirements": ["live trading execution", "broker order management"],
    "nice_to_have_requirements": [],
    "responsibilities": ["Execute live trades on behalf of clients"],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

FINANCIAL_ADVICE_JOB = {
    "title": "Investment Advisor",
    "seniority": "mid",
    "remote_policy": "onsite",
    "location": "Warsaw, Poland",
    "degree_requirement": "required",
    "matura_requirement": "none",
    # "financial advisor licence" triggers text-based hard-skip detection
    "must_have_requirements": ["financial advisor licence", "CFA certification"],
    "nice_to_have_requirements": [],
    "responsibilities": ["Provide financial advice to clients"],
    "language_requirement": {"required": ["Polish", "English"]},
    "positive_signals": [],
}

GUARANTEED_RETURNS_JOB = {
    "title": "Trading Results Manager",
    "seniority": "mid",
    "remote_policy": "remote",
    "location": "Remote",
    "degree_requirement": "required",
    "matura_requirement": "none",
    # Multiple hard-skip triggers: live trading + financial advice
    "must_have_requirements": [
        "guarantee client returns",
        "live trading execution",
        "financial advice required",
    ],
    "nice_to_have_requirements": [],
    "responsibilities": [
        "Guarantee profitable trades for clients",
        "execute live broker orders",
    ],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

NORMAL_JOB = {
    "title": "Junior Python Developer — FinTech",
    "seniority": "junior",
    "remote_policy": "remote",
    "location": "Remote Poland",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": ["Python", "REST API", "Git"],
    "nice_to_have_requirements": ["FastAPI", "Docker"],
    "responsibilities": ["Build Python backend services", "write tests"],
    "language_requirement": {"required": ["Polish"]},
    "positive_signals": ["No degree required", "portfolio accepted"],
}

GAP_TASK_JOB = {
    "title": "Backend Developer",
    "seniority": "junior",
    "remote_policy": "remote",
    "location": "Remote EU",
    "degree_requirement": "none",
    "matura_requirement": "none",
    # PostgreSQL → blocking gap → should map to a portfolio task, not a fabrication
    "must_have_requirements": ["Python", "PostgreSQL", "Docker", "GitHub Actions"],
    "nice_to_have_requirements": ["Kubernetes"],
    "responsibilities": ["Build backend services", "contribute to CI/CD"],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

RULES = load_rules()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _all_output_text(result: dict) -> str:
    """
    Collect every string value from the scoring result dict into one lowercase
    string for fabrication phrase scanning.
    """
    parts: list[str] = []
    for v in result.values():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    parts.append(item)
        elif isinstance(v, dict):
            for inner_v in v.values():
                if isinstance(inner_v, str):
                    parts.append(inner_v)
    return " ".join(parts).lower()


# ---------------------------------------------------------------------------
# NF-01: Mandatory degree → penalty fired; output contains no degree claim
# ---------------------------------------------------------------------------

def test_nf_01_degree_required_fires_penalty_no_false_claim():
    result = score_job(CANDIDATE, DEGREE_REQUIRED_JOB, RULES)

    # Penalty must fire
    assert "mandatory_degree_if_not_confirmed" in result["penalties"], (
        "Expected mandatory_degree_if_not_confirmed penalty for degree-required job"
    )
    assert result["penalties"]["mandatory_degree_if_not_confirmed"] == -25

    # Score is visibly penalised
    assert result["score"] < 90, "Degree penalty should reduce score below 90"

    # Output text must NOT claim the candidate holds a degree
    output = _all_output_text(result)
    for phrase in ("has a degree", "holds a degree", "degree confirmed", "university graduate"):
        assert phrase not in output, f"False degree claim in output: '{phrase}'"

    # Safety invariants always present
    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False
    assert result["advisory_only"] is True
    assert result["no_fabrication_required"] is True


# ---------------------------------------------------------------------------
# NF-02: Mandatory matura → penalty fired; output contains no matura claim
# ---------------------------------------------------------------------------

def test_nf_02_matura_required_fires_penalty_no_false_claim():
    result = score_job(CANDIDATE, MATURA_REQUIRED_JOB, RULES)

    # Penalty must fire
    assert "mandatory_matura_if_not_confirmed" in result["penalties"], (
        "Expected mandatory_matura_if_not_confirmed penalty"
    )
    assert result["penalties"]["mandatory_matura_if_not_confirmed"] == -20

    # Output must NOT claim matura is complete
    output = _all_output_text(result)
    for phrase in ("matura confirmed", "matura completed", "matura: completed", "completed matura"):
        assert phrase not in output, f"False matura claim in output: '{phrase}'"

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False
    assert result["advisory_only"] is True
    assert result["no_fabrication_required"] is True


# ---------------------------------------------------------------------------
# NF-03: Commercial IT required → penalty fired; output contains no commercial claim
# ---------------------------------------------------------------------------

def test_nf_03_commercial_it_required_fires_penalty_no_false_claim():
    result = score_job(CANDIDATE, COMMERCIAL_IT_JOB, RULES)

    # Penalty must fire via text detection of "commercial IT experience required"
    assert "commercial_it_required_if_missing" in result["penalties"], (
        "Expected commercial_it_required_if_missing penalty"
    )
    assert result["penalties"]["commercial_it_required_if_missing"] == -20

    # Output must NOT claim the candidate has commercial IT employment
    output = _all_output_text(result)
    for phrase in (
        "commercial it confirmed",
        "has commercial it",
        "commercial employment confirmed",
        "paid it experience confirmed",
    ):
        assert phrase not in output, f"False commercial IT claim in output: '{phrase}'"

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False
    assert result["advisory_only"] is True
    assert result["no_fabrication_required"] is True


# ---------------------------------------------------------------------------
# NF-04: Senior-only role → penalised; must NOT be tagged apply_now
# ---------------------------------------------------------------------------

def test_nf_04_senior_role_penalised_not_apply_now():
    result = score_job(CANDIDATE, SENIOR_DEV_JOB, RULES)

    # Senior penalty must fire
    assert "senior_only_role" in result["penalties"], (
        "Expected senior_only_role penalty for senior job"
    )
    assert result["penalties"]["senior_only_role"] == -30

    # Candidate is not senior — must NOT be apply_now
    assert result["tag"] != "apply_now", (
        f"Senior role must not be apply_now; got tag={result['tag']}, score={result['score']}"
    )

    # Output must NOT claim senior experience
    output = _all_output_text(result)
    for phrase in (
        "candidate is senior",
        "senior experience confirmed",
        "is a senior developer",
        "5 years confirmed",
    ):
        assert phrase not in output, f"False seniority claim in output: '{phrase}'"

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False
    assert result["advisory_only"] is True
    assert result["no_fabrication_required"] is True


# ---------------------------------------------------------------------------
# NF-05: Production fintech required → blocking gap logged; no production claim
# ---------------------------------------------------------------------------

def test_nf_05_production_fintech_no_production_ownership_claim():
    result = score_job(CANDIDATE, PRODUCTION_FINTECH_JOB, RULES)

    # Production / commercial requirements must be in blocking gaps
    blocking_lower = [g.lower() for g in result["missing_skills"]["blocking"]]
    assert any(
        "production" in g or "commercial" in g or "2 years" in g
        for g in blocking_lower
    ), (
        f"Expected production/commercial requirement in blocking gaps, got: {blocking_lower}"
    )

    # Evidence labels describe MellyTrade portfolio — must NOT claim production ownership
    evidence_text = " ".join(result["matched_project_evidence"]).lower()
    for false_claim in (
        "owns production",
        "runs production",
        "deployed to production clients",
        "production system owner",
    ):
        assert false_claim not in evidence_text, (
            f"False production ownership found in evidence labels: '{false_claim}'"
        )

    # If evidence is present it must reference MellyTrade or portfolio framing
    if evidence_text.strip():
        assert any(kw in evidence_text for kw in (
            "mellytrade", "portfolio", "read-only", "fastapi", "routes", "scripts",
        )), (
            f"Evidence labels must reference MellyTrade portfolio; got: {evidence_text[:200]}"
        )

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False
    assert result["advisory_only"] is True
    assert result["no_fabrication_required"] is True


# ---------------------------------------------------------------------------
# NF-06: Live trading → hard skip; score ≤ 24; tag = skip
# ---------------------------------------------------------------------------

def test_nf_06_live_trading_is_hard_skipped():
    result = score_job(CANDIDATE, LIVE_TRADING_JOB, RULES)

    assert result["hard_skip"] is True, "Live trading job must be hard-skipped"
    assert result["score"] <= 24, (
        f"Hard skip must force score ≤ 24, got {result['score']}"
    )
    assert result["tag"] == "skip", (
        f"Hard skip must produce tag=skip, got {result['tag']}"
    )

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False
    assert result["advisory_only"] is True
    assert result["no_fabrication_required"] is True


# ---------------------------------------------------------------------------
# NF-07: Financial advice licence → hard skip
# ---------------------------------------------------------------------------

def test_nf_07_financial_advice_licence_is_hard_skipped():
    result = score_job(CANDIDATE, FINANCIAL_ADVICE_JOB, RULES)

    assert result["hard_skip"] is True, (
        "Financial advisor licence requirement must be hard-skipped"
    )
    assert result["score"] <= 24, (
        f"Hard skip must force score ≤ 24, got {result['score']}"
    )
    assert result["tag"] == "skip"

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False
    assert result["advisory_only"] is True
    assert result["no_fabrication_required"] is True


# ---------------------------------------------------------------------------
# NF-08: Guaranteed trading results + live execution → hard skip
# ---------------------------------------------------------------------------

def test_nf_08_guaranteed_trading_results_is_hard_skipped():
    result = score_job(CANDIDATE, GUARANTEED_RETURNS_JOB, RULES)

    # live trading execution + financial advice required → both hard-skip triggers present
    assert result["hard_skip"] is True, (
        "Job requiring guaranteed returns + live trading must be hard-skipped"
    )
    assert result["score"] <= 24, (
        f"Hard skip score must be ≤ 24, got {result['score']}"
    )
    assert result["tag"] == "skip"

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False
    assert result["advisory_only"] is True
    assert result["no_fabrication_required"] is True


# ---------------------------------------------------------------------------
# NF-09: Every scored job always carries all four safety invariants
# ---------------------------------------------------------------------------

def test_nf_09_all_outputs_always_carry_safety_invariants():
    jobs = [
        DEGREE_REQUIRED_JOB,
        MATURA_REQUIRED_JOB,
        COMMERCIAL_IT_JOB,
        SENIOR_DEV_JOB,
        PRODUCTION_FINTECH_JOB,
        NORMAL_JOB,
        GAP_TASK_JOB,
    ]
    for job in jobs:
        result = score_job(CANDIDATE, job, RULES)
        title = job.get("title", "unknown")
        assert result["manual_review_required"] is True, (
            f"manual_review_required must always be True (job: {title})"
        )
        assert result["auto_apply_allowed"] is False, (
            f"auto_apply_allowed must always be False (job: {title})"
        )
        assert result["advisory_only"] is True, (
            f"advisory_only must always be True (job: {title})"
        )
        assert result["no_fabrication_required"] is True, (
            f"no_fabrication_required must always be True (job: {title})"
        )


# ---------------------------------------------------------------------------
# NF-10: Suggested portfolio tasks are learning/building tasks — not fabrications
# ---------------------------------------------------------------------------

def test_nf_10_suggested_portfolio_tasks_are_learning_tasks_not_fabrication():
    result = score_job(CANDIDATE, GAP_TASK_JOB, RULES)
    tasks = result["suggested_next_portfolio_tasks"]

    assert isinstance(tasks, dict), (
        "suggested_next_portfolio_tasks must be a dict"
    )

    # Phrases that would indicate the scorer is telling the user to lie
    FORBIDDEN_PHRASES = [
        "claim",
        "lie",
        "fabricate",
        "tell them you",
        "pretend",
        "say you have",
        "fake",
        "exaggerate",
        "invent",
    ]

    # Phrases that indicate legitimate learning / portfolio activity
    LEARNING_PHRASES = (
        "add", "build", "create", "containerise", "containerize",
        "migrate", "complete", "extend", "defer", "not on",
    )

    for gap, task_text in tasks.items():
        task_lower = task_text.lower()
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in task_lower, (
                f"Suggested task for gap '{gap}' contains forbidden phrase '{phrase}': {task_text}"
            )
        assert any(kw in task_lower for kw in LEARNING_PHRASES), (
            f"Suggested task for gap '{gap}' does not look like a learning/building task: {task_text}"
        )
