import { Link } from "react-router-dom";

import { GITHUB_REPO_URL } from "../../fixtures/publicShowcaseFixtures";

/**
 * RecruiterCTA — PUBLIC-SITE-001
 *
 * Final call-to-action band. Links only — no forms, no PII collection
 * beyond what the visitor already exposes by clicking an external link.
 */
export function RecruiterCTA() {
  return (
    <section id="cta" className="public-cta">
      <h2>Read the case study. Inspect the code. Everything is on the record.</h2>
      <p>
        If you&apos;re evaluating whether this team can build safe,
        auditable, AI-assisted tooling — the evidence is one click away.
      </p>
      <div className="public-cta__actions">
        <Link to="/case-study" className="public-button public-button--primary">
          Read the case study
        </Link>
        <a
          href={GITHUB_REPO_URL}
          target="_blank"
          rel="noreferrer"
          className="public-button public-button--ghost"
        >
          View the repository on GitHub
        </a>
      </div>
    </section>
  );
}
