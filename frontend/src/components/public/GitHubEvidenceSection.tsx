import { githubEvidenceCards } from "../../fixtures/publicShowcaseFixtures";

/**
 * GitHubEvidenceSection — PUBLIC-SITE-001
 *
 * Proof grid linking out to the real repository, CI workflows, and
 * evidence docs referenced in README.md. Links only — no tokens, no
 * secrets, no private URLs, no fabricated metrics.
 */
export function GitHubEvidenceSection() {
  return (
    <section id="github-evidence" className="public-section">
      <p className="public-section__eyebrow">GitHub Evidence</p>
      <h2>Don&apos;t take the website&apos;s word for it.</h2>
      <p className="public-section__lead">
        The tests, the safety scans, the CI runs, and the commit history are
        public.
      </p>
      <div className="public-evidence-grid">
        {githubEvidenceCards.map((card) => (
          <a
            key={card.title}
            href={card.href}
            target="_blank"
            rel="noreferrer"
            className="public-evidence-card"
          >
            <span className="public-evidence-card__tag">{card.tag}</span>
            <h3>{card.title}</h3>
            <p>{card.detail}</p>
          </a>
        ))}
      </div>
    </section>
  );
}
