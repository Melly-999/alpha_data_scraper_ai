#!/bin/bash
# SessionStart hook — installs all Python dependencies needed for tests and
# linters in a Claude Code on the web session. Safe to run multiple times.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# ── Python deps ─────────────────────────────────────────────────────────────
# Core CI deps: pytest, black, flake8, mypy, numpy, pandas, scikit-learn
pip install --quiet --disable-pip-version-check \
  -r "$REPO_ROOT/requirements-ci.txt"

# MellyTrade backend + adapter deps (FastAPI, SQLAlchemy, httpx, pydantic…)
pip install --quiet --disable-pip-version-check \
  -r "$REPO_ROOT/mellytrade_v3/mellytrade-api/requirements.txt"

# ── PYTHONPATH ───────────────────────────────────────────────────────────────
# Root: so `import lstm_model`, `import signal_generator` etc. work.
# mellytrade_v3: so `from mt5 import ...` works when running mt5/tests.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PYTHONPATH=\"$REPO_ROOT:$REPO_ROOT/mellytrade_v3\${PYTHONPATH:+:\$PYTHONPATH}\"" \
    >> "$CLAUDE_ENV_FILE"
fi

echo "session-start: dependencies installed"
