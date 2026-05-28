# MellyTrade 3-Tab Prototype Evidence

This folder is a docs-only prototype evidence package generated from the Open Design MellyTrade 3-tab concept suite.

## What this is

- A static prototype evidence bundle for the MellyTrade terminal concept suite.
- Covers three read-only tabs: Positions, Trade Blotter, and Backtest Lab.
- Includes three visual directions for each tab: A, B, and C.
- Includes an icon concept page for the Melly PET brand mark.

## What this is not

- Not production frontend code.
- Not backend runtime code.
- Not a trading control surface.
- Not a production execution interface.
- Not a broker execution UI.

## Safety posture

- Read-only.
- Display-only.
- Advisory-only.
- No execution controls.
- No order placement controls.
- No active trading CTAs.
- No execution cues.
- No broker connection or execution routes.

## How to open locally

Option 1:

```powershell
Start-Process .\index.html
```

Option 2:

```powershell
python -m http.server 7788
```

Then open `http://localhost:7788/`.

## Review checklist

- Check the layout hierarchy for each tab.
- Compare Versions A, B, and C side by side.
- Verify all copy remains read-only and audit-focused.
- Confirm Melly PET stays subtle and premium.
- Confirm the icon concept stays clean and fintech-oriented.
- Confirm no execution controls, order buttons, or execution language appear.

## Recommended next step

Choose the approved visual patterns first, then port only those patterns into the frontend runtime.
