import type { ReactNode } from "react";

interface Column<T> {
  key: string;
  label: string;
  render: (row: T) => ReactNode;
}

interface TableProps<T extends { id: string }> {
  columns: Array<Column<T>>;
  rows: T[];
  onRowClick?: (row: T) => void;
}

export function Table<T extends { id: string }>({
  columns,
  rows,
  onRowClick,
}: TableProps<T>) {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id} onClick={() => onRowClick?.(row)}>
              {columns.map((column) => (
                <td key={column.key}>{column.render(row)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

