import { githubEvidenceCards, GITHUB_REPO_URL, roadmapMilestones } from "../fixtures/publicShowcaseFixtures";
import { MELLYTRADE_PUBLIC_MEDIA } from "../fixtures/mediaAssets";
import { CinematicHeroMedia } from "../components/public/CinematicHeroMedia";
import { PublicSiteFooter } from "../components/public/PublicSiteFooter";
import { PublicSiteNav } from "../components/public/PublicSiteNav";
import "./public-site.css";

/**
 * CaseStudyPage — PUBLIC-SITE-001 / MEDIA-WIRING-PREP-001
 *
 * Public case-study route (`/case-study`). Content is ported from
 * README.md's existing narrative sections (Safety Contract, Architecture,
 * Validation & Evidence, What This Project Demonstrates, Roadmap) rather
 * than rewritten from scratch, per the design pack's instruction to reuse
 * the existing evidence copy.
 *
 * The case-study hero shares the same hero image (cropped band) as the
 * landing page, per the design pack. `heroPosterSrc`/`heroVideoSrc` are
 * optional and forwarded to `CinematicHeroMedia`; this page defaults to
 * the accepted hero image as a static poster (no autoplay video) — a
 * deliberately calmer treatment than the landing hero for this secondary
 * page. Callers may still override either prop.
 */
type CaseStudyPageProps = {
  heroPosterSrc?: string;
  heroVideoSrc?: string;
};
const ARCHITECTURE_DIAGRAM = `┌──────────────────────────────────────────────────────┐
│  Frontend  (React + TypeScript + Vite)               │
│  /terminal   — institutional dashboard               │
│  /mobile     — PWA AI companion                     │
│  /brokers    — read-only broker status               │
│  Poll-only: apiGet() — no mutation helpers           │
└───────────────────┬──────────────────────────────────┘
                    │  HTTPS  GET-only
┌───────────────────▼──────────────────────────────────┐
│  Backend  (FastAPI + Python 3.11+)                   │
│  GET /api/health          liveness + safety posture  │
│  GET /api/terminal/*      dashboard payloads         │
│  GET /api/risk/config     dry_run / autotrade gates  │
│  GET /paper/run/preview   paper plan preview         │
│  No POST/PUT/PATCH/DELETE on trading surfaces        │
└──────────────────────────────────────────────────────┘`;

const DEMONSTRATES: Array<{ skill: string; where: string }> = [
  { skill: "AI product engineering", where: "Signal reasoning panel, screenshot review flow, safety-aware UX patterns" },
  { skill: "Safe fintech UX", where: "Read-only posture enforced simultaneously at UI, API, and test layers" },
  { skill: "FastAPI + React architecture", where: "Typed Pydantic schemas, poll-only frontend, CORS-safe cross-origin hosting" },
  { skill: "Safety-first automation", where: "config.json + pytest safety contract, forbidden-path testing, validator script" },
  { skill: "PWA / mobile engineering", where: "iOS/iPad-installable PWA, responsive mobile companion, multi-viewport CI" },
  { skill: "CI/CD", where: "GitHub Actions: pytest, Playwright e2e (54 tests, iPad + mobile viewports)" },
];

export function CaseStudyPage({
  heroPosterSrc = MELLYTRADE_PUBLIC_MEDIA.heroPoster,
  heroVideoSrc,
}: CaseStudyPageProps = {}) {
  return (
    <div className="public-page">
      <a href="#case-main" className="public-skip-link">
        Skip to content
      </a>
      <PublicSiteNav />
      <main id="case-main">
        <section className="public-case-hero">
          <CinematicHeroMedia posterSrc={heroPosterSrc} videoSrc={heroVideoSrc} />
          <div className="public-case-hero__content">
            <p className="public-section__eyebrow">Case Study</p>
            <h1>A production-quality trading platform that refuses to trade.</h1>
            <p className="public-section__lead" style={{ margin: "0 auto" }}>
              This case study covers the architecture, the safety engineering,
              and the AI-assisted workflow behind it.
            </p>
            <div className="public-pillars">
              <div className="public-pillar">
                <h3>Platform Engineering</h3>
                <p>FastAPI + React/TypeScript/Vite, typed schemas, poll-only frontend, GET-only API surface.</p>
              </div>
              <div className="public-pillar">
                <h3>Safety Engineering</h3>
                <p>Config-level contract, forbidden-path tests, denylist scanning, pytest safety-regression suite.</p>
              </div>
              <div className="public-pillar">
                <h3>AI Workflow</h3>
                <p>Signal reasoning, advisory-only outputs, human-review framing on every AI surface.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="public-section">
          <p className="public-section__eyebrow">Problem</p>
          <h2>Trading-adjacent software is the hardest place to prove engineering judgment.</h2>
          <p className="public-section__lead">
            High stakes, regulatory sensitivity, and a hype-saturated field.
            The problem framed here: demonstrate production-grade capability
            without creating execution risk.
          </p>
        </section>

        <section className="public-section">
          <p className="public-section__eyebrow">Solution</p>
          <h2>An AIOS-style read-only intelligence platform.</h2>
          <p className="public-section__lead">
            Signal analysis, risk framing, paper simulation, and audit
            evidence — with execution structurally removed, not merely
            disabled.
          </p>
        </section>

        <section className="public-section">
          <p className="public-section__eyebrow">Architecture</p>
          <h2>Read-only by construction.</h2>
          <pre className="public-architecture-block">{ARCHITECTURE_DIAGRAM}</pre>
          <p className="public-section__lead">
            <strong>Stack:</strong> Python · FastAPI · Pydantic · React ·
            TypeScript · Vite · Vercel · Render · pytest · PWA
          </p>
        </section>

        <section className="public-section">
          <p className="public-section__eyebrow">Safety Engineering</p>
          <h2>What is intentionally blocked.</h2>
          <p className="public-section__lead">
            No control, button, or copy anywhere may say or imply Buy / Sell
            / Execute / Order / &quot;place a trade&quot; / &quot;connect
            live account.&quot; No execution control exists anywhere in the
            component tree — verified by an executable pytest suite on
            every push.
          </p>
          <div className="public-fact-grid">
            <div className="public-fact-card">
              <h4>autotrade = false · dry_run = true</h4>
              <p>Enforced in config.json and asserted in pytest.</p>
            </div>
            <div className="public-fact-card">
              <h4>Forbidden-path test</h4>
              <p>test_openapi_forbidden_paths.py fails the build if a mutating route appears under a guarded prefix.</p>
            </div>
            <div className="public-fact-card">
              <h4>Safety validator</h4>
              <p>scripts/validate_safety_config.py runs in CI and locally.</p>
            </div>
            <div className="public-fact-card">
              <h4>Static safety scan</h4>
              <p>No placeOrder(), no executeOrder(), no order/execute button text, no broker write paths.</p>
            </div>
          </div>
        </section>

        <section className="public-section">
          <p className="public-section__eyebrow">UI System</p>
          <h2>Institutional dark, amber accent, black glass.</h2>
          <p className="public-section__lead">
            Terminal theme tokens, black-glass panels, a consistent
            safety-badge language, and an MT pixel-monogram identity carried
            across the terminal, mobile companion, and this public layer.
          </p>
        </section>

        <section className="public-section">
          <p className="public-section__eyebrow">Validation / Evidence</p>
          <h2>Evidence, not claims.</h2>
          <div className="public-evidence-grid">
            {githubEvidenceCards.map((card) => (
              <a key={card.title} href={card.href} target="_blank" rel="noreferrer" className="public-evidence-card">
                <span className="public-evidence-card__tag">{card.tag}</span>
                <h3>{card.title}</h3>
                <p>{card.detail}</p>
              </a>
            ))}
          </div>
        </section>

        <section className="public-section">
          <p className="public-section__eyebrow">What This Project Demonstrates</p>
          <div className="public-fact-grid">
            {DEMONSTRATES.map((row) => (
              <div className="public-fact-card" key={row.skill}>
                <h4>{row.skill}</h4>
                <p>{row.where}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="public-section">
          <p className="public-section__eyebrow">Roadmap</p>
          <h2>Honest, dated, no vaporware.</h2>
          <div className="public-roadmap-grid">
            {roadmapMilestones.map((m) => (
              <div
                key={m.label}
                className={`public-roadmap-card public-roadmap-card--${m.status}`}
              >
                <h4>
                  {m.status === "shipped" ? "✓ " : "→ "}
                  {m.label}
                </h4>
                <p>{m.detail}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="public-cta">
          <h2>If you&apos;re evaluating this team&apos;s work, start here.</h2>
          <p>
            What this project demonstrates: full-stack + AI product engineering
            plus safety engineering. Links only — no forms, no PII collection.
          </p>
          <div className="public-cta__actions">
            <a href={GITHUB_REPO_URL} target="_blank" rel="noreferrer" className="public-button public-button--primary">
              View the repository on GitHub
            </a>
          </div>
        </section>
      </main>
      <PublicSiteFooter />
    </div>
  );
}
