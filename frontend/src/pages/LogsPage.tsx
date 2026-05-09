import { Card } from "../components/shared/Card";
import { ResourceState } from "../components/shared/ResourceState";
import { Table } from "../components/shared/Table";
import { useLogs } from "../hooks/useLogs";

export function LogsPage() {
  const { data, loading, error, lastUpdatedAt } = useLogs();

  return (
    <Card title="Logs">
      <ResourceState
        loading={loading}
        error={error}
        empty={!data || data.length === 0}
        lastUpdatedAt={lastUpdatedAt}
        emptyMessage="No log entries in the current window."
        loadingMessage="Loading recent log entries …"
      >
        {data ? (
          <Table
            columns={[
              {
                key: "timestamp",
                label: "Time",
                render: (row) => row.timestamp,
              },
              {
                key: "category",
                label: "Category",
                render: (row) => row.category,
              },
              {
                key: "severity",
                label: "Severity",
                render: (row) => row.severity,
              },
              {
                key: "message",
                label: "Message",
                render: (row) => row.message,
              },
            ]}
            rows={data}
          />
        ) : null}
      </ResourceState>
    </Card>
  );
}
