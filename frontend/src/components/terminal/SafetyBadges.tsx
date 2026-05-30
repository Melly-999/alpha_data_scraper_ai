import { safetyBadges } from "../../design/terminalTheme";

export function SafetyBadges() {
  return (
    <div className="safety-badges" aria-label="Global safety posture">
      {safetyBadges.map((badge) => (
        <span
          key={badge.label}
          className={`safety-badge safety-badge--${badge.variant}`}
        >
          {badge.label}
        </span>
      ))}
    </div>
  );
}
