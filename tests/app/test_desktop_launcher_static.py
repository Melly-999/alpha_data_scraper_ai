"""
tests/app/test_desktop_launcher_static.py

Static inspection tests for the desktop launcher scripts.
These tests read file content only — they do NOT launch any process,
start any server, or make any network call.

Scope:
  - scripts/desktop_launcher.py
  - scripts/build_desktop_launcher.ps1

Safety invariants verified:
  - Safety posture strings present in launcher
  - Helper script references present
  - Standard-library-only HTTP (no requests/httpx)
  - No forbidden execution/trading strings
  - No auto-install of PyInstaller in build script
  - Build script warns against committing generated artifacts
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LAUNCHER_PY = REPO_ROOT / "scripts" / "desktop_launcher.py"
BUILD_PS1 = REPO_ROOT / "scripts" / "build_desktop_launcher.ps1"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1 — File existence
# ---------------------------------------------------------------------------


class TestFileExistence:
    def test_launcher_py_exists(self) -> None:
        assert (
            LAUNCHER_PY.is_file()
        ), f"scripts/desktop_launcher.py not found at: {LAUNCHER_PY}"

    def test_build_ps1_exists(self) -> None:
        assert (
            BUILD_PS1.is_file()
        ), f"scripts/build_desktop_launcher.ps1 not found at: {BUILD_PS1}"


# ---------------------------------------------------------------------------
# Test 2 — Safety posture strings in launcher
# ---------------------------------------------------------------------------


class TestLauncherSafetyPosture:
    @pytest.fixture(scope="class")
    def launcher_text(self) -> str:
        return _read(LAUNCHER_PY)

    def test_autotrade_false(self, launcher_text: str) -> None:
        assert (
            "autotrade=false" in launcher_text
        ), "launcher must declare autotrade=false in its safety banner"

    def test_dry_run_true(self, launcher_text: str) -> None:
        assert (
            "dry_run=true" in launcher_text
        ), "launcher must declare dry_run=true in its safety banner"

    def test_read_only_true(self, launcher_text: str) -> None:
        assert (
            "read_only=true" in launcher_text
        ), "launcher must declare read_only=true in its safety banner"

    def test_live_orders_blocked(self, launcher_text: str) -> None:
        assert (
            "live_orders_blocked=true" in launcher_text
        ), "launcher must declare live_orders_blocked=true in its safety banner"


# ---------------------------------------------------------------------------
# Test 3 — Launcher references existing helper scripts
# ---------------------------------------------------------------------------


class TestLauncherHelperReferences:
    @pytest.fixture(scope="class")
    def launcher_text(self) -> str:
        return _read(LAUNCHER_PY)

    def test_references_start_backend_local(self, launcher_text: str) -> None:
        assert (
            "start_backend_local.ps1" in launcher_text
        ), "launcher must reference start_backend_local.ps1"

    def test_references_start_frontend_local(self, launcher_text: str) -> None:
        assert (
            "start_frontend_local.ps1" in launcher_text
        ), "launcher must reference start_frontend_local.ps1"

    def test_helper_scripts_exist_on_disk(self) -> None:
        backend_script = REPO_ROOT / "scripts" / "start_backend_local.ps1"
        frontend_script = REPO_ROOT / "scripts" / "start_frontend_local.ps1"
        assert (
            backend_script.is_file()
        ), f"scripts/start_backend_local.ps1 not found: {backend_script}"
        assert (
            frontend_script.is_file()
        ), f"scripts/start_frontend_local.ps1 not found: {frontend_script}"


# ---------------------------------------------------------------------------
# Test 4 — Standard library only — no third-party HTTP client
# ---------------------------------------------------------------------------


class TestLauncherHttpPattern:
    @pytest.fixture(scope="class")
    def launcher_text(self) -> str:
        return _read(LAUNCHER_PY)

    def test_uses_urllib_request(self, launcher_text: str) -> None:
        assert (
            "urllib.request" in launcher_text
        ), "launcher must use urllib.request for HTTP readiness checks"

    def test_no_requests_import(self, launcher_text: str) -> None:
        # 'import requests' or 'from requests' — third-party, not allowed
        assert (
            "import requests" not in launcher_text
        ), "launcher must not import third-party 'requests' library"

    def test_no_httpx_import(self, launcher_text: str) -> None:
        assert (
            "import httpx" not in launcher_text
        ), "launcher must not import third-party 'httpx' library"

    def test_no_aiohttp_import(self, launcher_text: str) -> None:
        assert (
            "import aiohttp" not in launcher_text
        ), "launcher must not import third-party 'aiohttp' library"


# ---------------------------------------------------------------------------
# Test 5 — No forbidden execution / trading strings in launcher
# ---------------------------------------------------------------------------

_FORBIDDEN_ACTIVE = [
    "place_order",
    "execute_order",
    "cancel_order",
    "broker_execute",
    "connect_live",
    "autotrade=true",
    "dry_run=false",
    "read_only=false",
    "account_id",
    "api_key",
    "password",
    "SUPABASE_SERVICE_ROLE_KEY",
]

# Terms that require a more precise check — the raw word may appear in
# prohibition/docstring text, so we check for active credential-use patterns only.
_FORBIDDEN_CREDENTIAL_PATTERNS = [
    # Catches: secret =, secret=, _secret, secret_key, SECRET_KEY, SECRET =
    # Does NOT fire on: "No secrets, ..." prohibition text.
    "secret_key",
    "SECRET_KEY",
    "_secret",
    "secret =",
    "secret=",
]


def _active_code_lines(text: str) -> str:
    # Return non-comment, non-docstring lines joined as a single string.
    # Uses a simple heuristic: track triple-quote boundaries and skip comment lines.
    # Conservative — only skips obvious cases, errs on the side of safety.
    TRIPLE_DQ = '"""'
    TRIPLE_SQ = "'''"
    result = []
    in_docstring = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(TRIPLE_DQ) or stripped.startswith(TRIPLE_SQ):
            in_docstring = not in_docstring
            continue
        if in_docstring:
            continue
        if stripped.startswith("#"):
            continue
        result.append(line)
    return "\n".join(result)


class TestLauncherForbiddenStrings:
    @pytest.fixture(scope="class")
    def launcher_text(self) -> str:
        return _read(LAUNCHER_PY)

    @pytest.fixture(scope="class")
    def launcher_code_lines(self, launcher_text: str) -> str:
        """Active code lines only — docstrings and comments stripped."""
        return _active_code_lines(launcher_text)

    @pytest.mark.parametrize("forbidden", _FORBIDDEN_ACTIVE)
    def test_no_forbidden_string(self, launcher_text: str, forbidden: str) -> None:
        assert (
            forbidden not in launcher_text
        ), f"launcher must not contain forbidden string: {forbidden!r}"

    @pytest.mark.parametrize("pattern", _FORBIDDEN_CREDENTIAL_PATTERNS)
    def test_no_forbidden_credential_pattern(
        self, launcher_code_lines: str, pattern: str
    ) -> None:
        assert (
            pattern not in launcher_code_lines
        ), f"launcher must not contain credential pattern: {pattern!r}"


# ---------------------------------------------------------------------------
# Test 6 — No POST/PUT/PATCH/DELETE in launcher
# ---------------------------------------------------------------------------


class TestLauncherNoMutationMethods:
    @pytest.fixture(scope="class")
    def launcher_text(self) -> str:
        return _read(LAUNCHER_PY)

    def test_no_post_method_string(self, launcher_text: str) -> None:
        # Allow the string "POST" in comments that explicitly prohibit it,
        # but it must not appear as an active HTTP method call.
        # We check for method="POST" and method='POST' patterns.
        assert 'method="POST"' not in launcher_text, "launcher must not use HTTP POST"
        assert "method='POST'" not in launcher_text, "launcher must not use HTTP POST"

    def test_no_put_method_string(self, launcher_text: str) -> None:
        assert 'method="PUT"' not in launcher_text, "launcher must not use HTTP PUT"
        assert "method='PUT'" not in launcher_text, "launcher must not use HTTP PUT"

    def test_no_patch_method_string(self, launcher_text: str) -> None:
        assert 'method="PATCH"' not in launcher_text, "launcher must not use HTTP PATCH"
        assert "method='PATCH'" not in launcher_text, "launcher must not use HTTP PATCH"

    def test_no_delete_method_string(self, launcher_text: str) -> None:
        assert (
            'method="DELETE"' not in launcher_text
        ), "launcher must not use HTTP DELETE"
        assert (
            "method='DELETE'" not in launcher_text
        ), "launcher must not use HTTP DELETE"


# ---------------------------------------------------------------------------
# Test 7 — Build script does not auto-install packages
# ---------------------------------------------------------------------------


class TestBuildScriptNoAutoInstall:
    @pytest.fixture(scope="class")
    def build_text(self) -> str:
        return _read(BUILD_PS1)

    def test_no_pip_install_pyinstaller_unconditional(self, build_text: str) -> None:
        """Build script must not silently pip install PyInstaller.

        It may PRINT an instruction like 'py -3.11 -m pip install pyinstaller'
        but must not execute it as a command.  We check that there is no line
        that both calls pip/install AND is not inside a Write-Host/echo.
        """
        lines = build_text.splitlines()
        for line in lines:
            stripped = line.strip().lower()
            # Lines that are just printing instructions are fine
            is_print_line = stripped.startswith("write-host") or stripped.startswith(
                "#"
            )
            if not is_print_line:
                # A real pip install call would look like:
                # & py -3.11 -m pip install pyinstaller
                # pip install pyinstaller
                if (
                    "pip install pyinstaller" in stripped
                    and "pip install pyinstaller" in line
                ):
                    assert False, (  # noqa: PT015
                        f"Build script must not auto-install PyInstaller.\n"
                        f"Offending line: {line!r}"
                    )


# ---------------------------------------------------------------------------
# Test 8 — Build script warns against committing generated artifacts
# ---------------------------------------------------------------------------


class TestBuildScriptNoCommitWarning:
    @pytest.fixture(scope="class")
    def build_text(self) -> str:
        return _read(BUILD_PS1)

    def test_warns_against_committing_dist(self, build_text: str) -> None:
        assert (
            "dist" in build_text
        ), "build script must mention 'dist/' to warn against committing it"

    def test_warns_against_committing_build(self, build_text: str) -> None:
        assert (
            "build" in build_text.lower()
        ), "build script must mention 'build/' to warn against committing it"

    def test_warns_against_committing_spec(self, build_text: str) -> None:
        assert (
            ".spec" in build_text
        ), "build script must mention '.spec' to warn against committing it"

    def test_has_do_not_commit_wording(self, build_text: str) -> None:
        lower = build_text.lower()
        assert (
            "not commit" in lower or "do not commit" in lower or "must not" in lower
        ), "build script must contain wording advising NOT to commit generated artifacts"


# ---------------------------------------------------------------------------
# Test 9 — PyInstaller frozen repo-root detection (DESKTOP-001C-BUG fix)
# ---------------------------------------------------------------------------


class TestLauncherFrozenRootDetection:
    """Verify that the launcher handles PyInstaller --onefile frozen mode.

    These tests read file content only — they do NOT run the EXE,
    execute PyInstaller, or start backend/frontend.

    Background: When running as a PyInstaller --onefile EXE, __file__
    resolves to the temp extraction directory, not the repo root.
    The fix detects sys.frozen and uses sys.executable to determine
    the repo root instead.
    """

    @pytest.fixture(scope="class")
    def launcher_text(self) -> str:
        return _read(LAUNCHER_PY)

    def test_detects_sys_frozen(self, launcher_text: str) -> None:
        assert (
            'sys, "frozen"' in launcher_text or "sys.frozen" in launcher_text
        ), "launcher must detect PyInstaller frozen mode via getattr(sys, 'frozen', False)"

    def test_uses_sys_executable(self, launcher_text: str) -> None:
        assert (
            "sys.executable" in launcher_text
        ), "launcher must use sys.executable for repo root resolution in frozen mode"

    def test_uses_parent_parent_for_frozen(self, launcher_text: str) -> None:
        """Ensure the .parent.parent chain is present for frozen path resolution.

        In the frozen path: sys.executable → dist/MellyTradeLauncher.exe
        .parent  → dist/
        .parent.parent → repo root
        Both .parent calls must be present.
        """
        assert launcher_text.count(".parent") >= 2, (
            "launcher must use .parent.parent (or equivalent) to walk up from "
            "dist/MellyTradeLauncher.exe to the repo root in frozen mode"
        )

    def test_repo_root_override_still_present(self, launcher_text: str) -> None:
        assert (
            "--repo-root" in launcher_text
        ), "launcher must still support --repo-root CLI override after frozen-mode fix"

    def test_frozen_branch_before_source_fallback(self, launcher_text: str) -> None:
        """frozen detection must appear before the __file__-based fallback."""
        frozen_idx = launcher_text.find('"frozen"')
        file_idx = launcher_text.find("Path(__file__)")
        assert frozen_idx != -1, "sys.frozen check not found"
        assert file_idx != -1, "Path(__file__) fallback not found"
        assert (
            frozen_idx < file_idx
        ), "sys.frozen detection must appear before Path(__file__) fallback"

    def test_helper_script_references_unchanged(self, launcher_text: str) -> None:
        assert (
            "start_backend_local.ps1" in launcher_text
        ), "launcher must still reference start_backend_local.ps1 after frozen-mode fix"
        assert (
            "start_frontend_local.ps1" in launcher_text
        ), "launcher must still reference start_frontend_local.ps1 after frozen-mode fix"

    def test_no_mutation_http_added(self, launcher_text: str) -> None:
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            assert (
                f'method="{method}"' not in launcher_text
                and f"method='{method}'" not in launcher_text
            ), f"frozen-mode fix must not add {method} HTTP calls"
