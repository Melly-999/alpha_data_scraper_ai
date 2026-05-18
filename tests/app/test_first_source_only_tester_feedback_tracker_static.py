from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TRACKER_DOC = REPO_ROOT / "docs" / "beta" / "first_source_only_tester_feedback_tracker.md"
REVIEW_GATE_DOC = REPO_ROOT / "docs" / "qa" / "first_source_only_tester_feedback_review_gate.md"
PLAN_DOC = REPO_ROOT / "docs" / "tasks" / "desktop_launcher_exe_plan.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _import_lines() -> list[str]:
    src = Path(__file__).read_text(encoding="utf-8")
    return [
        line.strip()
        for line in src.splitlines()
        if line.strip().startswith(("import ", "from "))
        and not line.strip().startswith("#")
    ]


class TestFeedbackTrackerDoc:
    @pytest.fixture(scope="class")
    def tracker_text(self) -> str:
        return _read(TRACKER_DOC)

    def test_tracker_doc_exists(self) -> None:
        assert TRACKER_DOC.is_file(), f"missing doc: {TRACKER_DOC}"

    def test_tracker_mentions_safety_posture(self, tracker_text: str) -> None:
        for token in (
            "autotrade=false",
            "dry_run=true",
            "read_only=true",
            "live_orders_blocked=true",
            "max risk <=1%",
        ):
            assert token in tracker_text

    def test_tracker_mentions_no_broker_credentials(self, tracker_text: str) -> None:
        assert "no broker credentials" in tracker_text.lower()

    def test_tracker_mentions_no_investment_advice(self, tracker_text: str) -> None:
        assert "no investment advice" in tracker_text.lower()

    def test_tracker_mentions_no_guaranteed_profit(self, tracker_text: str) -> None:
        assert "no guaranteed profit" in tracker_text.lower()

    def test_tracker_mentions_no_live_trading(self, tracker_text: str) -> None:
        assert "no live trading" in tracker_text.lower()

    def test_tracker_mentions_no_order_execution_controls(self, tracker_text: str) -> None:
        lower = tracker_text.lower()
        assert "no order/execution controls" in lower or "no order execution controls" in lower

    def test_tracker_has_severity_definitions(self, tracker_text: str) -> None:
        for token in ("P0", "P1", "P2", "P3"):
            assert token in tracker_text

    def test_tracker_has_expansion_decision(self, tracker_text: str) -> None:
        lower = tracker_text.lower()
        assert "expansion decision" in lower
        assert "pass" in lower
        assert "hold" in lower
        assert "blocked" in lower

    def test_tracker_links_related_docs(self, tracker_text: str) -> None:
        for path in (
            "source_only_first_tester_rollout.md",
            "source_only_tester_feedback_form.md",
            "source_only_beta_rollout_gate.md",
            "local_demo_tester_smoke_checklist.md",
            "local_demo_404_regression_checklist.md",
        ):
            assert path in tracker_text


class TestFeedbackReviewGateDoc:
    @pytest.fixture(scope="class")
    def review_gate_text(self) -> str:
        return _read(REVIEW_GATE_DOC)

    def test_review_gate_doc_exists(self) -> None:
        assert REVIEW_GATE_DOC.is_file(), f"missing doc: {REVIEW_GATE_DOC}"

    def test_review_gate_mentions_safety_posture(self, review_gate_text: str) -> None:
        for token in (
            "autotrade=false",
            "dry_run=true",
            "read_only=true",
            "live_orders_blocked=true",
            "max risk <=1%",
        ):
            assert token in review_gate_text

    def test_review_gate_has_pass_hold_blocked(self, review_gate_text: str) -> None:
        lower = review_gate_text.lower()
        assert "pass" in lower
        assert "hold" in lower
        assert "blocked" in lower

    def test_review_gate_blocks_second_tester_on_p0(self, review_gate_text: str) -> None:
        lower = review_gate_text.lower()
        assert "p0" in lower
        assert "second tester" in lower
        assert "blocked" in lower

    def test_review_gate_mentions_no_public_release_or_artifacts(self, review_gate_text: str) -> None:
        lower = review_gate_text.lower()
        for token in (
            "no public release",
            "no zip",
            "no exe",
            "no installer",
            "public release",
            "zip distribution",
            "exe distribution",
            "installer distribution",
        ):
            assert token in lower

    def test_review_gate_mentions_red_flags(self, review_gate_text: str) -> None:
        lower = review_gate_text.lower()
        assert "red flag" in lower
        assert "stop immediately" in lower


class TestPlanDocUpdate:
    @pytest.fixture(scope="class")
    def plan_text(self) -> str:
        return _read(PLAN_DOC)

    def test_plan_mentions_beta_feedback_section(self, plan_text: str) -> None:
        assert "BETA-FEEDBACK-001" in plan_text

    def test_plan_mentions_feedback_tracker_docs(self, plan_text: str) -> None:
        assert "first_source_only_tester_feedback_tracker.md" in plan_text
        assert "first_source_only_tester_feedback_review_gate.md" in plan_text

    def test_plan_mentions_no_second_tester_without_pass(self, plan_text: str) -> None:
        lower = plan_text.lower()
        assert "do not invite a second tester" in lower
        assert "returns pass" in lower


class TestThisFileIsReadOnly:
    def test_no_process_execution_imports(self) -> None:
        banned = ("subprocess", "multiprocessing", "os.system", "shell", "powershell")
        for line in _import_lines():
            lower = line.lower()
            for token in banned:
                assert token not in lower, f"unexpected execution import line: {line!r}"

    def test_no_network_imports(self) -> None:
        banned = ("requests", "httpx", "aiohttp", "socket", "urllib", "webbrowser")
        for line in _import_lines():
            lower = line.lower()
            for token in banned:
                assert token not in lower, f"unexpected network import line: {line!r}"

    def test_no_grant_access_or_message_imports(self) -> None:
        banned = (
            "github",
            "pygithub",
            "ghapi",
            "discord",
            "slack",
            "oauth",
            "sendgrid",
            "mailgun",
            "smtplib",
            "twilio",
        )
        for line in _import_lines():
            lower = line.lower()
            for token in banned:
                assert token not in lower, f"unexpected access/message import line: {line!r}"

    def test_no_artifact_creation_imports(self) -> None:
        banned = ("zipfile", "tarfile", "shutil", "tempfile")
        for line in _import_lines():
            lower = line.lower()
            for token in banned:
                assert token not in lower, f"unexpected artifact import line: {line!r}"

    def test_file_uses_read_text_only_for_docs(self) -> None:
        src = Path(__file__).read_text(encoding="utf-8")
        assert "read_text" in src
        imports_blob = "\n".join(_import_lines()).lower()
        assert "write_text" not in imports_blob
        assert "subprocess" not in imports_blob
