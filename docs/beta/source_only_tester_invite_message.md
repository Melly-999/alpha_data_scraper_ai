# Source-Only Tester Invite Message

> Ready-to-send templates for source-only beta testers.
> Customise with the tester's name before sending.
> Do not include secrets, API keys, broker credentials, or account data.
> Do not send a pre-built EXE, ZIP, or installer.

---

## Short invite

```
Hey [Name],

I'd like to invite you to test MellyTrade as a source-only beta tester.

What this is:
- a local read-only dry-run demo
- an AI trading research terminal — advisory output only
- not live trading
- not investment advice
- no broker execution

What you will receive:
- read-only GitHub repository access
- setup instructions
- a safe first-run guide

What you will NOT receive:
- a pre-built EXE or installer
- a ZIP bundle
- any broker credentials or secrets

You will clone the repo and build the local launcher yourself
(instructions are provided — it's a single PowerShell command).

Please do not enter broker credentials, API keys, account IDs,
or any secrets into the application. The demo does not require them.

If the safety banner at launch is missing, or if you see any order
or execution controls, please stop immediately and let me know.

Let me know if you are interested.
```

---

## Technical invite

```
Hey [Name],

I'd like to invite you to review MellyTrade as a source-only beta tester.

Scope:
- local read-only dry-run demo (source access only — no pre-built EXE)
- advisory AI scanner terminal
- no live trading, no broker execution, no mutation controls
- safety posture: autotrade=false, dry_run=true, read_only=true, live_orders_blocked=true

You will receive read-only GitHub repository access.
No pre-built EXE, ZIP bundle, or installer is shared at this stage.

Setup overview (full instructions in the source access guide):

1. Clone the repository (read-only HTTPS URL)
2. Run: py -3.11 scripts/validate_safety_config.py  (expected: OVERALL: PASS)
3. Build local launcher: .\scripts\build_desktop_launcher.ps1 -Build
4. Optionally create desktop shortcut: .\scripts\create_desktop_shortcut.ps1
5. Launch and confirm safety banner is visible

Please verify:
- safety banner is printed at launch (autotrade=false, dry_run=true, read_only=true, live_orders_blocked=true)
- no order buttons, execution buttons, or broker connection controls are visible
- no broker credential inputs are shown
- scanner output is advisory only

Please report:
- anything that looks like it could place a real order
- anything that requests broker credentials, API keys, or secrets
- anything that sounds like investment advice or profit guarantees
- any setup errors or broken UI

Please do not enter broker credentials, MT5 login details, API keys, account IDs,
or Supabase keys anywhere in the application. The demo does not require any of these.

Let me know if you are interested and I will share repository access.
```

---

## Follow-up after access granted

```
Hey [Name],

Thank you for agreeing to review MellyTrade.

I have granted read-only GitHub repository access.
You can clone the repository using the HTTPS URL from the GitHub invite.

Please start with the source access guide:
  docs/product/beta_tester_source_access_guide.md   [included in repo]

Other useful docs once you have cloned:
  docs/product/beta_tester_desktop_launcher_quick_start.md   [launcher quick start]
  docs/product/beta_tester_desktop_distribution_notes.md     [distribution notes]

Feedback form:
  docs/beta/source_only_tester_feedback_form.md   [use this to report findings]

Important reminders:
- This is a local read-only demo — not live trading.
- No order execution. No broker execution.
- No guaranteed profit claims are made by this application.
- Please do not enter broker credentials, MT5 login details, API keys, account IDs,
  or Supabase keys anywhere in the application.
- If the safety banner is missing at launch — stop and let me know.
- If any order or execution control appears — stop and let me know.
- If the app asks for broker credentials — stop and let me know.

Thank you for your time. Every observation helps.
```

---

## Safety reminder (add to any message)

```
IMPORTANT:
- MellyTrade is not investment advice.
- It does not place trades or connect to live broker execution.
- Do not enter broker credentials, account data, or API keys.
- All outputs are advisory and observational only.
- If the safety banner is missing or order controls appear — stop and report immediately.
```

---

*MellyTrade BETA-ACCESS-001 - Source-Only Tester Invite Message - not to be sent automatically.*
