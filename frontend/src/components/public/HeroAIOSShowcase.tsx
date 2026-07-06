import { Link } from "react-router-dom";

import { CinematicHeroMedia } from "./CinematicHeroMedia";

/**
 * HeroAIOSShowcase — PUBLIC-SITE-001 / MEDIA-WIRING-PREP-001
 *
 * Full-viewport hero band for the public landing page. Copy is taken
 * verbatim from the Copy Blocks section of
 * docs/design/mellytrade_website_design_pack_001.md.
 *
 * `posterSrc`/`videoSrc` are optional and forwarded as-is to
 * `CinematicHeroMedia`. No asset exists yet, so the default (no props from
 * `PublicLandingPage`) renders the CSS placeholder — behavior is unchanged
 * until a future run passes real paths (see
 * `frontend/src/fixtures/mediaAssets.ts`).
 */
type HeroAIOSShowcaseProps = {
  posterSrc?: string;
  videoSrc?: string;
};

export function HeroAIOSShowcase({ posterSrc, videoSrc }: HeroAIOSShowcaseProps = {}) {
  return (
    <section id="hero" className="public-hero">
      <CinematicHeroMedia posterSrc={posterSrc} videoSrc={videoSrc} />
      <div className="public-hero__content">
        <span className="public-hero__wordmark">
          <span className="public-monogram" aria-hidden="true">
            {Array.from({ length: 16 }).map((_, i) => (
              <span key={i} />
            ))}
          </span>
          MellyTrade
        </span>
        <span className="public-hero__badge">READ-ONLY · ADVISORY</span>
        <h1>Intelligence, not execution.</h1>
        <p className="public-hero__subhead">
          MellyTrade is a read-only AI market-analysis platform. It studies,
          simulates, and explains — and is engineered so it cannot trade.
        </p>
        <div className="public-hero__actions">
          <Link to="/case-study" className="public-button public-button--primary">
            View the case study
          </Link>
          <Link to="/terminal" className="public-button public-button--ghost">
            Explore the terminal preview
          </Link>
        </div>
        <span className="public-hero__scroll-cue" aria-hidden="true" />
      </div>
    </section>
  );
}
