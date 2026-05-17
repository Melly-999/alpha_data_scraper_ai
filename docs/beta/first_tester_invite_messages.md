# First Tester Invite Messages

> These are ready-to-send invite messages for trusted closed beta testers.
> Customise with the tester's name and any relevant context before sending.
> Do not include secrets, API keys, broker credentials, or account data.

---

## Short invite

```
Hey [Name],

I'm testing MellyTrade Closed Beta Demo v0.1 — a read-only AI trading research terminal.

It does not place trades, does not connect to live broker execution, and is not investment advice.

I'm looking for feedback on:
- whether the UI is clear
- whether the safety labels are obvious
- whether scanner explanations make sense
- whether anything looks confusing, risky, or broken

Release:
https://github.com/Melly-999/alpha_data_scraper_ai/releases/tag/v0.1-beta

Disclaimer: docs/product/closed_beta_disclaimer.md
Limitations: docs/product/closed_beta_limitations.md
```

---

## Longer invite

```
Hey [Name],

I've published a closed beta demo release of MellyTrade v0.1.

MellyTrade is a read-only, dry-run AI trading research terminal. The goal is to review
the product workflow, dashboard clarity, scanner explanations, risk posture, audit rail,
and broker safe-disconnected state.

Important:
- it is read-only
- it is dry-run only
- it does not place orders
- it does not connect to live broker execution
- it is not investment advice
- it does not guarantee profits

What I'd like you to check:
- can you understand what each screen is showing?
- are READ ONLY / DRY RUN / LIVE ORDERS BLOCKED labels visible?
- do scanner cards feel understandable?
- does anything look like it could execute a trade?
- do any labels sound too risky or too much like advice?
- does anything break visually?

Release:
https://github.com/Melly-999/alpha_data_scraper_ai/releases/tag/v0.1-beta

Please do not enter broker credentials, account data, API keys, or private financial
data anywhere in the terminal.
```

---

## Message for technical tester

```
Hey [Name],

I'm looking for a technical review of MellyTrade Closed Beta Demo v0.1.

Scope:
- local read-only demo
- no live trading
- no broker execution
- no mutation controls
- advisory scanner only
- risk posture locked to dry-run/read-only

Please check:
- local startup clarity
- browser UI smoke checklist
- console errors
- confusing UX
- unsafe wording
- any visible execution-like controls

Release:
https://github.com/Melly-999/alpha_data_scraper_ai/releases/tag/v0.1-beta

Useful docs:
- docs/beta/beta_tester_quick_start.md
- docs/product/closed_beta_disclaimer.md
- docs/product/closed_beta_limitations.md
- docs/product/closed_beta_bug_report_template.md
```

---

## Follow-up message after tester has access

```
Hey [Name],

Thanks for agreeing to check the MellyTrade closed beta demo.

Before you start:
- please read the disclaimer: docs/product/closed_beta_disclaimer.md
- please read the limitations: docs/product/closed_beta_limitations.md
- please do not enter any broker credentials, account data, or API keys

When you're ready to give feedback, please use this structure:

  Area:
  Severity:
  Summary:
  Expected:
  Actual:
  Safety labels visible: yes/no
  Screenshot attached: yes/no
  Console errors:
  Notes:

If you see anything that looks like it could place a real trade, submit an order,
or connect a live broker — please flag it immediately as a P0 safety issue.

Thank you for your time.
```

---

## Message after feedback received

```
Hey [Name],

Thanks for checking MellyTrade Closed Beta Demo v0.1 and for your feedback.

Please send your notes using this structure (or just freeform is fine too):

  Tester:
  Date:
  Version/tag: v0.1-beta
  Area:
  Severity:
  Summary:
  Expected:
  Actual:
  Safety labels visible:
  Screenshot attached:
  Console errors:
  Notes:

Please do not include secrets, account IDs, broker credentials, API keys, or private
financial data in your feedback.

Thanks again — every observation helps.
```

---

## Safety reminder (add to any message)

```
IMPORTANT:
- MellyTrade is not investment advice.
- It does not place trades.
- It does not connect to live broker execution.
- Please do not enter broker credentials or account data.
- All outputs are for educational and observational purposes only.
```

---

*MellyTrade Closed Beta Demo v0.1 — First tester invite messages*
