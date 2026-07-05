/**
 * PublicSiteFooter — PUBLIC-SITE-001
 *
 * Shared footer for the public `/` and `/case-study` pages: MT monogram,
 * persistent disclaimer, and an optional small community mascot mark
 * (secondary/community only, per the locked brand hierarchy).
 */
export function PublicSiteFooter() {
  return (
    <footer className="public-footer">
      <div className="public-footer__mark" aria-hidden="true">
        <span className="public-monogram">
          {Array.from({ length: 16 }).map((_, i) => (
            <span key={i} />
          ))}
        </span>
        MellyTrade
      </div>
      <p className="public-footer__disclaimer">
        Advisory and educational software. Read-only. All data shown is demo
        or simulated. Not financial advice. No live trading capability
        exists.
      </p>
      <p className="public-footer__pet-note">Melly Pet — community mascot, secondary mark only.</p>
    </footer>
  );
}
