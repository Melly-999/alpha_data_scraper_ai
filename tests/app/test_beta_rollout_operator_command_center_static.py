from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMMAND_CENTER_DOC = (
    REPO_ROOT / "docs" / "beta" / "beta_rollout_operator_command_center.md"
)
MASTER_CHECKLIST_DOC = (
    REPO_ROOT / "docs" / "qa" / "beta_rollout_operator_master_checklist.md"
)
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


class TestCommandCenterDocExists:
    def test_command_center_doc_exists(self) -> None:
        assert COMMAND_CENTER_DOC.is_file(), f"missing doc: {COMMAND_CENTER_DOC}"


class TestMasterChecklistDocExists:
    def test_master_checklist_doc_exists(self) -> None:
        assert MASTER_CHECKLIST_DOC.is_file(), f"missing doc: {MASTER_CHECKLIST_DOC}"


class TestPlanDocReferencesBetaOps001:
    @pytest.fixture(scope="class")
    def plan_text(self) -> str:
        return _read(PLAN_DOC)

    def test_plan_mentions_beta_ops_001(self, plan_text: str) -> None:
        assert "BETA-OPS-001" in plan_text

    def test_plan_mentions_docs_only_scope(self, plan_text: str) -> None:
        lower = plan_text.lower()
        assert "no runtime behavior changed" in lower
        assert "no tester access granted" in lower
        assert "no invite sent" in lower
        assert "no tester approved automatically" in lower


class TestCommandCenterContent:
    @pytest.fixture(scope="class")
    def command_center_text(self) -> str:
        return _read(COMMAND_CENTER_DOC)

    def test_command_center_mentions_safety_posture(
        self, command_center_text: str
    ) -> None:
        for token in (
            "autotrade=false",
            "dry_run=true",
            "read_only=true",
            "live_orders_blocked=true",
            "max risk <=1%",
        ):
            assert token in command_center_text

    def test_command_center_links_key_docs(self, command_center_text: str) -> None:
        for path in (
            "source_only_beta_package_review.md",
            "source_only_beta_preflight_checklist.md",
            "source_only_beta_rollout_gate.md",
            "source_only_first_tester_rollout.md",
            "source_only_tester_invite_message.md",
            "source_only_tester_feedback_form.md",
            "local_demo_tester_smoke_checklist.md",
            "local_demo_404_regression_checklist.md",
            "first_source_only_tester_feedback_tracker.md",
            "first_source_only_tester_feedback_review_gate.md",
            "second_source_only_tester_expansion_gate.md",
            "second_source_only_tester_pre_access_checklist.md",
        ):
            assert path in command_center_text

    def test_command_center_includes_all_phases(self, command_center_text: str) -> None:
        lower = command_center_text.lower()
        for token in ("phase 0", "phase 1", "phase 2", "phase 3", "phase 4"):
            assert token in lower

    def test_command_center_has_pass_hold_blocked(
        self, command_center_text: str
    ) -> None:
        lower = command_center_text.lower()
        assert "pass" in lower
        assert "hold" in lower
        assert "blocked" in lower

    def test_command_center_has_p0_p1_p2_p3(self, command_center_text: str) -> None:
        for token in ("P0", "P1", "P2", "P3"):
            assert token in command_center_text

    def test_command_center_says_no_access_or_invites_automatically(
        self, command_center_text: str
    ) -> None:
        lower = command_center_text.lower()
        assert "does not grant access" in lower
        assert "send invites automatically" in lower or "send invites" in lower
        assert "approve testers automatically" in lower

    def test_command_center_mentions_no_secrets_or_account_ids(
        self, command_center_text: str
    ) -> None:
        lower = command_center_text.lower()
        assert "secrets" in lower
        assert "account ids" in lower


class TestMasterChecklistContent:
    @pytest.fixture(scope="class")
    def checklist_text(self) -> str:
        return _read(MASTER_CHECKLIST_DOC)

    def test_checklist_mentions_safety_posture(self, checklist_text: str) -> None:
        for token in (
            "autotrade=false",
            "dry_run=true",
            "read_only=true",
            "live_orders_blocked=true",
            "max risk <=1%",
        ):
            assert token in checklist_text

    def test_checklist_includes_steps(self, checklist_text: str) -> None:
        lower = checklist_text.lower()
        for token in ("step 1", "step 2", "step 3", "step 4", "step 5", "step 6"):
            assert token in lower

    def test_checklist_mentions_result_labels(self, checklist_text: str) -> None:
        lower = checklist_text.lower()
        for token in ("pass", "hold", "blocked"):
            assert token in lower
        assert "pass with notes" in lower

    def test_checklist_mentions_stop_conditions(self, checklist_text: str) -> None:
        lower = checklist_text.lower()
        for token in (
            "live trading appears enabled",
            "order/execution controls",
            "broker credentials",
            "safety banner is missing",
            "dry_run=false",
            "read_only=false",
            "account ids",
            "guaranteed profit",
            "investment advice",
        ):
            assert token in lower

    def test_checklist_mentions_severity_labels(self, checklist_text: str) -> None:
        for token in ("P0", "P1", "P2", "P3"):
            assert token in checklist_text

    def test_checklist_mentions_no_auto_access_or_invites(
        self, checklist_text: str
    ) -> None:
        lower = checklist_text.lower()
        assert "does not grant access" in lower
        assert "send invites automatically" in lower

    def test_checklist_mentions_opencode_and_secrets(self, checklist_text: str) -> None:
        lower = checklist_text.lower()
        assert ".opencode" in lower
        assert "stash untouched" in lower
        assert "secrets" in lower


class TestThisFileIsReadOnly:
    def test_no_process_execution_imports(self) -> None:
        banned = ("subprocess", "multiprocessing", "os.system", "powershell")
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

    def test_no_access_or_message_imports(self) -> None:
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
                assert (
                    token not in lower
                ), f"unexpected access/message import line: {line!r}"

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
