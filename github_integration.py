"""GitHub integration for auto-committing trading signals and results.

This module provides real-time Git operations for the trading bot:
- Auto-commit trading signals to GitHub
- Push trading results and logs
- Trigger GitHub Actions via repository_dispatch
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class GitHubIntegration:
    """Handle Git commits and GitHub API interactions."""

    def __init__(self, token: Optional[str] = None, repo_path: Optional[Path] = None):
        """
        Initialize GitHub integration.

        Args:
            token: GitHub token (reads from GITHUB_TOKEN env if not provided)
            repo_path: Repository root path (auto-detects if None)
        """
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.repo_path = repo_path or self._find_repo_root()
        self.user = os.getenv("GITHUB_USER", "Alpha Trading Bot")
        self.email = os.getenv("GITHUB_EMAIL", "alpha-bot@github.com")

    @staticmethod
    def _find_repo_root() -> Path:
        """Find git repository root."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()

    def configure_git(self) -> None:
        """Set git user config."""
        try:
            subprocess.run(
                ["git", "config", "user.name", self.user],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.email", self.email],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
            )
            logger.info(f"✅ Git configured: {self.user} <{self.email}>")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git config failed: {e.stderr.decode()}")
            raise

    def stage_files(self, patterns: list[str]) -> bool:
        """
        Stage files for commit.

        Args:
            patterns: List of file patterns to stage (e.g., ['results/', 'logs/'])

        Returns:
            True if files were staged, False if nothing to stage
        """
        try:
            for pattern in patterns:
                subprocess.run(
                    ["git", "add", pattern],
                    cwd=self.repo_path,
                    check=False,  # Don't fail if pattern doesn't match
                    capture_output=True,
                )

            # Check if there are staged changes
            result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=self.repo_path,
                capture_output=True,
            )
            has_changes = result.returncode != 0
            return has_changes
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Staging failed: {e.stderr.decode()}")
            return False

    def commit(
        self, message: str, patterns: Optional[list[str]] = None
    ) -> Optional[str]:
        """
        Commit changes to git.

        Args:
            message: Commit message
            patterns: Files to stage (if None, uses already staged files)

        Returns:
            Commit SHA if successful, None otherwise
        """
        try:
            if patterns and not self.stage_files(patterns):
                logger.info("ℹ️ No changes to commit")
                return None

            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
            )
            commit_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()[:7]
            logger.info(f"✅ Committed: {commit_sha} - {message}")
            return commit_sha
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Commit failed: {e.stderr.decode()}")
            return None

    def push(self, branch: str = "main") -> bool:
        """
        Push changes to remote.

        Args:
            branch: Branch to push

        Returns:
            True if push succeeded
        """
        try:
            subprocess.run(
                ["git", "push", "origin", branch],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
            )
            logger.info(f"✅ Pushed to origin/{branch}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Push failed: {e.stderr.decode()}")
            return False

    def commit_and_push(
        self, message: str, patterns: list[str], branch: str = "main"
    ) -> bool:
        """
        Commit and push in one operation.

        Args:
            message: Commit message
            patterns: Files to commit
            branch: Target branch

        Returns:
            True if successful
        """
        self.configure_git()
        if not self.stage_files(patterns):
            logger.info("ℹ️ No changes to commit")
            return False

        sha = self.commit(message)
        if sha:
            return self.push(branch)
        return False

    def trigger_workflow(
        self,
        event_type: str,
        payload: dict[str, Any],
        repo_owner: Optional[str] = None,
        repo_name: Optional[str] = None,
    ) -> bool:
        return _run_async(
            self.trigger_workflow_async(
                event_type=event_type,
                payload=payload,
                repo_owner=repo_owner,
                repo_name=repo_name,
            )
        )

    async def trigger_workflow_async(
        self,
        event_type: str,
        payload: dict[str, Any],
        repo_owner: Optional[str] = None,
        repo_name: Optional[str] = None,
    ) -> bool:
        """
        Trigger GitHub Actions workflow via repository_dispatch.

        Args:
            event_type: Event type (e.g., 'trade-signal')
            payload: Payload to send with event
            repo_owner: GitHub owner (reads from GITHUB_REPOSITORY env)
            repo_name: GitHub repo name (reads from GITHUB_REPOSITORY env)

        Returns:
            True if dispatched successfully
        """
        if not self.token:
            logger.warning("⚠️ GITHUB_TOKEN not set, workflow dispatch disabled")
            return False

        if not repo_owner or not repo_name:
            repo_full = os.getenv("GITHUB_REPOSITORY", "").split("/")
            if len(repo_full) != 2:
                logger.error("❌ Cannot determine repository")
                return False
            repo_owner, repo_name = repo_full

        try:
            import httpx

            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dispatches"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+raw+json",
            }
            data = {"event_type": event_type, "client_payload": payload}

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=data, headers=headers)
            if response.status_code == 204:
                logger.info(f"✅ Workflow dispatched: {event_type}")
                return True
            else:
                logger.error(
                    f"❌ Dispatch failed: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"❌ Workflow dispatch error: {e}")
            return False


class TradingResultsCommitter:
    """Convenience wrapper for committing trading results and signals."""

    def __init__(self):
        """Initialize committer with default config."""
        self.git = GitHubIntegration()
        self.results_dir = Path("results")
        self.logs_dir = Path("logs")

    def record_signal(
        self,
        signal: str,
        symbol: str,
        confidence: float,
        repo_owner: Optional[str] = None,
        repo_name: Optional[str] = None,
    ) -> bool:
        """
        Record a trade signal and commit + push to GitHub.

        Args:
            signal: Signal type (BUY/SELL/HOLD)
            symbol: Trading symbol (e.g., EURUSD)
            confidence: Confidence level (0-100)
            repo_owner: GitHub owner
            repo_name: GitHub repo name

        Returns:
            True if recorded and committed
        """
        try:
            # Create signal record
            signal_dir = self.results_dir / "signals"
            signal_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.utcnow().isoformat()
            signal_file = (
                signal_dir
                / f"{symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            )

            signal_data = {
                "timestamp": timestamp,
                "signal": signal,
                "symbol": symbol,
                "confidence": confidence,
            }

            with open(signal_file, "w") as f:
                json.dump(signal_data, f, indent=2)

            logger.info(f"📊 Signal recorded: {signal_file}")

            # Commit and push
            message = f"🚀 Signal: {signal} {symbol} (confidence: {confidence:.0f}%)"
            success = self.git.commit_and_push(message, ["results/signals/"])

            # Trigger workflow for high-confidence signals
            if success and confidence >= 80:
                self.git.trigger_workflow(
                    "trade-signal",
                    {
                        "signal": signal,
                        "symbol": symbol,
                        "confidence": int(confidence),
                    },
                    repo_owner,
                    repo_name,
                )

            return success
        except Exception as e:
            logger.error(f"❌ Failed to record signal: {e}")
            return False

    def commit_results(self) -> bool:
        """
        Commit trading results and logs.

        Returns:
            True if committed
        """
        try:
            message = f"📊 Trading cycle: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
            return self.git.commit_and_push(message, ["results/", "logs/"])
        except Exception as e:
            logger.error(f"❌ Failed to commit results: {e}")
            return False


def _run_async(awaitable):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(awaitable)
    if hasattr(awaitable, "close"):
        awaitable.close()
    raise RuntimeError("Use the async API when an event loop is already running")
