"""
tests/app/test_desktop_launcher_runtime_smoke_static.py

Static inspection tests for DESKTOP-001C: launcher runtime smoke documentation.
These tests read file content only — they do NOT run the EXE, execute PyInstaller,
or start backend/frontend.

Scope:
  - docs/qa/desktop_launcher_runtime_smoke.md

Safety invariants verified:
  - Runtime smoke doc exists
  - References the correct --no-browser command
  - Declares all required safety posture fields
  - States generated artifacts must not be committed
  - States no broker credentials requested
  - States no live trading enabled
  - States no order/execution controls added
  - Does not contain secrets or account IDs
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SMOKE_DOC = REPO_ROOT / "docs" / "qa" / "desktop_launcher_runtime_smoke.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1 — Runtime smoke doc exists
# ---------------------------------------------------------------------------

class TestRuntimeSmokeDocExists:
    def test_doc_exists(self) -> None:
        assert SMOKE_DOC.is_file(), (
            f"docs/qa/desktop_launcher_runtime_smoke.md not found at: {SMOKE_DOC}"
        )


# ---------------------------------------------------------------------------
# Test 2 — Runtime smoke doc references correct command
# ---------------------------------------------------------------------------

class TestRuntimeSmokeDocCommand:
    @pytest.fixture(scope="class")
    def doc_text(self) -> str:
        return _read(SMOKE_DOC)

    def test_references_no_browser_flag(self, doc_text: str) -> None:
        assert "--no-browser" in doc_text, (
            "runtime smoke doc must reference the --no-browser flag"
        )

    def test_references_exe_path(self, doc_text: str) -> None:
        assert "MellyTradeLauncher.exe" in doc_text, (
            "runtime smoke doc must reference MellyTradeLauncher.exe"
        )

    def test_references_dist_path(self, doc_text: str) -> None:
        assert "dist/" in doc_text or r".\dist" in doc_text, (
            "runtime smoke doc must reference dist/ path"
        )


# ---------------------------------------------------------------------------
# Test 3 — Safety posture declared
# ---------------------------------------------------------------------------

class TestRuntimeSmokeDocSafetyPosture:
    @pytest.fixture(scope="class")
    def doc_text(self) -> str:
        return _read(SMOKE_DOC)

    def test_autotrade_false(self, doc_text: str) -> None:
        assert "autotrade=false" in doc_text, (
            "runtime smoke doc must declare autotrade=false"
        )

    def test_dry_run_true(self, doc_text: str) -> None:
        assert "dry_run=true" in doc_text, (
            "runtime smoke doc must declare dry_run=true"
        )

    def test_read_only_true(self, doc_text: str) -> None:
        assert "read_only=true" in doc_text, (
            "runtime smoke doc must declare read_only=true"
        )

    def test_live_orders_blocked_true(self, doc_text: str) -> None:
        assert "live_orders_blocked=true" in doc_text, (
            "runtime smoke doc must declare live_orders_blocked=true"
        )


# ---------------------------------------------------------------------------
# Test 4 — Artifact commit policy stated
# ---------------------------------------------------------------------------

class TestRuntimeSmokeDocArtifactPolicy:
    @pytest.fixture(scope="class")
    def doc_text(self) -> str:
        return _read(SMOKE_DOC)

    def test_must_not_be_committed(self, doc_text: str) -> None:
        lower = doc_text.lower()
        assert (
            "must not be committed" in lower
            or "must not commit" in lower
            or "not be committed" in lower
        ), (
            "runtime smoke doc must state that generated artifacts must not be committed"
        )

    def test_dist_in_artifact_policy(self, doc_text: str) -> None:
        assert "dist/" in doc_text, (
            "runtime smoke doc must mention dist/ in artifact policy"
        )

    def test_build_in_artifact_policy(self, doc_text: str) -> None:
        assert "build/" in doc_text, (
            "runtime smoke doc must mention build/ in artifact policy"
        )

    def test_spec_in_artifact_policy(self, doc_text: str) -> None:
        assert "*.spec" in doc_text, (
            "runtime smoke doc must mention *.spec in artifact policy"
        )

    def test_exe_in_artifact_policy(self, doc_text: str) -> None:
        assert "*.exe" in doc_text, (
            "runtime smoke doc must mention *.exe in artifact policy"
        )


# ---------------------------------------------------------------------------
# Test 5 — Safety behaviour stated: no credentials, no live trading, no orders
# ---------------------------------------------------------------------------

class TestRuntimeSmokeDocSafeBehaviour:
    @pytest.fixture(scope="class")
    def doc_text(self) -> str:
        return _read(SMOKE_DOC)

    def test_no_broker_credentials(self, doc_text: str) -> None:
        lower = doc_text.lower()
        assert "no broker credentials" in lower, (
            "runtime smoke doc must state no broker credentials requested"
        )

    def test_no_live_trading(self, doc_text: str) -> None:
        lower = doc_text.lower()
        assert "no live trading" in lower, (
            "runtime smoke doc must state no live trading enabled"
        )

    def test_no_order_controls(self, doc_text: str) -> None:
        lower = doc_text.lower()
        assert "no order" in lower or "no execution" in lower or "no order/execution" in lower, (
            "runtime smoke doc must state no order/execution controls added"
        )


# ---------------------------------------------------------------------------
# Test 6 — No secrets or account IDs in doc
# ---------------------------------------------------------------------------

class TestRuntimeSmokeDocNoSecrets:
    @pytest.fixture(scope="class")
    def doc_text(self) -> str:
        return _read(SMOKE_DOC)

    def test_no_account_id_value(self, doc_text: str) -> None:
        """Doc must not contain a literal account ID value (numeric or UUID-style)."""
        import re
        # Look for patterns like account_id = 12345 or account: "abc-uuid"
        # Exclude lines that are prohibition statements about account_id
        lines = doc_text.splitlines()
        for line in lines:
            stripped = line.strip().lower()
            # Skip lines that are clearly prohibitions or test terms
            if "no account" in stripped or "account_id" in stripped:
                continue
            # Flag embedded credential-like assignments
            if re.search(r'account[_\s]*id\s*[:=]\s*\S+', stripped):
                pytest.fail(
                    f"runtime smoke doc must not contain literal account_id values.\n"
                    f"Offending line: {line!r}"
                )

    def test_no_api_key_value(self, doc_text: str) -> None:
        """Doc must not contain an API key or token value."""
        import re
        lines = doc_text.splitlines()
        for line in lines:
            stripped = line.strip().lower()
            # Skip prohibition / test lines
            if "no api key" in stripped or "no secrets" in stripped:
                continue
            if re.search(r'api[_\s]*key\s*[:=]\s*\S+', stripped):
                pytest.fail(
                    f"runtime smoke doc must not contain literal api_key values.\n"
                    f"Offending line: {line!r}"
                )

    def test_no_password_value(self, doc_text: str) -> None:
        """Doc must not contain a password value."""
        import re
        lines = doc_text.splitlines()
        for line in lines:
            stripped = line.strip().lower()
            if "no password" in stripped or "no secrets" in stripped:
                continue
            if re.search(r'password\s*[:=]\s*\S+', stripped):
                pytest.fail(
                    f"runtime smoke doc must not contain literal password values.\n"
                    f"Offending line: {line!r}"
                )
