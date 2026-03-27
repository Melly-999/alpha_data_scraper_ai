# Grok Alpha AI - Automated Trading Terminal

[![Pytest CI (main)](https://github.com/Melly-999/alpha_data_scraper_ai/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/Melly-999/alpha_data_scraper_ai/actions/workflows/pytest.yml?query=branch%3Amain)

## 3-Layer LSTM | RSI Fusion | Stochastic | MT5 Live Trading Engine

Grok Alpha AI to zaawansowany terminal tradingowy oparty o:

- **LSTM (3 warstwy) + RSI Fusion**
- **Stochastic Oscillator**
- **MACD Histogram**
- **Bollinger Bands Position**
- **Dynamiczny system sygnalow BUY/SELL**
- **Confidence Engine (33-85%)**
- **Live MT5 Tick Feed**
- **Wykres w czasie rzeczywistym**
- **Modulowa architektura (7 plikow)**

Projekt jest w pelni testowalny, konteneryzowalny i gotowy do CI/CD.

---

## Struktura projektu

```text
grok_alpha_ai/
|-- config.json
|-- main.py
|-- gui.py
|-- mt5_fetcher.py
|-- indicators.py
|-- lstm_model.py
|-- signal_generator.py
|-- tests/
|   |-- test_indicators.py
|   |-- test_signal_generator.py
|   |-- test_lstm_model.py
|   |-- test_integration_pipeline.py
|   |-- test_integration_gui_pipeline.py
|   |-- test_stress_extended.py
|   `-- conftest.py
|-- profiling/
|   |-- profile_cpu.py
|   `-- profile_memory.py
|-- Dockerfile
|-- dev.sh
|-- run_tests.sh
|-- requirements.txt
`-- .pre-commit-config.yaml
```

---

## Instalacja

### 1. Klonowanie repo

```bash
git clone https://github.com/Melly-999/alpha_data_scraper_ai.git
cd grok_alpha_ai
```

### 2. Instalacja zaleznosci

```bash
pip install -r requirements.txt
```

Uwaga:

- `tensorflow` i `MetaTrader5` sa traktowane jako zaleznosci opcjonalne na niewspieranych wersjach Pythona.
- Pipeline uruchomi sie bez nich, korzystajac z fallbacku dla modelu i danych syntetycznych.

### Windows setup

Preferowana sciezka lokalna na Windows:

```powershell
.\setup_windows.ps1
```

Jesli masz problem z lokalnym Pythonem, uruchamiaj projekt przez Docker z sekcji ponizej.

---

## Uruchamianie aplikacji

```bash
python main.py
```

### Auto-trade MetaTrader5

Auto-trade jest sterowany przez sekcje `autotrade` w `config.json`.

Domyslnie:

- `enabled: false` (brak wysylki zlecen),
- `dry_run: true` (symulacja requestu do MT5 bez realnego ordera).

Zalecana kolejnosc:

1. Ustaw `enabled: true` i zostaw `dry_run: true`, uruchom aplikacje i sprawdzaj pole `autotrade` w snapshotach.
2. Po weryfikacji ustaw `dry_run: false`, aby wlaczyc realne zlecenia rynkowe BUY/SELL.

Przykladowe klucze:

- `min_confidence` - minimalna pewnosc sygnalu do wyslania zlecenia,
- `volume` - wolumen pozycji,
- `sl_points` / `tp_points` - odleglosc SL/TP w punktach,
- `cooldown_seconds` - minimalny odstep miedzy kolejnymi zleceniami,
- `allow_same_signal` - czy pozwolic na kolejne zlecenie w tym samym kierunku.

Gotowe profile (folder `profiles/`):

1. `paper_safe.json` - bezpieczny paper-trading (`dry_run: true`)
2. `real_conservative.json` - real trading konserwatywny
3. `real_aggressive.json` - real trading agresywny

Uruchamianie z profilem:

```powershell
.[0m\.venv\Scripts\python.exe main.py --config profiles/paper_safe.json --continuous --interval 2
```

```powershell
.[0m\.venv\Scripts\python.exe main.py --config profiles/real_conservative.json --continuous --interval 2
```

```powershell
.[0m\.venv\Scripts\python.exe main.py --config profiles/real_aggressive.json --continuous --interval 2
```

---

## Testy

Uruchom wszystkie testy:

```bash
./run_tests.sh
```

PowerShell:

```powershell
.\run_tests.ps1 -q
```

GitHub Actions:

- Workflow: [Pytest CI](https://github.com/Melly-999/alpha_data_scraper_ai/actions/workflows/pytest.yml)
- Wszystkie runy: [Actions](https://github.com/Melly-999/alpha_data_scraper_ai/actions)

Szybki workflow git dla tego repo:

```bash
git add .
git commit -m "opis zmian"
git push
```

---

## Docker

Budowanie obrazu:

```bash
docker build -t grok-alpha .
```

Budowanie wersji produkcyjnej na lzejszym obrazie:

```bash
docker build -f Dockerfile.prod -t grok-alpha:prod .
```

Uruchamianie:

```bash
docker run --rm -it grok-alpha
```

Uruchamianie wersji produkcyjnej:

```bash
docker run --rm -it grok-alpha:prod
```

Docker Compose:

```bash
docker compose up app
docker compose run --rm tests
docker compose run --rm dev
```

---

## Profilowanie wydajnosci

CPU profiling:

```bash
python profiling/profile_cpu.py
```

Memory profiling:

```bash
python profiling/profile_memory.py
```

---

## Pre-commit hooks

Instalacja:

```bash
pre-commit install
```

Uruchomienie reczne:

```bash
pre-commit run --all-files
```

---

## Windows Dev I Test Commands

Setup lokalny:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup_windows.ps1
```

Aktywacja srodowiska:

```powershell
.\.venv\Scripts\Activate.ps1
```

Uruchomienie aplikacji:

```powershell
.\.venv\Scripts\python.exe main.py
```

Uruchomienie wszystkich testow:

```powershell
.\run_tests.ps1 -q
```

Uruchomienie tylko nowych testow pipeline:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_integration_pipeline.py tests/test_integration_gui_pipeline.py tests/test_stress_extended.py
```

Formatowanie, lint i coverage:

```powershell
bash ./dev.sh
```

Jesli nie chcesz aktywowac `.venv`, mozesz uzywac bezposrednio:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m black .
.\.venv\Scripts\python.exe -m flake8 .
.\.venv\Scripts\python.exe -m mypy .
```

---

## Licencja

MIT License.
