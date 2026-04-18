# claude_ai.py
from __future__ import annotations

import logging
from typing import Optional

import requests

from prompts import get_prompt

logger = logging.getLogger(__name__)


class ClaudeAIIntegration:
    """Integracja z Claude API (Anthropic)"""

    BASE_URL = "https://api.anthropic.com/v1/messages"
    MODEL = "claude-opus-4-20250514"  # lub claude-sonnet-4-20250514 dla szybszych

    def __init__(self, api_key: Optional[str] = None, enabled: bool = True):
        import os

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.enabled = enabled and bool(self.api_key)
        if not self.enabled:
            logger.warning("Claude AI integration disabled - no API key")

    def get_full_analysis(self, report_type: str, **kwargs) -> str:
        """Generate professional analysis using Claude"""
        if not self.enabled:
            return "Claude AI is disabled"

        try:
            prompt_text = get_prompt(report_type, **kwargs)

            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            body = {
                "model": self.MODEL,
                "max_tokens": 4000,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt_text}],
            }

            response = requests.post(
                self.BASE_URL, headers=headers, json=body, timeout=60
            )
            response.raise_for_status()

            data = response.json()
            return data["content"][0].get("text", "No response from Claude")

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return f"Error: {str(e)}"

    def test_connection(self) -> bool:
        """Test if API key works"""
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            body = {
                "model": self.MODEL,
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Say 'Hello'"}],
            }
            response = requests.post(
                self.BASE_URL, headers=headers, json=body, timeout=10
            )
            return response.status_code == 200
        except Exception as exc:
            logger.debug("Claude connection test failed: %s", exc)
            return False
