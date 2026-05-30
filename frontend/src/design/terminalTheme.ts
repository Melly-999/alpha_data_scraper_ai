export const terminalTokens = {
  colors: {
    bg: "#070A0F",
    bgSoft: "#0B0F14",
    panel: "#10161F",
    panel2: "#131B26",
    border: "#263241",
    text: "#E6EDF3",
    muted: "#8B949E",
    dim: "#5F6B7A",
    amber: "#F5A524",
    amberSoft: "#FFB84D",
    amberDark: "#9A6100",
    cyan: "#4FD1C5",
    blue: "#58A6FF",
    purple: "#A78BFA",
    success: "#3FB950",
    danger: "#FF6B6B",
    warning: "#F5A524",
  },
  fonts: {
    ui: ["Inter", "\"Segoe UI\"", "system-ui", "sans-serif"],
    mono: [
      "\"JetBrains Mono\"",
      "\"Fira Code\"",
      "\"Cascadia Code\"",
      "Consolas",
      "monospace",
    ],
    display: ["\"Space Grotesk\"", "Inter", "system-ui", "sans-serif"],
  },
  radius: {
    terminal: "14px",
    panel: "18px",
  },
  shadows: {
    panel: "0 24px 60px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.02)",
    amberGlow: "0 0 0 1px rgba(245, 165, 36, 0.18), 0 0 24px rgba(245, 165, 36, 0.14)",
    cyanGlow: "0 0 0 1px rgba(79, 209, 197, 0.18), 0 0 24px rgba(79, 209, 197, 0.12)",
  },
  gradients: {
    terminal:
      "radial-gradient(circle at top right, rgba(245, 165, 36, 0.12), transparent 28%), linear-gradient(180deg, #0B0F14 0%, #070A0F 100%)",
    panel:
      "linear-gradient(180deg, rgba(19, 27, 38, 0.96), rgba(16, 22, 31, 0.92))",
  },
} as const;

export const tailwindThemeExtension = {
  colors: {
    terminal: {
      bg: terminalTokens.colors.bg,
      bgSoft: terminalTokens.colors.bgSoft,
      panel: terminalTokens.colors.panel,
      panel2: terminalTokens.colors.panel2,
      border: terminalTokens.colors.border,
      text: terminalTokens.colors.text,
      muted: terminalTokens.colors.muted,
      dim: terminalTokens.colors.dim,
    },
    accent: {
      amber: terminalTokens.colors.amber,
      amberSoft: terminalTokens.colors.amberSoft,
      amberDark: terminalTokens.colors.amberDark,
      cyan: terminalTokens.colors.cyan,
      blue: terminalTokens.colors.blue,
      purple: terminalTokens.colors.purple,
    },
    state: {
      success: terminalTokens.colors.success,
      danger: terminalTokens.colors.danger,
      warning: terminalTokens.colors.warning,
    },
  },
  boxShadow: {
    panel: terminalTokens.shadows.panel,
    amberGlow: terminalTokens.shadows.amberGlow,
    cyanGlow: terminalTokens.shadows.cyanGlow,
  },
  backgroundImage: {
    terminal: terminalTokens.gradients.terminal,
    panel: terminalTokens.gradients.panel,
  },
  borderRadius: {
    terminal: terminalTokens.radius.terminal,
    panel: terminalTokens.radius.panel,
  },
  fontFamily: terminalTokens.fonts,
} as const;

export const safetyBadges = [
  { label: "READ ONLY", variant: "read-only" },
  { label: "DRY RUN", variant: "dry-run" },
  { label: "AUTO TRADE OFF", variant: "auto-trade" },
  { label: "LIVE ORDERS BLOCKED", variant: "blocked" },
  { label: "HUMAN REVIEW REQUIRED", variant: "review" },
] as const;

