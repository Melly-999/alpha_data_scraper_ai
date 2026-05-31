# Melly Pet Master Plan

## Purpose

Melly Pet is the friendly mascot and read-only assistant for MellyTrade. It
represents safety, visibility, demo-readiness, and operator support. It must
never imply autonomous trading, broker execution, or guaranteed profit.

## Visual Direction

- pixel-art orange mascot
- black broker suit / market-maker vibe
- friendly, simple face
- dark institutional background
- amber/orange accents
- professional but playful
- readable as an app icon
- readable as a small favicon / head-only variant
- full-body variant for splash / README / demo screens

The character should read clearly as "MellyTrade / Melly Pet" and must not
include any imagery implying live order execution or autonomous trading.

## Usage Roadmap

| Task | Description | Status | Risk |
|---|---|---|---|
| MELLY-PET-001 | Brand/spec/icon requirements docs | Planned | Low |
| MELLY-PET-002 | Display-only frontend assistant card | Planned | Low-Med |
| MELLY-PET-003 | Favicon/app icon asset pipeline | Planned | Low-Med |
| MELLY-PET-004 | EXE icon packaging integration | Later | Med |
| MELLY-PET-005 | Splash/empty-state integration | Later | Low-Med |

## Current State

Currently Melly Pet is planned as a brand / spec / workflow mascot. It is **not
yet** physically integrated as:

- an EXE icon
- a favicon
- a frontend assistant card
- a packaged desktop app icon

## Future UI Assistant

A future display-only component (no forms, no API calls required):

**Melly Pet card copy**

- **Title:** Melly Pet
- **Subtitle:** Read-only assistant
- **Body:** "Melly Pet helps track repo status, safety checks, demo readiness,
  and operator tasks. It never places orders or enables live trading."
- **Badges:** `READ ONLY` · `DRY RUN` · `LIVE ORDERS BLOCKED` ·
  `HUMAN REVIEW REQUIRED`
- **Footer:** "No broker execution · No live orders"

**Rules:**

- display-only
- no forms
- no API calls required
- no trading controls
- no broker credentials
- no buy/sell/execute actions

## Icon / EXE Plan

- the source image should be stored manually later as
  `assets/branding/source/melly_pet_source.png`
- generated icon assets should **not** be committed unless explicitly approved
- required icon sizes: 16x16, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256,
  512x512, 1024x1024
- a Windows EXE requires an `.ico` later, depending on the packaging tool
  (Electron / Tauri / PyInstaller / Nuitka / other)
- do not hardcode local user paths
- do not commit generated `.exe` files

## Safety Copy

**Allowed:**

- `READ ONLY`
- `DRY RUN`
- `LIVE ORDERS BLOCKED`
- `HUMAN REVIEW REQUIRED`
- `PAPER ONLY`
- `SANDBOX PREVIEW`

**Forbidden:**

- guaranteed profit
- live execution enabled
- click to trade
- automatic trading active
- broker connected for live orders
- no-risk strategy

## Do / Don't

**Do:**

- use Melly Pet for safety explanations
- use it in empty / degraded states
- use it in demo onboarding
- use it in repo/docs workflow commands

**Don't:**

- put it near execution controls
- imply trading autonomy
- use it in profit claims
- use it with broker credentials
- use it as financial-advice branding
