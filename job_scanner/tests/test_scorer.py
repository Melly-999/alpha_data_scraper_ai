"""
job_scanner/tests/test_scorer.py

Advisory scoring engine tests.
All tests use inline dict fixtures — no network, no API, no env vars, no secrets.
Tests cover safety invariants, tag assignment, penalties, bridge-role detection,
hard-skip logic, and skill gap reporting.

ADVISORY TOOL ONLY. No auto-apply. No fabricated claims. Manual review required.
"""

from __future__ import annotations

import sys
import pathlib

# Make scorer importable without installing the package
sys.path.insert(0, str(pathlib.Path(__file__).parents[3]))

from job_scanner.scorer import score_job, load_rules

# ---------------------------------------------------------------------------
# Shared fixtures
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

JUNIOR_FINTECH_JOB = {
    "title": "Junior Python Developer — FinTech Support",
    "seniority": "junior",
    "remote_policy": "hybrid",
    "location": "Warsaw, Poland",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": ["Python", "REST API", "Git"],
    "nice_to_have_requirements": ["FastAPI", "SQL", "Docker"],
    "responsibilities": [
        "Support internal fintech tooling",
        "customer service communication",
        "Python scripting for automation",
    ],
    "language_requirement": {"required": ["Polish"], "nice_to_have": ["English B1+"]},
    "positive_signals": ["No degree required", "customer service valued"],
}

PARTIAL_FIT_JOB = {
    "title": "Python Backend Developer",
    "seniority": "mid",
    "remote_policy": "onsite",
    "location": "Berlin, Germany",
    "degree_requirement": "preferred",
    "matura_requirement": "none",
    "must_have_requirements": ["Python", "PostgreSQL", "Docker", "CI/CD"],
    "nice_to_have_requirements": ["FastAPI", "Kubernetes"],
    "responsibilities": ["Build backend microservices", "PostgreSQL schema design"],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

WEAK_FIT_JOB = {
    "title": "Senior Java Developer",
    "seniority": "senior",
    "remote_policy": "onsite",
    "location": "Tokyo, Japan",
    "degree_requirement": "required",
    "matura_requirement": "none",
    "must_have_requirements": ["Java", "Spring Boot", "Kubernetes", "PostgreSQL"],
    "nice_to_have_requirements": ["Scala", "Kafka"],
    "responsibilities": ["Lead backend development in Java", "System design"],
    "language_requirement": {"required": ["Japanese", "English"]},
    "positive_signals": [],
}

LIVE_TRADING_JOB = {
    "title": "Live Trading Specialist",
    "hard_skip_flags": ["live_trading_or_financial_advice_required"],
    "seniority": "mid",
    "remote_policy": "onsite",
    "location": "London",
    "degree_requirement": "required",
    "matura_requirement": "none",
    "must_have_requirements": ["live trading execution", "broker order management"],
    "nice_to_have_requirements": [],
    "responsibilities": ["Execute live trades on behalf of clients"],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

AUTO_APPLY_JOB = {
    "title": "Automated Outreach Bot Operator",
    "hard_skip_flags": ["auto_apply_or_spam_requirement"],
    "seniority": "junior",
    "remote_policy": "remote",
    "location": "Remote",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": ["bulk email automation"],
    "nice_to_have_requirements": [],
    "responsibilities": ["Mass-send application emails without human review"],
    "language_requirement": {"required": []},
    "positive_signals": [],
}

FABRICATION_JOB = {
    "title": "Senior ML Engineer",
    "hard_skip_flags": ["requires_false_claims"],
    "seniority": "senior",
    "remote_policy": "remote",
    "location": "Remote",
    "degree_requirement": "required",
    "matura_requirement": "none",
    "must_have_requirements": ["5 years commercial ML experience", "PhD"],
    "nice_to_have_requirements": [],
    "responsibilities": ["Lead production ML deployments"],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

SENIOR_ONLY_JOB = {
    "title": "Senior Python Engineer",
    "seniority": "senior",
    "remote_policy": "remote",
    "location": "Remote EU",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": ["Python", "FastAPI", "Docker"],
    "nice_to_have_requirements": ["Kubernetes"],
    "responsibilities": ["Lead backend architecture", "mentor junior developers"],
    "language_requirement": {"required": ["English"]},
    "positive_signals": [],
}

DEGREE_REQUIRED_JOB = {
    "title": "Junior Data Analyst",
    "seniority": "junior",
    "remote_policy": "hybrid",
    "location": "Warsaw, Poland",
    "degree_requirement": "required",
    "matura_requirement": "none",
    "must_have_requirements": ["Python", "SQL", "Excel"],
    "nice_to_have_requirements": ["Tableau"],
    "responsibilities": ["Analyse business data", "produce reports"],
    "language_requirement": {"required": ["Polish", "English"]},
    "positive_signals": [],
}

MATURA_REQUIRED_JOB = {
    "title": "Junior Support Specialist",
    "seniority": "junior",
    "remote_policy": "hybrid",
    "location": "Torun, Poland",
    "degree_requirement": "none",
    "matura_requirement": "required",
    "must_have_requirements": ["customer service", "Polish"],
    "nice_to_have_requirements": ["CRM"],
    "responsibilities": ["Handle customer tickets", "escalation workflows"],
    "language_requirement": {"required": ["Polish"]},
    "positive_signals": [],
}

BRIDGE_ROLE_JOB = {
    "title": "Technical Support Specialist — FinTech SaaS",
    "seniority": "junior",
    "remote_policy": "remote",
    "location": "Remote Poland",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": ["customer support", "Python basics"],
    "nice_to_have_requirements": ["CRM", "Zendesk", "automation"],
    "responsibilities": [
        "Support SaaS fintech clients",
        "triage escalation tickets via Zendesk",
        "improve automation workflows",
    ],
    "language_requirement": {"required": ["Polish", "English"]},
    "positive_signals": ["No degree required", "customer service background valued"],
}

MINIMAL_JOB = {
    "title": "Software Developer",
    "seniority": "",
    "remote_policy": "remote",
    "location": "Remote",
    "degree_requirement": "none",
    "matura_requirement": "none",
    "must_have_requirements": [],
    "nice_to_have_requirements": [],
    "responsibilities": [],
    "language_requirement": {"required": []},
    "positive_signals": [],
}

RULES = load_rules()


# ---------------------------------------------------------------------------
# TC-01: Safety invariants always present
# ---------------------------------------------------------------------------


def test_safety_invariants_always_present():
    result = score_job(CANDIDATE, JUNIOR_FINTECH_JOB, RULES)
    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False
    assert result["advisory_only"] is True
    assert result["no_fabrication_required"] is True


# ---------------------------------------------------------------------------
# TC-02: Deterministic — 5 identical calls return identical output
# ---------------------------------------------------------------------------


def test_deterministic_repeated_calls():
    results = [score_job(CANDIDATE, JUNIOR_FINTECH_JOB, RULES) for _ in range(5)]
    scores = [r["score"] for r in results]
    tags = [r["tag"] for r in results]
    assert len(set(scores)) == 1, f"Expected identical scores, got: {scores}"
    assert len(set(tags)) == 1, f"Expected identical tags, got: {tags}"


# ---------------------------------------------------------------------------
# TC-03: Apply-now tag for strong junior FinTech bridge fit
# ---------------------------------------------------------------------------


def test_apply_now_for_junior_fintech_bridge_fit():
    result = score_job(CANDIDATE, JUNIOR_FINTECH_JOB, RULES)
    assert result["score"] >= 65, f"Expected apply_now (>=65), got {result['score']}"
    assert result["tag"] == "apply_now"
    assert result["hard_skip"] is False


# ---------------------------------------------------------------------------
# TC-04: Stretch tag for partial fit (mid seniority, some skill gaps)
# ---------------------------------------------------------------------------


def test_stretch_tag_for_partial_fit():
    result = score_job(CANDIDATE, PARTIAL_FIT_JOB, RULES)
    assert (
        45 <= result["score"] <= 64
    ), f"Expected stretch (45-64), got {result['score']} / tag={result['tag']}"
    assert result["tag"] == "stretch"


# ---------------------------------------------------------------------------
# TC-05: Learn-first or skip tag for weak fit (senior Java, Japan, degree req)
# ---------------------------------------------------------------------------


def test_low_score_for_weak_fit():
    result = score_job(CANDIDATE, WEAK_FIT_JOB, RULES)
    assert (
        result["score"] <= 44
    ), f"Expected learn_first or skip (<=44), got {result['score']}"
    assert result["tag"] in ("learn_first", "skip")


# ---------------------------------------------------------------------------
# TC-06: Skip tag for hard-skip (live trading flag)
# ---------------------------------------------------------------------------


def test_skip_tag_for_live_trading_hard_skip():
    result = score_job(CANDIDATE, LIVE_TRADING_JOB, RULES)
    assert result["hard_skip"] is True
    assert result["score"] <= 24
    assert result["tag"] == "skip"


# ---------------------------------------------------------------------------
# TC-07: Skip tag for auto-apply/spam requirement
# ---------------------------------------------------------------------------


def test_skip_tag_for_auto_apply_requirement():
    result = score_job(CANDIDATE, AUTO_APPLY_JOB, RULES)
    assert result["hard_skip"] is True
    assert result["score"] <= 24
    assert result["tag"] == "skip"


# ---------------------------------------------------------------------------
# TC-08: Skip tag for fabricated claims required
# ---------------------------------------------------------------------------


def test_skip_tag_for_fabrication_requirement():
    result = score_job(CANDIDATE, FABRICATION_JOB, RULES)
    assert result["hard_skip"] is True
    assert result["score"] <= 24
    assert result["tag"] == "skip"


# ---------------------------------------------------------------------------
# TC-09: Senior-only penalty is applied
# ---------------------------------------------------------------------------


def test_senior_only_penalty_applied():
    result = score_job(CANDIDATE, SENIOR_ONLY_JOB, RULES)
    assert (
        result["penalties"].get("senior_only_role", 0) == -30
    ), f"Expected -30 senior penalty, got {result['penalties']}"
    assert "senior_only_role" in result["penalties"]


# ---------------------------------------------------------------------------
# TC-10: Mandatory degree penalty when candidate has no confirmed degree
# ---------------------------------------------------------------------------


def test_mandatory_degree_penalty_applied():
    result = score_job(CANDIDATE, DEGREE_REQUIRED_JOB, RULES)
    assert (
        result["penalties"].get("mandatory_degree_if_not_confirmed", 0) == -25
    ), f"Expected -25 degree penalty, got {result['penalties']}"
    assert "mandatory_degree_if_not_confirmed" in result["penalties"]


# ---------------------------------------------------------------------------
# TC-11: Mandatory matura penalty when matura is in_progress (not confirmed)
# ---------------------------------------------------------------------------


def test_mandatory_matura_penalty_applied():
    result = score_job(CANDIDATE, MATURA_REQUIRED_JOB, RULES)
    assert (
        result["penalties"].get("mandatory_matura_if_not_confirmed", 0) == -20
    ), f"Expected -20 matura penalty, got {result['penalties']}"
    assert "mandatory_matura_if_not_confirmed" in result["penalties"]


# ---------------------------------------------------------------------------
# TC-12: Bridge-role detection produces signals for qualifying role
# ---------------------------------------------------------------------------


def test_bridge_role_detected_for_qualifying_role():
    result = score_job(CANDIDATE, BRIDGE_ROLE_JOB, RULES)
    assert (
        result["categories"]["bridge_role_fit"] == 10
    ), f"Expected bridge bonus 10, got {result['categories']['bridge_role_fit']}"
    assert len(result["bridge_role_signals"]) >= 2


# ---------------------------------------------------------------------------
# TC-13: Bridge-role bonus NOT awarded for non-qualifying role
# ---------------------------------------------------------------------------


def test_bridge_role_not_awarded_for_weak_fit():
    result = score_job(CANDIDATE, WEAK_FIT_JOB, RULES)
    assert result["categories"]["bridge_role_fit"] == 0


# ---------------------------------------------------------------------------
# TC-14: Blocking skill gaps are reported
# ---------------------------------------------------------------------------


def test_blocking_skill_gaps_reported():
    result = score_job(CANDIDATE, PARTIAL_FIT_JOB, RULES)
    blocking = result["missing_skills"]["blocking"]
    assert len(blocking) > 0, "Expected at least one blocking gap for partial_fit_job"
    # Candidate lacks PostgreSQL and CI/CD
    blocking_lower = [g.lower() for g in blocking]
    assert any(
        "postgresql" in g or "postgres" in g or "ci" in g for g in blocking_lower
    ), f"Expected postgres or CI/CD in blocking gaps, got {blocking}"


# ---------------------------------------------------------------------------
# TC-15: Private contact fields are NOT required for scoring
# ---------------------------------------------------------------------------


def test_no_private_contact_data_required():
    # Candidate profile with no phone/email/address — scoring must succeed
    minimal_candidate = {
        "languages": [{"language": "Polish", "level": "native"}],
        "skills": {
            "programming_languages": [{"name": "Python", "level": 2}],
            "frameworks": [],
            "testing": [],
            "tooling": [],
            "ai_tools": [],
            "databases": [],
            "monitoring": [],
            "concepts": [],
        },
    }
    result = score_job(minimal_candidate, MINIMAL_JOB, RULES)
    # Must not raise; must include safety invariants
    assert "score" in result
    assert result["manual_review_required"] is True
    assert result["auto_apply_allowed"] is False


# ---------------------------------------------------------------------------
# TC-16: Score is always within 0–100 range
# ---------------------------------------------------------------------------


def test_score_clamped_to_0_100():
    jobs = [
        JUNIOR_FINTECH_JOB,
        PARTIAL_FIT_JOB,
        WEAK_FIT_JOB,
        LIVE_TRADING_JOB,
        AUTO_APPLY_JOB,
        SENIOR_ONLY_JOB,
        BRIDGE_ROLE_JOB,
        MINIMAL_JOB,
    ]
    for job in jobs:
        result = score_job(CANDIDATE, job, RULES)
        assert (
            0 <= result["score"] <= 100
        ), f"Score out of range: {result['score']} for job '{job.get('title')}'"


# ---------------------------------------------------------------------------
# TC-17: Suggested portfolio tasks emitted for known blocking gaps
# ---------------------------------------------------------------------------


def test_suggested_portfolio_tasks_for_blocking_gaps():
    result = score_job(CANDIDATE, PARTIAL_FIT_JOB, RULES)
    tasks = result["suggested_next_portfolio_tasks"]
    # Partial fit job requires Docker — candidate has level 1, may show as gap
    # At minimum the output key exists and is a dict
    assert isinstance(tasks, dict)


# ---------------------------------------------------------------------------
# TC-18: load_rules returns dict with expected keys
# ---------------------------------------------------------------------------


def test_load_rules_returns_expected_shape():
    rules = load_rules()
    assert "category_weights" in rules
    assert "penalties" in rules
    assert "score_tags" in rules
    assert "hard_skip_flags" in rules
    assert "safety_invariants" in rules or "schema_version" in rules


# ---------------------------------------------------------------------------
# TC-19: Multiple stacking penalties do not produce negative score
# ---------------------------------------------------------------------------


def test_stacking_penalties_floor_at_zero():
    # Job with several penalties stacking
    heavy_penalty_job = {
        "title": "Senior Financial Advisor",
        "hard_skip_flags": ["live_trading_or_financial_advice_required"],
        "seniority": "senior",
        "remote_policy": "onsite",
        "location": "Singapore",
        "degree_requirement": "required",
        "matura_requirement": "required",
        "must_have_requirements": ["CFA", "live trading", "5 years finance"],
        "nice_to_have_requirements": [],
        "responsibilities": ["Provide live financial advice", "execute trade orders"],
        "language_requirement": {"required": ["Mandarin", "English"]},
        "positive_signals": [],
    }
    result = score_job(CANDIDATE, heavy_penalty_job, RULES)
    assert result["score"] >= 0
    assert result["score"] <= 24  # hard skip + heavy penalties
    assert result["tag"] == "skip"


# ---------------------------------------------------------------------------
# TC-20: Remote job scores maximum on location category
# ---------------------------------------------------------------------------


def test_remote_job_scores_max_location():
    result = score_job(CANDIDATE, BRIDGE_ROLE_JOB, RULES)
    assert (
        result["categories"]["location_work_mode_fit"] == 10
    ), f"Expected 10 for remote, got {result['categories']['location_work_mode_fit']}"
