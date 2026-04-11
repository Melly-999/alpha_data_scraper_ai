# Alpha AI – Automated Trading Terminal

Profesjonalny system analizy handlowej z integracją Claude AI + Wall Street promptów + automatycznym tradingiem.

## 🎯 Cechy

- ✅ **Analiza XTB** (cash flow, dywidendy, pozycje z XLSX)
- ✅ **Wall Street prompty** (Goldman Sachs, Bridgewater, Harvard, McKinsey itd.)
- ✅ **Multi-broker** (XTB, IBKR, Alpaca)
- ✅ **Automatyczne raporty** (daily, weekly, monthly)
- ✅ **TradingView webhook** (alerty → Claude analiza)
- ✅ **Powiadomienia** (Telegram, Discord)
- ✅ **Docker 24/7**

---

## 🚀 SZYBKI START

### **OPCJA A: Test Parsera (5 minut)**

```bash
# 1. Zainstaluj zależności
pip install -r requirements.txt

# 2. Wrzuć pliki XLSX z XTB do folderu data/
# Sprawdź config/brokers.yaml - ścieżki są już tam

# 3. Test
python test_parser.py
```

**Powinno pokazać:**
- Liczbę wczytanych pozycji
- Dywidendy netto, brutto
- Top dywidendy
- Wartość portfela

---

### **OPCJA B: Pełne Uruchomienie Lokalnie (30 minut)**

```bash
# 1. Setup
pip install -r requirements.txt
cp .env.example .env

# 2. EDYTUJ .env - wpisz ANTHROPIC_API_KEY
# Pobierz klucz: https://console.anthropic.com

# 3. Testuj pojedyncze raporty
python daily_analysis.py      # → raport w reports/
python weekly_analysis.py     # pełny raport
python monthly_dividend_report.py  # dywidendy

# 4. Logi
tail -f alpha_ai.log
```

---

### **OPCJA C: Docker 24/7 (45 minut)**

```bash
# 1. Setup
cp .env.example .env
# EDYTUJ .env - ANTHROPIC_API_KEY

# 2. Uruchom
chmod +x build_and_run.sh
./build_and_run.sh

# 3. Sprawdzenie
docker-compose ps
docker-compose logs -f alpha-ai-scheduler

# 4. Webhook (TradingView)
curl http://localhost:8000/health
```

Scheduler działa:
- **08:30** codziennie → daily_analysis
- **09:00 poniedziałek** → weekly_analysis
- **10:00 1. dnia miesiąca** → monthly_dividend_report

---

## 📁 Struktura

```
alpha_data_scraper_ai/
├── config/                    # Konfiguracja
│   ├── brokers.yaml          # Wybór brokera
│   └── notifications.yaml     # Telegram/Discord
├── brokers/                   # Multi-broker abstrakacja
│   ├── xtb_broker.py         # XTB (XLSX)
│   ├── ibkr_broker.py        # Interactive Brokers
│   ├── alpaca_broker.py      # Alpaca
│   └── broker_factory.py     # Przełączanie
├── data/                      # Pliki XLSX z XTB
├── reports/                   # Wygenerowane raporty
├── prompts.py                # 10 Wall Street promptów
├── claude_ai.py              # Integracja Claude API
├── ai_engine.py              # Serce systemu
├── daily_analysis.py         # Daily report
├── weekly_analysis.py        # Weekly report
├── monthly_dividend_report.py # Dywidendy
├── scheduler.py              # APScheduler (24/7)
├── webhook_server.py         # TradingView API
├── test_parser.py            # Test XLSX parsera
├── Dockerfile                # Docker image
├── docker-compose.yml        # Docker Compose
├── build_and_run.sh          # Auto-build script
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## ⚙️ Konfiguracja

### **1. Wybór Brokera** (`config/brokers.yaml`)

```yaml
active_broker: xtb    # zmień na: xtb, ibkr, alpaca

xtb:
  closed_positions_xlsx_paths:
    - "./data/IKE_54250698_2026-03-07_2026-04-07.xlsx"
    - "./data/PLN_51514835_2026-03-07_2026-04-07.xlsx"
```

### **2. API Key** (`.env`)

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### **3. Powiadomienia** (`config/notifications.yaml`)

```yaml
telegram:
  enabled: true
  bot_token: "TWÓJ_TOKEN"
  chat_id: "TWÓJ_ID"
```

---

## 🔌 Integracja TradingView

W TradingView utwórz alert z webhook:

**URL:** `http://your-ip:8000/webhook`

**Message (JSON):**
```json
{
  "ticker": "NVDA",
  "action": "buy",
  "message": "RSI oversold + MACD crossover"
}
```

Alpha AI automatycznie:
1. Otrzyma alert
2. Uruchomi analizę Claude (Citadel Technical)
3. Zwróci rekomendację

---

## 📊 Prompty (Wall Street)

System zawiera 10 profesjonalnych promptów:

1. **Goldman Screener** – screening akcji
2. **Morgan Stanley DCF** – wycena
3. **Bridgewater Risk** – analiza ryzyka
4. **JPMorgan Earnings** – earnings preview
5. **BlackRock Portfolio** – budowa portfela
6. **Citadel Technical** – analiza techniczna
7. **Harvard Dividend** – portfel dywidendowy
8. **Bain Competitive** – analiza konkurencji
9. **Renaissance Quant** – wzorce statystyczne
10. **McKinsey Macro** – analiza makro

Wszystkie automatycznie wstrzykują dane o **cash flow, dywidendach i ryzyku** z Twojego portfela.

---

## 🛠️ Polecenia

### Lokalne
```bash
python test_parser.py              # Test XLSX
python daily_analysis.py           # Codzienny raport
python scheduler.py                # APScheduler (24/7)
python webhook_server.py           # TradingView API
```

### Docker
```bash
./build_and_run.sh                 # Build + start
docker-compose down                # Stop
docker-compose logs -f             # Logi
docker-compose restart             # Restart
```

---

## 🚨 Troubleshooting

### Parser nie czyta XLSX
- Sprawdź ścieżki w `config/brokers.yaml`
- Uruchom: `python test_parser.py`

### Claude API error
- Sprawdź `.env` - czy `ANTHROPIC_API_KEY` jest prawidłowy
- Test: `python -c "from claude_ai import ClaudeAIIntegration; c = ClaudeAIIntegration(); print(c.test_connection())"`

### Docker nie uruchamia się
- Sprawdź czy Docker jest zainstalowany: `docker --version`
- Logi: `docker-compose logs`

---

## 📝 Licencja

Apache-2.0 License

## 👨‍💻 Autor

Alpha AI Team – Automated Trading Intelligence

---

**Pytania?** Sprawdź `reports/` folder – tam są wszystkie wygenerowane raporty.

