# Poradnik: Scalanie i uzupełnienie projektu `alpha_data_scraper_ai`

## Wprowadzenie

Ta paczka ZIP zawiera kompletną wersję zoptymalizowanego projektu **alpha_data_scraper_ai** oraz zebrane w jednym miejscu instrukcje dotyczące dalszych usprawnień.  Celem jest ułatwienie wdrożenia wszystkich poprawek i modyfikacji opisanych w naszych rozmowach, tak aby można było łatwo pracować z projektem lokalnie lub w środowisku takiem jak Codex.

## Szczegóły wprowadzonej optymalizacji

Na podstawie przekazanego repozytorium wprowadzono szereg usprawnień w warstwie konfiguracji i struktury kodu:

- **Dataclasses zamiast słowników konfiguracji.**  Dodano klasy `AutotradeConfig` i `AppConfig`, które zbiorczo przechowują parametry konfiguracyjne.  Pozwala to ograniczyć błędy wynikające z literówek przy odwoływaniu się do kluczy i ułatwia korzystanie z podpowiedzi typów【185373840217463†L104-L110】.
- **Uproszczony loader konfiguracji.**  Funkcja `_load_config()` zwraca teraz obiekt `AppConfig`, łącząc domyślne wartości z ustawieniami użytkownika i wykonując niezbędne konwersje typów (str → int/float).  Eliminuje to konieczność ręcznej obsługi słowników w innych modułach.
- **Refaktoryzacja inicjalizacji runtime.**  Obiekt `AppRuntime` przyjmuje `AppConfig` i tworzy słownik `LSTMPipeline` dla każdego instrumentu, aby uniknąć wielokrotnego ładowania modeli.  Ustawienia takie jak cooldown i blokada duplikatów są przekazywane bezpośrednio z konfiguracji.
- **Czytelniejszy dostęp do parametrów.**  W kodzie zamiast `cfg.get("key", domyślna)` używa się `cfg.timeframe`, `cfg.bars` itp.  Zmniejsza to liczbę wywołań słownikowych i poprawia czytelność.

## Dalsze optymalizacje: lista zadań

Poniżej znajduje się lista zadań, która może posłużyć jako pojedynczy prompt dla agenta (np. w Codex) lub jako plan wdrożenia.  Zadania skupiają się na trzech obszarach: przetwarzanie przyrostowe (incremental), asynchroniczne pobieranie danych oraz centralizacja ryzyka.

1. **Utwórz i skonfiguruj środowisko.**  Rozpakuj projekt, utwórz nowe środowisko wirtualne (`python3 -m venv venv && source venv/bin/activate`), zainstaluj zależności (`pip install -r requirements.txt`) oraz dodatkowe biblioteki asynchroniczne (`pip install httpx aiohttp`).
2. **Przetwarzanie przyrostowe wskaźników.**  W module `strategy/indicators.py` wprowadź bufor danych (np. za pomocą klasy `deque` lub własnej implementacji `RollingWindow`) przechowujący ostatnie *n* świec.  Aktualizuj wskaźniki jedynie dla najnowszego punktu zamiast ponownie liczyć całe serie【366958259369711†L789-L798】.
3. **Asynchroniczne zapytania sieciowe.**  Zlokalizuj wszystkie żądania HTTP i przerób je na funkcje `async` wykorzystujące `httpx.AsyncClient` lub `aiohttp.ClientSession`.  Wywołuj wiele żądań równolegle za pomocą `asyncio.gather`, aby poprawić wydajność【506246105154751†L46-L59】【506246105154751†L221-L246】.
4. **Centralizacja kontroli ryzyka.**  Rozszerz moduł `risk/risk_manager.py` o klasy konfiguracyjne oraz metodę `validate`, która sprawdza wszystkie reguły przed zawarciem transakcji (limit ryzyka na zlecenie, minimalny współczynnik zysku do ryzyka, obecność SL/TP i limit liczby pozycji).  Scalone, pre‑trade kontrole ryzyka chronią system przed błędnymi zleceniami【554396219266516†L30-L34】【554396219266516†L38-L42】.
5. **Aktualizacja konfiguracji i dokumentacji.**  Dodaj do plików konfiguracyjnych nowe parametry (rozmiar bufora, time‑out dla zapytań, parametry risk managera), a w plikach README/Poradnik opis nowej funkcjonalności.

## Poradnik krok po kroku: gdzie dodać zmiany

Poniższe wskazówki ułatwią integrację zmian w konkretnych plikach:

1. **Ładowanie i konfiguracja projektu:**
   - Rozpakuj plik `alpha_data_scraper_ai-main-optimized.zip` do katalogu roboczego.  Upewnij się, że wirtualne środowisko jest aktywne i zainstalowane są wszystkie zależności.

2. **Implementacja bufora wskaźników:**
   - Otwórz plik `strategy/indicators.py` i zaimportuj `collections.deque`.  Na początku modułu zainicjuj bufor, np. `rolling_window = deque(maxlen=<rozmiar>)`.  W funkcji dodającej wskaźniki dopisuj nowy wiersz do bufora i aktualizuj wskaźniki tylko dla tego wiersza.
   - Modyfikuj `mt5_fetcher.py`, aby zamiast pobierać całą historię, pobierał jedynie najnowsze świeczki i aktualizował bufor.

3. **Asynchroniczne I/O:**
   - W modułach odpowiedzialnych za pobieranie newsów, sentymentu czy integrację z GitHub zastąp `requests.get` wywołaniami `async with httpx.AsyncClient() as client:` lub analogicznymi w `aiohttp`.  Jeśli wysyłasz wiele zapytań, umieść je w liście i uruchom równocześnie za pomocą `asyncio.gather`.
   - W pliku `main.py` lub `ai_engine.py` utwórz pętlę asynchroniczną (`asyncio.run(...)`) i wywołuj w niej funkcje asynchroniczne.  Jeśli pętla główna pozostaje synchroniczna, oddeleguj asynchroniczne zadania do osobnych funkcji z `await`.

4. **Centralny moduł ryzyka:**
   - Edytuj `risk/risk_manager.py`, aby zaimplementować dataklasę `RiskConfig` z parametrami takimi jak `max_risk_per_trade`, `min_confidence`, `min_rr`, `max_open_positions`.  W metodzie `validate` oblicz wielkość pozycji i sprawdź wszystkie warunki przed wysłaniem zlecenia.  Oprzyj się na sprawdzonych zasadach pre‑trade risk checks【554396219266516†L30-L34】.
   - Usuń zduplikowaną logikę zarządzania ryzykiem z innych plików i korzystaj zawsze z `risk_manager.validate(...)` w miejscu wysyłania zlecenia.

5. **Testy i weryfikacja:**
   - Upewnij się, że testy jednostkowe przechodzą, a nowe testy na poprawność wskaźników i risk managera są dodane.  Profiluj czas wykonywania pętli, aby potwierdzić poprawę wydajności.

## Zawartość folderu `complete_package`

W folderze `complete_package` znajdują się:

| Plik                              | Opis                                                                |
|-----------------------------------|---------------------------------------------------------------------|
| `alpha_data_scraper_ai-main-optimized.zip` | Zoptymalizowana wersja projektu do rozpakowania lokalnie. |
| `PORADNIK.md`                    | Niniejszy dokument z instrukcjami i listą zadań.                |

## Jak korzystać z paczki i dodać ją do Google Drive

1. Pobierz archiwum ZIP `complete_package.zip` i rozpakuj je na swoim komputerze.  W środku znajdziesz zoptymalizowane repozytorium oraz plik **PORADNIK.md** z opisem kroków i zadań.
2. Otwórz plik `PORADNIK.md` w edytorze tekstu lub przeglądarce Markdown, aby uzyskać szczegółowe wytyczne dotyczące implementacji.
3. Aby dodać paczkę na Google Drive, zaloguj się na swoje konto Google, otwórz Drive i wciśnij „Nowy” → „Prześlij plik”.  Wskaż plik `complete_package.zip`.  Po przesłaniu możesz także rozpakować zawartość w środowisku Google Drive (np. poprzez integrację zip) lub pozostawić spakowane.

Jeśli w przyszłości wtyczka do Google Drive umożliwi bezpośrednie przesyłanie plików, można będzie zautomatyzować powyższy krok poprzez API.  Aktualnie wtyczka w tym środowisku udostępnia jedynie odczyt danych z Drive.

