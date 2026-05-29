"""
tests/app/test_desktop_launcher_build_static.py

Static inspection tests for DESKTOP-001B: PyInstaller build validation.
These tests read file content and inspect git state only — they do NOT run
PyInstaller, execute the EXE, or start backend/frontend.

Scope:
  - docs/qa/desktop_launcher_build_validation.md
  - docs/tasks/desktop_launcher_exe_plan.md
  - scripts/build_desktop_launcher.ps1
  - .gitignore
  - git-tracked file list (via subprocess git ls-files)

Safety invariants verified:
  - Build validation doc exists and contains required content
  - Commit policy clearly documented
  - Build wrapper has explicit -Build mode
  - Build wrapper does not auto-install PyInstaller
  - Generated artifacts (dist/, build/, *.spec) are not git-tracked
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BUILD_VALIDATION_DOC = (
    REPO_ROOT / "docs" / "qa" / "desktop_launcher_build_validation.md"
)
PLAN_DOC = REPO_ROOT / "docs" / "tasks" / "desktop_launcher_exe_plan.md"
BUILD_PS1 = REPO_ROOT / "scripts" / "build_desktop_launcher.ps1"
GITIGNORE = REPO_ROOT / ".gitignore"
DIST_EXE = REPO_ROOT / "dist" / "MellyTradeLauncher.exe"
SPEC_FILE = REPO_ROOT / "MellyTradeLauncher.spec"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _git_ls_files() -> set[str]:
    """Return the set of files tracked by git (relative paths, forward slashes)."""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


# ---------------------------------------------------------------------------
# Test 1 — Build validation doc exists
# ---------------------------------------------------------------------------


class TestBuildValidationDocExists:
    def test_doc_exists(self) -> None:
        assert (
            BUILD_VALIDATION_DOC.is_file()
        ), f"docs/qa/desktop_launcher_build_validation.md not found at: {BUILD_VALIDATION_DOC}"


# ---------------------------------------------------------------------------
# Test 2 — Build validation doc content
# ---------------------------------------------------------------------------


class TestBuildValidationDocContent:
    @pytest.fixture(scope="class")
    def doc_text(self) -> str:
        return _read(BUILD_VALIDATION_DOC)

    def test_references_exe(self, doc_text: str) -> None:
        assert (
            "dist/MellyTradeLauncher.exe" in doc_text
        ), "build validation doc must reference dist/MellyTradeLauncher.exe"

    def test_commit_policy_no_dist(self, doc_text: str) -> None:
        assert (
            "dist/" in doc_text
        ), "build validation doc must mention dist/ in commit policy"

    def test_commit_policy_no_build(self, doc_text: str) -> None:
        assert (
            "build/" in doc_text
        ), "build validation doc must mention build/ in commit policy"

    def test_commit_policy_no_spec(self, doc_text: str) -> None:
        assert (
            "*.spec" in doc_text
        ), "build validation doc must mention *.spec in commit policy"

    def test_commit_policy_no_exe(self, doc_text: str) -> None:
        assert (
            "*.exe" in doc_text
        ), "build validation doc must mention *.exe in commit policy"

    def test_must_not_be_committed_wording(self, doc_text: str) -> None:
        lower = doc_text.lower()
        assert (
            "must not be committed" in lower
            or "must not commit" in lower
            or "not be committed" in lower
        ), "build validation doc must contain wording that generated artifacts must not be committed"

    def test_safety_posture_autotrade(self, doc_text: str) -> None:
        assert (
            "autotrade=false" in doc_text
        ), "build validation doc must declare autotrade=false"

    def test_safety_posture_dry_run(self, doc_text: str) -> None:
        assert (
            "dry_run=true" in doc_text
        ), "build validation doc must declare dry_run=true"

    def test_safety_posture_read_only(self, doc_text: str) -> None:
        assert (
            "read_only=true" in doc_text
        ), "build validation doc must declare read_only=true"

    def test_safety_posture_live_orders(self, doc_text: str) -> None:
        assert (
            "live_orders_blocked=true" in doc_text
        ), "build validation doc must declare live_orders_blocked=true"


# ---------------------------------------------------------------------------
# Test 3 — Build wrapper has explicit -Build mode
# ---------------------------------------------------------------------------


class TestBuildWrapperBuildMode:
    @pytest.fixture(scope="class")
    def ps1_text(self) -> str:
        return _read(BUILD_PS1)

    def test_has_build_parameter(self, ps1_text: str) -> None:
        assert (
            "[switch]$Build" in ps1_text
        ), "build_desktop_launcher.ps1 must have an explicit -Build switch parameter"

    def test_build_parameter_set(self, ps1_text: str) -> None:
        assert (
            "ParameterSetName = 'Build'" in ps1_text
        ), "build_desktop_launcher.ps1 must use a 'Build' ParameterSetName"

    def test_checkonly_is_default(self, ps1_text: str) -> None:
        assert (
            "DefaultParameterSetName = 'CheckOnly'" in ps1_text
        ), "build_desktop_launcher.ps1 must have CheckOnly as DefaultParameterSetName"


# ---------------------------------------------------------------------------
# Test 4 — Build wrapper does NOT auto-install PyInstaller
# ---------------------------------------------------------------------------


class TestBuildWrapperNoAutoInstall:
    @pytest.fixture(scope="class")
    def ps1_text(self) -> str:
        return _read(BUILD_PS1)

    def test_no_pip_install_in_active_code(self, ps1_text: str) -> None:
        """Build wrapper must not execute pip install PyInstaller automatically.

        Write-Host print lines may contain the install instruction as text.
        Active code lines must not.
        """
        lines = ps1_text.splitlines()
        for line in lines:
            stripped = line.strip().lower()
            is_print_line = stripped.startswith("write-host") or stripped.startswith(
                "#"
            )
            if not is_print_line:
                if "pip install pyinstaller" in stripped:
                    pytest.fail(
                        f"build_desktop_launcher.ps1 must not auto-install PyInstaller.\n"
                        f"Offending line: {line!r}"
                    )


# ---------------------------------------------------------------------------
# Test 5 — No generated binary is tracked by git
# ---------------------------------------------------------------------------


class TestNoGeneratedArtifactsTracked:
    @pytest.fixture(scope="class")
    def tracked_files(self) -> set[str]:
        return _git_ls_files()

    def test_dist_exe_not_tracked(self, tracked_files: set[str]) -> None:
        """dist/MellyTradeLauncher.exe must not be in git-tracked files."""
        assert (
            "dist/MellyTradeLauncher.exe" not in tracked_files
        ), "dist/MellyTradeLauncher.exe must not be committed to git"

    def test_no_exe_in_dist_tracked(self, tracked_files: set[str]) -> None:
        """No .exe file under dist/ should be tracked."""
        tracked_exes = [
            f for f in tracked_files if f.startswith("dist/") and f.endswith(".exe")
        ]
        assert (
            tracked_exes == []
        ), f"No .exe files under dist/ should be tracked by git. Found: {tracked_exes}"

    def test_spec_not_tracked(self, tracked_files: set[str]) -> None:
        """MellyTradeLauncher.spec must not be tracked."""
        tracked_specs = [f for f in tracked_files if f.endswith(".spec")]
        assert (
            tracked_specs == []
        ), f"No .spec files should be tracked by git. Found: {tracked_specs}"

    def test_no_build_dir_tracked(self, tracked_files: set[str]) -> None:
        """No files under build/ should be tracked by git."""
        tracked_build = [f for f in tracked_files if f.startswith("build/")]
        assert (
            tracked_build == []
        ), f"No files under build/ should be tracked by git. Found: {tracked_build}"
