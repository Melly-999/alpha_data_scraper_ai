from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXPANSION_GATE_DOC = (
    REPO_ROOT / "docs" / "beta" / "second_source_only_tester_expansion_gate.md"
)
PRE_ACCESS_DOC = (
    REPO_ROOT / "docs" / "qa" / "second_source_only_tester_pre_access_checklist.md"
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


class TestExpansionGateDocExists:
    def test_expansion_gate_doc_exists(self) -> None:
        assert EXPANSION_GATE_DOC.is_file(), f"missing doc: {EXPANSION_GATE_DOC}"


class TestPreAccessChecklistDocExists:
    def test_pre_access_doc_exists(self) -> None:
        assert PRE_ACCESS_DOC.is_file(), f"missing doc: {PRE_ACCESS_DOC}"


class TestPlanDocReferencesBetaAccess002:
    @pytest.fixture(scope="class")
    def plan_text(self) -> str:
        return _read(PLAN_DOC)

    def test_plan_mentions_beta_access_002(self, plan_text: str) -> None:
        assert "BETA-ACCESS-002" in plan_text

    def test_plan_mentions_docs_only_scope(self, plan_text: str) -> None:
        lower = plan_text.lower()
        assert "no runtime behavior changed" in lower
        assert "no tester access granted" in lower
        assert "no invite sent" in lower


class TestExpansionGateContent:
    @pytest.fixture(scope="class")
    def gate_text(self) -> str:
        return _read(EXPANSION_GATE_DOC)

    def test_gate_mentions_safety_posture(self, gate_text: str) -> None:
        for token in (
            "autotrade=false",
            "dry_run=true",
            "read_only=true",
            "live_orders_blocked=true",
            "max risk <=1%",
        ):
            assert token in gate_text

    def test_gate_references_first_tester_docs(self, gate_text: str) -> None:
        for token in (
            "first_source_only_tester_feedback_tracker.md",
            "first_source_only_tester_feedback_review_gate.md",
        ):
            assert token in gate_text

    def test_gate_requires_no_p0_and_no_p1(self, gate_text: str) -> None:
        lower = gate_text.lower()
        assert "no unresolved p0" in lower
        assert "no unresolved launch-blocking p1" in lower

    def test_gate_says_only_one_second_tester(self, gate_text: str) -> None:
        lower = gate_text.lower()
        assert "only one second tester" in lower
        assert "do not invite more than one additional tester" in lower

    def test_gate_says_no_public_release_or_artifacts(self, gate_text: str) -> None:
        lower = gate_text.lower()
        for token in (
            "public release",
            "zip",
            "exe",
            "msi",
            "generated artifacts",
        ):
            assert token in lower

    def test_gate_says_no_live_trading(self, gate_text: str) -> None:
        assert "live trading" in gate_text.lower()

    def test_gate_says_no_broker_credentials(self, gate_text: str) -> None:
        assert "broker credentials" in gate_text.lower()

    def test_gate_says_no_investment_advice(self, gate_text: str) -> None:
        assert "investment advice" in gate_text.lower()

    def test_gate_says_no_guaranteed_profit(self, gate_text: str) -> None:
        assert (
            "guaranteed profits" in gate_text.lower()
            or "guaranteed profit" in gate_text.lower()
        )


class TestPreAccessChecklistContent:
    @pytest.fixture(scope="class")
    def checklist_text(self) -> str:
        return _read(PRE_ACCESS_DOC)

    def test_checklist_mentions_safety_posture(self, checklist_text: str) -> None:
        for token in (
            "autotrade=false",
            "dry_run=true",
            "read_only=true",
            "live_orders_blocked=true",
            "max risk <=1%",
        ):
            assert token in checklist_text

    def test_checklist_includes_validation_commands(self, checklist_text: str) -> None:
        for token in (
            "validate_safety_config.py",
            "test_local_demo_readonly_endpoints.py",
            "test_local_demo_smoke_docs_static.py",
            "test_safety_invariants.py",
            "test_openapi_forbidden_paths.py",
        ):
            assert token in checklist_text

    def test_checklist_includes_artifact_checks(self, checklist_text: str) -> None:
        for token in ("dist", "build", "*.spec", "*.exe", "*.lnk", "*.msi", "*.zip"):
            assert token in checklist_text

    def test_checklist_mentions_pass_hold_blocked(self, checklist_text: str) -> None:
        lower = checklist_text.lower()
        assert "pass" in lower
        assert "hold" in lower
        assert "blocked" in lower

    def test_checklist_does_not_auto_grant_access(self, checklist_text: str) -> None:
        lower = checklist_text.lower()
        assert "does not grant access" in lower
        assert "send invites automatically" in lower


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
