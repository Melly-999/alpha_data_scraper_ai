import { SafetyBadges } from "./SafetyBadges";

const bootSteps = [
  "Initializing terminal...",
  "Loading market modules...",
  "Verifying safety posture...",
  "Connecting broker adapters...",
  "Starting audit feed...",
];

export function LoadingScreen() {
  return (
    <section className="loading-screen" aria-label="Terminal boot status">
      <div>
        <p className="terminal-eyebrow">MellyTrade V1 Terminal</p>
        <h1>Safe read-only trading workstation</h1>
      </div>
      <div className="boot-grid">
        {bootSteps.map((step) => (
          <div key={step} className="boot-row">
            <span className="boot-dot" />
            <span>{step}</span>
          </div>
        ))}
      </div>
      <SafetyBadges />
    </section>
  );
}
