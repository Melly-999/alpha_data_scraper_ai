import { Link } from "react-router-dom";

import { MellyPetMascot } from "../components/branding/MellyPetMascot";
import "../components/terminal/terminal.css";
import "./mobile-app.css";

/**
 * MobileAppPage — MOBILE-APP-001
 *
 * Mobile-first PWA app shell preview for MellyTrade ("Mobile Command Center").
 * Read-only / display-only surface. No API mutations, no trading controls,
 * no POST/PUT/PATCH/DELETE calls.
 * Safety posture: READ ONLY · DRY RUN · LIVE ORDERS BLOCKED · EXECUTION OFF
 */

const SAFETY_BADGES = [
  "READ ONLY",
  "DRY RUN",
  "LIVE ORDERS BLOCKED",
  "HUMAN REVIEW REQUIRED",
] as const;

type ReadinessCard = {
  title: string;
  status: string;
  description: string;
  to?: string;
};

// `to` is only set for routes that exist in App.tsx. Cards without `to`
// render as read-only text (no broken links).
const READINESS_CARDS: ReadinessCard[] = [
  {
    title: "Terminal UI",
    status: "Ready",
    description: "Read-only institutional terminal shell.",
    to: "/terminal",
  },
  {
    title: "Agent MCP",
    status: "Docs",
    description: "Read-only repo/PR/checks agent contract (documentation).",
  },
  {
    title: "Paper Sandbox",
    status: "Preview",
    description: "Deterministic paper run preview. Sandbox only.",
    to: "/terminal/paper-run-preview",
  },
  {
    title: "Deploy Demo",
    status: "Planned",
    description: "Render backend + Vercel frontend demo (planned).",
  },
  {
    title: "Mobile PWA",
    status: "You are here",
    description: "Mobile-first read-only command center shell.",
    to: "/mobile",
  },
];

type QuickLink = {
  label: string;
  to: string;
};

// Only routes that exist in App.tsx are linked here.
const QUICK_LINKS: QuickLink[] = [
  { label: "Terminal", to: "/terminal" },
  { label: "Workspace", to: "/workspace" },
  { label: "Paper Run Preview", to: "/terminal/paper-run-preview" },
  { label: "Audit Trail", to: "/audit" },
  { label: "Mobile", to: "/mobile" },
];

export function MobileAppPage() {
  return (
    <div className="mobile-app-page">
      <main className="mobile-app-shell" aria-label="MellyTrade mobile command center">
        <header className="mobile-app-header">
          <p className="mobile-app-eyebrow">Mobile Command Center</p>
          <h1 className="mobile-app-title">MellyTrade Mobile</h1>
          <p className="mobile-app-subtitle">Read-only command center</p>
        </header>

        <section
          className="mobile-safety-strip"
          aria-label="Active safety constraints"
        >
          {SAFETY_BADGES.map((badge) => (
            <span key={badge} className="mobile-safety-badge">
              {badge}
            </span>
          ))}
        </section>

        <section
          className="mobile-melly-pet-card"
          aria-label="Melly Pet read-only assistant"
        >
          <MellyPetMascot />
          <p className="mobile-melly-pet-copy">
            Melly Pet helps monitor demo readiness, safety status, and operator
            tasks. It never places orders or enables live trading.
          </p>
        </section>

        <section aria-label="Demo readiness">
          <h2 className="mobile-section-title">Demo readiness</h2>
          <div className="mobile-readiness-grid">
            {READINESS_CARDS.map((card) => {
              const body = (
                <>
                  <div className="mobile-readiness-top">
                    <span className="mobile-readiness-name">{card.title}</span>
                    <span className="mobile-readiness-status">{card.status}</span>
                  </div>
                  <p className="mobile-readiness-desc">{card.description}</p>
                </>
              );
              return card.to ? (
                <Link
                  key={card.title}
                  to={card.to}
                  className="mobile-readiness-card mobile-readiness-card--link"
                >
                  {body}
                </Link>
              ) : (
                <div
                  key={card.title}
                  className="mobile-readiness-card mobile-readiness-card--static"
                  aria-disabled="true"
                >
                  {body}
                </div>
              );
            })}
          </div>
        </section>

        <section aria-label="Quick navigation">
          <h2 className="mobile-section-title">Quick navigation</h2>
          <nav className="mobile-quick-links">
            {QUICK_LINKS.map((link) => (
              <Link key={link.to} to={link.to} className="mobile-quick-link">
                {link.label}
              </Link>
            ))}
          </nav>
        </section>

        <footer className="mobile-app-footer">
          <p>
            This mobile shell is a read-only demo surface. It does not connect to
            live broker execution.
          </p>
        </footer>
      </main>
    </div>
  );
}
