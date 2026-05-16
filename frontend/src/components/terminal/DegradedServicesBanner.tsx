import type { IBKRStatus, MT5Status, TerminalSummary } from "../../lib/terminalApi";

type DegradedServicesBannerProps = {
  summary: TerminalSummary;
  mt5: MT5Status;
  broker: IBKRStatus;
};

type ServicePill = {
  key: string;
  label: string;
  state: "degraded" | "safe";
};

function derivePills(
  summary: TerminalSummary,
  mt5: MT5Status,
  broker: IBKRStatus,
): ServicePill[] {
  const pills: ServicePill[] = [];

  if (summary.backend !== "online") {
    pills.push({ key: "demo", label: "DEMO DATA", state: "degraded" });
  }

  if (!mt5.connected) {
    const mode = mt5.mode === "synthetic" ? "SYNTHETIC" : mt5.mode.toUpperCase();
    pills.push({ key: "mt5", label: `MT5 · ${mode}`, state: "degraded" });
  }

  if (broker.status !== "connected") {
    const label =
      broker.status === "degraded"
        ? "IBKR · DEGRADED"
        : broker.status === "paper" || broker.status === "read-only"
          ? "IBKR · READ-ONLY"
          : "IBKR · SAFE-DISCONNECTED";
    pills.push({ key: "ibkr", label, state: "degraded" });
  }

  // Safety locks always visible in the banner when degraded services are shown.
  pills.push({ key: "ro", label: "READ ONLY", state: "safe" });
  pills.push({ key: "dr", label: "DRY RUN ACTIVE", state: "safe" });
  pills.push({ key: "lob", label: "LIVE ORDERS BLOCKED", state: "safe" });

  return pills;
}

export function DegradedServicesBanner({
  summary,
  mt5,
  broker,
}: DegradedServicesBannerProps) {
  const isDegraded =
    summary.backend !== "online" ||
    !mt5.connected ||
    broker.status !== "connected";

  if (!isDegraded) {
    return null;
  }

  const pills = derivePills(summary, mt5, broker);

  return (
    <div className="degraded-services-banner" role="status" aria-live="polite">
      <p className="degraded-banner-message">
        Some services are running in degraded or fallback mode. MellyTrade
        remains read-only and dry-run; live orders are blocked.
      </p>
      <div className="degraded-banner-pills">
        {pills.map((pill) => (
          <span
            key={pill.key}
            className={`service-pill service-pill--${pill.state}`}
          >
            {pill.label}
          </span>
        ))}
      </div>
    </div>
  );
}
