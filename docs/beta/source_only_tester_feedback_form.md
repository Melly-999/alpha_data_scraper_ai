# Source-Only Tester Feedback Form

> Use this form to report your observations after reviewing MellyTrade locally.
> This is not live trading. No generated artifacts (EXE, ZIP, MSI) are shared.
> Do not include broker credentials, API keys, account IDs, or secrets in your feedback.

---

## Tester info

```
Name / handle:
OS version (e.g. Windows 11 22H2):
Python version (e.g. 3.11.x):
Node version (e.g. 18.x):
Did setup complete successfully? yes / no / partial
```

---

## Setup feedback

For each step, record: pass / fail / skip (with notes if fail).

```
Clone success:
  Result: pass / fail
  Notes:

Dependency install success (pip install -r requirements.txt):
  Result: pass / fail
  Notes:

Safety validation command result (py -3.11 scripts/validate_safety_config.py):
  Result: OVERALL: PASS / FAIL
  Output (paste relevant lines):

Build command result (.\scripts\build_desktop_launcher.ps1 -Build):
  Result: pass / fail / skipped
  Notes:

Launcher run result (double-click MellyTrade Terminal or .\dist\MellyTradeLauncher.exe):
  Result: pass / fail / skipped
  Notes:

Shortcut helper result (.\scripts\create_desktop_shortcut.ps1):
  Result: pass / fail / skipped
  Notes:
```

---

## Safety checks

Answer each question:

```
Was the safety banner visible at launch?
  yes / no / unsure
  Notes:

Did you see autotrade=false in the safety banner?
  yes / no / unsure

Did you see dry_run=true in the safety banner?
  yes / no / unsure

Did you see read_only=true in the safety banner?
  yes / no / unsure

Did you see live_orders_blocked=true in the safety banner?
  yes / no / unsure

Did the application ask for broker credentials at any point?
  yes / no
  If yes — describe what you saw:

Did the application show any order or execution controls?
(Buy button, Sell button, Execute button, Place Order button, Connect Broker button)
  yes / no
  If yes — describe what you saw:

Did anything in the interface look like investment advice?
(e.g. "this stock will rise", "guaranteed return", "buy now for profit")
  yes / no
  If yes — describe what you saw:

Did the application connect to any address outside localhost?
  yes / no / unknown
  Notes:
```

---

## Bugs

For each issue found, copy this block:

```
--- Bug report ---
Area: (setup / scanner / risk / broker / audit-rail / shortcut / safety-banner / other)
Severity: P0 safety blocker / P1 setup blocker / P2 confusing UX / P3 polish
Summary:
Steps to reproduce:
  1.
  2.
  3.
Expected:
Actual:
Screenshot attached: yes / no
Console errors (paste relevant lines):
Notes:
--- End bug report ---
```

### Severity guide

- **P0 — Safety blocker**: Stop rollout immediately. Examples: execution control visible, app asks for broker credentials, investment-advice copy, guaranteed-profit claim, safety banner missing.
- **P1 — Setup blocker**: Fix before inviting more testers. Examples: launcher does not start, validation fails, build fails with no workaround.
- **P2 — Confusing UX**: Collect and batch. Examples: unclear label, confusing safety state, scanner explanation hard to follow.
- **P3 — Polish**: Backlog. Examples: spacing issue, minor wording tweak, colour contrast.

---

## Overall verdict

```
Verdict: PASS / BLOCKED
  PASS   — safe enough to consider inviting a second tester
  BLOCKED — P0 or P1 issues must be resolved first

Summary of key observations:

Recommended next step:
```

---

## Notes

```
Any other observations:

Docs that were confusing or missing:

Suggestions:
```

---

*MellyTrade BETA-ACCESS-001 - Source-Only Tester Feedback Form - do not include secrets or credentials in feedback.*
