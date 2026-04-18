# DOCUMENTATION-WORKFLOW.md – Documentation Rules

Rules for creating, updating, and maintaining documentation in Alpha AI.

---

## When Documentation is Required

Use the `should_document()` MCP tool to determine:

```python
should_document({
    "change_type": "feature",        # feature, bugfix, refactor, architecture, config
    "complexity": "complex",         # simple, medium, complex
    "description": "Add Twitter sentiment as signal source"
})

# Returns: { "needs_documentation": true, "level": "user-facing" }
```

### Quick Decision Tree

```
Is it a feature or architectural change?
├─ YES → Documentation required
│  ├─ Is it user-facing (CLI, config, API)?
│  │  ├─ YES → User guide required
│  │  └─ NO → Developer guide required
│  └─ Is it complex or non-obvious?
│     ├─ YES → Detailed guide required
│     └─ NO → README update sufficient
│
└─ NO (bugfix, refactor, config)
   ├─ Is it breaking?
   │  ├─ YES → Migration guide required
   │  └─ NO → Only code comments needed
   │
   └─ Is it security-related?
      ├─ YES → Security notice required
      └─ NO → Changelog entry sufficient
```

---

## Documentation Hierarchy

### Level 1: Code Comments (Minimal)
**When**: Simple bugfixes, refactoring  
**Location**: `.py` file docstrings  
**Example**:

```python
def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index.
    
    Args:
        df: OHLCV DataFrame with 'close' column
        period: RSI lookback period (default: 14)
    
    Returns:
        Series with RSI values [0, 100]
    """
    # ... implementation ...
```

### Level 2: README Updates (Simple Changes)
**When**: Feature flags, configuration changes  
**Location**: `README.md`  
**Example**:

```markdown
### New Features
- Added Twitter sentiment as signal source
- Configure via `config.json` (optional)
```

### Level 3: User Guide (User-Facing Changes)
**When**: New CLI commands, config options  
**Location**: `./docs/GUIDE_*.md`  
**Files to Create**: One guide per major feature

```markdown
# Configuration Guide

## Available Parameters

- `symbol` — Trading pair (e.g., "EURUSD")
- `timeframe` — Candle period (e.g., "M5")
- `autotrade.enabled` — Enable live trading (default: false)
- `autotrade.dry_run` — Paper trading mode (default: true)
- `autotrade.min_confidence` — Min signal confidence (default: 0.70)
```

### Level 4: Developer Guide (Complex Changes)
**When**: New modules, refactoring, architecture changes  
**Location**: `./docs/DEV_*.md`  
**Files to Create**: One guide per module

```markdown
# Signal Generation Architecture

## Overview

The signal pipeline combines technical analysis, LSTM prediction, 
and multi-timeframe fusion to generate trading signals with 
confidence scores [33, 85].

## Components

### 1. Data Fetching
- File: `mt5_fetcher.py`
- Fetches OHLCV data from MT5 or synthetic fallback

### 2. Indicator Calculation
- File: `indicators.py`
- Calculates RSI, MACD, Bollinger Bands, etc.

...
```

### Level 5: Architecture Decision Record (ADR)
**When**: Major architectural decisions  
**Location**: `./docs/ADR_*.md`  
**Format**:

```markdown
# ADR-001: Signal Confidence Clamping

## Decision

All signal confidence values must be clamped to [33, 85] range.

## Rationale

- [33, 85] represents realistic trader confidence
- Prevents extreme overconfidence in predictions
- Ensures risk gates work effectively

## Consequences

- No signal can exceed 85 confidence
- Requires clamping after every confidence calculation
- Simplifies risk management logic
```

---

## Documentation File Naming

| Type | Naming Pattern | Example |
|---|---|---|
| **User Guide** | `GUIDE_*.md` | `GUIDE_configuration.md` |
| **Developer Guide** | `DEV_*.md` | `DEV_signal_generation.md` |
| **Architecture Decision** | `ADR_*.md` | `ADR_001_confidence_clamping.md` |
| **API Reference** | `API_*.md` | `API_endpoints.md` |
| **Deployment** | `DEPLOY_*.md` | `DEPLOY_kubernetes.md` |
| **Troubleshooting** | `TROUBLESHOOT_*.md` | `TROUBLESHOOT_mt5_connection.md` |

---

## Check Before Creating Documentation

```python
# Always call this first to avoid duplicates
check_existing_documentation({
    "title": "Signal Generation Guide",
    "context": "backend",
    "keywords": ["signal", "generation", "pipeline"],
    "topics": ["LSTM", "indicators", "confidence"]
})

# Returns existing docs that cover this topic
# If found, update existing instead of creating new
```

### Example Workflow

```python
# 1. Check for existing docs
existing = check_existing_documentation({
    "title": "Sentiment Analysis",
    "context": "backend"
})

# 2a. If docs exist, update them
if existing:
    manage_documentation({
        "action": "update",
        "file": "./docs/DEV_sentiment_analysis.md",
        "section": "## Available Sentiment Sources",
        "new_content": "- News (ForexFactory + NewsAPI)\n- Twitter (real-time sentiment)"
    })

# 2b. If no docs exist, create new
else:
    manage_documentation({
        "action": "create",
        "title": "Sentiment Analysis Integration",
        "context": "backend",
        "content": "...\n..."
    })

# 3. Register the feature
register_feature({
    "name": "sentiment_analysis",
    "context": "backend",
    "documentation": "./docs/DEV_sentiment_analysis.md"
})
```

---

## Content Guidelines

### DOs

✅ **Be specific**: Include code examples, not just descriptions  
✅ **Include why**: Explain rationale behind decisions  
✅ **Link between docs**: Cross-reference related topics  
✅ **Update examples**: Keep code samples current with repo  
✅ **Add diagrams**: Use ASCII art or Mermaid for flow visualization  
✅ **Version your docs**: Note which version of code each doc covers  
✅ **Include setup steps**: Walk through installation for new features

### DON'Ts

❌ **Avoid generic templates**: Make it specific to this project  
❌ **Don't duplicate info**: Link to existing docs instead  
❌ **Avoid time-sensitive info**: Use "old patterns" section for deprecated features  
❌ **Don't explain basics**: Assume reader knows Python/trading  
❌ **Avoid excessive detail**: Keep guides < 1000 words each  

---

## Markdown Template: User Guide

```markdown
# [Feature Name] Guide

## Overview

[One-paragraph explanation of feature and why it exists]

## Quick Start

[Copy-paste steps to get running in 5 minutes]

```bash
# Step 1: Install
pip install -r requirements.txt

# Step 2: Configure
# Edit config.json - set [feature-specific-param] = [value]

# Step 3: Run
python main.py --[feature-flag]
```

## Configuration

| Parameter | Type | Default | Description |
|---|---|---|---|
| `param1` | string | "value" | What it does |
| `param2` | float | 0.75 | What it does |

## Examples

### Example 1: Basic Usage
[Code block with explanation]

### Example 2: Advanced Usage
[Code block with explanation]

## Troubleshooting

### Issue: X doesn't work
**Solution**: [Steps to fix]

### Issue: Y is slow
**Solution**: [Steps to fix]

## See Also
- [Related Guide](./GUIDE_related.md)
- [API Reference](./API_endpoints.md)
```

---

## Markdown Template: Developer Guide

```markdown
# [Module] Architecture

## Overview

[Brief explanation of module's purpose in the system]

## Architecture Diagram

```
Input
  ↓
[Process 1]
  ↓
[Process 2]
  ↓
Output
```

## Key Components

### Component 1: [Name]
- **File**: `./path/to/file.py`
- **Purpose**: [What it does]
- **Key Functions**: `func1()`, `func2()`
- **Dependencies**: [Other modules it uses]

### Component 2: [Name]
- **File**: `./path/to/file.py`
- **Purpose**: [What it does]
- **Key Functions**: `func1()`, `func2()`
- **Dependencies**: [Other modules it uses]

## Contracts

All code in this module must satisfy:
- [Contract 1]: [Description]
- [Contract 2]: [Description]

See [CONTRACT-REFERENCE.md](./CONTRACT-REFERENCE.md) for details.

## Patterns Used

- [Pattern name]: See [PATTERNS-REFERENCE.md](./PATTERNS-REFERENCE.md)

## Example Usage

```python
from signal_generator import generate_signal

signal = generate_signal(df)
print(f"{signal.signal} @ {signal.confidence}%")
```

## Testing

Tests for this module: `tests/test_*.py`

```bash
# Run all tests for this module
python -m pytest tests/test_signal_generator.py -v

# Run specific test
python -m pytest tests/test_signal_generator.py::test_confidence_bounds -v
```

## Performance Considerations

- [Performance note 1]
- [Performance note 2]

## Future Improvements

- [ ] Improvement 1
- [ ] Improvement 2

## References

- [External link](https://example.com)
- [Related ADR](./ADR_001.md)
```

---

## Markdown Template: Architecture Decision Record (ADR)

```markdown
# ADR-NNN: [Title]

**Status**: Proposed | Accepted | Deprecated | Superseded  
**Proposed**: [Date]  
**Accepted**: [Date]  
**Deprecated**: [Date]  

## Decision

[Statement of the decision made]

## Rationale

[Explanation of why this decision was made]

[List pros and cons if complex]

### Pros
- [Benefit 1]
- [Benefit 2]

### Cons
- [Drawback 1]
- [Drawback 2]

## Consequences

[What this decision means for the codebase going forward]

[Positive and negative consequences]

## Alternatives Considered

### Alternative 1: [Name]
- Pros: [...]
- Cons: [...]
- Why rejected: [...]

### Alternative 2: [Name]
- Pros: [...]
- Cons: [...]
- Why rejected: [...]

## Related ADRs

- [ADR-001: Some other decision](./ADR_001.md)

## Implementation Notes

- [Implementation detail 1]
- [Implementation detail 2]

## References

- [Link](https://example.com)
```

---

## Documentation Synchronization

Docs should be kept in sync with code. Use:

```python
sync_documentation_files({
    "project_id": "alpha_data_scraper_ai",
    "scan_path": "./docs",
    "auto_register": True  # Automatically register found docs
})

# This:
# 1. Scans ./docs/ for .md files
# 2. Checks against registered documentation
# 3. Registers any new docs found
# 4. Alerts if registered docs are missing
```

---

## Documentation Workflow Example

### Scenario: Adding New Signal Source

```python
# 1. Check for existing docs
existing = check_existing_documentation({
    "title": "Signal Sources",
    "context": "backend",
    "keywords": ["signal", "source", "sentiment"]
})
# Returns: ./docs/DEV_signal_sources.md exists

# 2. Update existing rather than create new
manage_documentation({
    "action": "update",
    "file": "./docs/DEV_signal_sources.md",
    "section": "## Available Signal Sources",
    "append": """
### New: Twitter Sentiment
- File: `./sentiment/twitter_analyzer.py`
- Returns: Sentiment score [0.0, 1.0]
- Fallback: Neutral (0.5) if API fails
"""
})

# 3. Update user guide
manage_documentation({
    "action": "update",
    "file": "./docs/GUIDE_configuration.md",
    "section": "## Signal Sources Configuration",
    "append": """
### Twitter Sentiment

Enable Twitter sentiment in `config.json`:

```json
{
  "signal_sources": {
    "twitter_sentiment": {
      "enabled": true,
      "weight": 0.2
    }
  }
}
```
"""
})

# 4. Register the feature
register_feature({
    "name": "twitter_sentiment",
    "context": "backend",
    "description": "Real-time Twitter sentiment scoring",
    "documentation": "./docs/DEV_signal_sources.md",
    "user_guide": "./docs/GUIDE_configuration.md"
})

# 5. Sync documentation registry
sync_documentation_files({
    "project_id": "alpha_data_scraper_ai",
    "auto_register": True
})
```

---

## Common Documentation Tasks

### Task: Document a New Module

```python
# 1. Create developer guide
manage_documentation({
    "action": "create",
    "title": f"[Module Name] Architecture",
    "context": "backend",
    "path": f"./docs/DEV_{module_name}.md",
    "template": "developer-guide",
    "module_name": "signal_generator",
    "file_path": "./signal_generator.py"
})

# 2. Add to navigation (if exists)
manage_documentation({
    "action": "update",
    "file": "./docs/README.md",
    "section": "## Developer Guides",
    "append": f"- [{module_name}](./DEV_{module_name}.md)"
})
```

### Task: Create an ADR

```python
manage_documentation({
    "action": "create",
    "title": "Confidence Clamping Strategy",
    "context": "backend",
    "path": "./docs/ADR_001_confidence_clamping.md",
    "template": "adr",
    "status": "Proposed",
    "summary": "All signal confidence values must be clamped to [33, 85]"
})
```

### Task: Update Examples in Existing Doc

```python
manage_documentation({
    "action": "update",
    "file": "./docs/GUIDE_configuration.md",
    "section": "## Examples",
    "subsection": "### Example 1: Basic Setup",
    "new_content": """
# ... updated example code ...
"""
})
```

---

## Documentation Quality Checklist

Before considering docs complete:

- [ ] Clear title and description
- [ ] Target audience identified (user/developer)
- [ ] Examples provided with explanations
- [ ] Links to related docs
- [ ] Links to relevant code files
- [ ] No time-sensitive information
- [ ] Consistent with existing docs
- [ ] Registered via `register_feature()` or `manage_documentation()`
- [ ] Passes markdown linting (if available)
- [ ] Matches project terminology and conventions

---

## Documentation Tools

### Linting Markdown

```bash
# If markdownlint installed
markdownlint-cli2 ./docs/**/*.md

# Check for dead links
# If markdown-link-check installed
markdown-link-check ./docs/**/*.md
```

### Generating Table of Contents

```bash
# Add to top of doc (if using mdtoc)
mdtoc ./docs/GUIDE_configuration.md

# Output:
# [Setup](#setup)
# [Configuration](#configuration)
# ...
```

---

**Remember**: Documentation is code. Keep it current, organized, and linked. Outdated docs are worse than no docs.
