import { Link } from "react-router-dom";

/**
 * PublicSiteNav — PUBLIC-SITE-001
 *
 * Persistent header for the public `/` and `/case-study` pages. Provides
 * the always-visible "Enter terminal" link required to preserve the old
 * `/ -> /terminal` behaviour for returning users, now that `/` renders the
 * public landing page instead of redirecting.
 *
 * Display-only. No API calls, no execution affordances.
 */
export function PublicSiteNav() {
  return (
    <header className="public-nav">
      <Link to="/" className="public-nav__brand" aria-label="MellyTrade home">
        <span className="public-monogram" aria-hidden="true">
          {Array.from({ length: 16 }).map((_, i) => (
            <span key={i} />
          ))}
        </span>
        MellyTrade
      </Link>
      <nav className="public-nav__links" aria-label="Public site navigation">
        <Link to="/case-study">Case study</Link>
        <a href="https://github.com/Melly-999/alpha_data_scraper_ai" target="_blank" rel="noreferrer">
          GitHub
        </a>
      </nav>
      <Link to="/terminal" className="public-nav__cta">
        Enter terminal →
      </Link>
    </header>
  );
}
