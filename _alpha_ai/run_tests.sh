#!/usr/bin/env bash
set -euo pipefail

pytest -q --cov=. --cov-report=term-missing
