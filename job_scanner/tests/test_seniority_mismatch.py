"""
job_scanner/tests/test_seniority_mismatch.py

Hardening tests asserting the scoring engine correctly handles seniority mismatches.

Rules under test:
- Senior-only roles receive -30 penalty regardless of skill overlap.
- "Lead", "principal", "staff" title signals trigger the senior penalty.
- Mid roles requiring commercial IT experience are penalised and not apply_now.
- Junior / internship roles with good skill overlap can score stretch or apply_now.
- Bridge roles (FinTech support, Customer Success Technical) get bridge bonus signals.
- Team leadership and production ownership requirements are logged as blocking gaps —
  never fabricated as existing candidate experience.
- Degree + seniority penalties stack correctly.
- All seniority-related scoring is fully deterministic.

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
        "matura": "in_progress",
        "formal_it_degree": False,
    },
    "experience_summary": {
        "commercial_it_years": 0,
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

SENIOR_BACKEND_JOB = {
    "title": "Senior Python Backend Developer",
    "seniority": "senior",  # hard mismatch — candidate is entry/junior level
    "remote_policy": "remote",
    "location": "Remote EU",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": ["Python", "FastAPI", "Docker", "PostgreSQL"],
    "nice_to_have_requirements": ["Kubernetes"],
    "responsibilities": [
        "Lead backend architecture decisions",
        "mentor junior developers",
        "own production services",
    ],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

MID_COMMERCIAL_JOB = {
    "title": "Python Backend Developer",
    "seniority": "mid",
    "remote_policy": "remote",
    "location": "Remote EU",
    "degree_requirement": "none",
    "matura_requirement": "none",
    # text-based penalty: "commercial IT experience required"
    "must_have_requirements": [
        "Python",
        "FastAPI",
        "PostgreSQL",
        "commercial IT experience required",
    ],
    "nice_to_have_requirements": ["Docker", "CI/CD"],
    "responsibilities": [
        "Build and own Python microservices",
        "3+ years commercial backend development",
    ],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

JUNIOR_INTERNSHIP_JOB = {
    "title": "Junior Python Backend Developer",
    "seniority": "junior",
    "remote_policy": "remote",
    "location": "Remote Poland",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": ["Python", "REST API", "Git"],
    "nice_to_have_requirements": ["FastAPI", "SQL", "Docker"],
    "responsibilities": [
        "Assist in Python backend development",
        "write tests and documentation",
    ],
    "language_requirement": {"required": ["Polish"]},
    "positive_signals": ["No degree required", "portfolio accepted"],
}

FINTECH_SUPPORT_JOB = {
    "title": "Technical Support Engineer — FinTech SaaS",
    "seniority": "junior",
    "remote_policy": "remote",
    "location": "Remote Poland",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": ["customer support", "Python basics", "Polish"],
    "nice_to_have_requirements": ["CRM", "Zendesk", "automation"],
    "responsibilities": [
        "Support SaaS fintech clients via escalation tickets",
        "improve automation workflows for support processes",
        "communicate with stakeholders on issue resolution",
    ],
    "language_requirement": {"required": ["Polish", "English"]},
    "positive_signals": ["No degree required", "customer service background valued"],
}

CUSTOMER_SUCCESS_JOB = {
    "title": "Customer Success Technical Specialist",
    "seniority": "junior",
    "remote_policy": "hybrid",
    "location": "Warsaw, Poland",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": ["customer support", "SaaS", "Python basics"],
    "nice_to_have_requirements": ["CRM", "automation", "Zendesk"],
    "responsibilities": [
        "Manage customer success workflows for SaaS clients",
        "provide technical support and escalation handling",
        "improve customer communication and process documentation",
    ],
    "language_requirement": {"required": ["Polish", "English"]},
    "positive_signals": ["No degree required", "customer-facing experience valued"],
}

LEAD_ROLE_JOB = {
    "title": "Lead Developer — Python Backend",
    # "lead developer" appears in both title and senior_signals detection
    "seniority": "senior",
    "remote_policy": "remote",
    "location": "Remote EU",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": ["Python", "FastAPI", "lead developer experience"],
    "nice_to_have_requirements": ["Kubernetes", "PostgreSQL"],
    "responsibilities": ["Lead the Python backend development team"],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

PRINCIPAL_ROLE_JOB = {
    "title": "Principal Engineer",
    # "principal engineer" appears in senior_signals text detection
    "seniority": "senior",
    "remote_policy": "remote",
    "location": "Remote EU",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": ["Python", "system design", "5+ years experience"],
    "nice_to_have_requirements": [],
    "responsibilities": [
        "Principal engineer — define technical strategy",
        "drive architecture decisions across teams",
    ],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

TEAM_LEADERSHIP_JOB = {
    "title": "Backend Engineering Manager",
    "seniority": "senior",
    "remote_policy": "remote",
    "location": "Remote EU",
    "degree_requirement": "required",
    "matura_requirement": "none",
    "must_have_requirements": [
        "manage team of 5 developers",
        "Python",
        "hiring experience",
    ],
    "nice_to_have_requirements": ["FastAPI"],
    "responsibilities": [
        "Manage and grow an engineering team",
        "conduct performance reviews",
        "own team hiring pipeline",
    ],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

PRODUCTION_OWNERSHIP_JOB = {
    "title": "Site Reliability Engineer",
    "seniority": "mid",
    "remote_policy": "remote",
    "location": "Remote EU",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": [
        "own production services",
        "Python",
        "Docker",
        "Kubernetes",
    ],
    "nice_to_have_requirements": ["Prometheus", "Grafana"],
    "responsibilities": [
        "Own production reliability and on-call rotation",
        "maintain production Kubernetes clusters",
    ],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

STACKED_PENALTY_JOB = {
    "title": "Senior Data Engineer",
    "seniority": "senior",  # → -30 penalty
    "remote_policy": "onsite",
    "location": "Berlin, Germany",
    "degree_requirement": "required",  # → -25 penalty  (stacks with senior)
    "matura_requirement": "none",
    "must_have_requirements": [
        "Python",
        "PostgreSQL",
        "Apache Spark",
        "5+ years experience",
    ],
    "nice_to_have_requirements": ["AWS", "Kubernetes"],
    "responsibilities": ["Lead data engineering team", "design data architecture"],
    "language_requirement": {"required": ["English", "German"]},
    "positive_signals": [],
}

RULES = load_rules()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _all_output_text(result: dict) -> str:
    """Collect all string content from the scoring result for text assertions."""
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
# SM-01: Senior backend role → -30 penalty; score not apply_now
# ---------------------------------------------------------------------------


def test_sm_01_senior_backend_role_gets_senior_penalty():
    result = score_job(CANDIDATE, SENIOR_BACKEND_JOB, RULES)

    assert (
        "senior_only_role" in result["penalties"]
    ), "Expected senior_only_role penalty for seniority=senior job"
    assert result["penalties"]["senior_only_role"] == -30

    # Penalty must visibly reduce the score
    base = result["categories"]["base_before_penalties"]
    assert (
        result["score"] < base
    ), f"Score {result['score']} should be below base {base} due to senior penalty"

    # Must not be apply_now — candidate is not senior
    assert (
        result["tag"] != "apply_now"
    ), f"Senior job must not be apply_now; got tag={result['tag']}, score={result['score']}"

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False


# ---------------------------------------------------------------------------
# SM-02: Mid-level with commercial IT requirement → not apply_now
# ---------------------------------------------------------------------------


def test_sm_02_mid_commercial_role_is_not_apply_now():
    result = score_job(CANDIDATE, MID_COMMERCIAL_JOB, RULES)

    # Commercial IT penalty must fire
    assert (
        "commercial_it_required_if_missing" in result["penalties"]
    ), "Expected commercial_it_required_if_missing penalty"

    # Score after penalty must be below apply_now threshold (65)
    assert result["tag"] != "apply_now", (
        f"Mid commercial role should not be apply_now; got tag={result['tag']}, "
        f"score={result['score']}"
    )

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False


# ---------------------------------------------------------------------------
# SM-03: Junior / internship role with good skill overlap → stretch or apply_now
# ---------------------------------------------------------------------------


def test_sm_03_junior_internship_role_can_score_apply_now():
    result = score_job(CANDIDATE, JUNIOR_INTERNSHIP_JOB, RULES)

    # Must reach at least stretch (45) — candidate skills strongly match
    assert result["score"] >= 45, (
        f"Junior role with strong skill match should score ≥ 45 (stretch), "
        f"got {result['score']}"
    )
    assert result["tag"] in (
        "stretch",
        "apply_now",
    ), f"Junior role should be stretch or apply_now, got tag={result['tag']}"
    assert result["hard_skip"] is False

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False


# ---------------------------------------------------------------------------
# SM-04: FinTech Support bridge role → bridge signals detected; bridge bonus awarded
# ---------------------------------------------------------------------------


def test_sm_04_fintech_support_bridge_role_gets_bridge_signals():
    result = score_job(CANDIDATE, FINTECH_SUPPORT_JOB, RULES)

    # Bridge bonus must be awarded (criteria: customer support + fintech + no degree)
    assert (
        result["categories"]["bridge_role_fit"] == 10
    ), f"Expected full bridge bonus (10), got {result['categories']['bridge_role_fit']}"

    # At least 2 distinct bridge signals must be logged
    assert (
        len(result["bridge_role_signals"]) >= 2
    ), f"Expected ≥ 2 bridge signals, got: {result['bridge_role_signals']}"

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False


# ---------------------------------------------------------------------------
# SM-05: Customer Success Technical → bridge signals and bonus
# ---------------------------------------------------------------------------


def test_sm_05_customer_success_bridge_role_gets_bridge_signals():
    result = score_job(CANDIDATE, CUSTOMER_SUCCESS_JOB, RULES)

    # "customer success" in support_titles + "customer support" in support_communication
    # + "saas" in fintech_saas_domain + no degree → multiple criteria met
    assert (
        result["categories"]["bridge_role_fit"] == 10
    ), f"Expected full bridge bonus (10), got {result['categories']['bridge_role_fit']}"
    assert (
        len(result["bridge_role_signals"]) >= 2
    ), f"Expected ≥ 2 bridge signals, got: {result['bridge_role_signals']}"

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False


# ---------------------------------------------------------------------------
# SM-06: "Lead" and "Principal" titles → senior penalty; never apply_now
# ---------------------------------------------------------------------------


def test_sm_06_lead_and_principal_roles_get_senior_penalty():
    for job in (LEAD_ROLE_JOB, PRINCIPAL_ROLE_JOB):
        result = score_job(CANDIDATE, job, RULES)

        assert (
            "senior_only_role" in result["penalties"]
        ), f"Expected senior_only_role penalty for '{job['title']}'"
        assert (
            result["penalties"]["senior_only_role"] == -30
        ), f"Expected -30 senior penalty for '{job['title']}'"
        assert result["tag"] != "apply_now", (
            f"Lead/principal role must not be apply_now; "
            f"got tag={result['tag']} for '{job['title']}'"
        )

        assert result["manual_review_required"] is True
        assert result["auto_apply_allowed"] is False


# ---------------------------------------------------------------------------
# SM-07: Team leadership required → blocking gap logged; no leadership claim
# ---------------------------------------------------------------------------


def test_sm_07_team_leadership_required_no_leadership_claim():
    result = score_job(CANDIDATE, TEAM_LEADERSHIP_JOB, RULES)

    # Leadership / management requirements must surface as blocking gaps
    blocking_lower = [g.lower() for g in result["missing_skills"]["blocking"]]
    assert any(
        "manage" in g or "team" in g or "hiring" in g for g in blocking_lower
    ), f"Expected leadership/management requirement in blocking gaps, got: {blocking_lower}"

    # Output must NOT fabricate leadership experience
    output = _all_output_text(result)
    for false_claim in (
        "can manage a team",
        "has leadership experience",
        "team management confirmed",
        "hiring experience confirmed",
    ):
        assert (
            false_claim not in output
        ), f"False leadership claim found in output: '{false_claim}'"

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False
    assert result["advisory_only"] is True
    assert result["no_fabrication_required"] is True


# ---------------------------------------------------------------------------
# SM-08: Production ownership required → blocking gap logged; no ownership claim
# ---------------------------------------------------------------------------


def test_sm_08_production_ownership_required_no_ownership_claim():
    result = score_job(CANDIDATE, PRODUCTION_OWNERSHIP_JOB, RULES)

    # "own production services" must be in blocking gaps
    blocking_lower = [g.lower() for g in result["missing_skills"]["blocking"]]
    assert any(
        "production" in g or "own" in g or "kubernetes" in g for g in blocking_lower
    ), f"Expected production/ownership/kubernetes in blocking gaps, got: {blocking_lower}"

    # Output must NOT claim production ownership
    output = _all_output_text(result)
    for false_claim in (
        "owns production services",
        "production ownership confirmed",
        "runs production systems",
        "on-call confirmed",
    ):
        assert (
            false_claim not in output
        ), f"False production ownership claim found in output: '{false_claim}'"

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False
    assert result["advisory_only"] is True
    assert result["no_fabrication_required"] is True


# ---------------------------------------------------------------------------
# SM-09: Degree + seniority penalties stack correctly
# ---------------------------------------------------------------------------


def test_sm_09_degree_plus_seniority_stacks_penalties():
    result = score_job(CANDIDATE, STACKED_PENALTY_JOB, RULES)

    # Both penalties must be present
    assert (
        "senior_only_role" in result["penalties"]
    ), "Expected senior_only_role penalty"
    assert (
        "mandatory_degree_if_not_confirmed" in result["penalties"]
    ), "Expected mandatory_degree_if_not_confirmed penalty"

    # Total penalty must be at least -55 (-30 senior + -25 degree)
    total = result["penalty_total"]
    assert total <= -55, f"Expected stacked penalty ≤ -55, got {total}"

    # Score must be skip (penalties overwhelm any base score for this role)
    assert result["tag"] == "skip", (
        f"Stacked senior+degree penalties should produce skip tag, "
        f"got tag={result['tag']}, score={result['score']}"
    )

    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False


# ---------------------------------------------------------------------------
# SM-10: Seniority mismatch scoring is fully deterministic (5 repeated calls)
# ---------------------------------------------------------------------------


def test_sm_10_seniority_scoring_is_deterministic():
    jobs_under_test = [
        SENIOR_BACKEND_JOB,
        MID_COMMERCIAL_JOB,
        LEAD_ROLE_JOB,
        PRINCIPAL_ROLE_JOB,
        STACKED_PENALTY_JOB,
    ]
    for job in jobs_under_test:
        scores = [score_job(CANDIDATE, job, RULES)["score"] for _ in range(5)]
        tags = [score_job(CANDIDATE, job, RULES)["tag"] for _ in range(5)]
        assert (
            len(set(scores)) == 1
        ), f"Non-deterministic score for '{job['title']}': {scores}"
        assert (
            len(set(tags)) == 1
        ), f"Non-deterministic tag for '{job['title']}': {tags}"
