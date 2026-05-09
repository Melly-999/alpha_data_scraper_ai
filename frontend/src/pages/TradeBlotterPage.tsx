import { Card } from "../components/shared/Card";
import { ResourceState } from "../components/shared/ResourceState";
import { Table } from "../components/shared/Table";
import { usePollingResource } from "../hooks/usePollingResource";
import { apiGet } from "../lib/api";
import type { OrderRow } from "../types/api";

export function TradeBlotterPage() {
  const orders = usePollingResource(() => apiGet<OrderRow[]>("/orders"), 5000);

  return (
    <Card title="Trade Blotter">
      <ResourceState
        loading={orders.loading}
        error={orders.error}
        empty={!orders.data || orders.data.length === 0}
        lastUpdatedAt={orders.lastUpdatedAt}
        emptyMessage="No dry-run orders recorded yet."
        loadingMessage="Loading dry-run blotter …"
      >
        {orders.data ? (
          <Table
            columns={[
              { key: "symbol", label: "Symbol", render: (row) => row.symbol },
              {
                key: "direction",
                label: "Direction",
                render: (row) => row.direction,
              },
              { key: "status", label: "Status", render: (row) => row.status },
              { key: "notes", label: "Notes", render: (row) => row.notes },
            ]}
            rows={orders.data}
          />
        ) : null}
      </ResourceState>
    </Card>
  );
}
