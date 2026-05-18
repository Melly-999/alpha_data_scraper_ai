# Codzienny workflow OpenClaw — Discord / Telefon

> Wszystkie przykłady zakładają korzystanie z **Discorda na telefonie** (Discord mobile app).  
> Wszystkie działania są **wyłącznie read-only i advisory**.  
> OpenClaw nie wykonuje żadnych zleceń ani nie modyfikuje konfiguracji runtime.

---

## Przykładowe prompty na Discord (telefon)

### Status i safety

```
Discord / telefon:
Sprawdź status MellyTrade i powiedz czy safety jest nienaruszone.
```

Oczekiwana odpowiedź (format kompaktowy na telefon):

```
MellyTrade Status

Safety:
✅ autotrade=false
✅ dry_run=true
✅ live_orders_blocked=true
✅ max risk <=1%

Repo:
✅ clean  (branch: feature/..., 0 uncommitted)

PR:
- #88 ready for review

Signals:
- XAUUSD WATCH 78%, advisory only
- EURUSD NO_TRADE

Next:
1. Review PR #88
2. Run safety validation
3. Do not touch execution routes
```

---

### Logi i błędy

```
Discord / telefon:
Na Discordzie pokaż ostatnie błędy z logów i zaproponuj bezpieczny następny krok.
```

Oczekiwana odpowiedź:

```
Logi (ostatnie 200 linii, trading-bot)

Błędy:
⚠️  [12:03] ConnectionTimeout — external data feed
⚠️  [12:07] Retry #2 — feed reconnect

Ostrzeżenia:
• [12:10] Scanner: low data confidence on GBPUSD

Bezpieczny następny krok:
→ Sprawdź połączenie sieciowe lub uruchom ponownie container.
→ Nie dotykaj konfiguracji autotrade ani dry_run.
→ Zrób PR z notatką o timeout jeśli to pattern.
```

---

### Walidacja safety

```
Discord / telefon:
Uruchom walidację safety i streść wynik.
```

Oczekiwana odpowiedź:

```
Safety Validation

python scripts/validate_safety_config.py

✅ autotrade.enabled = false
✅ dry_run = true
✅ live_orders_blocked = true
✅ max_risk <= 1%
✅ no forbidden execution segments (16 route files)

WYNIK: PASS
```

---

### Przegląd PR-ów

```
Discord / telefon:
Sprawdź ostatnie PR-y i powiedz, który jest gotowy do review.
```

Oczekiwana odpowiedź:

```
Otwarte PR-y

#88  docs(openclaw): add Discord-first operator setup
     Status: ready for review, CI green, no conflicts

#85  feature/supa-012-audit-cleanup
     Status: WIP, awaiting tests

#81  fix/scanner-confidence-threshold
     Status: approved, merge when ready

Rekomendacja: zacznij od #88 (docs-only, brak ryzyka runtime).
```

---

### Raport dnia

```
Discord / telefon:
Zrób raport dnia: PR-y, testy, sygnały, błędy, następne 3 taski.
```

Oczekiwana odpowiedź:

```
Raport dnia — 2026-05-18

PR-y:
- #88 ready for review (docs)
- #85 WIP
- #81 approved

Testy:
✅ 47 passed, 0 failed  (pytest tests/app -q)

Sygnały (advisory only):
- XAUUSD  WATCH  78%
- EURUSD  NO_TRADE
- GBPUSD  WATCH  61%  (low confidence — skip)

Błędy:
⚠️  ConnectionTimeout x2 (external feed)

Następne 3 taski:
1. Review i merge #88
2. Zbadaj timeout w logach, dodaj ticket
3. Uruchom smoke test po merge
```

---

### Wysyłanie raportu na kanał

```
Discord / telefon:
Wyślij dzienny raport na #mellytrade-reports.
```

OpenClaw wygeneruje raport i opublikuje go w `#mellytrade-reports` jako wiadomość.

---

### Alert warunkowy

```
Discord / telefon:
Daj alert tylko jeśli safety validation fail albo scanner pokaże high-confidence advisory signal.
```

OpenClaw będzie cicho, dopóki:
- `validate_safety_config.py` nie zwróci FAIL, lub
- scanner nie zgłosi sygnału z confidence >= progu (np. 80%)

W przypadku alertu format:

```
⚠️ ALERT #mellytrade-alerts

Typ: Safety Validation FAIL
Czas: 2026-05-18 14:22
Szczegóły: [FAIL] autotrade.enabled = true  ← VIOLATION

Akcja: Natychmiast sprawdź config.json. Nie puszczaj żadnych PR-ów.
Human review required.
```

---

## Czego OpenClaw nie może robić

| Zabronione | Dlaczego |
|---|---|
| Włączyć live trading | Naruszenie safety contract |
| Zmienić `autotrade.enabled` na `true` | Naruszenie safety contract |
| Ustawić `dry_run=false` | Naruszenie safety contract |
| Wyłączyć `live_orders_blocked` | Naruszenie safety contract |
| Odczytać `.env` lub zmienne środowiskowe | Ryzyko wycieku sekretów |
| Wydrukować tokeny, credentiale, account IDs | Ryzyko wycieku |
| Pushować bezpośrednio do `main` | Naruszenie procesu review |
| Force push | Ryzyko utraty historii |
| Modyfikować backend routes, broker modules | Out of scope |
| Składać, modyfikować, anulować zlecenia | Absolutnie zabronione |
| Modyfikować workflow YAML, Docker runtime | Out of scope |
| Zmieniać risk policy, profile, config.json | Out of scope |

---

## Najlepszy workflow z Codex / Claude Code / OpenCode

| Narzędzie | Rola |
|---|---|
| **OpenClaw** | Discord/mobile read-only operator i reporter — status, logi, sygnały, raporty |
| **Claude Code** | Planner i reviewer — projektowanie, code review, analiza architektury |
| **Codex** | Executor na scoped branch — implementacja zadań w izolacji |
| **OpenCode** | Lokalny helper do inspectowania i pisania kodu (jeśli używany) |
| **GitHub PR** | Gate review/merge — każda zmiana runtime przechodzi przez PR |

Przykładowy cykl:

```
1. OpenClaw (Discord/telefon): /daily-report → widzisz co jest do zrobienia
2. Claude Code: zaplanuj i zrecenzuj podejście
3. Codex: implementuj na feature branch
4. OpenClaw: /prs → sprawdź czy CI jest zielone
5. Claude Code: code review na PR
6. Merge przez GitHub PR gate
```

---

## Najlepsze kanały Discord

| Kanał | Użycie |
|---|---|
| `#mellytrade-ops` | Status cockpit — codzienny driver z telefonu, `/status`, `/safety`, `/validate` |
| `#mellytrade-alerts` | Alerty safety, CI failures, advisory signal alerts (wysoki confidence) |
| `#mellytrade-dev` | PR-y, walidacja, prompty dla Codex/Claude Code |
| `#mellytrade-reports` | Dzienne i tygodniowe podsumowania, scanner preview |

---

## Related Files

- [`docs/openclaw/README.md`](README.md) — architektura i safety contract
- [`docs/openclaw/INSTALL_CHECKLIST.md`](INSTALL_CHECKLIST.md) — instalacja krok po kroku
- [`docs/openclaw/SECURITY_MODEL.md`](SECURITY_MODEL.md) — model bezpieczeństwa
- [`skills/mellytrade-operator/SKILL.md`](../../skills/mellytrade-operator/SKILL.md) — definicja skilla
