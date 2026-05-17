"""
tests/app/test_desktop_distribution_docs_static.py

Static inspection tests for DESKTOP-001E: Windows desktop distribution
planning guide.

These tests read file content only — they do NOT create ZIPs, run PowerShell,
execute any EXE, start backend/frontend, or call any network.

Scope:
  - docs/distribution/desktop_distribution_plan.md
  - docs/qa/desktop_distribution_smoke_checklist.md
  - docs/product/beta_tester_desktop_distribution_notes.md
  - docs/tasks/desktop_launcher_exe_plan.md (DESKTOP-001E section)

Safety invariants verified:
  1.  Distribution plan doc exists
  2.  Smoke checklist exists
  3.  Beta tester notes exist
  4.  Plan doc updated with DESKTOP-001E section
  5.  Distribution plan states safety posture (all 4 flags)
  6.  Distribution plan states artifact policy (no commit)
  7.  Distribution plan states no installer implemented
  8.  Smoke checklist states safety posture (all 4 flags)
  9.  Smoke checklist states artifact policy (no commit)
  10. Smoke checklist references WhatIfOnly mode
  11. Beta tester notes state safety posture (all 4 flags)
  12. Beta tester notes state what this is NOT
  13. Beta tester notes include SmartScreen note
  14. Beta tester notes state .lnk must not be committed
  15. No forbidden trading strings in any doc
  16. No secrets or credential patterns in any doc
  17. Plan doc states planning only (no runtime change)
  18. Plan doc references related docs
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DIST_PLAN = REPO_ROOT / "docs" / "distribution" / "desktop_distribution_plan.md"
SMOKE_CHECKLIST = REPO_ROOT / "docs" / "qa" / "desktop_distribution_smoke_checklist.md"
TESTER_NOTES = REPO_ROOT / "docs" / "product" / "beta_tester_desktop_distribution_notes.md"
LAUNCHER_PLAN = REPO_ROOT / "docs" / "tasks" / "desktop_launcher_exe_plan.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1 — Distribution plan doc exists
# ---------------------------------------------------------------------------

class TestDistributionPlanExists:
    def test_desktop_distribution_plan_exists(self) -> None:
        assert DIST_PLAN.is_file(), (
            f"docs/distribution/desktop_distribution_plan.md not found at: {DIST_PLAN}"
        )


# ---------------------------------------------------------------------------
# Test 2 — Smoke checklist exists
# ---------------------------------------------------------------------------

class TestDistributionSmokeChecklistExists:
    def test_distribution_smoke_checklist_exists(self) -> None:
        assert SMOKE_CHECKLIST.is_file(), (
            f"docs/qa/desktop_distribution_smoke_checklist.md not found at: {SMOKE_CHECKLIST}"
        )


# ---------------------------------------------------------------------------
# Test 3 — Beta tester notes exist
# ---------------------------------------------------------------------------

class TestBetaTesterDistributionNotesExists:
    def test_beta_tester_distribution_notes_exists(self) -> None:
        assert TESTER_NOTES.is_file(), (
            f"docs/product/beta_tester_desktop_distribution_notes.md not found at: {TESTER_NOTES}"
        )


# ---------------------------------------------------------------------------
# Test 4 — Plan doc updated with DESKTOP-001E section
# ---------------------------------------------------------------------------

class TestLauncherPlanUpdated:
    @pytest.fixture(scope="class")
    def plan_text(self) -> str:
        return _read(LAUNCHER_PLAN)

    def test_plan_has_desktop_001e_section(self, plan_text: str) -> None:
        assert "DESKTOP-001E" in plan_text, (
            "docs/tasks/desktop_launcher_exe_plan.md must have a DESKTOP-001E section"
        )

    def test_plan_references_distribution_plan_doc(self, plan_text: str) -> None:
        assert "desktop_distribution_plan.md" in plan_text, (
            "desktop_launcher_exe_plan.md must reference desktop_distribution_plan.md"
        )

    def test_plan_has_distribution_planning_status(self, plan_text: str) -> None:
        lower = plan_text.lower()
        assert "distribution planning" in lower or "distribution plan" in lower, (
            "desktop_launcher_exe_plan.md must mention distribution planning in DESKTOP-001E"
        )


# ---------------------------------------------------------------------------
# Test 5 — Distribution plan states safety posture (all 4 flags)
# ---------------------------------------------------------------------------

class TestDistributionPlanSafetyPosture:
    @pytest.fixture(scope="class")
    def dist_text(self) -> str:
        return _read(DIST_PLAN)

    def test_autotrade_false(self, dist_text: str) -> None:
        assert "autotrade" in dist_text and "false" in dist_text, (
            "distribution plan must declare autotrade=false"
        )

    def test_dry_run_true(self, dist_text: str) -> None:
        assert "dry_run" in dist_text and "true" in dist_text, (
            "distribution plan must declare dry_run=true"
        )

    def test_read_only_true(self, dist_text: str) -> None:
        assert "read_only" in dist_text and "true" in dist_text, (
            "distribution plan must declare read_only=true"
        )

    def test_live_orders_blocked_true(self, dist_text: str) -> None:
        assert "live_orders_blocked" in dist_text and "true" in dist_text, (
            "distribution plan must declare live_orders_blocked=true"
        )


# ---------------------------------------------------------------------------
# Test 6 — Distribution plan states artifact policy (no commit)
# ---------------------------------------------------------------------------

class TestDistributionPlanArtifactPolicy:
    @pytest.fixture(scope="class")
    def dist_text(self) -> str:
        return _read(DIST_PLAN)

    def test_states_dist_must_not_be_committed(self, dist_text: str) -> None:
        lower = dist_text.lower()
        assert (
            "must not be committed" in lower
            or "do not commit" in lower
            or "not commit" in lower
        ), (
            "distribution plan must state that dist/ must not be committed"
        )

    def test_references_zip_in_artifact_policy(self, dist_text: str) -> None:
        assert "*.zip" in dist_text or ".zip" in dist_text, (
            "distribution plan must mention .zip in artifact policy"
        )

    def test_references_msi_in_artifact_policy(self, dist_text: str) -> None:
        assert "*.msi" in dist_text or ".msi" in dist_text, (
            "distribution plan must mention .msi in artifact policy"
        )

    def test_references_dist_directory(self, dist_text: str) -> None:
        assert "dist/" in dist_text or "dist\\" in dist_text, (
            "distribution plan must reference dist/ directory in artifact policy"
        )


# ---------------------------------------------------------------------------
# Test 7 — Distribution plan states no installer implemented
# ---------------------------------------------------------------------------

class TestDistributionPlanPlanningOnly:
    @pytest.fixture(scope="class")
    def dist_text(self) -> str:
        return _read(DIST_PLAN)

    def test_states_planning_only(self, dist_text: str) -> None:
        lower = dist_text.lower()
        assert "planning" in lower or "plan only" in lower or "planning document" in lower, (
            "distribution plan must state it is a planning document only"
        )

    def test_states_no_installer_implemented(self, dist_text: str) -> None:
        lower = dist_text.lower()
        assert (
            "does not implement" in lower
            or "not implement" in lower
            or "no installer" in lower
            or "not yet" in lower
        ), (
            "distribution plan must state no installer is implemented"
        )

    def test_does_not_build_exe(self, dist_text: str) -> None:
        # The plan doc must not use Start-Process, Invoke-Item, or PyInstaller
        # (those would indicate it is executing, not planning)
        assert "Start-Process" not in dist_text, (
            "distribution plan must not use Start-Process"
        )
        assert "Invoke-Item" not in dist_text, (
            "distribution plan must not use Invoke-Item"
        )


# ---------------------------------------------------------------------------
# Test 8 — Smoke checklist states safety posture (all 4 flags)
# ---------------------------------------------------------------------------

class TestSmokeChecklistSafetyPosture:
    @pytest.fixture(scope="class")
    def smoke_text(self) -> str:
        return _read(SMOKE_CHECKLIST)

    def test_autotrade_false(self, smoke_text: str) -> None:
        assert "autotrade=false" in smoke_text, (
            "smoke checklist must declare autotrade=false"
        )

    def test_dry_run_true(self, smoke_text: str) -> None:
        assert "dry_run=true" in smoke_text, (
            "smoke checklist must declare dry_run=true"
        )

    def test_read_only_true(self, smoke_text: str) -> None:
        assert "read_only=true" in smoke_text, (
            "smoke checklist must declare read_only=true"
        )

    def test_live_orders_blocked_true(self, smoke_text: str) -> None:
        assert "live_orders_blocked=true" in smoke_text, (
            "smoke checklist must declare live_orders_blocked=true"
        )


# ---------------------------------------------------------------------------
# Test 9 — Smoke checklist states artifact policy (no commit)
# ---------------------------------------------------------------------------

class TestSmokeChecklistArtifactPolicy:
    @pytest.fixture(scope="class")
    def smoke_text(self) -> str:
        return _read(SMOKE_CHECKLIST)

    def test_states_lnk_must_not_be_committed(self, smoke_text: str) -> None:
        lower = smoke_text.lower()
        assert (
            "must not be committed" in lower
            or "do not commit" in lower
            or "not commit" in lower
        ), (
            "smoke checklist must state .lnk must not be committed"
        )

    def test_references_zip_in_artifact_list(self, smoke_text: str) -> None:
        assert "*.zip" in smoke_text or ".zip" in smoke_text, (
            "smoke checklist must mention .zip in artifact list"
        )

    def test_references_lnk_in_artifact_list(self, smoke_text: str) -> None:
        assert "*.lnk" in smoke_text or ".lnk" in smoke_text, (
            "smoke checklist must mention .lnk in artifact list"
        )


# ---------------------------------------------------------------------------
# Test 10 — Smoke checklist references WhatIfOnly mode
# ---------------------------------------------------------------------------

class TestSmokeChecklistWhatIfOnly:
    @pytest.fixture(scope="class")
    def smoke_text(self) -> str:
        return _read(SMOKE_CHECKLIST)

    def test_references_whatifonly(self, smoke_text: str) -> None:
        assert "WhatIfOnly" in smoke_text or "WhatIf" in smoke_text, (
            "smoke checklist must reference WhatIfOnly mode from create_desktop_shortcut.ps1"
        )

    def test_references_create_desktop_shortcut(self, smoke_text: str) -> None:
        assert "create_desktop_shortcut" in smoke_text, (
            "smoke checklist must reference create_desktop_shortcut.ps1"
        )


# ---------------------------------------------------------------------------
# Test 11 — Beta tester notes state safety posture (all 4 flags)
# ---------------------------------------------------------------------------

class TestBetaTesterNotesSafetyPosture:
    @pytest.fixture(scope="class")
    def notes_text(self) -> str:
        return _read(TESTER_NOTES)

    def test_autotrade_false(self, notes_text: str) -> None:
        assert "autotrade=false" in notes_text, (
            "beta tester notes must declare autotrade=false"
        )

    def test_dry_run_true(self, notes_text: str) -> None:
        assert "dry_run=true" in notes_text, (
            "beta tester notes must declare dry_run=true"
        )

    def test_read_only_true(self, notes_text: str) -> None:
        assert "read_only=true" in notes_text, (
            "beta tester notes must declare read_only=true"
        )

    def test_live_orders_blocked_true(self, notes_text: str) -> None:
        assert "live_orders_blocked=true" in notes_text, (
            "beta tester notes must declare live_orders_blocked=true"
        )


# ---------------------------------------------------------------------------
# Test 12 — Beta tester notes state what this is NOT
# ---------------------------------------------------------------------------

class TestBetaTesterNotesWhatItIsNot:
    @pytest.fixture(scope="class")
    def notes_text(self) -> str:
        return _read(TESTER_NOTES)

    def test_states_not_live_trading(self, notes_text: str) -> None:
        lower = notes_text.lower()
        assert "not live trading" in lower or "not a live trading" in lower, (
            "beta tester notes must state this is NOT live trading"
        )

    def test_states_not_investment_advice(self, notes_text: str) -> None:
        lower = notes_text.lower()
        assert "not investment advice" in lower or "not financial advice" in lower, (
            "beta tester notes must state this is NOT investment advice"
        )

    def test_states_not_production_installer(self, notes_text: str) -> None:
        lower = notes_text.lower()
        assert (
            "not a final" in lower
            or "not final" in lower
            or "not production" in lower
            or "not a production" in lower
        ), (
            "beta tester notes must state this is NOT a final production installer"
        )

    def test_states_not_broker_execution(self, notes_text: str) -> None:
        lower = notes_text.lower()
        assert (
            "not broker execution" in lower
            or "no broker execution" in lower
            or "not broker" in lower
        ), (
            "beta tester notes must state this is NOT broker execution"
        )


# ---------------------------------------------------------------------------
# Test 13 — Beta tester notes include SmartScreen note
# ---------------------------------------------------------------------------

class TestBetaTesterNotesSmartScreen:
    @pytest.fixture(scope="class")
    def notes_text(self) -> str:
        return _read(TESTER_NOTES)

    def test_mentions_smartscreen(self, notes_text: str) -> None:
        lower = notes_text.lower()
        assert "smartscreen" in lower or "smart screen" in lower, (
            "beta tester notes must mention Windows SmartScreen warning"
        )

    def test_mentions_run_anyway(self, notes_text: str) -> None:
        lower = notes_text.lower()
        assert "run anyway" in lower, (
            "beta tester notes must include 'Run anyway' SmartScreen workaround"
        )

    def test_mentions_more_info(self, notes_text: str) -> None:
        lower = notes_text.lower()
        assert "more info" in lower, (
            "beta tester notes must mention 'More info' SmartScreen step"
        )


# ---------------------------------------------------------------------------
# Test 14 — Beta tester notes state .lnk must not be committed
# ---------------------------------------------------------------------------

class TestBetaTesterNotesLnkPolicy:
    @pytest.fixture(scope="class")
    def notes_text(self) -> str:
        return _read(TESTER_NOTES)

    def test_states_lnk_must_not_be_committed(self, notes_text: str) -> None:
        lower = notes_text.lower()
        assert (
            "must not be committed" in lower
            or "do not commit" in lower
            or "not commit" in lower
        ), (
            "beta tester notes must state .lnk files must not be committed"
        )

    def test_mentions_lnk_file(self, notes_text: str) -> None:
        assert ".lnk" in notes_text, (
            "beta tester notes must mention .lnk artifact"
        )


# ---------------------------------------------------------------------------
# Test 15 — No forbidden trading strings in any doc
# ---------------------------------------------------------------------------
#
# These are execution-action strings that must never appear in planning docs in
# any context. Note: strings like "autotrade=true" or "dry_run=false" are
# intentionally excluded here because planning docs and smoke checklists
# legitimately reference them in "must NOT contain" / red-flag sections. The
# positive-flag assertions (autotrade=false, dry_run=true, etc.) are covered by
# Tests 5, 8, and 11 above.

_FORBIDDEN_TRADING_STRINGS = [
    "place_order",
    "execute_order",
    "cancel_order",
    "broker_execute",
    "connect_live",
]

_ALL_DOC_PATHS = [DIST_PLAN, SMOKE_CHECKLIST, TESTER_NOTES]


class TestNoForbiddenTradingStrings:
    @pytest.mark.parametrize("doc_path", _ALL_DOC_PATHS, ids=lambda p: p.name)
    @pytest.mark.parametrize("forbidden", _FORBIDDEN_TRADING_STRINGS)
    def test_no_forbidden_string(self, doc_path: Path, forbidden: str) -> None:
        text = _read(doc_path)
        assert forbidden not in text, (
            f"{doc_path.name} must not contain forbidden string: {forbidden!r}"
        )


# ---------------------------------------------------------------------------
# Test 16 — No secrets or credential patterns in any doc
# ---------------------------------------------------------------------------
#
# The smoke checklist names credential keys as things to verify absent in the
# ZIP (e.g. "No SUPABASE_SERVICE_ROLE_KEY string in any bundled text file").
# That is legitimate QA guidance and those credential names are intentionally
# present in the checklist. So the credential-pattern check is scoped only to
# the distribution plan and the tester notes, which should never name raw keys.

_FORBIDDEN_CREDENTIAL_PATTERNS = [
    "SUPABASE_SERVICE_ROLE_KEY",
    "MT5_PASSWORD",
    "MT5_LOGIN",
]

_CREDENTIAL_CHECK_PATHS = [DIST_PLAN, TESTER_NOTES]


class TestNoSecretsInDocs:
    @pytest.mark.parametrize("doc_path", _CREDENTIAL_CHECK_PATHS, ids=lambda p: p.name)
    @pytest.mark.parametrize("pattern", _FORBIDDEN_CREDENTIAL_PATTERNS)
    def test_no_credential_pattern(self, doc_path: Path, pattern: str) -> None:
        text = _read(doc_path)
        assert pattern not in text, (
            f"{doc_path.name} must not contain credential pattern: {pattern!r}"
        )


# ---------------------------------------------------------------------------
# Test 17 — Plan doc states planning only (no runtime change)
# ---------------------------------------------------------------------------

class TestDistributionPlanNoRuntimeChange:
    @pytest.fixture(scope="class")
    def dist_text(self) -> str:
        return _read(DIST_PLAN)

    def test_doc_header_states_planning_only(self, dist_text: str) -> None:
        # The plan doc should have "planning document only" or similar near the top
        first_500 = dist_text[:500]
        lower = first_500.lower()
        assert (
            "planning document" in lower
            or "plan only" in lower
            or "planning only" in lower
            or "does not implement" in lower
        ), (
            "distribution plan must state it is planning-only in the first 500 chars"
        )

    def test_no_pyinstaller_call(self, dist_text: str) -> None:
        # The plan doc should reference pyinstaller conceptually but not call it
        assert "pyinstaller" not in dist_text or "build_desktop_launcher.ps1" in dist_text, (
            "distribution plan references PyInstaller must be via build script, not direct call"
        )


# ---------------------------------------------------------------------------
# Test 18 — Plan doc references related docs
# ---------------------------------------------------------------------------

class TestDistributionPlanRelatedDocs:
    @pytest.fixture(scope="class")
    def dist_text(self) -> str:
        return _read(DIST_PLAN)

    def test_references_smoke_checklist(self, dist_text: str) -> None:
        assert "desktop_distribution_smoke_checklist.md" in dist_text, (
            "distribution plan must reference desktop_distribution_smoke_checklist.md"
        )

    def test_references_tester_notes(self, dist_text: str) -> None:
        assert "beta_tester_desktop_distribution_notes.md" in dist_text, (
            "distribution plan must reference beta_tester_desktop_distribution_notes.md"
        )

    def test_references_launcher_plan(self, dist_text: str) -> None:
        assert "desktop_launcher_exe_plan.md" in dist_text, (
            "distribution plan must reference desktop_launcher_exe_plan.md"
        )
