import { Card } from "../components/shared/Card";
import { Table } from "../components/shared/Table";
import { useLogs } from "../hooks/useLogs";

export function LogsPage() {
  const { data } = useLogs();

  return (
    <Card title="Logs">
      {data ? (
        <Table
          columns={[
            { key: "timestamp", label: "Time", render: (row) => row.timestamp },
            { key: "category", label: "Category", render: (row) => row.category },
            { key: "severity", label: "Severity", render: (row) => row.severity },
            { key: "message", label: "Message", render: (row) => row.message },
          ]}
          rows={data}
        />
      ) : null}
    </Card>
  );
}

