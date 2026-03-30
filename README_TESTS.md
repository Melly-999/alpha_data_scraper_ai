# Testing Guide

This project uses `pytest` with optional markers for slow and MT5-related tests.

## 1) Install test dependencies

```bash
pip install -r requirements.txt
```

## 2) Run tests locally

- Fast/default suite (recommended for quick checks):
  - `pytest -m "not slow and not mt5"`
- Include slow tests:
  - `pytest --run-slow`
- Include MT5-marked tests (mocked MT5 module in tests):
  - `pytest --run-mt5`
- Run everything:
  - `pytest --run-slow --run-mt5`

## 3) Markers and flags

- Marker `slow`:
  - skipped unless `--run-slow` is passed
- Marker `mt5`:
  - skipped unless `--run-mt5` is passed

Configured in:

- `pytest.ini` (marker declarations)
- `tests/conftest.py` (runtime skip logic and CLI flags)

## 4) CI command matrix

Use this minimal matrix to balance runtime and coverage:

| CI Job | Command | Purpose |
|---|---|---|
| `tests-fast` | `pytest -m "not slow and not mt5"` | Fast feedback on core logic |
| `tests-slow` | `pytest --run-slow -m "slow and not mt5"` | Extended computations/performance-oriented checks |
| `tests-mt5` | `pytest --run-mt5 -m "mt5 and not slow"` | MT5 behavior via mocks, no real trading env required |
| `tests-full` (optional/nightly) | `pytest --run-slow --run-mt5` | Full suite smoke |

## 5) Suggested CI order

1. Run `tests-fast` on every push/PR.
2. Run `tests-slow` and `tests-mt5` on PRs or protected branches.
3. Run `tests-full` nightly or before release tags.
