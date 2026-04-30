// Persistent safety banner. Surfaces the four MellyTrade safety pills on
// every page so the operator can verify at a glance that the dashboard
// is in research / decision-support mode (no live execution).
//
// Inputs come from the Sprint 1A `/health` contract. If that backend is
// unreachable the banner stays visible with neutral pills and surfaces a
// `degraded` flag so the operator notices the missing telemetry.
//
// The max-risk pill label reflects the live value from `/risk/config`
// (via useMellyRiskConfig) so it tracks the operator's actual configuration
// rather than a hard-coded frontend constant.

import { useMellyHealth } from "../hooks/useMellyHealth";
import { useMellyRiskConfig } from "../hooks/useMellyRiskConfig";
import type { HealthInfo } from "../types/melly";
import { AccessStatusBanner } from "./AccessStatusBanner";

// Amber warning threshold: pill turns amber when configured max risk exceeds
// this Direction B safety invariant, even if the backend allows more.
const AMBER_RISK_THRESHOLD = 1.0;

type PillTone = "green" | "amber" | "red" | "muted";

interface PillSpec {
  label: string;
  description: string;
  tone: PillTone;
}

function pills(health: HealthInfo | null, configuredMax: number): PillSpec[] {
  const riskLabel = `MAX RISK ≤ ${configuredMax.toFixed(1)}%`;

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
        label: riskLabel,
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
    configuredMax <= AMBER_RISK_THRESHOLD ? "green" : "amber";

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
      label: riskLabel,
      description: `Per-trade risk ceiling enforced by the API (${health.max_risk_percent.toFixed(
        2,
      )}% configured)`,
      tone: riskTone,
    },
  ];
}

export function SafetyBanner() {
  const { data: health, error: healthError } = useMellyHealth();
  const { data: riskConfig } = useMellyRiskConfig();

  // Prefer live /risk/config value; fall back to health's copy, then to the
  // amber threshold so the label is never blank while data is loading.
  const configuredMax =
    riskConfig?.max_risk_percent ??
    health?.max_risk_percent ??
    AMBER_RISK_THRESHOLD;

  const items = pills(health, configuredMax);
  const degraded = !health && Boolean(healthError);

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
          title={`Health endpoint unreachable: ${healthError}`}
        >
          Safety telemetry unavailable
        </span>
      ) : null}
      <AccessStatusBanner health={health} healthError={healthError} />
    </div>
  );
}
