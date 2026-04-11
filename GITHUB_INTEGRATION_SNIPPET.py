"""
Quick integration snippet for main.py and ai_engine.py

Add this to enable real-time GitHub commits while your trading bot runs.
"""

# ============================================================================
# OPTION A: Add to main.py (recommended)
# ============================================================================

# Near the top of main.py, after other imports:
from github_integration import TradingResultsCommitter


# In your main() function or trading loop:
def main():
    # Initialize GitHub committer (requires GITHUB_TOKEN env var)
    try:
        committer = TradingResultsCommitter()
    except Exception as e:
        logger.warning(f"GitHub integration disabled: {e}")
        committer = None

    # ... your existing bot logic ...

    # After each signal generation:
    signal = engine.generate_signal(symbol)

    # Auto-commit signals >= 75% confidence
    if committer and signal.confidence >= 75:
        success = committer.record_signal(
            signal=signal.signal, symbol=symbol, confidence=signal.confidence
        )
        if success:
            logger.info(f"✅ Signal committed to GitHub: {signal.signal} {symbol}")

    # Periodically commit accumulated results (every 60 minutes)
    if committer and iteration % 720 == 0:  # 720 cycles at 5-sec interval = ~60 min
        committer.commit_results()


# ============================================================================
# OPTION B: Add to ai_engine.py
# ============================================================================

from github_integration import GitHubIntegration


class AIEngine:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.git = GitHubIntegration()  # Initialize GitHub integration
        # ... rest of your init ...

    def generate_signal(self, symbol: str) -> UnifiedSignal:
        # ... your existing signal generation logic ...
        signal = ...  # result from strategy

        # Auto-trigger GitHub workflow for high-confidence signals
        if signal.confidence >= 80:
            try:
                self.git.trigger_workflow(
                    event_type="trade-signal",
                    payload={
                        "signal": signal.signal,
                        "symbol": symbol,
                        "confidence": int(signal.confidence),
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to trigger workflow: {e}")

        return signal


# ============================================================================
# ENVIRONMENT VARIABLES REQUIRED
# ============================================================================

"""
Set these before running:

Windows PowerShell:
    $env:GITHUB_TOKEN = "ghp_YourTokenHere"
    $env:GITHUB_USER = "Alpha Trading Bot"
    $env:GITHUB_EMAIL = "alpha-bot@github.com"

Linux/Mac:
    export GITHUB_TOKEN="ghp_YourTokenHere"
    export GITHUB_USER="Alpha Trading Bot"
    export GITHUB_EMAIL="alpha-bot@github.com"

.env file (git-ignored):
    GITHUB_TOKEN=ghp_YourTokenHere
    GITHUB_USER=Alpha Trading Bot
    GITHUB_EMAIL=alpha-bot@github.com
"""


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Test GitHub integration locally:
    from github_integration import TradingResultsCommitter

    committer = TradingResultsCommitter()

    # Test signal recording
    success = committer.record_signal(signal="BUY", symbol="EURUSD", confidence=82.5)

    if success:
        print("✅ GitHub integration working!")
        print("Check your GitHub repo: results/signals/")
    else:
        print("❌ GitHub integration has issues (check GITHUB_TOKEN)")
