# Claude + GitHub Integration Guide

Complete setup for linking Claude with your trading bot for auto-committing, pushing, and triggering GitHub Actions.

---

## ⚡ Quick Start

### 1️⃣ Create GitHub Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Give it a name: `alpha-trading-bot`
4. Scopes needed:
   - ✅ `repo` (full control of private repositories)
   - ✅ `workflow` (update GitHub Actions workflows)
5. Copy the token (you'll only see it once)

### 2️⃣ Add Secrets to GitHub

In your repository settings:

1. Go to **Settings → Secrets and variables → Actions**
2. Add these **Repository Secrets**:

| Secret | Value | Source |
|--------|-------|--------|
| `GITHUB_TOKEN` | Your token from step 1 | Generate new token |
| `CLAUDE_API_KEY` | Your Anthropic API key | https://console.anthropic.com |
| `NEWSAPI_KEY` | Your NewsAPI key | https://newsapi.org |
| `MT5_LOGIN` | Your MT5 account login | MetaTrader5 |
| `MT5_PASSWORD` | Your MT5 password | MetaTrader5 |
| `MT5_SERVER` | Your broker server | MetaTrader5 |

### 3️⃣ Set Local Environment Variables

```powershell
# In PowerShell (Windows):
$env:GITHUB_TOKEN = "ghp_YourTokenHere"
$env:CLAUDE_API_KEY = "sk-ant-..."
$env:NEWSAPI_KEY = "your_key"
$env:GITHUB_USER = "Alpha Trading Bot"
$env:GITHUB_EMAIL = "alpha-bot@github.com"

# Or create .env file (git-ignored):
# GITHUB_TOKEN=ghp_...
# CLAUDE_API_KEY=sk-ant-...
```

---

## 🚀 Three Integration Methods

### **Method 1: GitHub Actions Auto-Commit (Scheduled)**

**What it does:** Runs your trading bot every hour, auto-commits results

**File:** `.github/workflows/auto-commit-results.yml` ✅ *Already created*

**How it works:**
- Runs on schedule: `0 9-16 * * 1-5` (trading hours, weekdays)
- Or manually via **Actions → Auto-Commit Trading Results → Run workflow**
- Commits to `results/` and `logs/` directories

**No code changes needed** — workflow handles everything!

---

### **Method 2: High-Confidence Signal Alerts (Triggered)**

**What it does:** When confidence ≥ 80%, auto-commits signal + creates GitHub Issue

**File:** `.github/workflows/trade-signal-commit.yml` ✅ *Already created*

**Trigger from Python:**

```python
# In main.py or ai_engine.py
from github_integration import GitHubIntegration

git = GitHubIntegration()

# Dispatch workflow when signal confidence is high
if signal.confidence >= 80:
    git.trigger_workflow(
        event_type="trade-signal",
        payload={
            "signal": signal.signal,
            "symbol": "EURUSD",
            "confidence": int(signal.confidence)
        }
    )
```

---

### **Method 3: Real-Time Commits from App (Active)**

**What it does:** App commits signals immediately after generation

**Installation:**

```python
# At end of ai_engine.py or main.py:
from github_integration import TradingResultsCommitter

committer = TradingResultsCommitter()

# After generating a signal:
signal = engine.generate_signal("EURUSD")
if signal.confidence >= 70:
    committer.record_signal(
        signal=signal.signal,
        symbol="EURUSD",
        confidence=signal.confidence
    )
```

---

## 📝 Integration Examples

### Add to `main.py`:

```python
from github_integration import TradingResultsCommitter

# After imports
committer = TradingResultsCommitter()

# In your main trading loop:
def main():
    # ... your existing code ...
    
    signal = engine.generate_signal(symbol)
    
    # Auto-commit high-confidence signals
    if signal.confidence >= 70:
        committer.record_signal(
            signal=signal.signal,
            symbol=symbol,
            confidence=signal.confidence
        )
    
    # Periodically commit results
    if iteration % 10 == 0:  # Every 10 cycles
        committer.commit_results()
```

### Add to `ai_engine.py`:

```python
from github_integration import GitHubIntegration

class AIEngine:
    def __init__(self, config):
        self.git = GitHubIntegration()
        # ... rest of init ...
    
    def generate_signal(self, symbol: str) -> UnifiedSignal:
        signal = ... # your existing logic
        
        # Auto-trigger workflow for high-confidence signals
        if signal.confidence >= 80:
            self.git.trigger_workflow(
                "trade-signal",
                {
                    "signal": signal.signal,
                    "symbol": symbol,
                    "confidence": int(signal.confidence)
                }
            )
        return signal
```

---

## 🎮 Using Copilot for Git Workflow

### In VS Code:

**GitLens Commit Composer** — Organize commits with AI:
```
Ctrl+Shift+P → "GitLens: Open Commit Composer"
```
- Organize changes into coherent commits
- Generate commit messages with Copilot suggestions

**Copilot Chat for Git:**
```
Ctrl+I → Ask Copilot:
  "Help me write a commit message for trading signal changes"
  "Generate a meaningful git log summary"
  "What were the recent changes to signal_generator.py?"
```

**GitLens Launchpad** — Manage PRs:
```
Ctrl+Shift+P → "GitLens: Open Launchpad"
```
- Prioritizes PRs by status (ready, conflicts, reviews pending)

**Start Review:**
```
Ctrl+Shift+P → "GitLens: Start Review"
```
- Creates a separate worktree for reviewing PRs with AI assistance

---

## 🔄 Workflow: Complete Example

### Scenario: High-confidence BUY signal on EURUSD

**Step 1: App generates signal**
```
✅ Signal confidence: 82% (BUY EURUSD)
```

**Step 2: Real-time commit (Method 3)**
```powershell
$ committer.record_signal("BUY", "EURUSD", 82)
✅ Signal recorded: results/signals/EURUSD_20260409_123456.json
✅ Committed: a1b2c3d - 🚀 Signal: BUY EURUSD (confidence: 82%)
✅ Pushed to origin/main
```

**Step 3: Workflow triggered (Method 2)**
```
📤 Dispatching trade-signal workflow...
✅ Workflow dispatched: trade-signal
```

**Step 4: GitHub Actions runs**
```
🤖 GitHub Actions processes:
  ├── Record signal data
  ├── Commit to main
  ├── Create GitHub Issue for high-confidence signal
  └── ✅ Complete
```

**Step 5: GitHub Issue created**
```
Title: 🚀 HIGH CONFIDENCE BUY Signal: EURUSD (82%)
Status: Open
Labels: [auto-signal, high-confidence, buy]
```

**Step 6: Copilot in VS Code**
```
User: "Summarize recent trades"
Copilot: (reads recent commits + signals)
  "Recent trading activity:
   - BUY EURUSD @ 82% confidence
   - HOLD GBPUSD @ 65% confidence
   - [2 more signals]..."
```

---

## 🛡️ Best Practices

### ✅ DO:
- `GITHUB_TOKEN` with only `repo` + `workflow` scopes
- Commit to separate `results/` directory (not main code)
- Use dry-run for auto-trades until tested
- Require approval for live trading in GitHub Actions
- Monitor workflow runs in **Actions** tab

### ❌ DON'T:
- Commit API keys or secrets (use GitHub Secrets)
- Push directly to main without PR reviews
- Enable live trading in workflows without heavy gates
- Leave old workflow runs without cleanup

---

## 🔧 Troubleshooting

### "GITHUB_TOKEN not found in environment"
```powershell
# Check:
$env:GITHUB_TOKEN

# If empty, set it:
$env:GITHUB_TOKEN = "ghp_YourTokenHere"
```

### Workflow not triggering
1. Check token has `workflow` scope
2. Verify `.github/workflows/*.yml` syntax (check "Actions" tab)
3. Ensure secrets are added to repo settings
4. Run workflow manually: **Actions → [Workflow] → Run workflow**

### Commits not pushing
1. Verify git user is configured: `git config user.name`
2. Check branch exists: `git branch -a`
3. Check push permissions: GitHub token scope

### No results to commit
- Ensure `results/` directory exists
- Check `main.py` is creating output files
- Run `python main.py` locally first to verify

---

## 📊 File Structure

After setup, your repo structure will have:

```
.github/workflows/
├── auto-commit-results.yml      ✅ Scheduled commits (created)
├── trade-signal-commit.yml      ✅ Signal triggers (created)
├── deploy-k8s.yml              (existing)
├── docker.yml                  (existing)
└── pytest.yml                  (existing)

results/                         (auto-created by workflows)
├── trading_metrics.json
└── signals/
    └── EURUSD_20260409_123456.json

logs/                            (auto-created by workflows)
└── trading_20260409_090000.log

github_integration.py            ✅ New Python module (created)
```

---

## ✨ Next Steps

1. **Set GitHub token** (Step 1-2 above)
2. **Test locally**: 
   ```powershell
   python -c "from github_integration import GitHubIntegration; g = GitHubIntegration(); print('✅ Module loaded')"
   ```
3. **Add to main.py** (see examples above)
4. **Push to GitHub**: 
   ```powershell
   git add .github/ github_integration.py
   git commit -m "🔗 Add GitHub integration"
   git push origin main
   ```
5. **Manually run workflow**: Actions → Auto-Commit Results → Run workflow
6. **Monitor**: Actions tab shows all runs and logs

---

**Questions?** Check GitHub Actions docs: https://docs.github.com/en/actions
