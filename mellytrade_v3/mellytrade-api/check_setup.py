from __future__ import annotations

import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - diagnostic fallback
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


API_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8001").rstrip("/")
API_KEY = os.getenv("FASTAPI_KEY", "change-me-fastapi-key")


def status(name: str, ok: bool, detail: str = "") -> bool:
    result = "OK" if ok else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"[{result}] {name}{suffix}")
    return ok


def request_json(
    method: str,
    path: str,
    payload: dict[str, object] | None = None,
    api_key: str | None = API_KEY,
) -> tuple[int, str]:
    data = None
    headers = {"Content-Type": "application/json"}
    if api_key is not None:
        headers["X-API-Key"] = api_key
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{API_URL}{path}",
        data=data,
        method=method,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


def check_env() -> bool:
    required = [
        "DATABASE_URL",
        "FASTAPI_KEY",
        "CF_HUB_URL",
        "CF_API_SECRET",
        "MIN_CONFIDENCE",
        "MAX_RISK_PERCENT",
    ]
    missing = [key for key in required if not os.getenv(key)]
    return status("environment", not missing, f"missing: {', '.join(missing)}" if missing else "")


def check_sqlite() -> bool:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./mellytrade.db")
    if not database_url.startswith("sqlite:///"):
        return status("sqlite", True, f"skipped for {database_url}")
    db_path = Path(database_url.replace("sqlite:///", "", 1))
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("select 1")
        conn.close()
    except sqlite3.Error as exc:
        return status("sqlite", False, str(exc))
    return status("sqlite", db_path.exists(), str(db_path.resolve()))


def check_backend() -> bool:
    health_status, health_body = request_json("GET", "/health", api_key=None)
    ok_health = status("health", health_status == 200, health_body)

    valid = {
        "symbol": "EURUSD",
        "direction": "BUY",
        "confidence": 80,
        "price": 1.1,
        "stopLoss": 1.09,
        "takeProfit": 1.12,
        "riskPercent": 0.5,
        "source": "check_setup",
    }
    unauthorized_status, _ = request_json("POST", "/signal", valid, api_key=None)
    ok_auth = status("signal unauthorized", unauthorized_status == 401)

    low_confidence = {**valid, "symbol": "USDJPY", "confidence": 69.9}
    low_conf_status, low_conf_body = request_json("POST", "/signal", low_confidence)
    ok_low_conf = status("signal min confidence", low_conf_status == 400, low_conf_body)

    missing_sltp = {**valid, "symbol": "XAUUSD"}
    missing_sltp.pop("stopLoss")
    sltp_status, sltp_body = request_json("POST", "/signal", missing_sltp)
    ok_sltp = status("signal SL/TP", sltp_status == 400, sltp_body)

    return all([ok_health, ok_auth, ok_low_conf, ok_sltp])


def check_lstm_adapter() -> bool:
    mt5_dir = Path(__file__).resolve().parents[1] / "mt5"
    sys.path.insert(0, str(mt5_dir))
    try:
        import pandas as pd

        from lstm_signal_adapter import LSTMSignalAdapter

        rows = 80
        close = [1.10 + (idx * 0.0001) for idx in range(rows)]
        frame = pd.DataFrame(
            {
                "close": close,
                "open": [value - 0.00005 for value in close],
                "high": [value + 0.0002 for value in close],
                "low": [value - 0.0002 for value in close],
                "volume": [1000 + idx for idx in range(rows)],
            }
        )
        result = LSTMSignalAdapter("EURUSD").predict(frame)
    except Exception as exc:
        return status("lstm adapter", False, str(exc))
    return status(
        "lstm adapter",
        result.available,
        (
            f"available={result.available} direction={result.direction} "
            f"confidence={result.confidence} reasons={result.reasons}"
        ),
    )


def main() -> int:
    checks = [check_env(), check_sqlite(), check_backend(), check_lstm_adapter()]
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
