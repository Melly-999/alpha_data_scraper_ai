import { Link } from "react-router-dom";

import { GitHubEvidenceSection } from "../components/public/GitHubEvidenceSection";
import { HeroAIOSShowcase } from "../components/public/HeroAIOSShowcase";
import { ProductPreviewGrid } from "../components/public/ProductPreviewGrid";
import { PublicSafetyContract } from "../components/public/PublicSafetyContract";
import { PublicSiteFooter } from "../components/public/PublicSiteFooter";
import { PublicSiteNav } from "../components/public/PublicSiteNav";
import { RecruiterCTA } from "../components/public/RecruiterCTA";
import { SectionHUDChip } from "../components/public/SectionHUDChip";
import { MELLYTRADE_PUBLIC_MEDIA } from "../fixtures/mediaAssets";
import "../components/terminal/terminal.css";
import "./public-site.css";

/**
 * PublicLandingPage — PUBLIC-SITE-001
 *
 * Public landing route (`/`). Replaces the previous `/ -> /terminal`
 * redirect. Single scroll narrative per
 * docs/design/mellytrade_website_design_pack_001.md: Hero → Product
 * Snapshot → AIOS Preview → Safety Contract → Product Previews →
 * GitHub Evidence → Mobile/PWA → CTA. All data is static/DEMO — no
 * network calls are made from this page.
 */
const JOURNEY_STEPS = [
  { label: "Signal Intake", detail: "Market data and indicators feed a deterministic advisory layer." },
  { label: "Risk Layer", detail: "Every signal passes through a hard-coded risk gate before it is shown." },
  { label: "Paper Sandbox", detail: "Simulated plans only — no path from sandbox to a live account." },
  { label: "Audit Rail", detail: "Every analysis and safety check leaves an append-only record." },
];

export function PublicLandingPage() {
  return (
    <div className="public-page">
      <a href="#main-content" className="public-skip-link">
        Skip to content
      </a>
      <PublicSiteNav />
      <SectionHUDChip />
      <main id="main-content">
        {/* Poster-only hero: see docs/showcase/media_integration_001.md for
            why the accepted C1 clip (aios-assembly.mp4) is not autoplayed
            here — its rising-line motif read too close to a "line go up"
            trading visual once viewed full-bleed behind the headline. */}
        <HeroAIOSShowcase posterSrc={MELLYTRADE_PUBLIC_MEDIA.heroPoster} />

        <section id="snapshot" className="public-kinetic">
          <div className="public-kinetic__beats" aria-hidden="true">
            <span className="is-lit">READ-ONLY.</span>
            <span className="is-lit">PAPER-FIRST.</span>
            <span className="is-lit">AUDITED.</span>
          </div>
          <p className="public-section__lead" style={{ margin: "24px auto 0" }}>
            An AIOS-style command center for market intelligence: signal
            analysis, risk framing, paper simulation, and a full audit
            trail. Built as engineering evidence, not as a trading product.
          </p>
          <p className="public-section__lead" style={{ margin: "12px auto 0", color: "var(--text-muted)" }}>
            It is not a live trading bot, a broker, a signal-selling
            product, or a fake performance dashboard.
          </p>
        </section>

        <section id="aios-preview" className="public-section">
          <p className="public-section__eyebrow">AIOS Preview</p>
          <h2>How a read-only analysis flows through the system.</h2>
          <div className="public-journey">
            {JOURNEY_STEPS.map((step, index) => (
              <div className="public-journey__step" key={step.label}>
                <span className="public-journey__step-index">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <h3>{step.label}</h3>
                <p>{step.detail}</p>
              </div>
            ))}
          </div>
        </section>

        <PublicSafetyContract />

        <ProductPreviewGrid />

        <GitHubEvidenceSection />

        <section id="mobile-pwa" className="public-section">
          <p className="public-section__eyebrow">Mobile / iPad PWA</p>
          <h2>Installable, responsive, still read-only.</h2>
          <div className="public-mobile-split">
            <div className="public-mobile-split__frame" aria-hidden="true">
              MELLYTRADE
              <br />
              MOBILE PWA
              <br />
              DEMO PREVIEW
            </div>
            <div>
              <p className="public-section__lead">
                A full mobile-first companion — AI chart review, paper game
                plan, safety score, watchlist — installable as a PWA on iOS,
                Android, and iPad. No execution controls, no order entry.
              </p>
              <Link to="/mobile" className="public-button public-button--ghost">
                Open the mobile preview →
              </Link>
            </div>
          </div>
        </section>

        <RecruiterCTA />
      </main>
      <PublicSiteFooter />
    </div>
  );
}
