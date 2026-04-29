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
  const hasRows = rows.length > 0;

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
          {hasRows ? (
            rows.map((row) => (
              <tr
                key={row.id}
                className={onRowClick ? "table-row-clickable" : undefined}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((column) => (
                  <td key={column.key}>{column.render(row)}</td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td className="table-empty" colSpan={columns.length}>
                No rows available
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
