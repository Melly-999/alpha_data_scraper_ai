import { Card } from "../components/shared/Card";
import { ResourceState } from "../components/shared/ResourceState";
import { Table } from "../components/shared/Table";
import { useOpenPositions, usePositionHistory } from "../hooks/usePositions";

export function PositionsPage() {
  const openPositions = useOpenPositions();
  const history = usePositionHistory();

  return (
    <div className="page-grid">
      <Card title="Open Positions">
        <ResourceState
          loading={openPositions.loading}
          error={openPositions.error}
          empty={!openPositions.data || openPositions.data.length === 0}
          lastUpdatedAt={openPositions.lastUpdatedAt}
          emptyMessage="No open positions in the dry-run book yet."
          loadingMessage="Loading open positions …"
        >
          {openPositions.data ? (
            <Table
              columns={[
                { key: "symbol", label: "Symbol", render: (row) => row.symbol },
                {
                  key: "direction",
                  label: "Direction",
                  render: (row) => row.direction,
                },
                {
                  key: "unrealized_pnl",
                  label: "Unrealized",
                  render: (row) => row.unrealized_pnl?.toFixed(2) ?? "—",
                },
              ]}
              rows={openPositions.data}
            />
          ) : null}
        </ResourceState>
      </Card>
      <Card title="Position History">
        <ResourceState
          loading={history.loading}
          error={history.error}
          empty={!history.data || history.data.length === 0}
          lastUpdatedAt={history.lastUpdatedAt}
          emptyMessage="No closed positions recorded yet."
          loadingMessage="Loading position history …"
        >
          {history.data ? (
            <Table
              columns={[
                { key: "symbol", label: "Symbol", render: (row) => row.symbol },
                {
                  key: "direction",
                  label: "Direction",
                  render: (row) => row.direction,
                },
                {
                  key: "realized_pnl",
                  label: "Realized",
                  render: (row) => row.realized_pnl?.toFixed(2) ?? "—",
                },
              ]}
              rows={history.data}
            />
          ) : null}
        </ResourceState>
      </Card>
    </div>
  );
}
