import { SafetyBadges } from "../terminal/SafetyBadges";

/**
 * PublicSafetyContract — PUBLIC-SITE-001
 *
 * Renders the safety contract as monospace config lines with a
 * plain-language line beneath each, per the design pack. Reuses
 * `SafetyBadges` as-is (static, no network calls) rather than
 * `SafetyBanner`, which polls the live `/health` endpoint — the public
 * pages must not expose a live backend feed to anonymous visitors.
 */
const CONTRACT_LINES: Array<{ config: string; plain: string }> = [
  { config: "autotrade = false", plain: "No automated order placement exists anywhere in this codebase." },
  { config: "dry_run = true", plain: "Every execution path resolves to a dry-run log, never a live order." },
  { config: "read_only = true", plain: "The dashboard cannot place, modify, or cancel trades." },
  { config: "live_orders_blocked = true", plain: "Order-submission endpoints are structurally absent from the API." },
  { config: "max_risk <= 1%", plain: "Even in simulation, per-trade risk is capped and enforced by tests." },
];

export function PublicSafetyContract() {
  return (
    <section id="safety-contract" className="public-section">
      <p className="public-section__eyebrow">Safety Contract</p>
      <h2>Safety is the architecture, not the disclaimer.</h2>
      <p className="public-section__lead">
        Autotrade is off. Orders are blocked. Risk is capped at one percent.
        Every surface is read-only — by construction, and verified by tests.
      </p>
      <div className="public-safety-panel">
        <SafetyBadges />
        <div className="public-safety-panel__config">
          {CONTRACT_LINES.map((line) => (
            <div className="public-safety-panel__row" key={line.config}>
              <code>{line.config}</code>
              <span>{line.plain}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
