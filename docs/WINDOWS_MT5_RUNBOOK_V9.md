# Windows + MT5 runbook for v9

## Install
- Python 3.11
- MetaTrader 5 desktop terminal
- VS Code

## Create virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configure
Create a local `.env` file and set:
- dashboard API keys
- webhook secret
- MT5 credentials
- MT5 terminal path if needed

## Start backend
```powershell
uvicorn app.main:app --reload
```

## Validate
- open `/health`
- open `/docs`
- verify role-based API key access
- verify `/ops/mt5-health`
- verify WebSocket replay / notifications

## MT5 troubleshooting
- run MT5 under the same Windows user as Python
- log into the account before the backend starts
- ensure symbols are visible in Market Watch
- set `MT5_PATH` explicitly if automatic detection fails