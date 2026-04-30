// Persistent safety banner. Surfaces the four MellyTrade safety pills on
// every page so the operator can verify at a glance that the dashboard
// is in research / decision-support mode (no live execution).
//
// Inputs come from the Sprint 1A `/health` contract. If that backend is
// unreachable the banner stays visible with neutral pills and surfaces a
// `degraded` flag so the operator notices the missing telemetry.

import { useMellyHealth } from "../hooks/useMellyHealth";
import type { HealthInfo } from "../types/melly";

// Direction B safety invariant: per-trade risk must not exceed 1%.
const EXPECTED_MAX_RISK_PERCENT = 1.0;

type PillTone = "green" | "amber" | "red" | "muted";

interface PillSpec {
  label: string;
  description: string;
  tone: PillTone;
}

function pills(health: HealthInfo | null): PillSpec[] {
  if (!health) {
    return [
      {
        label: "DRY RUN",
        description: "Safety status unknown",
        tone: "muted",
      },
      {
        label: "READ-ONLY MODE",
        description: "Safety status unknown",
        tone: "muted",
      },
      {
        label: "LIVE ORDERS BLOCKED",
        description: "Safety status unknown",
        tone: "muted",
      },
      {
        label: `MAX RISK ≤ ${EXPECTED_MAX_RISK_PERCENT.toFixed(0)}%`,
        description: "Risk gate not yet loaded",
        tone: "muted",
      },
    ];
  }

  const dryRunTone: PillTone = health.dry_run ? "green" : "red";
  const readOnlyTone: PillTone = health.read_only ? "green" : "red";
  const liveBlockedTone: PillTone = health.live_orders_blocked
    ? "green"
    : "red";
  const riskTone: PillTone =
    health.max_risk_percent <= EXPECTED_MAX_RISK_PERCENT ? "green" : "amber";

  return [
    {
      label: "DRY RUN",
      description: health.dry_run
        ? "Paper trading only — no live orders are sent"
        : "Dry run is OFF; live execution is NOT blocked",
      tone: dryRunTone,
    },
    {
      label: "READ-ONLY MODE",
      description: health.read_only
        ? "Dashboard cannot place trades"
        : "Read-only mode is OFF",
      tone: readOnlyTone,
    },
    {
      label: "LIVE ORDERS BLOCKED",
      description: health.live_orders_blocked
        ? "All execution paths are gated"
        : "WARNING: live orders are NOT blocked",
      tone: liveBlockedTone,
    },
    {
      label: `MAX RISK ≤ ${EXPECTED_MAX_RISK_PERCENT.toFixed(0)}%`,
      description: `Per-trade risk ceiling enforced by the API (${health.max_risk_percent.toFixed(
        2,
      )}% reported)`,
      tone: riskTone,
    },
  ];
}

export function SafetyBanner() {
  const { data, error } = useMellyHealth();
  const items = pills(data);
  const degraded = !data && Boolean(error);

  return (
    <div
      className="safety-banner"
      role="status"
      aria-label="MellyTrade safety posture"
    >
      <div className="safety-banner-pills">
        {items.map((pill) => (
          <span
            key={pill.label}
            className={`safety-pill safety-pill-${pill.tone}`}
            data-tone={pill.tone}
            title={pill.description}
          >
            {pill.label}
          </span>
        ))}
      </div>
      {degraded ? (
        <span
          className="safety-banner-note"
          title={`Health endpoint unreachable: ${error}`}
        >
          Safety telemetry unavailable
        </span>
      ) : null}
    </div>
  );
}
