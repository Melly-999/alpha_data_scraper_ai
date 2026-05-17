"""
tests/app/test_desktop_launcher_shortcut_static.py

Static inspection tests for DESKTOP-001D: Windows shortcut helper and docs.
These tests read file content only — they do NOT create shortcuts, run the
PowerShell script, execute the EXE, start backend/frontend, or call any network.

Scope:
  - scripts/create_desktop_shortcut.ps1
  - docs/qa/desktop_launcher_shortcut_smoke_checklist.md
  - docs/product/beta_tester_desktop_launcher_quick_start.md

Safety invariants verified:
  1.  Script file exists
  2.  References WScript.Shell COM object
  3.  References .lnk extension
  4.  Has -WhatIfOnly parameter
  5.  Has -NoBrowser parameter
  6.  References dist/MellyTradeLauncher.exe
  7.  Does not run/execute the EXE (no Start-Process or Invoke-Item)
  8.  Does not call PyInstaller
  9.  No mutation HTTP methods
  10. No forbidden active execution/trading strings
  11. No secrets or account IDs
  12. Shortcut smoke checklist exists
  13. Beta tester quick start exists
  14. Docs include safety posture strings
  15. Docs state .lnk must not be committed
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SHORTCUT_PS1 = REPO_ROOT / "scripts" / "create_desktop_shortcut.ps1"
SMOKE_CHECKLIST = REPO_ROOT / "docs" / "qa" / "desktop_launcher_shortcut_smoke_checklist.md"
QUICK_START = REPO_ROOT / "docs" / "product" / "beta_tester_desktop_launcher_quick_start.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1 — Script file exists
# ---------------------------------------------------------------------------

class TestShortcutScriptExists:
    def test_create_desktop_shortcut_ps1_exists(self) -> None:
        assert SHORTCUT_PS1.is_file(), (
            f"scripts/create_desktop_shortcut.ps1 not found at: {SHORTCUT_PS1}"
        )


# ---------------------------------------------------------------------------
# Test 2 — WScript.Shell reference
# ---------------------------------------------------------------------------

class TestShortcutUsesWScriptShell:
    @pytest.fixture(scope="class")
    def script_text(self) -> str:
        return _read(SHORTCUT_PS1)

    def test_references_wscript_shell(self, script_text: str) -> None:
        assert "WScript.Shell" in script_text, (
            "create_desktop_shortcut.ps1 must use WScript.Shell COM object to create .lnk"
        )

    def test_uses_createshortcut_method(self, script_text: str) -> None:
        lower = script_text.lower()
        assert "createshortcut" in lower, (
            "create_desktop_shortcut.ps1 must call CreateShortcut() to create .lnk"
        )


# ---------------------------------------------------------------------------
# Test 3 — .lnk reference
# ---------------------------------------------------------------------------

class TestShortcutLnkReference:
    @pytest.fixture(scope="class")
    def script_text(self) -> str:
        return _read(SHORTCUT_PS1)

    def test_references_lnk_extension(self, script_text: str) -> None:
        assert ".lnk" in script_text, (
            "create_desktop_shortcut.ps1 must reference .lnk extension"
        )


# ---------------------------------------------------------------------------
# Test 4 — -WhatIfOnly parameter
# ---------------------------------------------------------------------------

class TestShortcutWhatIfOnlyParam:
    @pytest.fixture(scope="class")
    def script_text(self) -> str:
        return _read(SHORTCUT_PS1)

    def test_has_whatifonly_parameter(self, script_text: str) -> None:
        assert "WhatIfOnly" in script_text, (
            "create_desktop_shortcut.ps1 must have a -WhatIfOnly parameter"
        )

    def test_whatifonly_does_not_save_shortcut(self, script_text: str) -> None:
        """When -WhatIfOnly is active, $Shortcut.Save() must not be reached.

        Implementation check: the WhatIfOnly block must have an early exit
        (exit 0 or return) before the .Save() call.
        """
        whatif_idx = script_text.find("WhatIfOnly")
        save_idx = script_text.find(".Save()")
        assert whatif_idx != -1, "WhatIfOnly not found"
        assert save_idx != -1, ".Save() not found"
        # exit 0 must appear in the WhatIfOnly block, before .Save()
        exit_idx = script_text.find("exit 0", whatif_idx)
        assert exit_idx != -1 and exit_idx < save_idx, (
            "create_desktop_shortcut.ps1 must exit before .Save() in -WhatIfOnly mode"
        )


# ---------------------------------------------------------------------------
# Test 5 — -NoBrowser parameter
# ---------------------------------------------------------------------------

class TestShortcutNoBrowserParam:
    @pytest.fixture(scope="class")
    def script_text(self) -> str:
        return _read(SHORTCUT_PS1)

    def test_has_nobrowser_parameter(self, script_text: str) -> None:
        assert "NoBrowser" in script_text, (
            "create_desktop_shortcut.ps1 must have a -NoBrowser parameter"
        )

    def test_nobrowser_sets_no_browser_argument(self, script_text: str) -> None:
        assert "--no-browser" in script_text, (
            "create_desktop_shortcut.ps1 must set --no-browser argument when -NoBrowser is used"
        )


# ---------------------------------------------------------------------------
# Test 6 — References dist/MellyTradeLauncher.exe
# ---------------------------------------------------------------------------

class TestShortcutTargetReference:
    @pytest.fixture(scope="class")
    def script_text(self) -> str:
        return _read(SHORTCUT_PS1)

    def test_references_mellytrade_launcher_exe(self, script_text: str) -> None:
        assert "MellyTradeLauncher.exe" in script_text, (
            "create_desktop_shortcut.ps1 must reference MellyTradeLauncher.exe as default target"
        )

    def test_references_dist_directory(self, script_text: str) -> None:
        assert "dist" in script_text, (
            "create_desktop_shortcut.ps1 must reference dist/ directory for EXE path"
        )


# ---------------------------------------------------------------------------
# Test 7 — Does not run/execute the EXE
# ---------------------------------------------------------------------------

class TestShortcutNoExeExecution:
    @pytest.fixture(scope="class")
    def script_text(self) -> str:
        return _read(SHORTCUT_PS1)

    def test_no_start_process(self, script_text: str) -> None:
        assert "Start-Process" not in script_text, (
            "create_desktop_shortcut.ps1 must not use Start-Process (does not run the EXE)"
        )

    def test_no_invoke_item(self, script_text: str) -> None:
        assert "Invoke-Item" not in script_text, (
            "create_desktop_shortcut.ps1 must not use Invoke-Item"
        )

    def test_no_invoke_expression(self, script_text: str) -> None:
        assert "Invoke-Expression" not in script_text, (
            "create_desktop_shortcut.ps1 must not use Invoke-Expression"
        )

    def test_no_call_operator_exe(self, script_text: str) -> None:
        # Must not launch the EXE via & ... .exe (call operator with .exe)
        assert "& $TargetPath" not in script_text and "& $ExePath" not in script_text, (
            "create_desktop_shortcut.ps1 must not invoke the target EXE via call operator"
        )


# ---------------------------------------------------------------------------
# Test 8 — Does not call PyInstaller
# ---------------------------------------------------------------------------

class TestShortcutNoPyInstaller:
    @pytest.fixture(scope="class")
    def script_text(self) -> str:
        return _read(SHORTCUT_PS1)

    def test_no_pyinstaller(self, script_text: str) -> None:
        assert "PyInstaller" not in script_text and "pyinstaller" not in script_text, (
            "create_desktop_shortcut.ps1 must not call PyInstaller"
        )


# ---------------------------------------------------------------------------
# Test 9 — No mutation HTTP methods
# ---------------------------------------------------------------------------

class TestShortcutNoMutationHttp:
    @pytest.fixture(scope="class")
    def script_text(self) -> str:
        return _read(SHORTCUT_PS1)

    def test_no_invoke_webrequest_post(self, script_text: str) -> None:
        lower = script_text.lower()
        assert "invoke-webrequest" not in lower and "invoke-restmethod" not in lower, (
            "create_desktop_shortcut.ps1 must not make HTTP calls"
        )

    def test_no_curl_post(self, script_text: str) -> None:
        lower = script_text.lower()
        assert "curl" not in lower, (
            "create_desktop_shortcut.ps1 must not use curl"
        )


# ---------------------------------------------------------------------------
# Test 10 — No forbidden active execution/trading strings
# ---------------------------------------------------------------------------

_FORBIDDEN_STRINGS = [
    "place_order",
    "execute_order",
    "cancel_order",
    "broker_execute",
    "connect_live",
    "autotrade=true",
    "dry_run=false",
    "read_only=false",
    "risk_allowed=true",
]


class TestShortcutNoForbiddenStrings:
    @pytest.fixture(scope="class")
    def script_text(self) -> str:
        return _read(SHORTCUT_PS1)

    @pytest.mark.parametrize("forbidden", _FORBIDDEN_STRINGS)
    def test_no_forbidden_string(self, script_text: str, forbidden: str) -> None:
        assert forbidden not in script_text, (
            f"create_desktop_shortcut.ps1 must not contain forbidden string: {forbidden!r}"
        )


# ---------------------------------------------------------------------------
# Test 11 — No secrets or account IDs
# ---------------------------------------------------------------------------

_FORBIDDEN_CREDENTIAL_PATTERNS = [
    "SUPABASE_SERVICE_ROLE_KEY",
    "api_key",
    "API_KEY",
    "account_id",
    "ACCOUNT_ID",
]


class TestShortcutNoSecrets:
    @pytest.fixture(scope="class")
    def script_text(self) -> str:
        return _read(SHORTCUT_PS1)

    @pytest.mark.parametrize("pattern", _FORBIDDEN_CREDENTIAL_PATTERNS)
    def test_no_credential_pattern(self, script_text: str, pattern: str) -> None:
        assert pattern not in script_text, (
            f"create_desktop_shortcut.ps1 must not contain credential pattern: {pattern!r}"
        )


# ---------------------------------------------------------------------------
# Test 12 — Shortcut smoke checklist exists
# ---------------------------------------------------------------------------

class TestShortcutSmokeChecklistExists:
    def test_smoke_checklist_exists(self) -> None:
        assert SMOKE_CHECKLIST.is_file(), (
            f"docs/qa/desktop_launcher_shortcut_smoke_checklist.md not found at: {SMOKE_CHECKLIST}"
        )


# ---------------------------------------------------------------------------
# Test 13 — Beta tester quick start exists
# ---------------------------------------------------------------------------

class TestBetaTesterQuickStartExists:
    def test_quick_start_exists(self) -> None:
        assert QUICK_START.is_file(), (
            f"docs/product/beta_tester_desktop_launcher_quick_start.md not found at: {QUICK_START}"
        )


# ---------------------------------------------------------------------------
# Test 14 — Docs include safety posture strings
# ---------------------------------------------------------------------------

class TestDocsHaveSafetyPosture:
    @pytest.fixture(scope="class")
    def smoke_text(self) -> str:
        return _read(SMOKE_CHECKLIST)

    @pytest.fixture(scope="class")
    def quick_start_text(self) -> str:
        return _read(QUICK_START)

    def test_smoke_checklist_autotrade_false(self, smoke_text: str) -> None:
        assert "autotrade=false" in smoke_text, (
            "smoke checklist must declare autotrade=false"
        )

    def test_smoke_checklist_dry_run_true(self, smoke_text: str) -> None:
        assert "dry_run=true" in smoke_text, (
            "smoke checklist must declare dry_run=true"
        )

    def test_smoke_checklist_read_only_true(self, smoke_text: str) -> None:
        assert "read_only=true" in smoke_text, (
            "smoke checklist must declare read_only=true"
        )

    def test_smoke_checklist_live_orders_blocked(self, smoke_text: str) -> None:
        assert "live_orders_blocked=true" in smoke_text, (
            "smoke checklist must declare live_orders_blocked=true"
        )

    def test_quick_start_autotrade_false(self, quick_start_text: str) -> None:
        assert "autotrade=false" in quick_start_text, (
            "quick start must declare autotrade=false"
        )

    def test_quick_start_dry_run_true(self, quick_start_text: str) -> None:
        assert "dry_run=true" in quick_start_text, (
            "quick start must declare dry_run=true"
        )

    def test_quick_start_read_only_true(self, quick_start_text: str) -> None:
        assert "read_only=true" in quick_start_text, (
            "quick start must declare read_only=true"
        )

    def test_quick_start_live_orders_blocked(self, quick_start_text: str) -> None:
        assert "live_orders_blocked=true" in quick_start_text, (
            "quick start must declare live_orders_blocked=true"
        )

    def test_script_autotrade_false(self) -> None:
        script_text = _read(SHORTCUT_PS1)
        assert "autotrade=false" in script_text, (
            "create_desktop_shortcut.ps1 must print autotrade=false in safety banner"
        )

    def test_script_dry_run_true(self) -> None:
        script_text = _read(SHORTCUT_PS1)
        assert "dry_run=true" in script_text, (
            "create_desktop_shortcut.ps1 must print dry_run=true in safety banner"
        )

    def test_script_read_only_true(self) -> None:
        script_text = _read(SHORTCUT_PS1)
        assert "read_only=true" in script_text, (
            "create_desktop_shortcut.ps1 must print read_only=true in safety banner"
        )

    def test_script_live_orders_blocked(self) -> None:
        script_text = _read(SHORTCUT_PS1)
        assert "live_orders_blocked=true" in script_text, (
            "create_desktop_shortcut.ps1 must print live_orders_blocked=true in safety banner"
        )


# ---------------------------------------------------------------------------
# Test 15 — Docs state .lnk must not be committed
# ---------------------------------------------------------------------------

class TestDocsLnkMustNotBeCommitted:
    @pytest.fixture(scope="class")
    def smoke_text(self) -> str:
        return _read(SMOKE_CHECKLIST)

    @pytest.fixture(scope="class")
    def script_text(self) -> str:
        return _read(SHORTCUT_PS1)

    def test_smoke_checklist_states_lnk_must_not_be_committed(self, smoke_text: str) -> None:
        lower = smoke_text.lower()
        assert (
            "must not be committed" in lower
            or "do not commit" in lower
            or "not commit" in lower
        ), (
            "smoke checklist must state that .lnk files must not be committed"
        )

    def test_smoke_checklist_mentions_lnk_artifact(self, smoke_text: str) -> None:
        assert "*.lnk" in smoke_text or ".lnk" in smoke_text, (
            "smoke checklist must mention .lnk in artifact policy"
        )

    def test_script_warns_not_to_commit_lnk(self, script_text: str) -> None:
        lower = script_text.lower()
        assert "do not commit" in lower or "not commit" in lower, (
            "create_desktop_shortcut.ps1 must warn not to commit .lnk files"
        )
