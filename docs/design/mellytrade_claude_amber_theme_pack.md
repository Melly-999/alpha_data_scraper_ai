# MellyTrade Claude Amber Theme Pack

Frontend-only institutional terminal theme pack for MellyTrade. This pack is display-only and preserves the existing read-only trading workstation posture.

## Palette

| Token | HEX |
|---|---|
| `bg` | `#070A0F` |
| `bgSoft` | `#0B0F14` |
| `panel` | `#10161F` |
| `panel2` | `#131B26` |
| `border` | `#263241` |
| `text` | `#E6EDF3` |
| `muted` | `#8B949E` |
| `dim` | `#5F6B7A` |
| `amber` | `#F5A524` |
| `amberSoft` | `#FFB84D` |
| `amberDark` | `#9A6100` |
| `cyan` | `#4FD1C5` |
| `blue` | `#58A6FF` |
| `purple` | `#A78BFA` |
| `success` | `#3FB950` |
| `danger` | `#FF6B6B` |
| `warning` | `#F5A524` |

## Font Stack

- UI: `Inter, "Segoe UI", system-ui, sans-serif`
- Mono: `"JetBrains Mono", "Fira Code", "Cascadia Code", Consolas, monospace`
- Display: `"Space Grotesk", Inter, system-ui, sans-serif`

## Glow And Shadow Settings

- Panel shadow: `0 24px 60px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.02)`
- Amber glow: `0 0 0 1px rgba(245, 165, 36, 0.18), 0 0 24px rgba(245, 165, 36, 0.14)`
- Cyan glow: `0 0 0 1px rgba(79, 209, 197, 0.18), 0 0 24px rgba(79, 209, 197, 0.12)`
- Terminal background:
  `radial-gradient(circle at top right, rgba(245, 165, 36, 0.12), transparent 28%), radial-gradient(circle at left center, rgba(88, 166, 255, 0.05), transparent 24%), linear-gradient(180deg, #0B0F14 0%, #070A0F 100%)`
- Panel background:
  `linear-gradient(180deg, rgba(19, 27, 38, 0.96), rgba(16, 22, 31, 0.92))`

## Tailwind Token Reference

The current frontend does not ship Tailwind. The reusable equivalent lives in [terminalTheme.ts](/C:/AI/MellyTrade_Workspace/02_Repo/alpha_data_scraper_ai-open-design-tabs-ui/frontend/src/design/terminalTheme.ts).

If Tailwind is introduced later, use this extension shape:

```ts
export default {
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: "#070A0F",
          bgSoft: "#0B0F14",
          panel: "#10161F",
          panel2: "#131B26",
          border: "#263241",
          text: "#E6EDF3",
          muted: "#8B949E",
          dim: "#5F6B7A",
        },
        accent: {
          amber: "#F5A524",
          amberSoft: "#FFB84D",
          amberDark: "#9A6100",
          cyan: "#4FD1C5",
          blue: "#58A6FF",
          purple: "#A78BFA",
        },
        state: {
          success: "#3FB950",
          danger: "#FF6B6B",
          warning: "#F5A524",
        },
      },
      boxShadow: {
        panel: "0 24px 60px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.02)",
        amberGlow: "0 0 0 1px rgba(245,165,36,0.18), 0 0 24px rgba(245,165,36,0.14)",
        cyanGlow: "0 0 0 1px rgba(79,209,197,0.18), 0 0 24px rgba(79,209,197,0.12)",
      },
      backgroundImage: {
        terminal: "radial-gradient(circle at top right, rgba(245,165,36,0.12), transparent 28%), linear-gradient(180deg, #0B0F14 0%, #070A0F 100%)",
        panel: "linear-gradient(180deg, rgba(19,27,38,0.96), rgba(16,22,31,0.92))",
      },
      borderRadius: {
        terminal: "14px",
        panel: "18px",
      },
      fontFamily: {
        ui: ["Inter", "Segoe UI", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", "monospace"],
        display: ["Space Grotesk", "Inter", "system-ui", "sans-serif"],
      },
    },
  },
};
```

## VS Code / Cursor Settings Snippet

```json
{
  "editor.fontFamily": "JetBrains Mono, Fira Code, Cascadia Code, Consolas, monospace",
  "editor.fontLigatures": true,
  "terminal.integrated.fontFamily": "JetBrains Mono, Fira Code, Cascadia Code, Consolas, monospace",
  "terminal.integrated.cursorStyle": "line",
  "workbench.colorCustomizations": {
    "editor.background": "#070A0F",
    "terminal.background": "#070A0F",
    "terminal.foreground": "#E6EDF3",
    "terminalCursor.foreground": "#F5A524",
    "terminal.ansiYellow": "#F5A524",
    "terminal.ansiBrightYellow": "#FFB84D",
    "terminal.ansiCyan": "#4FD1C5",
    "terminal.ansiBlue": "#58A6FF"
  }
}
```

## Windows Terminal Scheme

```json
{
  "name": "MellyTrade Claude Amber",
  "background": "#070A0F",
  "foreground": "#E6EDF3",
  "cursorColor": "#F5A524",
  "selectionBackground": "#263241",
  "black": "#0B0F14",
  "red": "#FF6B6B",
  "green": "#3FB950",
  "yellow": "#F5A524",
  "blue": "#58A6FF",
  "purple": "#A78BFA",
  "cyan": "#4FD1C5",
  "white": "#E6EDF3",
  "brightBlack": "#5F6B7A",
  "brightRed": "#FF8A8A",
  "brightGreen": "#63D471",
  "brightYellow": "#FFB84D",
  "brightBlue": "#79B8FF",
  "brightPurple": "#C4B5FD",
  "brightCyan": "#76E4DA",
  "brightWhite": "#F7FAFC"
}
```

## Warp Theme YAML

```yaml
name: MellyTrade Claude Amber
accent: "#F5A524"
background: "#070A0F"
foreground: "#E6EDF3"
details: darker
terminal_colors:
  normal:
    black: "#0B0F14"
    red: "#FF6B6B"
    green: "#3FB950"
    yellow: "#F5A524"
    blue: "#58A6FF"
    magenta: "#A78BFA"
    cyan: "#4FD1C5"
    white: "#E6EDF3"
  bright:
    black: "#5F6B7A"
    red: "#FF8A8A"
    green: "#63D471"
    yellow: "#FFB84D"
    blue: "#79B8FF"
    magenta: "#C4B5FD"
    cyan: "#76E4DA"
    white: "#F7FAFC"
```

## OpenCode / Claude Code Style Prompt

```text
Design this interface as a serious institutional terminal in an amber-on-dark visual language. Use dense but readable information design, compact panel spacing, amber uppercase section labels, JetBrains Mono for numeric surfaces, Space Grotesk or Inter for headings, subtle cyan secondary glows, and premium glass-dark panels. Keep everything read-only, advisory-only, and audit-first. Do not show execution controls, broker connection affordances, or CTA-style trading actions.
```

## Safety UX Rules

- Always surface `READ ONLY`, `DRY RUN`, `AUTO TRADE OFF`, `LIVE ORDERS BLOCKED`, and `HUMAN REVIEW REQUIRED`.
- Use amber for cautionary posture, green for safe status, cyan for passive signal quality, and red only for blocked or degraded conditions.
- Tables may visualize direction and outcome states, but must not present action controls.
- GET-only data visibility is allowed; mutating trading affordances are not.
- No personalized investment claims, no order placement cues, and no connect-live prompts.
- Preserve risk posture visibility, including max risk `<= 1%`.

