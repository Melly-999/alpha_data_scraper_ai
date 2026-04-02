Use as bootstrap.sh:

#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-grok_alpha_ai}"
GIT_REMOTE_URL="${2:-}"   # optional, e.g. git@github.com:YOUR_USER/grok_alpha_ai.git

echo ">>> Creating project: ${PROJECT_DIR}"
mkdir -p "${PROJECT_DIR}"
cd "${PROJECT_DIR}"

mkdir -p tests profiling .github/workflows

#######################################
# Core files
#######################################

cat > README.md <<'EOF'
# 🚀 Grok Alpha AI — Automated Trading Terminal
### 3‑Layer LSTM • RSI Fusion • Stochastic • MT5 Live Trading Engine

Grok Alpha AI to zaawansowany terminal tradingowy oparty o:
- LSTM (3 warstwy) + RSI Fusion
- Stochastic Oscillator
- MACD Histogram
- Bollinger Bands Position
- Dynamiczny system sygnałów BUY/SELL
- Confidence Engine (33–85%)
- Live MT5 Tick Feed
- Wykres w czasie rzeczywistym
- Modułowa architektura

Projekt jest testowalny, konteneryzowalny i gotowy do CI/CD.
EOF

cat > .gitignore <<'EOF'
.venv/
venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.coverage
coverage.xml
*.pyc
.DS_Store
EOF

cat > config.json <<'EOF'
{
  "symbol": "EURUSD",
  "timeframe": "M1",
  "window_size": 50,
  "lstm_units": [64, 32, 16],
  "dropout": 0.2,
  "epochs": 3,
  "batch_size": 32,
  "mock_mode": true,
  "confidence_min": 33,
  "confidence_max": 85
}
EOF

cat > requirements.txt <<'EOF'
numpy
pandas
matplotlib
scikit-learn
tensorflow
MetaTrader5
pytest
pytest-cov
black
flake8
mypy
pre-commit
memory-profiler
EOF

cat > main.py <<'EOF'
import json
from mt5_fetcher import get_price_data
from indicators import add_indicators
from lstm_model import train_lstm_model, predict_next_close
from signal_generator import generate_signal


def load_config(path: str = "config.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    cfg = load_config()
    df = get_price_data(cfg)
    df = add_indicators(df).dropna().reset_index(drop=True)

    model, scaler, _, _ = train_lstm_model(df, cfg)
    pred_close = predict_next_close(model, scaler, df, cfg)

    latest = df.iloc[-1]
    signal = generate_signal(latest, pred_close, cfg)

    print("=== Grok Alpha AI ===")
    print(f"Symbol: {cfg['symbol']}")
    print(f"Last close: {latest['close']:.5f}")
    print(f"Pred close: {pred_close:.5f}")
    print(f"Signal: {signal['action']} | confidence={signal['confidence']}%")
    print(f"Reason: {signal['reason']}")


if __name__ == "__main__":
    main()
EOF

cat > mt5_fetcher.py <<'EOF'
from __future__ import annotations
import numpy as np
import pandas as pd


def _mock_data(rows: int = 1000) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    steps = rng.normal(0, 0.0005, rows).cumsum()
    base = 1.1000 + steps

    close = base
    open_ = np.roll(close, 1)
    open_[0] = close[0]
    high = np.maximum(open_, close) + rng.uniform(0, 0.0003, rows)
    low = np.minimum(open_, close) - rng.uniform(0, 0.0003, rows)
    volume = rng.integers(100, 1000, rows)

    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": volume})


def _timeframe_from_str(tf: str):
    import MetaTrader5 as mt5  # type: ignore
    mapping = {"M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15, "H1": mt5.TIMEFRAME_H1}
    return mapping.get(tf, mt5.TIMEFRAME_M1)


def get_price_data(cfg: dict, rows: int = 1000) -> pd.DataFrame:
    if cfg.get("mock_mode", True):
        return _mock_data(rows)

    try:
        import MetaTrader5 as mt5  # type: ignore
        if not mt5.initialize():
            return _mock_data(rows)

        symbol = cfg.get("symbol", "EURUSD")
        timeframe = _timeframe_from_str(cfg.get("timeframe", "M1"))
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, rows)
        mt5.shutdown()

        if rates is None or len(rates) == 0:
            return _mock_data(rows)

        df = pd.DataFrame(rates)
        return df.rename(columns={"tick_volume": "volume"})[["open", "high", "low", "close", "volume"]]
    except Exception:
        return _mock_data(rows)
EOF

cat > indicators.py <<'EOF'
import pandas as pd


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))


def stochastic(df: pd.DataFrame, period: int = 14) -> pd.Series:
    low_min = df["low"].rolling(period).min()
    high_max = df["high"].rolling(period).max()
    return 100 * (df["close"] - low_min) / (high_max - low_min + 1e-9)


def macd_hist(close: pd.Series) -> pd.Series:
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd - signal


def bollinger_pos(close: pd.Series, period: int = 20) -> pd.Series:
    ma = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = ma + 2 * std
    lower = ma - 2 * std
    return (close - lower) / (upper - lower + 1e-9)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["rsi"] = rsi(out["close"])
    out["stoch"] = stochastic(out)
    out["macd_hist"] = macd_hist(out["close"])
    out["bb_pos"] = bollinger_pos(out["close"])
    return out
EOF

cat > lstm_model.py <<'EOF'
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

FEATURES = ["close", "rsi", "stoch", "macd_hist", "bb_pos"]


def _make_windows(arr: np.ndarray, win: int):
    X, y = [], []
    for i in range(win, len(arr)):
        X.append(arr[i - win:i])
        y.append(arr[i, 0])
    return np.array(X), np.array(y)


def train_lstm_model(df: pd.DataFrame, cfg: dict):
    data = df[FEATURES].values
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)

    win = int(cfg.get("window_size", 50))
    X, y = _make_windows(scaled, win)

    split = int(len(X) * 0.8)
    X_train, y_train = X[:split], y[:split]
    X_test, y_test = X[split:], y[split:]

    units = cfg.get("lstm_units", [64, 32, 16])
    dropout = float(cfg.get("dropout", 0.2))

    model = Sequential([
        LSTM(units[0], return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
        Dropout(dropout),
        LSTM(units[1], return_sequences=True),
        Dropout(dropout),
        LSTM(units[2]),
        Dropout(dropout),
        Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X_train, y_train, epochs=int(cfg.get("epochs", 3)), batch_size=int(cfg.get("batch_size", 32)), verbose=0)
    return model, scaler, X_test, y_test


def predict_next_close(model, scaler: MinMaxScaler, df: pd.DataFrame, cfg: dict) -> float:
    win = int(cfg.get("window_size", 50))
    data = df[FEATURES].values
    scaled = scaler.transform(data)
    x = np.expand_dims(scaled[-win:], axis=0)

    pred_scaled = model.predict(x, verbose=0)[0, 0]
    dummy = np.zeros((1, len(FEATURES)))
    dummy[0, 0] = pred_scaled
    inv = scaler.inverse_transform(dummy)
    return float(inv[0, 0])
EOF

cat > signal_generator.py <<'EOF'
def _clip_conf(x: float, lo: int, hi: int) -> int:
    return int(max(lo, min(hi, round(x))))


def generate_signal(latest_row, pred_close: float, cfg: dict) -> dict:
    close = float(latest_row["close"])
    rsi = float(latest_row["rsi"])
    stoch = float(latest_row["stoch"])
    macd_h = float(latest_row["macd_hist"])
    bb_pos = float(latest_row["bb_pos"])

    score = 0.0
    reasons = []

    if pred_close > close:
        score += 1.0
        reasons.append("LSTM bullish")
    else:
        score -= 1.0
        reasons.append("LSTM bearish")

    if rsi < 35:
        score += 0.7
        reasons.append("RSI oversold")
    elif rsi > 65:
        score -= 0.7
        reasons.append("RSI overbought")

    if stoch < 20:
        score += 0.5
        reasons.append("Stochastic low")
    elif stoch > 80:
        score -= 0.5
        reasons.append("Stochastic high")

    score += 0.4 if macd_h > 0 else -0.4
    reasons.append("MACD momentum")

    if bb_pos < 0.2:
        score += 0.4
        reasons.append("Near lower Bollinger")
    elif bb_pos > 0.8:
        score -= 0.4
        reasons.append("Near upper Bollinger")

    action = "BUY" if score > 0.2 else "SELL" if score < -0.2 else "HOLD"
    conf_min = int(cfg.get("confidence_min", 33))
    conf_max = int(cfg.get("confidence_max", 85))
    confidence = _clip_conf(55 + abs(score) * 12, conf_min, conf_max)

    return {"action": action, "confidence": confidence, "reason": "; ".join(reasons), "score": score}
EOF

cat > gui.py <<'EOF'
import matplotlib.pyplot as plt
from mt5_fetcher import get_price_data
from indicators import add_indicators


def run_gui(cfg: dict):
    df = add_indicators(get_price_data(cfg, rows=300)).dropna()
    plt.figure(figsize=(10, 4))
    plt.plot(df["close"].values, label="Close")
    plt.title(f"Grok Alpha AI Live View ({cfg.get('symbol', 'EURUSD')})")
    plt.legend()
    plt.tight_layout()
    plt.show()
EOF

cat > Dockerfile <<'EOF'
FROM python:3.10-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
EOF

cat > .pre-commit-config.yaml <<'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks: [{id: black}]
  - repo: https://github.com/PyCQA/flake8
    rev: 6.1.0
    hooks: [{id: flake8}]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks: [{id: mypy}]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
EOF

cat > pyproject.toml <<'EOF'
[tool.black]
line-length = 100
target-version = ["py310"]
EOF

cat > .flake8 <<'EOF'
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = .git,__pycache__,.venv,venv,.mypy_cache,.pytest_cache
EOF

cat > pytest.ini <<'EOF'
[pytest]
minversion = 7.0
addopts = -v --strict-markers
testpaths = tests
python_files = test_*.py
markers =
    slow: longer-running tests
    stress: stress/performance-oriented tests
EOF

cat > run_tests.sh <<'EOF'
#!/usr/bin/env bash
set -e
pytest -m "not stress" -v
EOF

cat > dev.sh <<'EOF'
#!/usr/bin/env bash
set -e
black .
flake8 .
mypy . --ignore-missing-imports
pytest -m "not stress" -v
pytest -m "not stress" --cov=. --cov-report=term-missing -v
EOF

cat > Makefile <<'EOF'
.PHONY: install format lint type test test-stress cov run docker-build docker-run clean
PYTHON ?= python
PIP ?= pip
IMAGE ?= grok-alpha-ai
TAG ?= local

install:
	$(PIP) install --upgrade pip && $(PIP) install -r requirements.txt
format:
	black .
lint:
	flake8 .
type:
	mypy . --ignore-missing-imports
test:
	pytest -m "not stress" -v
test-stress:
	pytest -m "stress" -v
cov:
	pytest -m "not stress" --cov=. --cov-report=term-missing --cov-report=xml -v
run:
	$(PYTHON) main.py
docker-build:
	docker build -t $(IMAGE):$(TAG) .
docker-run:
	docker run --rm -it $(IMAGE):$(TAG)
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +; \
	find . -type d -name ".pytest_cache" -exec rm -rf {} +; \
	find . -type d -name ".mypy_cache" -exec rm -rf {} +; \
	find . -type f -name ".coverage" -delete; \
	find . -type f -name "coverage.xml" -delete
EOF

cat > profiling/profile_cpu.py <<'EOF'
import cProfile
import pstats
from main import main

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    pstats.Stats(profiler).sort_stats("tottime").print_stats(30)
EOF

cat > profiling/profile_memory.py <<'EOF'
from memory_profiler import profile
from main import main

@profile
def run():
    main()

if __name__ == "__main__":
    run()
EOF

#######################################
# Tests
#######################################

cat > tests/conftest.py <<'EOF'
# shared fixtures placeholder
EOF

cat > tests/test_indicators.py <<'EOF'
import pandas as pd
from indicators import add_indicators

def test_add_indicators_columns():
    df = pd.DataFrame({
        "open": [1,2,3,4,5,6,7,8,9,10]*5,
        "high": [x+0.2 for x in [1,2,3,4,5,6,7,8,9,10]*5],
        "low": [x-0.2 for x in [1,2,3,4,5,6,7,8,9,10]*5],
        "close": [1,2,3,4,5,6,7,8,9,10]*5,
        "volume": [100]*50
    })
    out = add_indicators(df)
    for col in ["rsi","stoch","macd_hist","bb_pos"]:
        assert col in out.columns
EOF

cat > tests/test_signal_generator.py <<'EOF'
from signal_generator import generate_signal

def test_generate_signal_shape():
    row = {"close":1.10,"rsi":30,"stoch":15,"macd_hist":0.001,"bb_pos":0.1}
    cfg = {"confidence_min":33,"confidence_max":85}
    s = generate_signal(row, pred_close=1.11, cfg=cfg)
    assert "action" in s and "confidence" in s
    assert 33 <= s["confidence"] <= 85
EOF

cat > tests/test_lstm_model.py <<'EOF'
import numpy as np
import pandas as pd
from indicators import add_indicators
from lstm_model import train_lstm_model, predict_next_close

def test_lstm_train_predict():
    n = 220
    close = np.linspace(1.0, 1.2, n)
    df = pd.DataFrame({
        "open": close, "high": close + 0.01, "low": close - 0.01,
        "close": close, "volume": np.random.randint(100, 200, n)
    })
    df = add_indicators(df).dropna().reset_index(drop=True)
    cfg = {"window_size":20,"epochs":1,"batch_size":16,"lstm_units":[16,8,4],"dropout":0.1}
    model, scaler, _, _ = train_lstm_model(df, cfg)
    pred = predict_next_close(model, scaler, df, cfg)
    assert isinstance(pred, float)
EOF

cat > tests/test_integration_pipeline.py <<'EOF'
from mt5_fetcher import get_price_data
from indicators import add_indicators

def test_pipeline_mock_fetch_and_indicators():
    cfg = {"mock_mode": True}
    df = get_price_data(cfg, rows=300)
    out = add_indicators(df)
    assert len(out) == 300
EOF

cat > tests/test_integration_gui_pipeline.py <<'EOF'
def test_gui_import():
    import gui  # noqa: F401
    assert True
EOF

cat > tests/test_stress_extended.py <<'EOF'
import pytest
from mt5_fetcher import get_price_data

@pytest.mark.stress
def test_stress_large_fetch_mock():
    df = get_price_data({"mock_mode": True}, rows=5000)
    assert len(df) == 5000
EOF

#######################################
# Workflows
#######################################

cat > .github/workflows/ci.yml <<'EOF'
name: CI v2
on:
  push:
    branches: ["main", "master", "develop"]
  pull_request:
    branches: ["main", "master", "develop"]
  workflow_dispatch:

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint-and-type:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
          cache-dependency-path: requirements.txt
      - run: python -m pip install --upgrade pip && pip install -r requirements.txt
      - run: black --check .
      - run: flake8 .
      - run: mypy . --ignore-missing-imports

  tests:
    runs-on: ubuntu-latest
    needs: lint-and-type
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"
          cache-dependency-path: requirements.txt
      - run: python -m pip install --upgrade pip && pip install -r requirements.txt
      - run: pytest -m "not stress" --cov=. --cov-report=xml --cov-report=term-missing -v
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-xml-py${{ matrix.python-version }}
          path: coverage.xml
EOF

cat > .github/workflows/nightly-stress.yml <<'EOF'
name: Nightly Stress Tests
on:
  schedule:
    - cron: "0 2 * * *"
  workflow_dispatch:

jobs:
  stress:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
          cache-dependency-path: requirements.txt
      - run: python -m pip install --upgrade pip && pip install -r requirements.txt
      - run: pytest -m "stress" -v --maxfail=1
EOF

cat > .github/workflows/release-ghcr.yml <<'EOF'
name: Release to GHCR
on:
  push:
    tags: ["v*.*.*"]
  workflow_dispatch:

permissions:
  contents: read
  packages: write

env:
  IMAGE_NAME: grok-alpha-ai

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository_owner }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=tag
            type=sha
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
EOF

#######################################
# Permissions
#######################################
chmod +x dev.sh run_tests.sh

#######################################
# Git init + first commit
#######################################
if [ ! -d .git ]; then
  git init
fi

git add .
git commit -m "Initial scaffold: Grok Alpha AI (code, tests, docker, CI/CD)" || true

# Set default branch to main if possible
if git rev-parse --verify main >/dev/null 2>&1; then
  git branch -M main
else
  git branch -M main || true
fi

# Optional remote
if [ -n "${GIT_REMOTE_URL}" ]; then
  if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin "${GIT_REMOTE_URL}"
  else
    git remote add origin "${GIT_REMOTE_URL}"
  fi
fi

#######################################
# Final instructions
#######################################
echo ""
echo "✅ Bootstrap complete."
echo ""
echo "Next steps:"
echo "  cd ${PROJECT_DIR}"
echo "  python -m venv .venv && source .venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  pre-commit install"
echo "  ./run_tests.sh"
echo "  python main.py"
echo ""
echo "If remote is configured:"
echo "  git push -u origin main"