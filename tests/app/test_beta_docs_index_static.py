from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def import_lines(text: str) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            lines.append(stripped.lower())
    return lines


class TestBetaDocsIndexStatic:
    def test_expected_files_exist(self) -> None:
        for path in (
            "docs/beta/README.md",
            "docs/README.md",
            "README.md",
            "docs/tasks/desktop_launcher_exe_plan.md",
        ):
            assert (ROOT / path).exists(), path

    def test_plan_mentions_beta_docs_index(self) -> None:
        assert "BETA-DOCS-INDEX-001" in read("docs/tasks/desktop_launcher_exe_plan.md")

    def test_beta_index_links_rollout_docs(self) -> None:
        text = read("docs/beta/README.md")
        for token in (
            "Beta Rollout Operator Command Center",
            "Beta Rollout Operator Master Checklist",
            "Source-Only Beta Package Review",
            "Source-Only Beta Preflight Checklist",
            "Source-Only First Tester Rollout",
            "Source-Only Beta Rollout Gate",
            "Source-Only Tester Invite Message",
            "Source-Only Tester Feedback Form",
            "Local Demo Tester Smoke Checklist",
            "Local Demo 404 Regression Checklist",
            "First Source-Only Tester Feedback Tracker",
            "First Source-Only Tester Feedback Review Gate",
            "Second Source-Only Tester Expansion Gate",
            "Second Source-Only Tester Pre-Access Checklist",
        ):
            assert token in text

    def test_entrypoints_link_beta_index(self) -> None:
        docs_readme = read("docs/README.md")
        root_readme = read("README.md")
        assert "MellyTrade Beta Docs Index" in docs_readme
        assert "Beta Docs Index" in docs_readme
        assert "Beta Docs Index" in root_readme
        assert "Beta Rollout Operator Command Center" in docs_readme
        assert "Beta Rollout Operator Master Checklist" in docs_readme
        assert "Beta Rollout Operator Command Center" in root_readme
        assert "Beta Rollout Operator Master Checklist" in root_readme

    def test_beta_docs_include_safety_posture(self) -> None:
        combined = "\n".join(
            [read("docs/beta/README.md"), read("docs/README.md"), read("README.md")]
        ).lower()
        for token in (
            "autotrade=false",
            "dry_run=true",
            "read_only=true",
            "live_orders_blocked=true",
            "max risk <=1%",
        ):
            assert token in combined

    def test_beta_docs_prohibit_high_risk_actions(self) -> None:
        combined = "\n".join(
            [read("docs/beta/README.md"), read("docs/README.md"), read("README.md")]
        ).lower()
        for token in (
            "live trading",
            "broker execution",
            "investment advice",
            "generated artifact release",
        ):
            assert token in combined
        assert "does not grant access" in combined
        assert "does not grant access, send invites" in combined

    def test_no_mutating_or_network_imports(self) -> None:
        import_lines_text = import_lines(
            read("tests/app/test_beta_docs_index_static.py")
        )
        banned = (
            "requests",
            "httpx",
            "aiohttp",
            "socket",
            "subprocess",
            "shutil",
            "playwright",
            "selenium",
            "webbrowser",
            "fastapi",
        )
        for line in import_lines_text:
            for token in banned:
                assert token not in line, f"unexpected import line: {line!r}"

    def test_tests_do_not_grant_access_or_send_messages(self) -> None:
        import_lines_text = import_lines(
            read("tests/app/test_beta_docs_index_static.py")
        )
        for line in import_lines_text:
            assert "grant" not in line
            assert "send" not in line
            assert "message" not in line
