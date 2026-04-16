# Alpha Data Scraper AI — Master Workflow Guide (PL)

## 1. Czym jest ten projekt
To jest modularny system AI-assisted trading pod MetaTrader 5, który łączy warstwę danych, silnik sygnałów, kontrolę ryzyka, execution, monitoring realtime, dashboard, Telegram alerts i przyszły pipeline monetyzacji. Projekt nie jest tylko botem do klikania pozycji. To ma być pełne środowisko tradingowe typu prop-firm / fintech MVP.

## 2. Główne warstwy systemu
- core/: konfiguracja i główna logika uruchomieniowa
- risk/: risk manager, FTMO guard, limity dzienne, exposure control
- monitoring/: live bridge, telemetry, Telegram, trade history, prop-firm stream
- api/: FastAPI, websocket stream, analytics endpoints
- frontend/: prosty dashboard bez build stepu
- db/: SQLite schema i lokalna persystencja
- mt5_*.py: pobieranie danych i execution przez MetaTrader 5
- lstm_model.py / signal_generator.py: AI + scoring + sygnał
- gui.py: desktop live control deck

## 3. Docelowy workflow całego projektu
### Etap A — Development local
1. Uruchom kod lokalnie.
2. Sprawdź paper-safe config.
3. Uruchom snapshot console.
4. Uruchom GUI.
5. Uruchom API realtime.
6. Zweryfikuj WebSocket, SQLite i Telegram.

### Etap B — Validation
1. Zbieraj sygnały przez minimum 2 tygodnie.
2. Mierz confidence, drawdown, winrate, SL/TP ratio.
3. Usuń niestabilne reguły.
4. Zablokuj overtrading.
5. Sprawdź stabilność MT5 session.

### Etap C — Paper trading 24/7
1. Windows VPS.
2. MT5 terminal uruchomiony stale.
3. Runtime loop + logging + auto-restart.
4. Telegram alerts.
5. Dashboard dostępny zdalnie.

### Etap D — Micro-live
1. Najmniejszy realny wolumen.
2. Maksymalnie 1% ryzyka per trade.
3. Tylko wysokie confidence trades.
4. Dzienny hard stop.
5. Tygodniowy review.

### Etap E — Scaling / monetization
1. Telegram premium signals.
2. Dashboard premium.
3. Prop-firm challenge mode.
4. White-label panel.
5. SaaS analytics for traders.

## 4. Jedno wielkie drzewo next steps
### Core system
- uporządkować import compatibility
- dodać central service runner
- dodać config profiles: paper_safe, ftmo_safe, live_micro, dashboard_only
- dodać rotating logs

### AI / Strategy
- rozbić score na explainable attribution
- dodać strategy profiler
- dodać walk-forward validation
- dodać symbol filtering
- dodać session filtering

### Risk
- daily reset UTC
- max daily loss
- max open positions
- cooldown logic
- duplicate signal blocking
- exposure limits cross-symbol

### Execution
- paper/live switch
- retry policy
- MT5 reconnect logic
- SL/TP verification
- partial fill / rejection handling

### Monitoring
- confidence heatmap
- equity curve
- closed trade winrate
- SL/TP hit alerts
- cooldown alerts
- prop-firm risk stream
- Prometheus + Grafana later

### Product
- dashboard polishing
- auth layer
- user roles
- subscription enforcement later
- landing page / docs / demo video

## 5. Kolejność uruchomienia na serwerze
Najbezpieczniejsza i najpraktyczniejsza ścieżka pod MT5 to Windows VPS, bo Python integration z MT5 jest oparta o terminal MetaTrader 5.

Kolejność:
1. Postaw Windows VPS.
2. Zainstaluj Python 3.11.
3. Zainstaluj MetaTrader 5 terminal.
4. Zaloguj konto brokerowe.
5. Wgraj repo.
6. Zainstaluj requirements.
7. Uruchom schema.sql.
8. Odpal runtime paper_safe.
9. Odpal FastAPI.
10. Odpal dashboard.
11. Odpal Telegram stream.
12. Dodaj auto-restart i scheduled reboot policy.

## 6. Jak tym zarabiać mądrze
Nie zakładaj, że samo postawienie na VPS zacznie drukować pieniądze. Serwer daje uptime, a nie edge. Zarabianie przychodzi dopiero po przejściu przez:
- paper trading
- kontrolę ryzyka
- review expectancy
- micro-live
- dopiero później skalowanie

Realne ścieżki monetyzacji:
- własny trading na małym kapitale
- sygnały premium Telegram
- dostęp do dashboardu premium
- konsulting / custom bot deployment
- później SaaS dla traderów

## 7. Zasada operacyjna
Najpierw stabilność.
Potem metryki.
Potem paper.
Potem micro-live.
Dopiero potem agresywniejsza monetyzacja.
