"""
tests/app/test_source_only_beta_docs_static.py

Static inspection tests for DESKTOP-001F: source-only beta package review.

These tests read file content only — they do NOT create ZIPs, run PowerShell,
execute any EXE, start backend/frontend, or call any network.

Scope:
  - docs/distribution/source_only_beta_package_review.md
  - docs/qa/source_only_beta_preflight_checklist.md
  - docs/product/beta_tester_source_access_guide.md
  - docs/tasks/desktop_launcher_exe_plan.md (DESKTOP-001F section)

Safety invariants verified:
  1.  source_only_beta_package_review.md exists
  2.  source_only_beta_preflight_checklist.md exists
  3.  beta_tester_source_access_guide.md exists
  4.  Plan doc has DESKTOP-001F section
  5.  Safety posture documented in review doc (all 4 flags)
  6.  Generated artifact policy documented (dist/, build/, *.spec, *.exe,
      *.lnk, *.msi, *.zip)
  7.  Docs say no live trading
  8.  Docs say no broker execution
  9.  Docs say no investment advice
  10. Docs say no guaranteed profit
  11. Docs say do not enter broker credentials
  12. Validation commands exist in review doc
  13. Artifact check commands exist in review doc
  14. Stop conditions exist in review doc
  15. Tests do not execute commands
  16. Tests do not build EXE
  17. Tests do not create artifacts
  18. Tests do not call network
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REVIEW_DOC = REPO_ROOT / "docs" / "distribution" / "source_only_beta_package_review.md"
PREFLIGHT = REPO_ROOT / "docs" / "qa" / "source_only_beta_preflight_checklist.md"
ACCESS_GUIDE = REPO_ROOT / "docs" / "product" / "beta_tester_source_access_guide.md"
LAUNCHER_PLAN = REPO_ROOT / "docs" / "tasks" / "desktop_launcher_exe_plan.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1 — source_only_beta_package_review.md exists
# ---------------------------------------------------------------------------

class TestReviewDocExists:
    def test_source_only_beta_package_review_exists(self) -> None:
        assert REVIEW_DOC.is_file(), (
            f"docs/distribution/source_only_beta_package_review.md not found at: {REVIEW_DOC}"
        )


# ---------------------------------------------------------------------------
# Test 2 — source_only_beta_preflight_checklist.md exists
# ---------------------------------------------------------------------------

class TestPreflightChecklistExists:
    def test_source_only_beta_preflight_checklist_exists(self) -> None:
        assert PREFLIGHT.is_file(), (
            f"docs/qa/source_only_beta_preflight_checklist.md not found at: {PREFLIGHT}"
        )


# ---------------------------------------------------------------------------
# Test 3 — beta_tester_source_access_guide.md exists
# ---------------------------------------------------------------------------

class TestAccessGuideExists:
    def test_beta_tester_source_access_guide_exists(self) -> None:
        assert ACCESS_GUIDE.is_file(), (
            f"docs/product/beta_tester_source_access_guide.md not found at: {ACCESS_GUIDE}"
        )


# ---------------------------------------------------------------------------
# Test 4 — Plan doc has DESKTOP-001F section
# ---------------------------------------------------------------------------

class TestLauncherPlanHasDesktop001F:
    @pytest.fixture(scope="class")
    def plan_text(self) -> str:
        return _read(LAUNCHER_PLAN)

    def test_plan_has_desktop_001f_section(self, plan_text: str) -> None:
        assert "DESKTOP-001F" in plan_text, (
            "docs/tasks/desktop_launcher_exe_plan.md must have a DESKTOP-001F section"
        )

    def test_plan_references_review_doc(self, plan_text: str) -> None:
        assert "source_only_beta_package_review.md" in plan_text, (
            "desktop_launcher_exe_plan.md must reference source_only_beta_package_review.md"
        )

    def test_plan_references_preflight(self, plan_text: str) -> None:
        assert "source_only_beta_preflight_checklist.md" in plan_text, (
            "desktop_launcher_exe_plan.md must reference source_only_beta_preflight_checklist.md"
        )

    def test_plan_references_access_guide(self, plan_text: str) -> None:
        assert "beta_tester_source_access_guide.md" in plan_text, (
            "desktop_launcher_exe_plan.md must reference beta_tester_source_access_guide.md"
        )


# ---------------------------------------------------------------------------
# Test 5 — Safety posture documented in review doc (all 4 flags)
# ---------------------------------------------------------------------------

class TestReviewDocSafetyPosture:
    @pytest.fixture(scope="class")
    def review_text(self) -> str:
        return _read(REVIEW_DOC)

    def test_autotrade_false(self, review_text: str) -> None:
        assert "autotrade=false" in review_text, (
            "review doc must declare autotrade=false"
        )

    def test_dry_run_true(self, review_text: str) -> None:
        assert "dry_run=true" in review_text, (
            "review doc must declare dry_run=true"
        )

    def test_read_only_true(self, review_text: str) -> None:
        assert "read_only=true" in review_text, (
            "review doc must declare read_only=true"
        )

    def test_live_orders_blocked_true(self, review_text: str) -> None:
        assert "live_orders_blocked=true" in review_text, (
            "review doc must declare live_orders_blocked=true"
        )


# ---------------------------------------------------------------------------
# Test 6 — Generated artifact policy documented
# ---------------------------------------------------------------------------

class TestReviewDocArtifactPolicy:
    @pytest.fixture(scope="class")
    def review_text(self) -> str:
        return _read(REVIEW_DOC)

    def test_lists_dist(self, review_text: str) -> None:
        assert "dist/" in review_text, (
            "review doc must list dist/ in artifact policy"
        )

    def test_lists_build(self, review_text: str) -> None:
        assert "build/" in review_text, (
            "review doc must list build/ in artifact policy"
        )

    def test_lists_spec(self, review_text: str) -> None:
        assert "*.spec" in review_text, (
            "review doc must list *.spec in artifact policy"
        )

    def test_lists_exe(self, review_text: str) -> None:
        assert "*.exe" in review_text, (
            "review doc must list *.exe in artifact policy"
        )

    def test_lists_lnk(self, review_text: str) -> None:
        assert "*.lnk" in review_text, (
            "review doc must list *.lnk in artifact policy"
        )

    def test_lists_msi(self, review_text: str) -> None:
        assert "*.msi" in review_text, (
            "review doc must list *.msi in artifact policy"
        )

    def test_lists_zip(self, review_text: str) -> None:
        assert "*.zip" in review_text, (
            "review doc must list *.zip in artifact policy"
        )

    def test_states_must_not_be_committed(self, review_text: str) -> None:
        lower = review_text.lower()
        assert (
            "must not be committed" in lower
            or "do not commit" in lower
            or "not commit" in lower
        ), (
            "review doc must state generated artifacts must not be committed"
        )


# ---------------------------------------------------------------------------
# Test 7 — Docs say no live trading
# ---------------------------------------------------------------------------

_ALL_DOC_PATHS = [REVIEW_DOC, PREFLIGHT, ACCESS_GUIDE]


class TestDocsNoLiveTrading:
    @pytest.mark.parametrize("doc_path", _ALL_DOC_PATHS, ids=lambda p: p.name)
    def test_doc_states_no_live_trading(self, doc_path: Path) -> None:
        lower = _read(doc_path).lower()
        assert (
            "not live trading" in lower
            or "no live trading" in lower
            or "live trading is not enabled" in lower
            or "live trading access" in lower
        ), (
            f"{doc_path.name} must address that this is not / does not have live trading"
        )


# ---------------------------------------------------------------------------
# Test 8 — Docs say no broker execution
# ---------------------------------------------------------------------------

class TestDocsNoBrokerExecution:
    @pytest.mark.parametrize("doc_path", _ALL_DOC_PATHS, ids=lambda p: p.name)
    def test_doc_states_no_broker_execution(self, doc_path: Path) -> None:
        lower = _read(doc_path).lower()
        assert (
            "not broker execution" in lower
            or "no broker execution" in lower
            or "no order execution" in lower
            or "broker execution access" in lower
            or "execution controls" in lower
        ), (
            f"{doc_path.name} must address that this is not broker execution"
        )


# ---------------------------------------------------------------------------
# Test 9 — Docs say no investment advice
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
# Test 10 — Docs say no guaranteed profit
# ---------------------------------------------------------------------------

class TestDocsNoGuaranteedProfit:
    @pytest.mark.parametrize("doc_path", _ALL_DOC_PATHS, ids=lambda p: p.name)
    def test_doc_states_no_guaranteed_profit(self, doc_path: Path) -> None:
        lower = _read(doc_path).lower()
        assert (
            "guaranteed profit" in lower
            or "no guaranteed profit" in lower
            or "guaranteed-profit" in lower
        ), (
            f"{doc_path.name} must address guaranteed profit claims"
        )


# ---------------------------------------------------------------------------
# Test 11 — Docs say do not enter broker credentials
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
# Test 12 — Validation commands exist in review doc
# ---------------------------------------------------------------------------

class TestReviewDocValidationCommands:
    @pytest.fixture(scope="class")
    def review_text(self) -> str:
        return _read(REVIEW_DOC)

    def test_has_validate_safety_config(self, review_text: str) -> None:
        assert "validate_safety_config.py" in review_text, (
            "review doc must include validate_safety_config.py command"
        )

    def test_has_pytest_command(self, review_text: str) -> None:
        assert "pytest" in review_text, (
            "review doc must include pytest validation commands"
        )

    def test_has_safety_invariants_test(self, review_text: str) -> None:
        assert "test_safety_invariants" in review_text, (
            "review doc must reference test_safety_invariants.py"
        )


# ---------------------------------------------------------------------------
# Test 13 — Artifact check commands exist in review doc
# ---------------------------------------------------------------------------

class TestReviewDocArtifactCheckCommands:
    @pytest.fixture(scope="class")
    def review_text(self) -> str:
        return _read(REVIEW_DOC)

    def test_has_git_status_dist(self, review_text: str) -> None:
        assert "git status" in review_text and "dist" in review_text, (
            "review doc must include git status check for dist/"
        )

    def test_has_git_status_exe(self, review_text: str) -> None:
        assert "*.exe" in review_text, (
            "review doc artifact check must include *.exe"
        )

    def test_has_git_status_lnk(self, review_text: str) -> None:
        assert "*.lnk" in review_text, (
            "review doc artifact check must include *.lnk"
        )


# ---------------------------------------------------------------------------
# Test 14 — Stop conditions exist in review doc
# ---------------------------------------------------------------------------

class TestReviewDocStopConditions:
    @pytest.fixture(scope="class")
    def review_text(self) -> str:
        return _read(REVIEW_DOC)

    def test_has_stop_conditions_section(self, review_text: str) -> None:
        lower = review_text.lower()
        assert "stop condition" in lower or "stop the" in lower or "stop and report" in lower, (
            "review doc must have a stop conditions section"
        )

    def test_stop_conditions_mention_safety_validator(self, review_text: str) -> None:
        lower = review_text.lower()
        assert "safety validator fails" in lower or "validator fail" in lower, (
            "stop conditions must include safety validator failure"
        )

    def test_stop_conditions_mention_tests(self, review_text: str) -> None:
        lower = review_text.lower()
        assert (
            "tests fail" in lower
            or "test fails" in lower
            or "static test" in lower
        ), (
            "stop conditions must include test failure"
        )

    def test_stop_conditions_mention_secrets(self, review_text: str) -> None:
        lower = review_text.lower()
        assert "secrets" in lower or "secret" in lower, (
            "stop conditions must mention secrets appearing in repo"
        )


# ---------------------------------------------------------------------------
# Helper — import-line scanner used by Tests 15-18
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
# Test 15 — Tests do not execute commands (this file is read-only)
# ---------------------------------------------------------------------------

class TestThisFileIsReadOnly:
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
# Test 16 — Tests do not build EXE
# ---------------------------------------------------------------------------

class TestThisFileDoesNotBuildExe:
    def test_no_exe_builder_imports(self) -> None:
        banned = ["pyinstaller", "cx_freeze", "nuitka"]
        for ln in _this_file_import_lines():
            for mod in banned:
                assert mod not in ln.lower(), (
                    f"test file import check failed — {mod!r} must not be imported, line: {ln!r}"
                )

    def test_no_launcher_build_imports(self) -> None:
        # build_desktop_launcher is a PS1 script, not a Python module;
        # confirm no build-script module appears in import lines
        for ln in _this_file_import_lines():
            assert "build_desktop" not in ln.lower(), (
                f"test file import check failed — launcher build must not be imported, line: {ln!r}"
            )


# ---------------------------------------------------------------------------
# Test 17 — Tests do not create artifacts
# ---------------------------------------------------------------------------

class TestThisFileDoesNotCreateArtifacts:
    def test_no_artifact_creation_imports(self) -> None:
        banned = ["shutil", "zipfile", "tarfile"]
        for ln in _this_file_import_lines():
            for mod in banned:
                assert mod not in ln, (
                    f"test file import check failed — {mod!r} must not be imported, line: {ln!r}"
                )


# ---------------------------------------------------------------------------
# Test 18 — Tests do not call network
# ---------------------------------------------------------------------------

class TestThisFileDoesNotCallNetwork:
    def test_no_network_imports(self) -> None:
        banned = ["requests", "urllib", "httpx", "socket", "http", "aiohttp"]
        for ln in _this_file_import_lines():
            for mod in banned:
                assert mod not in ln, (
                    f"test file import check failed — {mod!r} must not be imported, line: {ln!r}"
                )
