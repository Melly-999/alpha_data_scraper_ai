/**
 * MellyPetMascot — UI-MASCOT-001
 *
 * Original MellyTrade AI workspace companion mascot.
 * Design-only component. No API calls, no trading controls, no mutations.
 * Safety posture: READ ONLY · DRY RUN · LIVE ORDERS BLOCKED · EXECUTION OFF
 *
 * Do NOT copy or reference third-party brand assets.
 * All visuals are original MellyTrade styling.
 */

const safetyChips = [
  "READ ONLY",
  "DRY RUN",
  "LIVE ORDERS BLOCKED",
  "EXECUTION OFF",
] as const;

function MellyFigure() {
  return (
    <svg
      className="melly-pet-figure"
      viewBox="0 0 80 92"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      {/* Ambient glow behind figure */}
      <ellipse
        cx="40"
        cy="46"
        rx="28"
        ry="32"
        fill="rgba(214,164,76,0.04)"
      />

      {/* ── Suit body ─────────────────────────────────────────────────────── */}
      <rect x="18" y="54" width="44" height="34" rx="6" fill="#0d1016" />
      {/* Top edge highlight */}
      <rect x="18" y="54" width="44" height="3" rx="2" fill="#1a2030" />

      {/* White shirt / placket */}
      <path
        d="M40 57 L33 54 L33 74 L40 80 L47 74 L47 54 Z"
        fill="#dde3eb"
        opacity="0.88"
      />
      {/* Shirt shadow centre crease */}
      <path
        d="M40 57 L38 54 L38 72 L40 78 L42 72 L42 54 Z"
        fill="#c5ccd8"
        opacity="0.45"
      />

      {/* Left lapel */}
      <path
        d="M18 58 L33 54 L35 68 L28 84 L18 80 Z"
        fill="#111520"
      />
      {/* Right lapel */}
      <path
        d="M62 58 L47 54 L45 68 L52 84 L62 80 Z"
        fill="#111520"
      />

      {/* Amber tie — MellyTrade accent */}
      <path
        d="M38.5 59 L41.5 59 L40.5 75 L40 77 L39.5 75 Z"
        fill="#c49a3c"
      />
      {/* Tie knot */}
      <polygon
        points="40,57 37,60.5 40,62.5 43,60.5"
        fill="#d6a44c"
      />

      {/* ── Head ──────────────────────────────────────────────────────────── */}
      <rect x="13" y="6" width="54" height="50" rx="11" fill="#141820" />
      {/* Head border — amber tint */}
      <rect
        x="13"
        y="6"
        width="54"
        height="50"
        rx="11"
        stroke="rgba(214,164,76,0.22)"
        strokeWidth="1"
      />

      {/* Ear / sensor nubs */}
      <rect x="5" y="22" width="8" height="16" rx="3" fill="#1a1f2a" />
      <rect x="67" y="22" width="8" height="16" rx="3" fill="#1a1f2a" />
      {/* Sensor indicator dots */}
      <circle cx="9" cy="30" r="1.5" fill="rgba(214,164,76,0.5)" />
      <circle cx="71" cy="30" r="1.5" fill="rgba(214,164,76,0.5)" />

      {/* ── Eyes — amber scanner visor style ──────────────────────────────── */}
      {/* Left eye housing */}
      <rect
        x="19"
        y="21"
        width="17"
        height="12"
        rx="4"
        fill="rgba(214,164,76,0.10)"
        stroke="rgba(214,164,76,0.30)"
        strokeWidth="1"
      />
      {/* Left iris */}
      <circle cx="27.5" cy="27" r="4" fill="#d6a44c" />
      {/* Left pupil */}
      <circle cx="27.5" cy="27" r="2.2" fill="#07090c" />
      {/* Left specular */}
      <circle cx="26.5" cy="25.8" r="0.9" fill="rgba(255,255,255,0.75)" />

      {/* Right eye housing */}
      <rect
        x="44"
        y="21"
        width="17"
        height="12"
        rx="4"
        fill="rgba(214,164,76,0.10)"
        stroke="rgba(214,164,76,0.30)"
        strokeWidth="1"
      />
      {/* Right iris */}
      <circle cx="52.5" cy="27" r="4" fill="#d6a44c" />
      {/* Right pupil */}
      <circle cx="52.5" cy="27" r="2.2" fill="#07090c" />
      {/* Right specular */}
      <circle cx="51.5" cy="25.8" r="0.9" fill="rgba(255,255,255,0.75)" />

      {/* Expression — calm arc / micro-smile */}
      <path
        d="M30 40 Q40 44 50 40"
        stroke="rgba(214,164,76,0.55)"
        strokeWidth="1.5"
        strokeLinecap="round"
      />

      {/* Neck collar bar */}
      <rect x="31" y="52" width="18" height="4" rx="2" fill="#1c2230" />
    </svg>
  );
}

export function MellyPetMascot() {
  return (
    <article
      className="melly-pet-card"
      aria-label="Melly Pet — MellyTrade AI workspace companion"
    >
      <div className="melly-pet-visual" aria-hidden="true">
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
