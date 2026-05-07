const badges = ["READ ONLY", "DRY RUN", "AUTO TRADE OFF", "LIVE ORDERS BLOCKED"];

export function SafetyBadges() {
  return (
    <div className="safety-badges" aria-label="Global safety posture">
      {badges.map((badge) => (
        <span key={badge} className="safety-badge">
          {badge}
        </span>
      ))}
    </div>
  );
}
