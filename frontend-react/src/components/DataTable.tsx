interface TableRow {
  cells?: unknown[];
  id?: string | number;
  action_label?: string;
}

interface TableData {
  title?: string;
  columns?: unknown[];
  rows?: TableRow[];
}

export function isTableData(value: unknown): value is TableData {
  return typeof value === "object" && value !== null &&
    Array.isArray((value as TableData).columns) && Array.isArray((value as TableData).rows);
}

export function DataTable({ table }: { table: TableData }) {
  const columns = table.columns || [];
  const rows = table.rows || [];
  return (
    <section className="panel data-panel">
      <div className="panel-heading panel-heading--table"><h2>{table.title || "اطلاعات"}</h2></div>
      <div className="table-wrap">
        <table className="data-table">
          <thead><tr>{columns.map((column, index) => <th key={index} scope="col">{String(column ?? "")}</th>)}</tr></thead>
          <tbody>
            {rows.length ? rows.map((row, rowIndex) => (
              <tr key={row.id ?? rowIndex}>
                {(row.cells || []).map((cell, cellIndex) => <td key={cellIndex}>{displayCell(cell)}</td>)}
              </tr>
            )) : <tr><td className="empty-cell" colSpan={Math.max(columns.length, 1)}>اطلاعاتی برای نمایش ثبت نشده است.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function displayCell(value: unknown) {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "string" || typeof value === "number") return value;
  if (typeof value === "boolean") return value ? "بله" : "خیر";
  return JSON.stringify(value);
}
