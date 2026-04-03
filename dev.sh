#!/usr/bin/env bash
set -e

echo ">>> Formatowanie (black)"
python -m black .

echo ">>> Linting (flake8)"
python -m flake8 .

echo ">>> Typowanie (mypy)"
python -m mypy .

echo ">>> Testy jednostkowe"
python -m pytest -v

echo ">>> Coverage"
python -m pytest --cov=. --cov-report=term-missing -v

echo ">>> Wszystko OK"