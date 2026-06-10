/**
 * MellyPetMascot — UI-MASCOT-001 / MELLY-PET-BRANDING-001
 *
 * Official MellyTrade Melly Pet mascot.
 * Design-only component. No API calls, no trading controls, no mutations.
 * Safety posture: READ ONLY · DRY RUN · LIVE ORDERS BLOCKED · EXECUTION OFF
 *
 * The artwork is the original Melly Pet brand asset rendered as-is from
 * src/assets/melly-pet.png — no redraw, no restyle, no recolor.
 */

import mellyPetArt from "../../assets/melly-pet.png";

const safetyChips = [
  "READ ONLY",
  "DRY RUN",
  "LIVE ORDERS BLOCKED",
  "EXECUTION OFF",
] as const;

function MellyFigure() {
  return (
    <img
      className="melly-pet-figure"
      src={mellyPetArt}
      alt="Melly Pet safety mascot"
      loading="lazy"
      decoding="async"
      draggable={false}
    />
  );
}

export function MellyPetMascot() {
  return (
    <article
      className="melly-pet-card"
      aria-label="Melly Pet — MellyTrade AI workspace companion"
    >
      <div className="melly-pet-visual">
        <MellyFigure />
      </div>

      <div className="melly-pet-body">
        <div className="melly-pet-header">
          <span className="melly-pet-micro">DEMO COMPANION</span>
          <h3 className="melly-pet-name">Melly Pet</h3>
        </div>

        <p className="melly-pet-subtitle">
          Your read-only AI workspace companion.
        </p>

        <p className="melly-pet-copy">
          Guides the demo, explains safety posture, and keeps the workspace
          focused on paper-only previews.
        </p>

        <div
          className="melly-pet-chips"
          aria-label="Active safety constraints"
        >
          {safetyChips.map((chip) => (
            <span key={chip} className="melly-pet-chip">
              {chip}
            </span>
          ))}
        </div>
      </div>
    </article>
  );
}
