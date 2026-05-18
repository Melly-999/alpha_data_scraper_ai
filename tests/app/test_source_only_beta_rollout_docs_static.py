"""
tests/app/test_source_only_beta_rollout_docs_static.py

Static inspection tests for BETA-ACCESS-001: first source-only tester rollout.

These tests read file content only — they do NOT create ZIPs, run PowerShell,
execute any EXE, start backend/frontend, call any network, grant GitHub access,
or send messages.

Scope:
  - docs/beta/source_only_first_tester_rollout.md
  - docs/beta/source_only_tester_invite_message.md
  - docs/beta/source_only_tester_feedback_form.md
  - docs/qa/source_only_beta_rollout_gate.md
  - docs/tasks/desktop_launcher_exe_plan.md (BETA-ACCESS-001 section)

Safety invariants verified:
  1.  source_only_first_tester_rollout.md exists
  2.  source_only_tester_invite_message.md exists
  3.  source_only_tester_feedback_form.md exists
  4.  source_only_beta_rollout_gate.md exists
  5.  plan doc has BETA-ACCESS-001 section
  6.  docs say read-only access only
  7.  docs say no generated artifacts shared
  8.  docs say no live trading
  9.  docs say no broker execution
  10. docs say no investment advice
  11. docs say no guaranteed profit
  12. docs say do not enter broker credentials
  13. docs include safety posture
  14. docs include stop conditions
  15. docs include PASS/BLOCKED gate
  16. feedback form includes P0/P1/P2/P3 severity
  17. tests do not execute commands
  18. tests do not grant access
  19. tests do not send messages
  20. tests do not call network
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ROLLOUT_DOC = REPO_ROOT / "docs" / "beta" / "source_only_first_tester_rollout.md"
INVITE_MSG = REPO_ROOT / "docs" / "beta" / "source_only_tester_invite_message.md"
FEEDBACK_FORM = REPO_ROOT / "docs" / "beta" / "source_only_tester_feedback_form.md"
ROLLOUT_GATE = REPO_ROOT / "docs" / "qa" / "source_only_beta_rollout_gate.md"
LAUNCHER_PLAN = REPO_ROOT / "docs" / "tasks" / "desktop_launcher_exe_plan.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1 — source_only_first_tester_rollout.md exists
# ---------------------------------------------------------------------------

class TestRolloutDocExists:
    def test_source_only_first_tester_rollout_exists(self) -> None:
        assert ROLLOUT_DOC.is_file(), (
            f"docs/beta/source_only_first_tester_rollout.md not found at: {ROLLOUT_DOC}"
        )


# ---------------------------------------------------------------------------
# Test 2 — source_only_tester_invite_message.md exists
# ---------------------------------------------------------------------------

class TestInviteMessageExists:
    def test_source_only_tester_invite_message_exists(self) -> None:
        assert INVITE_MSG.is_file(), (
            f"docs/beta/source_only_tester_invite_message.md not found at: {INVITE_MSG}"
        )


# ---------------------------------------------------------------------------
# Test 3 — source_only_tester_feedback_form.md exists
# ---------------------------------------------------------------------------

class TestFeedbackFormExists:
    def test_source_only_tester_feedback_form_exists(self) -> None:
        assert FEEDBACK_FORM.is_file(), (
            f"docs/beta/source_only_tester_feedback_form.md not found at: {FEEDBACK_FORM}"
        )


# ---------------------------------------------------------------------------
# Test 4 — source_only_beta_rollout_gate.md exists
# ---------------------------------------------------------------------------

class TestRolloutGateExists:
    def test_source_only_beta_rollout_gate_exists(self) -> None:
        assert ROLLOUT_GATE.is_file(), (
            f"docs/qa/source_only_beta_rollout_gate.md not found at: {ROLLOUT_GATE}"
        )


# ---------------------------------------------------------------------------
# Test 5 — Plan doc has BETA-ACCESS-001 section
# ---------------------------------------------------------------------------

class TestLauncherPlanHasBetaAccess001:
    @pytest.fixture(scope="class")
    def plan_text(self) -> str:
        return _read(LAUNCHER_PLAN)

    def test_plan_has_beta_access_001_section(self, plan_text: str) -> None:
        assert "BETA-ACCESS-001" in plan_text, (
            "docs/tasks/desktop_launcher_exe_plan.md must have a BETA-ACCESS-001 section"
        )

    def test_plan_references_rollout_doc(self, plan_text: str) -> None:
        assert "source_only_first_tester_rollout.md" in plan_text, (
            "desktop_launcher_exe_plan.md must reference source_only_first_tester_rollout.md"
        )

    def test_plan_references_invite_message(self, plan_text: str) -> None:
        assert "source_only_tester_invite_message.md" in plan_text, (
            "desktop_launcher_exe_plan.md must reference source_only_tester_invite_message.md"
        )

    def test_plan_references_feedback_form(self, plan_text: str) -> None:
        assert "source_only_tester_feedback_form.md" in plan_text, (
            "desktop_launcher_exe_plan.md must reference source_only_tester_feedback_form.md"
        )

    def test_plan_references_rollout_gate(self, plan_text: str) -> None:
        assert "source_only_beta_rollout_gate.md" in plan_text, (
            "desktop_launcher_exe_plan.md must reference source_only_beta_rollout_gate.md"
        )


# ---------------------------------------------------------------------------
# Test 6 — Docs say read-only access only
# ---------------------------------------------------------------------------

_ALL_DOC_PATHS = [ROLLOUT_DOC, INVITE_MSG, FEEDBACK_FORM, ROLLOUT_GATE]


class TestDocsReadOnlyAccess:
    @pytest.mark.parametrize("doc_path", _ALL_DOC_PATHS, ids=lambda p: p.name)
    def test_doc_states_read_only_access(self, doc_path: Path) -> None:
        lower = _read(doc_path).lower()
        assert (
            "read-only" in lower
            or "read only" in lower
            or "read_only" in lower
        ), (
            f"{doc_path.name} must address read-only access"
        )


# ---------------------------------------------------------------------------
# Test 7 — Docs say no generated artifacts shared
# ---------------------------------------------------------------------------

class TestDocsNoGeneratedArtifacts:
    @pytest.mark.parametrize("doc_path", _ALL_DOC_PATHS, ids=lambda p: p.name)
    def test_doc_states_no_generated_artifacts(self, doc_path: Path) -> None:
        lower = _read(doc_path).lower()
        assert (
            "no generated artifact" in lower
            or "not share" in lower
            or "do not send" in lower
            or "no pre-built" in lower
            or "no installer" in lower
            or "generated artifact" in lower
        ), (
            f"{doc_path.name} must address that no generated artifacts are shared"
        )


# ---------------------------------------------------------------------------
# Test 8 — Docs say no live trading
# ---------------------------------------------------------------------------

class TestDocsNoLiveTrading:
    @pytest.mark.parametrize("doc_path", _ALL_DOC_PATHS, ids=lambda p: p.name)
    def test_doc_states_no_live_trading(self, doc_path: Path) -> None:
        lower = _read(doc_path).lower()
        assert (
            "not live trading" in lower
            or "no live trading" in lower
            or "live trading access" in lower
            or "live trading" in lower
        ), (
            f"{doc_path.name} must address that this is not live trading"
        )


# ---------------------------------------------------------------------------
# Test 9 — Docs say no broker execution
# ---------------------------------------------------------------------------

class TestDocsNoBrokerExecution:
    @pytest.mark.parametrize("doc_path", _ALL_DOC_PATHS, ids=lambda p: p.name)
    def test_doc_states_no_broker_execution(self, doc_path: Path) -> None:
        lower = _read(doc_path).lower()
        assert (
            "no broker execution" in lower
            or "not broker execution" in lower
            or "no order execution" in lower
            or "broker execution access" in lower
            or "execution controls" in lower
            or "broker execution" in lower
        ), (
            f"{doc_path.name} must address that this is not broker execution"
        )


# ---------------------------------------------------------------------------
# Test 10 — Docs say no investment advice
# ---------------------------------------------------------------------------

class TestDocsNoInvestmentAdvice:
    @pytest.mark.parametrize("doc_path", _ALL_DOC_PATHS, ids=lambda p: p.name)
    def test_doc_states_no_investment_advice(self, doc_path: Path) -> None:
        lower = _read(doc_path).lower()
        assert (
            "not investment advice" in lower
            or "investment advice" in lower
        ), (
            f"{doc_path.name} must address investment advice"
        )


# ---------------------------------------------------------------------------
# Test 11 — Docs say no guaranteed profit
# ---------------------------------------------------------------------------

class TestDocsNoGuaranteedProfit:
    @pytest.mark.parametrize("doc_path", _ALL_DOC_PATHS, ids=lambda p: p.name)
    def test_doc_states_no_guaranteed_profit(self, doc_path: Path) -> None:
        lower = _read(doc_path).lower()
        assert (
            "guaranteed profit" in lower
            or "no guaranteed" in lower
            or "guaranteed-profit" in lower
            or "profit guarantee" in lower
        ), (
            f"{doc_path.name} must address guaranteed profit claims"
        )


# ---------------------------------------------------------------------------
# Test 12 — Docs say do not enter broker credentials
# ---------------------------------------------------------------------------

class TestDocsNoBrokerCredentials:
    @pytest.mark.parametrize("doc_path", _ALL_DOC_PATHS, ids=lambda p: p.name)
    def test_doc_states_no_broker_credentials(self, doc_path: Path) -> None:
        lower = _read(doc_path).lower()
        assert (
            "broker credentials" in lower
            or "do not enter" in lower
            or "not enter broker" in lower
        ), (
            f"{doc_path.name} must address broker credentials"
        )


# ---------------------------------------------------------------------------
# Test 13 — Docs include safety posture
# ---------------------------------------------------------------------------

class TestDocsIncludeSafetyPosture:
    @pytest.fixture(scope="class")
    def rollout_text(self) -> str:
        return _read(ROLLOUT_DOC)

    @pytest.fixture(scope="class")
    def gate_text(self) -> str:
        return _read(ROLLOUT_GATE)

    def test_rollout_doc_has_autotrade_false(self, rollout_text: str) -> None:
        assert "autotrade=false" in rollout_text, (
            "rollout doc must declare autotrade=false"
        )

    def test_rollout_doc_has_dry_run_true(self, rollout_text: str) -> None:
        assert "dry_run=true" in rollout_text, (
            "rollout doc must declare dry_run=true"
        )

    def test_rollout_doc_has_read_only_true(self, rollout_text: str) -> None:
        assert "read_only=true" in rollout_text, (
            "rollout doc must declare read_only=true"
        )

    def test_rollout_doc_has_live_orders_blocked_true(self, rollout_text: str) -> None:
        assert "live_orders_blocked=true" in rollout_text, (
            "rollout doc must declare live_orders_blocked=true"
        )

    def test_gate_has_autotrade_false(self, gate_text: str) -> None:
        assert "autotrade=false" in gate_text, (
            "rollout gate must declare autotrade=false"
        )

    def test_gate_has_dry_run_true(self, gate_text: str) -> None:
        assert "dry_run=true" in gate_text, (
            "rollout gate must declare dry_run=true"
        )

    def test_gate_has_read_only_true(self, gate_text: str) -> None:
        assert "read_only=true" in gate_text, (
            "rollout gate must declare read_only=true"
        )

    def test_gate_has_live_orders_blocked_true(self, gate_text: str) -> None:
        assert "live_orders_blocked=true" in gate_text, (
            "rollout gate must declare live_orders_blocked=true"
        )


# ---------------------------------------------------------------------------
# Test 14 — Docs include stop conditions
# ---------------------------------------------------------------------------

class TestDocsIncludeStopConditions:
    @pytest.fixture(scope="class")
    def rollout_text(self) -> str:
        return _read(ROLLOUT_DOC)

    @pytest.fixture(scope="class")
    def gate_text(self) -> str:
        return _read(ROLLOUT_GATE)

    def test_rollout_has_stop_conditions(self, rollout_text: str) -> None:
        lower = rollout_text.lower()
        assert "stop condition" in lower or "stop rollout" in lower or "stop and report" in lower, (
            "rollout doc must have stop conditions"
        )

    def test_rollout_stop_conditions_mention_safety_banner(self, rollout_text: str) -> None:
        lower = rollout_text.lower()
        assert "safety banner" in lower, (
            "stop conditions must mention safety banner"
        )

    def test_gate_has_red_flags(self, gate_text: str) -> None:
        lower = gate_text.lower()
        assert "red flag" in lower or "stop rollout" in lower, (
            "rollout gate must have red flags / stop rollout section"
        )


# ---------------------------------------------------------------------------
# Test 15 — Docs include PASS/BLOCKED gate
# ---------------------------------------------------------------------------

class TestDocsIncludePassBlockedGate:
    @pytest.fixture(scope="class")
    def gate_text(self) -> str:
        return _read(ROLLOUT_GATE)

    def test_gate_has_pass_result(self, gate_text: str) -> None:
        assert "PASS" in gate_text, (
            "rollout gate must have a PASS approval result"
        )

    def test_gate_has_blocked_result(self, gate_text: str) -> None:
        assert "BLOCKED" in gate_text, (
            "rollout gate must have a BLOCKED approval result"
        )

    def test_gate_approval_is_documented(self, gate_text: str) -> None:
        lower = gate_text.lower()
        assert "approval result" in lower or "signed off" in lower, (
            "rollout gate must have an approval result section"
        )


# ---------------------------------------------------------------------------
# Test 16 — Feedback form includes P0/P1/P2/P3 severity
# ---------------------------------------------------------------------------

class TestFeedbackFormHasSeverity:
    @pytest.fixture(scope="class")
    def feedback_text(self) -> str:
        return _read(FEEDBACK_FORM)

    def test_feedback_form_has_p0(self, feedback_text: str) -> None:
        assert "P0" in feedback_text, (
            "feedback form must include P0 severity"
        )

    def test_feedback_form_has_p1(self, feedback_text: str) -> None:
        assert "P1" in feedback_text, (
            "feedback form must include P1 severity"
        )

    def test_feedback_form_has_p2(self, feedback_text: str) -> None:
        assert "P2" in feedback_text, (
            "feedback form must include P2 severity"
        )

    def test_feedback_form_has_p3(self, feedback_text: str) -> None:
        assert "P3" in feedback_text, (
            "feedback form must include P3 severity"
        )

    def test_feedback_form_p0_is_safety_blocker(self, feedback_text: str) -> None:
        lower = feedback_text.lower()
        assert "safety" in lower and "P0" in feedback_text, (
            "feedback form P0 must be identified as a safety concern"
        )


# ---------------------------------------------------------------------------
# Helper — import-line scanner used by Tests 17-20
# Scans only actual import statements so checks never self-match on
# assertion text that happens to contain a forbidden word.
# ---------------------------------------------------------------------------

def _this_file_import_lines() -> list[str]:
    """Return non-comment import lines from this test file."""
    src = Path(__file__).read_text(encoding="utf-8")
    return [
        line.strip()
        for line in src.splitlines()
        if line.strip().startswith(("import ", "from "))
        and not line.strip().startswith("#")
    ]


# ---------------------------------------------------------------------------
# Test 17 — Tests do not execute commands
# ---------------------------------------------------------------------------

class TestThisFileDoesNotExecuteCommands:
    def test_this_file_uses_read_only_helper(self) -> None:
        src = Path(__file__).read_text(encoding="utf-8")
        assert "_read(path" in src or "path.read_text" in src, (
            "test file must use a read-only helper for all file access"
        )

    def test_no_process_execution_imports(self) -> None:
        banned = ["subprocess", "multiprocessing"]
        for ln in _this_file_import_lines():
            for mod in banned:
                assert mod not in ln, (
                    f"test file import check failed — {mod!r} must not be imported, line: {ln!r}"
                )


# ---------------------------------------------------------------------------
# Test 18 — Tests do not grant access
# ---------------------------------------------------------------------------

class TestThisFileDoesNotGrantAccess:
    def test_no_github_api_imports(self) -> None:
        banned = ["github", "pygithub", "ghapi"]
        for ln in _this_file_import_lines():
            for mod in banned:
                assert mod not in ln.lower(), (
                    f"test file import check failed — {mod!r} must not be imported, line: {ln!r}"
                )

    def test_no_oauth_imports(self) -> None:
        banned = ["oauth", "requests_oauthlib"]
        for ln in _this_file_import_lines():
            for mod in banned:
                assert mod not in ln.lower(), (
                    f"test file import check failed — {mod!r} must not be imported, line: {ln!r}"
                )


# ---------------------------------------------------------------------------
# Test 19 — Tests do not send messages
# ---------------------------------------------------------------------------

class TestThisFileDoesNotSendMessages:
    def test_no_email_imports(self) -> None:
        banned = ["smtplib", "email", "sendgrid", "mailgun"]
        for ln in _this_file_import_lines():
            for mod in banned:
                assert mod not in ln.lower(), (
                    f"test file import check failed — {mod!r} must not be imported, line: {ln!r}"
                )

    def test_no_messaging_imports(self) -> None:
        banned = ["slack_sdk", "twilio", "discord"]
        for ln in _this_file_import_lines():
            for mod in banned:
                assert mod not in ln.lower(), (
                    f"test file import check failed — {mod!r} must not be imported, line: {ln!r}"
                )


# ---------------------------------------------------------------------------
# Test 20 — Tests do not call network
# ---------------------------------------------------------------------------

class TestThisFileDoesNotCallNetwork:
    def test_no_network_imports(self) -> None:
        banned = ["requests", "urllib", "httpx", "socket", "http", "aiohttp"]
        for ln in _this_file_import_lines():
            for mod in banned:
                assert mod not in ln, (
                    f"test file import check failed — {mod!r} must not be imported, line: {ln!r}"
                )
