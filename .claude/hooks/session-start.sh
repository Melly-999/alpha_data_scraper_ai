#!/bin/bash
# Session-start hook for Claude Code on the web.
# Installs CI dependencies so tests and linters work immediately.

set -euo pipefail

# Only run in remote (Claude Code on the web) environments.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "==> Installing CI dependencies..."

# ta 0.11.0 uses a legacy setup.py attribute (install_layout) that was
# removed in setuptools >=66. Pin setuptools first so ta builds correctly,
# then restore a modern version after ta is installed.
pip install --quiet "setuptools==65.5.0"
pip install --quiet ta

# Upgrade setuptools back to a recent release before installing everything else.
pip install --quiet --upgrade setuptools

# Install the full CI dependency set (ta is already installed; pip skips it).
pip install --quiet -r requirements-ci.txt

echo "==> Dependencies installed."

# Set PYTHONPATH so tests can import project modules without installation.
echo 'export PYTHONPATH="$CLAUDE_PROJECT_DIR"' >> "$CLAUDE_ENV_FILE"

echo "==> PYTHONPATH set to project root."
