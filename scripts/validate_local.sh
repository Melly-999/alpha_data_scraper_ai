#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

run_step() {
  local name="$1"
  shift

  echo
  echo "==> ${name}"
  if ! "$@"; then
    echo
    echo "VALIDATION FAILED: ${name}"
    exit 1
  fi
}

frontend_changed() {
  if ! git rev-parse --verify origin/main >/dev/null 2>&1; then
    echo "Warning: origin/main is unavailable; skipping frontend change detection and frontend build." >&2
    return 1
  fi

  local changed_files
  if ! changed_files="$(git diff --name-only origin/main...HEAD -- frontend)"; then
    echo "Warning: could not compare frontend changes against origin/main; skipping frontend build." >&2
    return 1
  fi

  [[ -n "${changed_files}" ]]
}

echo "MellyTrade local validation"
echo "Repo: ${REPO_ROOT}"

run_step "Safety configuration validation" python scripts/validate_safety_config.py
run_step "App pytest suite" python -m pytest tests/app/ -q

if frontend_changed; then
  run_step "Frontend build" bash -c 'cd frontend && npm run build'
else
  echo
  echo "Skipping frontend build: no frontend files changed."
fi

echo
echo "VALIDATION PASSED"
