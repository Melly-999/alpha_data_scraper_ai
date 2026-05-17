# Claude Design Theme Handoff

## Source

Generated from Claude Design export stored outside the repo:

```
C:\AI\MellyTrade_Workspace\03_Docs\ClaudeDesign\MellyTrade_Closed_Beta_Demo_UI_Pack
```

Raw export files are intentionally not committed.

## Purpose

Document the MellyTrade theme strategy generated in Claude Design.

---

## Theme strategy

**Two themes, one severity ramp.** Amber is the product. Navy is an opt-in palette swap. Crimson is *not* a full theme — it's a single token swap on the danger-severity color, used wherever risk actually lives.

### Amber — default product theme

Amber is the default MellyTrade theme.

Use for:
- main terminal identity
- institutional research feel
- default demo screenshots
- closed beta UI
- README/portfolio screenshots

Positioning:
- premium
- fintech
- institutional
- terminal-like
- safe/read-only research

**Palette:**

| Token | HEX | Role |
|---|---|---|
| `--bg` | `#0A0B0D` | Page background |
| `--bg-1` | `#0D1014` | Sidebar / topbar |
| `--surface` | `#11141A` | Cards |
| `--surface-2` | `#161A22` | Inset rows, locked fields |
| `--surface-3` | `#1B2029` | Tracks, wells |
| `--surface-hi` | `#20262F` | Row hover |
| `--border-1` | `#1C2129` | Card / row edge |
| `--border-2` | `#262D38` | Inputs |
| `--border-3` | `#353D4A` | Hover / focus |
| `--text-1` | `#E8ECF1` | Primary |
| `--text-2` | `#98A1AE` | Secondary |
| `--text-3` | `#677183` | Muted / labels |
| `--accent` | `#D4A24A` | Institutional gold |
| `--accent-hi` | `#E8B85C` | Hover / glow |
| `--accent-lo` | `#8A6B30` | Gradient base |
| `--sev-success` | `#4ADE80` | Posture confirmed, price up |
| `--sev-info` | `#60A5FA` | Routine events |
| `--sev-warning` | `#F5B14C` | Attention, SAFE-DISCONNECTED |
| `--sev-degraded` | `#F87171` | Degraded, NO_TRADE, price down |
| `--pos` | `#4ADE80` | Positive delta |
| `--neg` | `#F87171` | Negative delta |

---

### Navy — optional premium/client-friendly theme

Navy is an optional palette swap.

Use for:
- calmer long-session experience
- bank/enterprise feeling
- alternative screenshots
- future user preference

Activated via `[data-theme="navy"]` on `<html>`. Cooler register: navy-black surfaces, institutional blue accent. Identical component shapes and severity meanings — palette swap only. Good for boardroom screenshots and long sessions.

Rules:
- Navy must not change product semantics.
- Navy must not change copy.
- Navy must not add/remove functionality.
- Navy is color-only.

**Palette (overrides only — replaces surfaces and accent):**

| Token | HEX | Role |
|---|---|---|
| `--bg` | `#060912` | Page background |
| `--bg-1` | `#0A0F1C` | Sidebar / topbar |
| `--surface` | `#0F1626` | Cards |
| `--surface-2` | `#141D31` | Inset rows |
| `--surface-3` | `#1A2440` | Tracks, wells |
| `--border-1` | `#1B2543` | Card / row edge |
| `--border-2` | `#283356` | Inputs |
| `--border-3` | `#38446B` | Hover / focus |
| `--text-1` | `#E6ECF5` | Primary |
| `--text-2` | `#92A0BC` | Secondary |
| `--text-3` | `#5F6E8E` | Muted / labels |
| `--accent` | `#4A90D9` | Institutional blue |
| `--accent-hi` | `#6BB3F0` | Hover / glow |
| `--accent-lo` | `#2A5F94` | Gradient base |

*Severity ramp untouched — green/blue/amber/red carry through from Amber.*

---

### Crimson — severity/risk only

Crimson is **not** a full app theme.

Use only for:
- degraded critical states
- blocked states
- NO_TRADE chip
- risk warnings
- danger alerts
- live-orders-blocked severity styling

Activated via `[data-severity="crimson"]` on `<html>`. Orthogonal to `data-theme` — can compose with Amber or Navy underneath.

Rules:
- Do not make the whole app red.
- Do not use Crimson as the default UI.
- Crimson should be rare and meaningful.
- Crimson should never become the normal card surface or normal text accent.
- Crimson `#DC2626` is reserved for severity/risk surfaces only. It must not appear in `--accent`, `--bg-*`, `--border-*`, or any text color.

**Overrides (danger color only):**

| Token | Default | Crimson override |
|---|---|---|
| `--sev-degraded` | `#F87171` | `#DC2626` |
| `--sev-degraded-bg` | `rgba(248,113,113,.10)` | `rgba(220,38,38,.10)` |
| `--sev-degraded-br` | `rgba(248,113,113,.28)` | `rgba(220,38,38,.34)` |
| `--neg` | `#F87171` | `#DC2626` |

*Green / blue / amber severity unchanged in Crimson.*

**Combining themes:**

```
<html>                                    → Amber + standard red (default)
<html data-theme="navy">                  → Navy + standard red
<html data-severity="crimson">            → Amber + loud crimson danger
<html data-theme="navy" data-severity="crimson"> → Navy + loud crimson danger
```

---

## Safety rules

Theme work is color-only.

No:
- trading buttons
- buy/sell buttons
- execute buttons
- connect-live broker controls
- auto-trade toggle
- copy changes that imply investment advice
- guaranteed-profit language
- backend behavior changes
- risk-policy changes

Safety posture remains:

```
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk <=1%
```

Severity color meanings must be preserved across all theme combinations:

| Color | Meaning |
|---|---|
| Green (`--sev-success`) | Safe / confirmed / posture OK |
| Blue (`--sev-info`) | Informational / routine event |
| Amber (`--sev-warning`) | Warning / degraded / HUMAN_REVIEW |
| Red / Crimson (`--sev-degraded`) | Critical / blocked / risk / NO_TRADE |

---

## Suggested token architecture

Use CSS variables:

```css
:root {
  /* Amber default */
}

[data-theme="navy"] {
  /* Navy optional override */
}

[data-severity="crimson"] {
  /* Crimson severity/risk override only */
}
```

Recommended future implementation files:

- `frontend/src/components/terminal/terminal.css` — owns the base + theme tokens
- optional future: `frontend/src/styles/tokens.css` — Amber at `:root`, Navy at `[data-theme="navy"]`
- optional future: `frontend/src/styles/severity.css` — severity ramp + `[data-severity="crimson"]`

Suggested import structure:

```css
/* terminal.css */
@import "../../styles/tokens.css";
@import "../../styles/severity.css";
```

---

## Acceptance criteria for future CSS implementation

- Amber remains default.
- Navy changes palette only.
- Crimson only affects severity/risk states.
- Safety meanings remain unchanged:
  - green = safe/confirmed
  - amber = warning/degraded
  - red/crimson = critical/blocked
  - blue = informational
- No trading/execution controls added.
- `validate_safety_config.py` passes.
- frontend build passes.

---

## Crimson severity-only layer

Crimson is not a full app theme.

It only affects:
- degraded states (critical/blocked level — red severity)
- blocked states
- NO_TRADE surfaces
- hard-stop / danger surfaces
- compliance / risk emphasis views

It must not recolor:
- base app background
- main panels
- sidebar
- typography
- primary Amber/Navy brand accents

Base theme remains Amber by default or Navy when explicitly enabled.

### Implementation token mapping

The CSS implementation in `frontend/src/components/terminal/terminal.css` uses these
token names (mapped from the design palette above):

| Design token | CSS implementation token | Amber default | Crimson override |
|---|---|---|---|
| `--sev-degraded` / `--neg` | `--terminal-red` | `#ff6b6b` | `#dc2626` |
| `--sev-degraded-bg` | `--terminal-danger-bg` | `rgba(255,107,107,.10)` | `rgba(220,38,38,.10)` |
| `--sev-degraded-br` | `--terminal-danger-border` | `rgba(255,107,107,.30)` | `rgba(220,38,38,.34)` |
| *(new)* | `--terminal-danger-glow` | `rgba(255,107,107,.12)` | `rgba(220,38,38,.18)` |

### Component classes that consume danger tokens

These classes use the token variables and therefore respond to the Crimson layer:

| Class | Surface | Severity level |
|---|---|---|
| `.scanner-action--no-trade` | NO_TRADE action chip | Red / critical |
| `.scanner-preview-card--no-trade` | Scanner card left border | Red / critical |
| `.signal-chip--sell` | Signal SELL display chip | Red / critical |
| `.value-negative` | Negative price delta | Red / critical |
| `.permission-grid .denied strong` | Denied permission entry | Red / critical |
| `.event-entry.warning strong` | Warning event entry | Red / critical |

### Classes intentionally NOT affected by Crimson

These classes are amber/warning level (not critical/blocked) and correctly stay amber:

| Class | Reason |
|---|---|
| `.service-pill--degraded` | Service degraded = warning level (amber), not blocked |
| `.degraded-services-banner` | Advisory/attention banner = warning level (amber) |

### Combining

```
<html>                                           → Amber + standard red (default)
<html data-theme="navy">                         → Navy + standard red
<html data-severity="crimson">                   → Amber + loud crimson danger
<html data-theme="navy" data-severity="crimson"> → Navy + loud crimson danger
```

Crimson activates via devtools only. No user-facing theme switcher. No persistence.
