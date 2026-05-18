from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
QA_SMOKE_DOC = REPO_ROOT / "docs" / "qa" / "local_demo_tester_smoke_checklist.md"
QA_404_DOC = REPO_ROOT / "docs" / "qa" / "local_demo_404_regression_checklist.md"
PLAN_DOC = REPO_ROOT / "docs" / "tasks" / "desktop_launcher_exe_plan.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestLocalDemoSmokeChecklistDoc:
    @pytest.fixture(scope="class")
    def doc_text(self) -> str:
        return _read(QA_SMOKE_DOC)

    def test_doc_exists(self) -> None:
        assert QA_SMOKE_DOC.is_file(), f"missing doc: {QA_SMOKE_DOC}"

    def test_doc_includes_safety_posture(self, doc_text: str) -> None:
        for token in (
            "autotrade=false",
            "dry_run=true",
            "read_only=true",
            "live_orders_blocked=true",
            "max risk <=1%",
        ):
            assert token in doc_text

    def test_doc_includes_endpoint_paths(self, doc_text: str) -> None:
        for path in (
            "/api/backtest/summary",
            "/api/investment",
            "/api/signals/feed",
        ):
            assert path in doc_text

    def test_doc_says_no_live_trading(self, doc_text: str) -> None:
        assert "no live trading" in doc_text.lower()

    def test_doc_says_no_broker_credentials(self, doc_text: str) -> None:
        assert "broker credentials" in doc_text.lower()

    def test_doc_says_no_order_execution_controls(self, doc_text: str) -> None:
        lower = doc_text.lower()
        assert "order/execution controls" in lower or "order execution" in lower

    def test_doc_says_no_investment_advice(self, doc_text: str) -> None:
        assert "investment advice" in doc_text.lower()

    def test_doc_says_no_guaranteed_profit(self, doc_text: str) -> None:
        assert "guaranteed profit" in doc_text.lower()

    def test_doc_includes_result_labels(self, doc_text: str) -> None:
        lower = doc_text.lower()
        assert "pass" in lower
        assert "blocked" in lower

    def test_doc_includes_invoke_webrequest(self, doc_text: str) -> None:
        assert "Invoke-WebRequest" in doc_text

    def test_doc_mentions_local_demo_endpoint_test_file(self, doc_text: str) -> None:
        assert "test_local_demo_readonly_endpoints.py" in doc_text


class TestLocalDemo404RegressionChecklistDoc:
    @pytest.fixture(scope="class")
    def doc_text(self) -> str:
        return _read(QA_404_DOC)

    def test_doc_exists(self) -> None:
        assert QA_404_DOC.is_file(), f"missing doc: {QA_404_DOC}"

    def test_doc_includes_endpoint_paths(self, doc_text: str) -> None:
        for path in (
            "/api/backtest/summary",
            "/api/investment",
            "/api/signals/feed",
        ):
            assert path in doc_text

    def test_doc_includes_expected_posture(self, doc_text: str) -> None:
        for token in (
            "read-only",
            "dry-run-only",
            "degraded",
            "deterministic",
            "investment advice",
            "guaranteed-profit",
        ):
            assert token in doc_text.lower()

    def test_doc_includes_invoke_webrequest(self, doc_text: str) -> None:
        assert "Invoke-WebRequest" in doc_text

    def test_doc_mentions_local_demo_endpoint_test_file(self, doc_text: str) -> None:
        assert "test_local_demo_readonly_endpoints.py" in doc_text

    def test_doc_includes_pass_blocked(self, doc_text: str) -> None:
        lower = doc_text.lower()
        assert "pass" in lower
        assert "blocked" in lower


class TestDesktopLauncherPlanUpdate:
    @pytest.fixture(scope="class")
    def plan_text(self) -> str:
        return _read(PLAN_DOC)

    def test_plan_mentions_qa_local_demo_section(self, plan_text: str) -> None:
        assert "QA-LOCAL-DEMO-001" in plan_text

    def test_plan_mentions_checklists(self, plan_text: str) -> None:
        assert "local_demo_tester_smoke_checklist.md" in plan_text
        assert "local_demo_404_regression_checklist.md" in plan_text

