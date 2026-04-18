# SESSION-WORKFLOW.md – MCP Integration Guide

Detailed workflows for using AI Project Context MCP tools with this project. Read this when starting a new work session.

---

## Pre-Session Checklist (2 minutes)

Before opening an IDE or editor:

```bash
# Verify you're in the right directory
pwd  # Should output project root

# Check git status
git status

# Load this into your context
cat .ai-agents/QUICK-REFERENCE.md  # < 500 tokens, memorize key rules
```

---

## Workflow 1: Standard Work Session

### Step 1: Identify Context
Establish where you are in the codebase:

```python
# Via MCP tool
identify_context({ 
    file_path: "./ai_engine.py"  # MUST use relative path!
})

# Returns:
# {
#   "project": "alpha_data_scraper_ai",
#   "context": "backend",
#   "module": "AI orchestration",
#   "dependencies": ["claude_ai.py", "signal_generator.py", "multi_timeframe.py"]
# }
```

**Why**: Helps MCP understand which files are related and which guidelines apply.

### Step 2: Start or Resume Session

If there's no active session:

```python
start_session({
    "context": "backend",
    "current_focus": "signal generation",
    "goal": "Implement unified signal with confidence clamping [33-85]",
    "dependencies": ["signal_generator.py", "multi_timeframe.py", "claude_ai.py"]
})
```

If resuming an interrupted session:

```python
focus = get_current_focus()
print(focus)  # Shows active session, progress, and next steps

# If session is stale, refresh:
refresh_session_context()
```

### Step 3: Load Project Guidelines

Get merged guidelines (global + project-specific):

```python
guidelines = get_merged_guidelines({
    "context": "backend"
})

# Returns rules for:
# - Code style (black, flake8, mypy)
# - Testing (pytest with fixtures)
# - Logging (core/logger.py)
# - Safety rules (never enable autotrade, keep dry_run: true)
# - Patterns (dataclasses, type hints, graceful degradation)
```

### Step 4: Do Your Work

Now you have full context. Work on your task:

```python
# Edit files
# Run tests: python -m pytest tests/test_signal_generator.py -v
# Format: python -m black .
# Type check: python -m mypy .
```

### Step 5: Create Checkpoint (Important!)

When you finish a milestone or change direction, save progress:

```python
create_checkpoint({
    "summary": "Implemented SignalResult dataclass with confidence clamping [33-85]",
    "completed_files": ["./signal_generator.py"],
    "next_focus": "Multi-timeframe fusion logic",
    "blockers": None,
    "context_preserved": True
})
```

**Why**: If you get interrupted, you can resume exactly where you left off.

### Step 6: Complete Session

When done:

```python
complete_session({
    "final_summary": "Added unified signal aggregation with Claude validation",
    "tests_passing": True,
    "code_formatted": True,
    "type_check_passed": True,
    "ready_for_pr": True
})
```

---

## Workflow 2: Multi-Turn Development (Long Horizon)

For complex features spanning multiple coding sessions:

### Initial Session
```python
start_session({
    "context": "backend",
    "current_focus": "risk management refactor",
    "goal": "Split RiskManager into RiskGates + PositionCalculator",
    "duration_estimate": "3 sessions",
    "milestone": 1
})

# Work on Milestone 1...
create_checkpoint({
    "milestone": 1,
    "summary": "Extracted RiskGates class from RiskManager",
    "next_milestone": "Implement PositionCalculator"
})
```

### Resumed Session
```python
focus = get_current_focus()  # Get previous checkpoint

# Refresh context
refresh_session_context()

# Continue on Milestone 2
update_focus({
    "milestone": 2,
    "current_focus": "position calculator implementation"
})

# Work...
create_checkpoint({
    "milestone": 2,
    "summary": "Implemented PositionCalculator with kelly criterion",
    "next_milestone": "Integration tests"
})
```

### Final Session
```python
# Complete final milestone
# ... work ...
# All tests pass

complete_session({
    "final_summary": "Risk management refactored into modular components",
    "milestones_completed": 3,
    "tests_added": 12,
    "ready_for_pr": True
})
```

---

## Workflow 3: Bug Fix (Short Horizon)

For quick fixes:

```python
# 1. Identify
identify_context({ file_path: "./mt5_fetcher.py" })

# 2. Start (short session)
start_session({
    "context": "backend",
    "current_focus": "fix MT5 connection timeout",
    "goal": "Add retry logic with exponential backoff",
    "duration_estimate": "30 minutes"
})

# 3. Load guidelines
get_merged_guidelines({ context: "backend" })

# 4. Fix the bug
# - Edit mt5_fetcher.py
# - Add retry logic
# - Add logging
# - Test: python -m pytest tests/test_mt5_fetcher.py -v
# - Format: python -m black .
# - Type check: python -m mypy mt5_fetcher.py

# 5. Checkpoint (optional for quick fixes)
create_checkpoint({
    "summary": "Fixed MT5 timeout with exponential backoff (max 3 retries)"
})

# 6. Complete
complete_session({
    "final_summary": "MT5 timeout handling improved",
    "tests_passing": True,
    "ready_for_pr": True
})
```

---

## Workflow 4: Adding a New Feature (Signal Source)

Example: Adding a new sentiment data source to the pipeline.

### Phase 1: Planning
```python
start_session({
    "context": "backend",
    "current_focus": "sentiment analysis enhancement",
    "goal": "Add Twitter sentiment as new signal source",
    "tasks": [
        "Create TwitterSentimentAnalyzer class",
        "Integrate into MultiTimeframeAnalyzer",
        "Add tests",
        "Update documentation"
    ],
    "milestone": 1,
    "duration_estimate": "2 sessions"
})

# Check existing patterns
contracts = get_contracts()
print(contracts)  # See SentimentAnalyzer interface

patterns = learn_pattern({
    "name": "sentiment_analyzer",
    "context": "backend"
})
print(patterns)  # See how news_sentiment.py is structured
```

### Phase 2: Implementation
```python
# Create new file: ./sentiment/twitter_analyzer.py
# Follow existing pattern from news_sentiment.py

# Key requirements:
# - Implement get_sentiment(symbol: str) -> float
# - Return value in [0.0, 1.0] range
# - Add logging via core/logger.py
# - Use @dataclass for return types
# - Include fallback if Twitter API fails

create_checkpoint({
    "milestone": 1,
    "summary": "Created TwitterSentimentAnalyzer with fallback"
})
```

### Phase 3: Integration
```python
# Edit multi_timeframe.py to include twitter sentiment

# Test integration
# python -m pytest tests/test_multi_timeframe.py -v

# Type check
# python -m mypy ./sentiment/twitter_analyzer.py ./multi_timeframe.py

# Format
# python -m black .

create_checkpoint({
    "milestone": 2,
    "summary": "Integrated TwitterSentimentAnalyzer into pipeline",
    "next_focus": "documentation and final testing"
})
```

### Phase 4: Documentation & Testing
```python
# Add feature to project context
register_feature({
    "name": "twitter_sentiment_analysis",
    "context": "backend",
    "description": "Real-time Twitter sentiment scoring for signal validation",
    "files": ["./sentiment/twitter_analyzer.py", "./multi_timeframe.py"],
    "tests": ["tests/test_twitter_analyzer.py"],
    "use_case": "Reduce false BUY signals during negative sentiment"
})

# Update documentation
check_existing_documentation({
    "title": "Sentiment Analysis Integration",
    "context": "backend"
})

# If no docs exist, create them
manage_documentation({
    "action": "create",
    "title": "Sentiment Analysis: News + Twitter Integration",
    "context": "backend",
    "content": "..."
})

complete_session({
    "final_summary": "Added Twitter sentiment as signal source with full integration",
    "tests_added": 5,
    "documentation_updated": True,
    "ready_for_pr": True
})
```

---

## Workflow 5: Debugging Issues

When things break:

### Identify the Problem
```python
identify_context({ file_path: "./ai_engine.py" })

start_session({
    "context": "backend",
    "current_focus": "debugging signal aggregation",
    "goal": "Fix confidence values exceeding [33-85] bounds",
    "issue": "Issue #42: Confidence = 127"
})
```

### Gather Evidence
```python
# 1. Look at error logs
log_file = "./alpha_ai.log"  # Check recent entries

# 2. Run failing test in isolation
# python -m pytest tests/test_signal_generator.py::test_confidence_bounds -vv

# 3. Check current contracts
validate_contract({
    "contract": "SignalResult.confidence",
    "rule": "Must be in [33, 85]",
    "file": "./signal_generator.py"
})

# 4. Create minimal reproduction
# python -c "from signal_generator import generate_signal; ..."
```

### Fix & Verify
```python
# Edit the problematic file
# ... fix ...

# Test
# python -m pytest tests/test_signal_generator.py::test_confidence_bounds -vv

# Confirm it passes
# python -m mypy signal_generator.py
# python -m black signal_generator.py

create_checkpoint({
    "summary": "Fixed confidence clamping bug in SignalResult aggregation"
})

complete_session({
    "final_summary": "Resolved Issue #42: confidence bounds now enforced",
    "issue_closed": "42",
    "ready_for_pr": True
})
```

---

## Workflow 6: Code Review & Feedback Integration

When receiving review comments:

```python
start_session({
    "context": "backend",
    "current_focus": "address PR #15 review comments",
    "goal": "Fix linting, add type hints, improve docstrings"
})

# Load review comments
# (Simulated—from GitHub PR)
comments = [
    "Missing type hints on LSTMPipeline.predict()",
    "No logging in mt5_fetcher.py error handling",
    "Confidence calculation not clamped in signal_generator.py"
]

# Fix each comment
# 1. Add type hints to LSTMPipeline
# 2. Add logging to mt5_fetcher error paths
# 3. Verify confidence clamping (add test if missing)

# Test all fixes
# python -m pytest tests/ -v
# python -m mypy .
# python -m black .
# python -m flake8 .

create_checkpoint({
    "summary": "Addressed all PR #15 review comments"
})

complete_session({
    "final_summary": "PR #15 ready for re-review",
    "ready_for_pr": True
})
```

---

## Configuration Workflow: Changing Settings

When modifying trading parameters:

```python
start_session({
    "context": "backend",
    "current_focus": "adjust trading risk parameters",
    "goal": "Change min_confidence from 0.70 to 0.75"
})

# Load config validation rules
contracts = get_contracts()
# Look for "EngineConfig" contract

# Edit config.json
# {
#   "symbol": "EURUSD",
#   "autotrade": {
#     "enabled": false,           # ← DO NOT CHANGE
#     "dry_run": true,            # ← DO NOT CHANGE
#     "min_confidence": 0.75       # ← Changed from 0.70
#   }
# }

# Validate
# python -c "import json; cfg = json.load(open('config.json')); print(cfg['autotrade']['min_confidence'])"

# Test with new config
# python main.py --dry-run  # Verify it works

# Document the change
create_checkpoint({
    "summary": "Changed min_confidence threshold to 0.75 for stricter signal filtering"
})

complete_session({
    "final_summary": "Configuration updated and tested"
})
```

---

## Multi-File Editing Workflow

When changes span multiple files:

```python
start_session({
    "context": "backend",
    "current_focus": "refactor signal validation",
    "goal": "Move signal clamping logic to centralized validator",
    "files_affected": [
        "./signal_generator.py",
        "./multi_timeframe.py",
        "./claude_ai.py",
        "./tests/test_signal_generator.py"
    ]
})

# 1. Create the validator module
# ./signal_validator.py
# - validate_signal_result()
# - clamp_confidence()
# - validate_regime()

# 2. Update signal_generator.py to use validator
# 3. Update multi_timeframe.py to use validator
# 4. Update claude_ai.py to use validator
# 5. Add tests for new validator

# 6. Run full test suite
# python -m pytest tests/ -v

# 7. Format & type check
# python -m black .
# python -m mypy .

create_checkpoint({
    "summary": "Centralized signal validation logic",
    "files_changed": 4,
    "tests_added": 3
})

complete_session({
    "final_summary": "Signal validation refactored to DRY principle",
    "ready_for_pr": True
})
```

---

## Testing Workflow: TDD

Test-Driven Development approach:

```python
start_session({
    "context": "backend",
    "current_focus": "implement new indicator",
    "goal": "Add Volume-Weighted Moving Average (VWAP)",
    "tdd": True  # Test-first approach
})

# 1. Write failing test first
# tests/test_vwap_indicator.py:
#   def test_vwap_calculation():
#       vwap = calculate_vwap(sample_ohlcv)
#       assert vwap > 0
#       assert len(vwap) == len(sample_ohlcv)

# 2. Run test (it fails)
# python -m pytest tests/test_vwap_indicator.py -v  # RED

# 3. Implement minimal code to make it pass
# ./indicators.py:
#   def calculate_vwap(df: pd.DataFrame) -> np.ndarray:
#       ...

# 4. Run test again (it passes)
# python -m pytest tests/test_vwap_indicator.py -v  # GREEN

# 5. Refactor with confidence
# Improve implementation, add edge cases, add logging

# 6. Verify all tests still pass
# python -m pytest tests/ -v  # REFACTOR → Still GREEN

create_checkpoint({
    "summary": "Implemented VWAP indicator with TDD approach"
})

complete_session({
    "final_summary": "VWAP indicator complete with 100% test coverage",
    "test_coverage": "100%",
    "ready_for_pr": True
})
```

---

## Crisis Mode: Quick Emergency Fix

For production issues that need immediate attention:

```python
# SKIP CEREMONY - EMERGENCY MODE
start_session({
    "context": "backend",
    "current_focus": "emergency fix: MT5 disconnection",
    "goal": "Restore service within 5 minutes",
    "emergency": True
})

# 1. Identify root cause (2 min)
identify_context({ file_path: "./mt5_fetcher.py" })

# 2. Quick fix (2 min)
# Edit mt5_fetcher.py - add connection retry

# 3. Test (1 min)
# python -m pytest tests/test_mt5_fetcher.py -v

# 4. Deploy
# docker-compose up -d app

# 5. Document for later review
create_checkpoint({
    "summary": "EMERGENCY: Added MT5 reconnection logic",
    "needs_review": True,
    "cleanup_tasks": [
        "Add comprehensive error handling tests",
        "Refactor connection management",
        "Add monitoring alerts"
    ]
})

complete_session({
    "final_summary": "Service restored. Follow-up review scheduled."
})
```

---

## Tips for Efficient MCP Workflow

1. **Save Checkpoints Regularly**: Every 15-30 min of work
2. **Use Relative Paths Always**: `./src/file.py` not `/Users/...`
3. **Refresh Context Every 10 Turns**: `refresh_session_context()`
4. **Keep Focus Narrow**: One feature/fix per session
5. **Test Early, Test Often**: Run tests after each significant edit
6. **Format & Check Before Checkpoint**: `black .`, `flake8 .`, `mypy .`
7. **Document Changes**: Use checkpoints as commit message template

---

## Connecting to GitHub

When ready to submit:

```python
# All checkpoints should lead here
complete_session({
    "final_summary": "Feature complete and tested",
    "tests_passing": True,
    "code_formatted": True,
    "ready_for_pr": True
})

# Then create PR:
# git add .
# git commit -m "feat(signal): implement unified signal aggregation"
# git push origin branch-name
# (Create PR on GitHub)
```

---

**Remember**: Context is finite. Each MCP call should save a checkpoint or complete session to ensure continuity across conversation turns.
