# MellyTrade Open Design Tab Expansion Concepts

## Purpose

This document defines the next Open Design concept package for the MellyTrade institutional terminal. It expands the current terminal direction into three read-only tabs:

1. Positions
2. Trade Blotter
3. Backtest Lab

The concepts must stay inside the existing MellyTrade safety posture:

- read-only only
- no live trading
- no order placement controls
- no broker execution methods
- no Buy/Sell/Execute buttons
- no POST/PUT/PATCH/DELETE trading actions
- no change to `autotrade=false`
- no change to `dry_run=true`
- preserve `live_orders_blocked=true`
- max risk remains `<= 1%`

The goal is not to change runtime code. The goal is to generate a design concept package that can guide future UI implementation in Open Design and the terminal shell.

## Existing Direction To Preserve

The current MellyTrade terminal already reads as an institutional dark workstation:

- dense, high-information layouts
- amber/green/red status language
- audit-first framing
- read-only broker cards
- degraded-first / fallback-aware states
- compact tables and diagnostic surfaces

The new concepts should extend this language, not replace it.

## Tab Summary

### 1) Positions

The Positions tab should present the current book in a clear audit layout:

- open positions table
- closed today table
- summary KPIs for float PnL, realized PnL, open count, and exposure
- clean numeric alignment and strong status visibility
- read-only, display-only presentation

### 2) Trade Blotter

The Trade Blotter tab should act as a compact execution audit surface:

- order and execution list
- filters such as All / Filled / Pending
- compact readable table
- source, status, and direction visibility
- read-only, display-only presentation

### 3) Backtest Lab

The Backtest Lab tab should feel like a controlled research workspace:

- strategy simulation and historical performance section
- configuration card
- saved runs list
- KPI cards for win rate, profit factor, total trades, avg win
- equity curve panel
- drawdown panel
- read-only, display-only presentation

## Three Concept Directions

Each tab should be explored in three directions. The directions should stay consistent across the suite so the user can compare the same information architecture in different tones.

### Version A: Dense Institutional / Operator-Heavy

Best for power users and rapid monitoring.

- maximum information density
- tighter spacing
- stronger table hierarchy
- more visible row labels and state chips
- engineering-audit feel
- minimal decorative treatment

Use this when the priority is throughput, scan speed, and operational completeness.

### Version B: Cleaner Executive / Premium Dashboard

Best for leadership review or high-level oversight.

- slightly more breathing room
- refined spacing and typography
- premium card composition
- clearer KPI emphasis
- fewer competing visual elements
- calmer, more polished hierarchy

Use this when the priority is clarity, confidence, and a premium fintech feel.

### Version C: Mobile-Aware / Touch-Friendly / iPad-Friendly

Best for tablet and small-screen review.

- stacked card layouts
- larger touch targets
- simplified tables with priority columns
- scroll-friendly sections
- sticky status chips where appropriate
- reduced density without losing the audit tone

Use this when the priority is field usability, tablet access, and responsive readability.

## Positions Tab Concept Breakdown

### Core Layout

- top KPI strip
- open positions table
- closed today table
- compact side summary or status column if space allows
- no trade actions

### Recommended KPIs

- Float PnL
- Realized PnL
- Open Count
- Net Exposure
- Long / Short Split
- Max Risk Used

### Open Positions Table

Suggested columns:

- Symbol
- Direction
- Size
- Entry
- Mark
- Float PnL
- Stop
- Target
- Age
- Status

Design notes:

- numeric columns should right-align
- positive and negative values should use clear color semantics
- direction should be visible through both label and color
- status chips should be high-contrast and unambiguous
- table should remain legible when dense

### Closed Today Table

Suggested columns:

- Symbol
- Direction
- Entry
- Exit
- Realized PnL
- R Multiple
- Duration
- Close Reason

Design notes:

- separate it visually from the open book
- close reason should be a readable audit field, not a tooltip-only detail
- keep the table compact but not cramped

### Version Guidance

- A: two stacked tables with dense KPI strip
- B: KPI cards first, then a balanced two-column layout
- C: stacked panels with simplified columns and strong typography

## Trade Blotter Tab Concept Breakdown

### Core Layout

- header with time range context
- filter strip: All / Filled / Pending / Rejected / Cancelled if needed
- compact blotter table
- optional event summary or source legend

### Recommended KPIs

- Total Orders
- Filled
- Pending
- Rejected
- Average Fill Delay
- Sources Active

### Blotter Table

Suggested columns:

- Time
- Symbol
- Direction
- Type
- Source
- Status
- Price
- Qty
- Slippage
- Notes

Design notes:

- source should be explicit because the blotter is an audit tool
- status should be visually strong and consistent
- direction should be obvious at a glance
- notes should be short and readable
- avoid any interaction that implies order creation or modification

### Filters

The filters should behave as display-only state selectors in the concept:

- All
- Filled
- Pending
- Rejected
- Cancelled

If the concept includes segmented controls or pills, they should read as audit filters, not execution controls.

### Version Guidance

- A: dense blotter with fixed headers and many rows per viewport
- B: premium audit table with a lighter top bar and cleaner chip system
- C: touch-friendly stacked rows or cardized blotter entries with essential fields only

## Backtest Lab Tab Concept Breakdown

### Core Layout

- configuration card
- saved runs list
- KPI cards
- equity curve panel
- drawdown panel
- strategy notes or parameter summary

### Recommended KPIs

- Win Rate
- Profit Factor
- Total Trades
- Avg Win
- Avg Loss
- Max Drawdown
- Sharpe or similar research metric if space allows

### Configuration Card

Suggested fields:

- Strategy name
- Symbol universe
- Timeframe
- Date range
- Risk per trade
- Slippage assumption
- Commission assumption
- Warmup period

Design notes:

- keep it read-only if the run is historical
- show the configuration in a clean audit card rather than a form
- make assumptions visible so the user can trust the backtest

### Saved Runs

Suggested fields:

- Run name
- Date
- Strategy
- Timeframe
- Result summary
- Status badge

Design notes:

- allow quick scanning of prior experiments
- emphasize outcome and context
- keep it as a gallery or compact list depending on version

### Charts

Equity curve:

- primary performance chart
- should feel analytical, not promotional
- line emphasis with subtle volume or period markers if useful

Drawdown panel:

- should be legible and separate from the equity curve
- use distinct negative-space treatment
- emphasize recovery and depth

### Version Guidance

- A: dense research desk with full metric surface and smaller charts
- B: premium strategy lab with larger chart panels and clean metric cards
- C: tablet-friendly stacked cards with one chart at a time and swappable sections

## Melly PET Concept

Melly PET should feel like a branded micro-assistant, not a mascot that hijacks the UI.

### Behavior Concept

Use subtle, low-frequency motion only:

- idle float
- soft pulse
- blink
- hover response
- gentle wave

The motion should suggest attentiveness and confirmation, not playfulness.

### Placement Ideas

- lower-right assistant bubble
- onboarding tip helper near the command surface
- empty-state helper for sparse tables
- loading companion during data refresh
- optional status hint inside the terminal shell footer or side rail

### Tone

- helpful
- premium
- calm
- concise
- not childish
- not distracting

### Visual Language

- simplified silhouette or emblem
- line-based or geometric treatment
- amber accent with restrained secondary color use
- should still read clearly at small sizes

## Desktop App / EXE Icon Concept

The icon concept should combine Melly PET with the MellyTrade brand in a professional fintech way.

### Recommended Icon Direction

- use a simplified PET silhouette integrated with a shield, chart line, or terminal frame
- prefer strong geometry and clean negative space
- keep the mark readable at small sizes
- avoid cartoon traits, exaggerated eyes, or playful shapes
- use a dark base with a restrained amber highlight

### Suggested Output Variants

- app icon for desktop shell
- favicon or small launcher mark
- monochrome fallback for system menus
- squared icon with centered PET emblem

## UI / UX Improvement Recommendations

- make all high-value metrics visually scannable in under three seconds
- use consistent status chip language across all tabs
- keep read-only labels and safety signals visible in the header or footer
- use right-aligned numeric columns and fixed-width numerals where possible
- preserve the institutional dark palette but add clearer hierarchy
- separate summary, detail, and audit areas with stronger panel structure
- ensure tablet layouts collapse without losing the audit-first feel
- treat empty states as informative, not decorative
- preserve degraded / fallback states in all concept variants

## Next Recommended Implementation Steps

1. Generate the three tabs as a suite in Open Design, starting with a shared shell and shared status language.
2. Compare Version A, B, and C side by side before selecting a direction per tab.
3. Prototype Positions first if the goal is immediate operational value.
4. Prototype Trade Blotter first if the goal is audit and execution traceability.
5. Prototype Backtest Lab first if the goal is research communication and performance storytelling.
6. Only after selecting a direction, translate the chosen concept into frontend components.

## Handoff Notes For Open Design

When generating concepts, keep the following constant:

- MellyTrade institutional terminal identity
- read-only / advisory-only framing
- safety-first state visibility
- no execution or order placement UI
- no live trading cues
- no broker action affordances

The output should feel like a professional trading workstation that could sit inside a serious operations room, not a retail dashboard.

