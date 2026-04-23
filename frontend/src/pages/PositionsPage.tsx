import { Card } from "../components/shared/Card";
import { Table } from "../components/shared/Table";
import { useOpenPositions, usePositionHistory } from "../hooks/usePositions";

export function PositionsPage() {
  const openPositions = useOpenPositions();
  const history = usePositionHistory();

  return (
    <div className="page-grid">
      <Card title="Open Positions">
        {openPositions.data ? (
          <Table
            columns={[
              { key: "symbol", label: "Symbol", render: (row) => row.symbol },
              { key: "direction", label: "Direction", render: (row) => row.direction },
              {
                key: "unrealized_pnl",
                label: "Unrealized",
                render: (row) => row.unrealized_pnl?.toFixed(2) ?? "—",
              },
            ]}
            rows={openPositions.data}
          />
        ) : null}
      </Card>
      <Card title="Position History">
        {history.data ? (
          <Table
            columns={[
              { key: "symbol", label: "Symbol", render: (row) => row.symbol },
              { key: "direction", label: "Direction", render: (row) => row.direction },
              {
                key: "realized_pnl",
                label: "Realized",
                render: (row) => row.realized_pnl?.toFixed(2) ?? "—",
              },
            ]}
            rows={history.data}
          />
        ) : null}
      </Card>
    </div>
  );
}

