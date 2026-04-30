import { getMellyClientConfig } from "../lib/mellyApi";
import type { HealthInfo } from "../types/melly";
import { useMellyRiskConfig } from "../hooks/useMellyRiskConfig";

type AccessTone = "green" | "amber" | "red";

interface AccessItem {
  label: string;
  detail: string;
  tone: AccessTone;
}

interface AccessStatusBannerProps {
  health: HealthInfo | null;
  healthError: string | null;
}

function isUnauthorized(error: string | null): boolean {
  return Boolean(error && /unauthorized|401/i.test(error));
}

function safetyDegraded(health: HealthInfo): boolean {
  return (
    health.status !== "ok" ||
    !health.dry_run ||
    health.autotrade_enabled ||
    !health.read_only ||
    !health.live_orders_blocked ||
    health.max_risk_percent > 1.0
  );
}

export function AccessStatusBanner({
  health,
  healthError,
}: AccessStatusBannerProps) {
  const config = getMellyClientConfig();
  const protectedRead = useMellyRiskConfig();
  const items: AccessItem[] = [];

  if (healthError && !health) {
    items.push({
      label: "Backend offline",
      detail: healthError,
      tone: "red",
    });
  } else if (health && safetyDegraded(health)) {
    items.push({
      label: "Backend degraded",
      detail: "Safety posture differs from Direction B read-only invariants",
      tone: "red",
    });
  } else if (health) {
    items.push({
      label: "Backend online",
      detail: `${health.service} ${health.version}`,
      tone: "green",
    });
  }

  if (!config.hasApiKey) {
    items.push({
      label: "API key missing",
      detail: "Set VITE_MELLY_API_KEY in .env.local for protected read-only feeds",
      tone: "amber",
    });
  } else if (isUnauthorized(protectedRead.error)) {
    items.push({
      label: "API key rejected",
      detail: protectedRead.error ?? "Protected read-only endpoint returned 401",
      tone: "red",
    });
  } else if (protectedRead.error) {
    items.push({
      label: "Protected reads degraded",
      detail: protectedRead.error,
      tone: "amber",
    });
  } else if (protectedRead.data) {
    items.push({
      label: "Protected reads authorized",
      detail: `GET-only API access via ${config.baseUrl}`,
      tone: "green",
    });
  }

  if (items.length === 0) {
    items.push({
      label: "Access initializing",
      detail: `Checking ${config.baseUrl}`,
      tone: "amber",
    });
  }

  return (
    <div className="access-status-banner" aria-label="MellyTrade API access status">
      {items.map((item) => (
        <span
          key={item.label}
          className={`access-status-pill access-status-pill-${item.tone}`}
          title={item.detail}
        >
          {item.label}
        </span>
      ))}
    </div>
  );
}
