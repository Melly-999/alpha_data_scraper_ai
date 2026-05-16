import { useEffect, useMemo, useState } from "react";

import { Badge } from "../components/shared/Badge";
import { Card } from "../components/shared/Card";
import { Drawer } from "../components/shared/Drawer";
import { Table } from "../components/shared/Table";
import { SignalDecisionHistoryPanel } from "../components/signals/SignalDecisionHistoryPanel";
import { SignalLifecyclePanel } from "../components/signals/SignalLifecyclePanel";
import { SignalReasoningPanel } from "../components/signals/SignalReasoningPanel";
import { useMellySignals } from "../hooks/useMellySignals";
import { useSignalDecisions } from "../hooks/useSignalDecisions";
import { useSignalLifecycle } from "../hooks/useSignalLifecycle";
import { useSignals } from "../hooks/useSignals";
import { useStaleDetector } from "../hooks/useStaleDetector";
import { apiGet } from "../lib/api";
import { useUiStore } from "../stores/useUiStore";
import type {
  DecisionDirection,
  DecisionRiskStatus,
  DecisionType,
  Direction,
  SignalDetail,
  SignalReasoning,
} from "../types/api";
import type { Action, SignalSummary as MellySignalSummary } from "../types/melly";

function directionTone(direction: Direction): "green" | "red" | "amber" {
  if (direction === "BUY") {
    return "green";
  }
  if (direction === "SELL") {
    return "red";
  }
  return "amber";
}

function formatOptional(value: number | null | undefined) {
  return value == null ? "-" : value.toString();
}

function actionTone(action: Action): "green" | "red" | "amber" {
  if (action === "BUY") return "green";
  if (action === "SELL") return "red";
  return "amber";
}

function statusTone(status: string): "green" | "red" | "muted" {
  if (status === "accepted") return "green";
  if (status === "rejected") return "red";
  return "muted";
}

type MellyStatusFilter = "" | "accepted" | "rejected";
type DecisionHistoryDecisionFilter = DecisionType | "";
type DecisionHistoryRiskStatusFilter = DecisionRiskStatus | "";
type DecisionHistoryDirectionFilter = DecisionDirection | "";
type LifecycleDecisionFilter = DecisionType | "";
type LifecycleRiskStatusFilter = DecisionRiskStatus | "";

// SUPA-015: read-only date-range UI for decision history.
// Quick-ranges are computed at render time only (no persistence, no submit).
type DecisionDateQuickRange = "ALL" | "1H" | "4H" | "24H" | "7D";

const DECISION_DATE_QUICK_RANGES: Array<{
  key: DecisionDateQuickRange;
  label: string;
}> = [
  { key: "1H", label: "1H" },
  { key: "4H", label: "4H" },
  { key: "24H", label: "24H" },
  { key: "7D", label: "7D" },
  { key: "ALL", label: "ALL" },
];

function quickRangeMinutes(range: DecisionDateQuickRange): number | null {
  if (range === "1H") return 60;
  if (range === "4H") return 60 * 4;
  if (range === "24H") return 60 * 24;
  if (range === "7D") return 60 * 24 * 7;
  return null;
}

function quickRangeFromIso(range: DecisionDateQuickRange): string | null {
  const minutes = quickRangeMinutes(range);
  if (minutes === null) return null;
  return new Date(Date.now() - minutes * 60_000).toISOString();
}

/**
 * Convert a <input type="datetime-local"> value (e.g. "2026-05-16T10:00")
 * to an ISO 8601 UTC string. Returns null when the value is empty or invalid.
 * Read-only — no storage, no submit semantics.
 */
function localInputToIso(value: string): string | null {
  if (!value) return null;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed.toISOString();
}

function formatDateRangeLabel(
  quickRange: DecisionDateQuickRange,
  customFromIso: string | null,
  customToIso: string | null,
): string {
  if (customFromIso || customToIso) {
    const left = customFromIso
      ? new Date(customFromIso).toLocaleString([], {
          dateStyle: "short",
          timeStyle: "short",
        })
      : "—";
    const right = customToIso
      ? new Date(customToIso).toLocaleString([], {
          dateStyle: "short",
          timeStyle: "short",
        })
      : "—";
    return `custom ${left} → ${right}`;
  }
  if (quickRange === "ALL") return "all time";
  return `last ${quickRange.toLowerCase()}`;
}

function formatDecisionHistoryFilterSummary(
  symbol: string,
  decision: DecisionHistoryDecisionFilter,
  riskStatus: DecisionHistoryRiskStatusFilter,
  direction: DecisionHistoryDirectionFilter,
) {
  const parts = [];
  const trimmed = symbol.trim();
  if (trimmed !== "") parts.push(`symbol ${trimmed.toUpperCase()}`);
  if (decision !== "") parts.push(`decision ${decision}`);
  if (riskStatus !== "") parts.push(`risk ${riskStatus}`);
  if (direction !== "") parts.push(`direction ${direction}`);
  return parts.length === 0 ? "All dry-run decision records" : parts.join(" · ");
}

function formatLifecycleFilterSummary(
  symbol: string,
  decision: LifecycleDecisionFilter,
  riskStatus: LifecycleRiskStatusFilter,
) {
  const parts = [];
  const trimmed = symbol.trim();
  if (trimmed !== "") parts.push(`symbol ${trimmed.toUpperCase()}`);
  if (decision !== "") parts.push(`decision ${decision}`);
  if (riskStatus !== "") parts.push(`risk ${riskStatus}`);
  return parts.length === 0 ? "All lifecycle records" : parts.join(" · ");
}

export function SignalsPage() {
  const { data, loading, error } = useSignals();
  const [decisionSymbol, setDecisionSymbol] = useState("");
  const [decisionFilter, setDecisionFilter] =
    useState<DecisionHistoryDecisionFilter>("");
  const [decisionRiskStatus, setDecisionRiskStatus] =
    useState<DecisionHistoryRiskStatusFilter>("");
  const [decisionDirection, setDecisionDirection] =
    useState<DecisionHistoryDirectionFilter>("");
  const [decisionBlockedOnly, setDecisionBlockedOnly] = useState(false);
  const effectiveDecisionFilter = decisionBlockedOnly ? "blocked" : decisionFilter;
  // SUPA-015: date-range filter state. Quick-range and custom dates are
  // mutually exclusive — picking a custom date clears the quick-range, and
  // picking a quick-range clears the custom dates. Read-only filtering only;
  // no persistence, no localStorage, no submit handlers.
  const [decisionQuickRange, setDecisionQuickRange] =
    useState<DecisionDateQuickRange>("ALL");
  const [decisionFromInput, setDecisionFromInput] = useState<string>("");
  const [decisionToInput, setDecisionToInput] = useState<string>("");
  const customFromIso = useMemo(
    () => localInputToIso(decisionFromInput),
    [decisionFromInput],
  );
  const customToIso = useMemo(
    () => localInputToIso(decisionToInput),
    [decisionToInput],
  );
  const hasCustomRange = customFromIso !== null || customToIso !== null;
  const effectiveFromDate: string | null = hasCustomRange
    ? customFromIso
    : quickRangeFromIso(decisionQuickRange);
  const effectiveToDate: string | null = hasCustomRange ? customToIso : null;
  const dateRangeLabel = formatDateRangeLabel(
    decisionQuickRange,
    customFromIso,
    customToIso,
  );
  const {
    data: decisionsData,
    loading: decisionsLoading,
    error: decisionsError,
    lastUpdatedAt: decisionsLastUpdatedAt,
  } = useSignalDecisions({
    limit: 50,
    symbol: decisionSymbol,
    decision: effectiveDecisionFilter,
    riskStatus: decisionRiskStatus,
    direction: decisionDirection,
    fromDate: effectiveFromDate,
    toDate: effectiveToDate,
  });
  // SUPA-013: stale indicator for Decision History card.
  // Uses the same useStaleDetector / data-freshness-label pattern as
  // AuditEventsPreview (SUPA-009). Display-only — no execution semantics.
  const decisionsFreshness = useStaleDetector(decisionsLastUpdatedAt ?? null);
  let decisionsFreshnessLabel: string;
  if (decisionsFreshness === "initializing") {
    decisionsFreshnessLabel = "polling…";
  } else {
    const timeStr = (decisionsLastUpdatedAt as Date).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
    decisionsFreshnessLabel =
      decisionsFreshness === "stale"
        ? `updated ${timeStr} · stale`
        : `updated ${timeStr}`;
  }
  const [lifecycleSymbol, setLifecycleSymbol] = useState("");
  const [lifecycleDecision, setLifecycleDecision] =
    useState<LifecycleDecisionFilter>("");
  const [lifecycleRiskStatus, setLifecycleRiskStatus] =
    useState<LifecycleRiskStatusFilter>("");
  const [lifecycleBlockedOnly, setLifecycleBlockedOnly] = useState(false);
  const effectiveLifecycleDecision = lifecycleBlockedOnly
    ? "blocked"
    : lifecycleDecision;
  const {
    data: lifecycleData,
    loading: lifecycleLoading,
    error: lifecycleError,
  } = useSignalLifecycle({
    limit: 20,
    symbol: lifecycleSymbol,
    decision: effectiveLifecycleDecision,
    riskStatus: lifecycleRiskStatus,
  });
  const selectedSignalId = useUiStore((state) => state.selectedSignalId);
  const setSelectedSignalId = useUiStore((state) => state.setSelectedSignalId);
  const [detail, setDetail] = useState<SignalDetail | null>(null);
  const [reasoning, setReasoning] = useState<SignalReasoning | null>(null);

  const [mellySymbol, setMellySymbol] = useState("");
  const [mellyStatus, setMellyStatus] = useState<MellyStatusFilter>("");
  const trimmedSymbol = mellySymbol.trim();
  const {
    data: mellySignals,
    loading: mellyLoading,
    error: mellyError,
  } = useMellySignals({
    symbol: trimmedSymbol === "" ? undefined : trimmedSymbol,
    status: mellyStatus === "" ? undefined : mellyStatus,
    limit: 50,
  });
  const mellyRows = useMemo<MellySignalSummary[]>(
    () => mellySignals ?? [],
    [mellySignals],
  );

  useEffect(() => {
    if (!selectedSignalId) {
      setDetail(null);
      setReasoning(null);
      return;
    }
    void apiGet<SignalDetail>(`/signals/${selectedSignalId}`).then(setDetail);
    void apiGet<SignalReasoning>(`/signals/${selectedSignalId}/reasoning`).then(
      setReasoning,
    );
  }, [selectedSignalId]);

  const signals = data ?? [];
  const eligibleCount = signals.filter((signal) => !signal.blocked).length;
  const blockedCount = signals.filter((signal) => signal.blocked).length;
  const averageConfidence =
    signals.length > 0
      ? Math.round(
          signals.reduce((total, signal) => total + signal.confidence, 0) /
            signals.length,
        )
      : 0;

  return (
    <div className="page-grid with-drawer passive-page">
      <div className="passive-main">
        <section className="page-header">
          <div>
            <div className="eyebrow">Signals</div>
            <h1 className="page-title">Signal Review</h1>
            <div className="dashboard-muted">Read-only signal feed from FastAPI.</div>
          </div>
          <div className="page-header-meta">
            <Badge tone="green">{eligibleCount} eligible</Badge>
            <Badge tone="amber">{blockedCount} blocked</Badge>
            <Badge tone="blue">{averageConfidence}% avg confidence</Badge>
          </div>
        </section>

        <Card
          title="Signals"
          right={<Badge tone="muted">{signals.length} total</Badge>}
        >
          {loading && !data ? <div className="state">Loading signals...</div> : null}
          {error && !data ? <div className="state error">{error}</div> : null}
          {data ? (
            <Table
              columns={[
                { key: "symbol", label: "Symbol", render: (row) => row.symbol },
                {
                  key: "direction",
                  label: "Direction",
                  render: (row) => (
                    <Badge tone={directionTone(row.direction)}>{row.direction}</Badge>
                  ),
                },
                {
                  key: "confidence",
                  label: "Conf",
                  render: (row) => `${row.confidence}%`,
                },
                {
                  key: "mtf_alignment",
                  label: "MTF",
                  render: (row) => `${row.mtf_alignment}/${row.mtf_total}`,
                },
                {
                  key: "claude_status",
                  label: "Claude",
                  render: (row) => row.claude_status,
                },
                {
                  key: "blocked_reason",
                  label: "Risk",
                  render: (row) =>
                    row.blocked_reason ? (
                      <Badge tone="amber">{row.blocked_reason}</Badge>
                    ) : (
                      <Badge tone="green">Eligible</Badge>
                    ),
                },
              ]}
              rows={data}
              onRowClick={(row) => setSelectedSignalId(row.id)}
            />
          ) : null}
        </Card>

        <Card
          title="Decision History"
          right={
            <>
              <Badge tone="muted">
                {decisionsData ? `${decisionsData.total} records` : "—"} · dry-run
              </Badge>
              {/* SUPA-013: data-freshness label — display-only, no execution semantics */}
              <span
                className={`data-freshness-label${decisionsFreshness === "stale" ? " data-stale" : ""}`}
              >
                {decisionsFreshnessLabel}
              </span>
            </>
          }
        >
          <div className="dashboard-muted" style={{ marginBottom: "0.5rem" }}>
            Read-only log of dry-run signal decisions. No orders placed.
          </div>
          <div className="signal-lifecycle-controls">
            <label>
              <span>Symbol</span>
              <input
                type="text"
                placeholder="e.g. AAPL"
                value={decisionSymbol}
                onChange={(event) => setDecisionSymbol(event.target.value)}
                maxLength={16}
              />
            </label>
            <label>
              <span>Decision</span>
              <select
                value={effectiveDecisionFilter}
                disabled={decisionBlockedOnly}
                onChange={(event) =>
                  setDecisionFilter(
                    event.target.value as DecisionHistoryDecisionFilter,
                  )
                }
              >
                <option value="">All</option>
                <option value="dry_run_allowed">dry_run_allowed</option>
                <option value="blocked">blocked</option>
                <option value="watch_only">watch_only</option>
                <option value="no_action">no_action</option>
              </select>
            </label>
            <label>
              <span>Risk status</span>
              <select
                value={decisionRiskStatus}
                onChange={(event) =>
                  setDecisionRiskStatus(
                    event.target.value as DecisionHistoryRiskStatusFilter,
                  )
                }
              >
                <option value="">All</option>
                <option value="pass">pass</option>
                <option value="warn">warn</option>
                <option value="blocked">blocked</option>
                <option value="unknown">unknown</option>
              </select>
            </label>
            <label>
              <span>Direction</span>
              <select
                value={decisionDirection}
                onChange={(event) =>
                  setDecisionDirection(
                    event.target.value as DecisionHistoryDirectionFilter,
                  )
                }
              >
                <option value="">All</option>
                <option value="BUY">BUY</option>
                <option value="SELL">SELL</option>
                <option value="HOLD">HOLD</option>
                <option value="UNKNOWN">UNKNOWN</option>
              </select>
            </label>
            <label className="signal-lifecycle-toggle">
              <input
                type="checkbox"
                checked={decisionBlockedOnly}
                onChange={(event) => setDecisionBlockedOnly(event.target.checked)}
              />
              <span>Show blocked only</span>
            </label>
          </div>
          {/* SUPA-015: read-only date range controls.
              Quick ranges and custom pickers are mutually exclusive: any
              custom date overrides the quick range. Selecting a quick range
              clears any custom pickers. No forms, no submit, no storage. */}
          <div
            className="signal-lifecycle-controls signal-date-range-controls"
            role="group"
            aria-label="Decision history date range (read-only filter)"
          >
            <div className="signal-date-range-quicks" role="radiogroup">
              {DECISION_DATE_QUICK_RANGES.map((range) => {
                const active =
                  !hasCustomRange && decisionQuickRange === range.key;
                return (
                  <button
                    key={range.key}
                    type="button"
                    className={`signal-date-range-chip${active ? " active" : ""}`}
                    aria-pressed={active}
                    onClick={() => {
                      setDecisionQuickRange(range.key);
                      setDecisionFromInput("");
                      setDecisionToInput("");
                    }}
                  >
                    {range.label}
                  </button>
                );
              })}
            </div>
            <label>
              <span>From</span>
              <input
                type="datetime-local"
                value={decisionFromInput}
                onChange={(event) => setDecisionFromInput(event.target.value)}
                aria-label="Decision history from date (read-only filter)"
              />
            </label>
            <label>
              <span>To</span>
              <input
                type="datetime-local"
                value={decisionToInput}
                onChange={(event) => setDecisionToInput(event.target.value)}
                aria-label="Decision history to date (read-only filter)"
              />
            </label>
            {hasCustomRange ? (
              <button
                type="button"
                className="signal-date-range-clear"
                onClick={() => {
                  setDecisionFromInput("");
                  setDecisionToInput("");
                }}
              >
                Clear dates
              </button>
            ) : null}
          </div>
          <div className="signal-lifecycle-summary">
            {formatDecisionHistoryFilterSummary(
              decisionSymbol,
              effectiveDecisionFilter,
              decisionRiskStatus,
              decisionDirection,
            )}
            <span className="dashboard-muted"> · range: {dateRangeLabel}</span>
          </div>
          {decisionsLoading && !decisionsData ? (
            <div className="state">Loading decision history...</div>
          ) : null}
          {decisionsError && !decisionsData ? (
            <div className="state error">{decisionsError}</div>
          ) : null}
          {decisionsData ? (
            <SignalDecisionHistoryPanel
              records={decisionsData.decisions}
              generatedAt={decisionsData.generated_at}
              fallback={decisionsData.fallback}
              degraded={decisionsData.degraded}
              filters={{
                symbol: decisionSymbol,
                decision: effectiveDecisionFilter,
                riskStatus: decisionRiskStatus,
                direction: decisionDirection,
                blockedOnly: decisionBlockedOnly,
              }}
              hasActiveFilters={
                decisionSymbol.trim() !== "" ||
                effectiveDecisionFilter !== "" ||
                decisionRiskStatus !== "" ||
                decisionDirection !== "" ||
                hasCustomRange ||
                decisionQuickRange !== "ALL"
              }
            />
          ) : null}
        </Card>

        <Card
          title="Signal Lifecycle"
          right={
            <Badge tone="muted">
              {lifecycleData ? `${lifecycleData.total} paths` : "-"} · GET-only
            </Badge>
          }
        >
          <div className="dashboard-muted" style={{ marginBottom: "0.5rem" }}>
            Read-only signal path from receipt through safety checks, dry-run
            outcome, and audit correlation. Dry-run allowed is not an order.
          </div>
          <div className="signal-lifecycle-controls">
            <label>
              <span>Symbol</span>
              <input
                type="text"
                placeholder="e.g. AAPL"
                value={lifecycleSymbol}
                onChange={(event) => setLifecycleSymbol(event.target.value)}
                maxLength={16}
              />
            </label>
            <label>
              <span>Decision</span>
              <select
                value={effectiveLifecycleDecision}
                disabled={lifecycleBlockedOnly}
                onChange={(event) =>
                  setLifecycleDecision(event.target.value as LifecycleDecisionFilter)
                }
              >
                <option value="">All</option>
                <option value="dry_run_allowed">dry_run_allowed</option>
                <option value="blocked">blocked</option>
                <option value="watch_only">watch_only</option>
                <option value="no_action">no_action</option>
              </select>
            </label>
            <label>
              <span>Risk status</span>
              <select
                value={lifecycleRiskStatus}
                onChange={(event) =>
                  setLifecycleRiskStatus(
                    event.target.value as LifecycleRiskStatusFilter,
                  )
                }
              >
                <option value="">All</option>
                <option value="pass">pass</option>
                <option value="warn">warn</option>
                <option value="blocked">blocked</option>
                <option value="unknown">unknown</option>
              </select>
            </label>
            <label className="signal-lifecycle-toggle">
              <input
                type="checkbox"
                checked={lifecycleBlockedOnly}
                onChange={(event) => setLifecycleBlockedOnly(event.target.checked)}
              />
              <span>Show blocked only</span>
            </label>
          </div>
          <div className="signal-lifecycle-summary">
            {formatLifecycleFilterSummary(
              lifecycleSymbol,
              effectiveLifecycleDecision,
              lifecycleRiskStatus,
            )}
          </div>
          {lifecycleLoading && !lifecycleData ? (
            <div className="state">Loading signal lifecycle...</div>
          ) : null}
          {lifecycleError && !lifecycleData ? (
            <div className="state error">{lifecycleError}</div>
          ) : null}
          {lifecycleData ? (
            <SignalLifecyclePanel
              records={lifecycleData.lifecycle}
              generatedAt={lifecycleData.generated_at}
              filters={{
                symbol: lifecycleSymbol.trim(),
                decision: effectiveLifecycleDecision,
                riskStatus: lifecycleRiskStatus,
                blockedOnly: lifecycleBlockedOnly,
              }}
              hasActiveFilters={
                lifecycleSymbol.trim() !== "" ||
                effectiveLifecycleDecision !== "" ||
                lifecycleRiskStatus !== ""
              }
            />
          ) : null}
        </Card>

        <Card
          title="API Signal History"
          right={
            <Badge tone="muted">
              {mellyRows.length} entries · read-only
            </Badge>
          }
        >
          <div className="dashboard-muted" style={{ marginBottom: "0.5rem" }}>
            Sprint 1A signal records from the MellyTrade API (read-only,
            confidence clamped to [33, 85]).
          </div>
          <div className="audit-feed-controls">
            <label htmlFor="melly-symbol" className="dashboard-muted">
              Symbol
            </label>
            <input
              id="melly-symbol"
              type="text"
              placeholder="e.g. EURUSD"
              value={mellySymbol}
              onChange={(event) => setMellySymbol(event.target.value)}
              maxLength={16}
            />
            <label htmlFor="melly-status" className="dashboard-muted">
              Status
            </label>
            <select
              id="melly-status"
              value={mellyStatus}
              onChange={(event) =>
                setMellyStatus(event.target.value as MellyStatusFilter)
              }
            >
              <option value="">All</option>
              <option value="accepted">Accepted</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          {mellyLoading && !mellySignals ? (
            <div className="state">Loading API signals...</div>
          ) : null}
          {mellyError && !mellySignals ? (
            <div className="state error">{mellyError}</div>
          ) : null}
          {mellySignals && mellyRows.length === 0 ? (
            <div className="state">No signals match this filter.</div>
          ) : null}
          {mellyRows.length > 0 ? (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Symbol</th>
                    <th>Action</th>
                    <th>Conf</th>
                    <th>Clamped</th>
                    <th>Risk %</th>
                    <th>Status</th>
                    <th>Reason</th>
                    <th>Mode</th>
                  </tr>
                </thead>
                <tbody>
                  {mellyRows.map((row) => {
                    const ts = new Date(row.created_at);
                    const time = Number.isNaN(ts.getTime())
                      ? row.created_at
                      : ts.toLocaleString("en-GB", {
                          day: "2-digit",
                          month: "short",
                          hour: "2-digit",
                          minute: "2-digit",
                          second: "2-digit",
                        });
                    const rowClass =
                      row.status === "rejected" ? "signal-row-rejected" : undefined;
                    return (
                      <tr key={row.id} className={rowClass}>
                        <td>{time}</td>
                        <td>{row.symbol}</td>
                        <td>
                          <Badge tone={actionTone(row.action)}>{row.action}</Badge>
                        </td>
                        <td>{row.confidence.toFixed(1)}</td>
                        <td>{row.confidence_clamped.toFixed(1)}</td>
                        <td>{row.risk_pct.toFixed(2)}%</td>
                        <td>
                          <Badge tone={statusTone(row.status)}>{row.status}</Badge>
                        </td>
                        <td>{row.rejection_reason ?? row.reason ?? "-"}</td>
                        <td>
                          <Badge tone={row.dry_run ? "green" : "amber"}>
                            {row.dry_run ? "dry-run" : "live"}
                          </Badge>{" "}
                          <Badge tone={row.read_only ? "green" : "amber"}>
                            {row.read_only ? "read-only" : "writable"}
                          </Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : null}
        </Card>
      </div>

      <Drawer
        open={Boolean(selectedSignalId && detail)}
        title={detail ? `${detail.symbol} ${detail.direction}` : "Signal Detail"}
        onClose={() => setSelectedSignalId(null)}
      >
        {detail ? (
          <div className="stack">
            <div className="signal-drawer-grid">
              <div className="detail-tile">
                <span>Direction</span>
                <Badge tone={directionTone(detail.direction)}>{detail.direction}</Badge>
              </div>
              <div className="detail-tile">
                <span>Confidence</span>
                <strong>{detail.confidence}%</strong>
              </div>
              <div className="detail-tile">
                <span>Regime</span>
                <strong>{detail.regime}</strong>
              </div>
              <div className="detail-tile">
                <span>R:R</span>
                <strong>{formatOptional(detail.rr)}</strong>
              </div>
            </div>

            <div className="detail-row">
              <span>Levels</span>
              <div className="detail-grid">
                <strong>Entry {formatOptional(detail.entry)}</strong>
                <strong>SL {formatOptional(detail.sl)}</strong>
                <strong>TP {formatOptional(detail.tp)}</strong>
              </div>
            </div>

            {/* DATA-002: explainable AI reasoning panel.
                Replaces the previous inline reasoning + risk-gate rows
                with a structured, collapsible, safety-badged surface.
                Display-only — no execution controls. */}
            <SignalReasoningPanel detail={detail} reasoning={reasoning} />
          </div>
        ) : null}
      </Drawer>
    </div>
  );
}
