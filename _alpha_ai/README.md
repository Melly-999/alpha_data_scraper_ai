# Alpha AI - Automated Trading Terminal

## 3-Layer LSTM | RSI Fusion | Stochastic | MT5 Live Trading Engine

Alpha AI to zaawansowany terminal tradingowy oparty o:

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
_alpha_ai/
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
