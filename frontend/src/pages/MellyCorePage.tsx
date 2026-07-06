import "./mellycore.css";

import {
  commandCoreSignals,
  contextFlow,
  evidenceRail,
  heroBadges,
  marketOrbitSignals,
  mobilePanels,
  notionCards,
  obsidianClusters,
  providerNodes,
} from "../fixtures/mellycoreShowcase";

function SectionLink({
  href,
  label,
}: {
  href: string;
  label: string;
}) {
  return (
    <a className="mellycore-cta" href={href}>
      {label}
    </a>
  );
}

export function MellyCorePage() {
  return (
    <div className="mellycore-page">
      <header className="mellycore-hero" id="top">
        <div className="mellycore-hero-copy">
          <p className="mellycore-eyebrow">MellyCore showcase / static slice</p>
          <h1>MellyCore AIOS</h1>
          <p className="mellycore-hero-subtitle">
            A private AI control plane with a local-first knowledge graph,
            curated model routing, and safety-first module previews.
          </p>
          <div className="mellycore-badge-row" aria-label="Core positioning">
            {heroBadges.map((badge) => (
              <span key={badge} className="mellycore-chip">
                {badge}
              </span>
            ))}
          </div>
          <div className="mellycore-hero-actions">
            <SectionLink href="#architecture" label="Explore system" />
            <SectionLink href="#safety" label="View safeguards" />
          </div>
        </div>

        <div className="mellycore-command-core panel-glass" aria-hidden="true">
          <div className="mellycore-command-glow" />
          <div className="mellycore-orbit mellycore-orbit-outer" />
          <div className="mellycore-orbit mellycore-orbit-mid" />
          <div className="mellycore-orbit mellycore-orbit-inner" />
          <div className="mellycore-core-node" />
          <div className="mellycore-terminal-lines">
            {commandCoreSignals.map((line) => (
              <div key={line} className="mellycore-terminal-line">
                <span className="mellycore-line-dot" />
                <span>{line}</span>
              </div>
            ))}
          </div>
        </div>
      </header>

      <main className="mellycore-sections">
        <section className="mellycore-section" id="architecture">
          <div className="mellycore-section-copy">
            <p className="mellycore-eyebrow">Obsidian galaxy</p>
            <h2>Private graph, mirrored architecture, manual navigation</h2>
            <p>
              The knowledge layer stays local-first: repo docs remain
              canonical, the vault mirrors architecture into a generated zone,
              and MOCs connect the graph without exposing raw private notes.
            </p>
          </div>
          <div className="mellycore-visual-card panel-glass mellycore-galaxy">
            <div className="mellycore-galaxy-grid" aria-hidden="true">
              {obsidianClusters.map((cluster, index) => (
                <article
                  key={cluster.label}
                  className={`mellycore-galaxy-node mellycore-galaxy-node-${index + 1}`}
                >
                  <strong>{cluster.label}</strong>
                  <span>{cluster.detail}</span>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="mellycore-section mellycore-section-reverse">
          <div className="mellycore-section-copy">
            <p className="mellycore-eyebrow">Model hub constellation</p>
            <h2>Routing clarity without exposing credentials</h2>
            <p>
              Providers are shown as capability classes, not brands or keys.
              Context selection and routing stay distinct from any credential
              handling, and nothing in this slice performs external requests.
            </p>
          </div>
          <div className="mellycore-visual-card panel-glass mellycore-constellation">
            <div className="mellycore-constellation-center">Hub</div>
            {providerNodes.map((node, index) => (
              <article
                key={node.label}
                className={`mellycore-provider-node mellycore-provider-node-${index + 1}`}
              >
                <strong>{node.label}</strong>
                <span>{node.detail}</span>
              </article>
            ))}
          </div>
        </section>

        <section className="mellycore-section">
          <div className="mellycore-section-copy">
            <p className="mellycore-eyebrow">Context gateway flow</p>
            <h2>From canonical docs to curated context packs</h2>
            <p>
              The flow is static and explanatory: documents feed the local
              mirror, summaries shape context, and governance remains visible at
              every stage.
            </p>
          </div>
          <div className="mellycore-visual-card panel-glass mellycore-flow">
            {contextFlow.map((step, index) => (
              <div key={step} className="mellycore-flow-step">
                <span className="mellycore-flow-index">0{index + 1}</span>
                <p>{step}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mellycore-section mellycore-section-reverse">
          <div className="mellycore-section-copy">
            <p className="mellycore-eyebrow">Notion bridge dashboard</p>
            <h2>Curated summaries only, never a source of truth</h2>
            <p>
              The dashboard layer is clean and shareable, but it remains
              secondary. It receives approved summaries, not raw vault notes,
              and it never writes back automatically.
            </p>
          </div>
          <div className="mellycore-visual-card panel-glass mellycore-notion">
            {notionCards.map((card) => (
              <article key={card.label} className="mellycore-dashboard-card">
                <span className="mellycore-card-kicker">Curated layer</span>
                <strong>{card.label}</strong>
                <p>{card.detail}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="mellycore-section">
          <div className="mellycore-section-copy">
            <p className="mellycore-eyebrow">MellyTrade market orbit</p>
            <h2>Market intelligence preview, clearly simulated</h2>
            <p>
              MellyTrade appears here as an abstract orbit of regime,
              volatility, and risk posture. It is a read-only demonstration of
              intelligence framing, not a trading interface.
            </p>
            <p className="mellycore-disclaimer">
              Simulated demo visualization — read-only market intelligence
              preview.
            </p>
          </div>
          <div className="mellycore-visual-card panel-glass mellycore-orbit-card">
            <div className="mellycore-risk-core">Risk ≤ 1%</div>
            <div className="mellycore-market-ring mellycore-market-ring-1" />
            <div className="mellycore-market-ring mellycore-market-ring-2" />
            <div className="mellycore-market-ring mellycore-market-ring-3" />
            <div className="mellycore-market-points" aria-hidden="true">
              <span />
              <span />
              <span />
              <span />
            </div>
            <div className="mellycore-orbit-tags">
              {marketOrbitSignals.map((signal) => (
                <span key={signal} className="mellycore-chip mellycore-chip-muted">
                  {signal}
                </span>
              ))}
            </div>
          </div>
        </section>

        <section className="mellycore-section mellycore-section-reverse">
          <div className="mellycore-section-copy">
            <p className="mellycore-eyebrow">iOS / PWA preview</p>
            <h2>Poster-first command surface for mobile-safe review</h2>
            <p>
              The handheld preview prioritizes legibility, reduced motion, and
              local-first posture. It shows calm, summary-oriented cards rather
              than dense cockpit controls.
            </p>
          </div>
          <div className="mellycore-visual-card panel-glass mellycore-phone-preview">
            <div className="mellycore-phone-frame">
              <div className="mellycore-phone-notch" />
              <div className="mellycore-phone-screen">
                {mobilePanels.map((panel) => (
                  <article key={panel.label} className="mellycore-phone-card">
                    <strong>{panel.label}</strong>
                    <span>{panel.detail}</span>
                  </article>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="mellycore-section" id="safety">
          <div className="mellycore-section-copy">
            <p className="mellycore-eyebrow">Safety / evidence rail</p>
            <h2>Static, reviewable, and explicitly non-executing</h2>
            <p>
              This slice is a static front-end showcase. It uses no live data,
              no external requests, and no action-oriented controls. The goal is
              visual direction, not operational behavior.
            </p>
          </div>
          <div className="mellycore-visual-card panel-glass mellycore-evidence">
            <ol className="mellycore-evidence-list">
              {evidenceRail.map((item) => (
                <li key={item}>
                  <span className="mellycore-evidence-mark" aria-hidden="true">
                    +
                  </span>
                  <span>{item}</span>
                </li>
              ))}
            </ol>
            <p className="mellycore-static-note">
              Static showcase slice. No live claims. No external media or data
              dependencies.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
