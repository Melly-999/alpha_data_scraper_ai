# Przegląd Projektu — MellyTrade

## Czym jest projekt

MellyTrade to AI-assisted trading workstation rozwijany jako bezpieczne środowisko do researchu, paper-tradingu, integracji brokerskich i monitorowania sygnałów.

Projekt łączy:
- backend FastAPI
- dashboard React i TypeScript
- architekturę broker adapterów
- wsparcie IBKR Paper
- zachowaną ścieżkę integracji MT5
- lokalne skrypty uruchomieniowe i smoke testy

## Obecny status

Projekt jest obecnie w fazie lokalnego workstation i paper-trading.

Co działa:
- backend FastAPI
- dashboard lokalny
- broker health/account endpoints
- Broker card dla IBKR Paper
- safe disconnected state bez aktywnego TWS
- dry-run execution model
- lokalne skrypty Windows do uruchamiania i smoke testów

## Jak uruchomić lokalnie

### Backend

```powershell
cd C:\Users\highe\Desktop\alpha_data_scraper_ai-phase1-checkpoint
.\scripts\start_backend_ibkr_paper.ps1
```

### Frontend

```powershell
cd C:\Users\highe\Desktop\alpha_data_scraper_ai-phase1-checkpoint
.\scripts\start_frontend.ps1
```

### Smoke test

```powershell
cd C:\Users\highe\Desktop\alpha_data_scraper_ai-phase1-checkpoint
.\scripts\smoke_ibkr_paper.ps1
```

## Czego projekt nie robi

Projekt obecnie:
- nie składa realnych zleceń live
- nie uruchamia unattended live trading
- nie udostępnia kontrolek order-entry w dashboardzie
- nie obiecuje zyskowności ani automatycznego zarabiania

## Safety-first

Najważniejsze założenia bezpieczeństwa:
- `autotrade.enabled=false`
- `dry_run=true`
- `supports_live_orders=false`
- IBKR live orders są zablokowane
- dashboard pozostaje read-only dla warstwy brokerskiej
- MT5 path jest zachowany, ale nie został przerobiony na aktywną live execution path

## Roadmap

### Bliski termin
- dopięcie sesji TWS Paper
- heartbeat i reconnect monitoring dla brokera
- dalsze dopracowanie dashboardu
- uporządkowanie audit-first logów dla dry-run

### Później
- manual approval mode przed jakąkolwiek ścieżką non-dry-run
- rozszerzenie paper adapterów
- trwały storage dla execution i audit
- lepsza korelacja backtestu z execution path

## Disclaimer

Repozytorium ma charakter edukacyjny, badawczy i paper-tradingowy.

Nie stanowi porady finansowej, nie gwarantuje wyników tradingowych i nie powinno być używane do niekontrolowanego handlu live. Handel live jest celowo wyłączony domyślnie.
