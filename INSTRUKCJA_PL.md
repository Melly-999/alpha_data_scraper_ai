# 🚀 Alpha AI Trading Bot - Kompletna Instrukcja Wdrożenia

**Projekt:** `alpha_data_scraper_ai` | **Architektura:** Multi-broker + Claude AI  
**Broker wsparty:** XTB (IKE) + yfinance | **Raporty:** Daily/Weekly/Monthly | **Deploy:** Docker 24/7

---

## 📋 QUICK START (Pick One)

| Opcja | Opis | Czas | Dla kogo |
|-------|------|------|----------|
| **A** | Test Parser XTB | 5 min | Chcę sprawdzić czy ładuje moje dane |
| **B** | Pełne uruchomienie lokalne | 30 min | Chcę pracować z systemem na laptopie |
| **C** | Docker 24/7 | 45 min | Chcę to w chmurze / serwer |
| **D** | Wszystko na raz | N/A | Chcę mieć wszystko w ZIP |

---

## **A️⃣ TEST PARSER - XTB Data Validation** (5 min)

### Krok 1: Dodaj swoje XLSX pliki

```bash
# Umieść pliki w ./data/
cp /path/to/IKE_54250698_2026-03-07_2026-04-07.xlsx ./data/
cp /path/to/PLN_51514835_2026-03-07_2026-04-07.xlsx ./data/
```

### Krok 2: Uruchom test

```bash
python3 test_parser.py
```

### Oczekiwany output:

```
============================================================
TEST PARSERA XTB – CLOSED POSITIONS + CASH OPERATIONS
============================================================

✅ Wczytano 47 pozycji:
   AAPL.US    |     5.0000 szt. | avg  152.30
   VWRL.L     |    20.0000 szt. | avg   25.40
   ...

✅ Cash Operations:
   Transakcji: 156
   Net cash flow: -45000.00 PLN
   Dywidendy brutto: 3200.50 PLN
   Podatek: 640.10 PLN
   Dywidendy netto: 2560.40 PLN

✅ Wartość portfela (yfinance): 950000.00 PLN
```

### Co parser robi?

✅ Czyta XLSX z XTB (Closed Positions, Cash Operations)  
✅ Normalizuje tickery (.US → brak, .PL → .WA, .UK → .L)  
✅ Liczy dywidendy brutto/netto (19% Belka)  
✅ Pobiera aktualne ceny z yfinance  
✅ Eksportuje raport: `reports/daily_YYYY-MM-DD.md`

---

## **B️⃣ FULL LOCAL RUNTIME** (30 min)

### Krok 1: Setup environment

```bash
# Skopiuj .env
cp .env.example .env

# EDYTUJ .env:
nano .env
```

**Wymagane zmienne w .env:**

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx          # Twój Claude API key
ACTIVE_BROKER=xtb
XTB_DATA_PATH=./data/
TZ=Europe/Warsaw
```

**Opcjonalne:**

```bash
TELEGRAM_BOT_TOKEN=123456:ABCdefgh            # Dla powiadomień
TELEGRAM_CHAT_ID=-1001234567890
```

### Krok 2: Zainstaluj zależności

```bash
pip install -r requirements.txt
```

### Krok 3: Uruchom testy

```bash
# Test 1: Parser XTB
python3 test_parser.py

# Test 2: Claude AI connection
python3 -c "from claude_ai import ClaudeAIIntegration; c = ClaudeAIIntegration(); print(c.test_connection())"
```

### Krok 4: Uruchom raporty ręcznie

```bash
# Daily analysis
python3 daily_analysis.py

# Weekly analysis
python3 weekly_analysis.py

# Monthly dividend report
python3 monthly_dividend_report.py
```

### Krok 5: Uruchom scheduler (tło)

```bash
python3 scheduler.py
```

**Harmonogram:**
- **Codziennie 08:30** → Daily risk analysis (Bridgewater)
- **Każdy poniedziałek 09:00** → Weekly cash flow report
- **1. dzień miesiąca 10:00** → Monthly dividend analysis (Harvard)

### Krok 6: Webhook TradingView (port 8000)

W osobnym terminalu:

```bash
python3 webhook_server.py
```

Endpoint: `http://localhost:8000/webhook` (POST)  
Health: `http://localhost:8000/health` (GET)

### Struktura output'ów

```
reports/
├── daily_2026-04-07.md          # Risk analysis
├── weekly_2026-04-07_09-00.md   # Cash flow
└── monthly_dividend_2026-04-07.md  # Dividend strategy
```

---

## **C️⃣ DOCKER 24/7 PRODUCTION** (45 min)

### Wymagania

```bash
# Sprawdź czy masz Docker
docker --version    # Docker version 20.10+
docker-compose --version  # docker-compose 2.0+

# Jeśli nie masz - zainstaluj:
# Mac: brew install docker
# Linux: sudo apt install docker.io docker-compose
# Windows: https://docker.com/download
```

### Krok 1: Setup .env

```bash
cp .env.example .env
nano .env
# Wpisz ANTHROPIC_API_KEY
```

### Krok 2: Build & Run

```bash
./build_and_run.sh
```

**Co się dzieje:**

1. ✅ Sprawdza Docker (`docker-compose --version`)
2. ✅ Buduje images (`docker-compose build`)
3. ✅ Uruchamia 2 serwisy:
   - **alpha-ai-scheduler** (scheduler.py) — raporty co noc
   - **alpha-ai-webhook** (webhook_server.py) — port 8000

### Krok 3: Monitoruj logi

```bash
# Scheduler (raporty)
docker-compose logs -f alpha-ai-scheduler

# Webhook (TradingView alerts)
docker-compose logs -f alpha-ai-webhook

# Wszystko
docker-compose logs -f
```

### Zarządzanie serwisem

```bash
# Status
docker-compose ps

# Restart
docker-compose restart

# Stop
docker-compose down

# Clean rebuild
docker-compose down --volumes
./build_and_run.sh
```

### Skalowanie na serwer (np. AWS/DigitalOcean)

```bash
# 1. SSH na serwer
ssh ubuntu@your-server.com

# 2. Klonuj repo
git clone https://github.com/yourusername/alpha_data_scraper_ai
cd alpha_data_scraper_ai

# 3. Setup .env
echo "ANTHROPIC_API_KEY=sk-ant-xxxx" > .env

# 4. Uruchom
./build_and_run.sh

# 5. Setup reverse proxy (nginx/caddy) na port 8000
# (dokumentacja w sekcji "Production Deployment")
```

---

## **D️⃣ FULL PROJECT ZIP**

Zawarte w `alpha_ai_trading_bot.zip`:

```
alpha_data_scraper_ai/
├── brokers/                    # Multi-broker abstraction
│   ├── __init__.py
│   ├── broker_interface.py     # ABC interface
│   ├── xtb_broker.py           # XTB parser (XLSX reader)
│   ├── ibkr_broker.py          # Interactive Brokers
│   ├── alpaca_broker.py        # Alpaca API
│   ├── hybrid_broker.py        # XTB + Alpaca combo
│   └── broker_factory.py       # Factory pattern
│
├── config/
│   ├── brokers.yaml            # Broker config + paths
│   └── notifications.yaml      # Telegram/Discord
│
├── prompts.py                  # 10 Wall Street prompts
├── claude_ai.py                # Claude API integration
├── ai_engine.py                # Broker + AI pipeline
│
├── daily_analysis.py           # Risk analysis (Bridgewater)
├── weekly_analysis.py          # Cash flow report
├── monthly_dividend_report.py  # Dividend strategy (Harvard)
├── notifications.py            # Telegram/Discord sender
│
├── scheduler.py                # APScheduler (Poland tz)
├── webhook_server.py           # FastAPI + TradingView
├── test_parser.py              # XTB XLSX validator
│
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image
├── docker-compose.yml          # 2-container setup
├── build_and_run.sh           # Docker automation
│
├── .env.example                # Template (edit and save as .env)
├── .gitignore                  # Git ignore
├── README.md                   # This file
│
├── data/                       # Your XLSX files
│   ├── IKE_54250698_2026-03-07_2026-04-07.xlsx
│   └── PLN_51514835_2026-03-07_2026-04-07.xlsx
│
└── reports/                    # Output directory
    ├── daily_2026-04-07.md
    ├── weekly_2026-04-07_09-00.md
    └── monthly_dividend_2026-04-07.md
```

---

## 🔑 WALL STREET PROMPTS (Included)

System zawiera 10 profesjonalnych prompt'ów:

1. **goldman_screener** — Stock screening (P/E, growth)
2. **morgan_dcf** — DCF valuation model
3. **bridgewater_risk** — Portfolio risk analysis ⭐ (daily default)
4. **harvard_dividend** — Dividend strategy ⭐ (monthly)
5. **citadel_technical** — Technical analysis (TradingView)
6. **mckinsey_macro** — Macro economic factors
7. **jpmorgan_earnings** — Earnings analysis
8. **blackrock_portfolio** — Asset allocation
9. **bain_competitive** — Competitive analysis
10. **renaissance_quant** — Quantitative models

---

## 📊 DATA FLOW

```
XTB XLSX Files (./data/)
         ↓
   XTBBroker (parser)
         ↓
   get_positions() → yfinance prices
   get_cash_summary() → dividends + taxes (Belka 19%)
   get_portfolio_value()
         ↓
   AI Engine + Claude
         ↓
   Wall Street Prompts (Bridgewater, Harvard, etc.)
         ↓
   Reports (MD files)
         ↓
   Notifications (Telegram/Discord)
```

---

## 🚨 TROUBLESHOOTING

### Parser nie czyta XLSX

```bash
# Sprawdź ścieżki
ls -la ./data/

# Sprawdź format
python3 -c "import openpyxl; wb = openpyxl.load_workbook('./data/IKE_54250698_2026-03-07_2026-04-07.xlsx'); print(wb.sheetnames)"
# Powinno pokazać: ['Closed Positions', 'Cash Operations', ...]
```

### Claude API error

```bash
# Sprawdź API key
echo $ANTHROPIC_API_KEY

# Test connection
python3 -c "from claude_ai import ClaudeAIIntegration; c = ClaudeAIIntegration(); print(c.test_connection())"
```

### Docker doesn't start

```bash
# Logi
docker-compose logs

# Rebuild
docker-compose down --volumes
docker-compose build --no-cache
docker-compose up
```

---

## 📞 WSPARCIE

- **API Docs:** https://docs.anthropic.com
- **XTB Format:** Sprawdź `config/brokers.yaml`
- **Issues:** Check GitHub issues or contact support

---

## 📝 LICENSE & CONTEXT

**Investor:** Mati (Poland)  
**Accounts:** XTB IKE (PLN, 19% Belka tax)  
**Created:** Apr 2026  
**Architecture:** Based on Grok blueprint + Claude enhancement

---

## ✅ CHECKLIST PRZED PRODUKCJĄ

- [ ] .env zawiera ANTHROPIC_API_KEY
- [ ] XLSX pliki w ./data/
- [ ] Docker zainstalowany (dla C)
- [ ] Telegram token (opcjonalne)
- [ ] Cron/systemd dla scheduler (dla C)
- [ ] Backup danych (co tydzień)
- [ ] Monitoring alertów (Telegram/Discord)

---

**You're ready! Pick option A, B, C, or D and go. 🚀**
