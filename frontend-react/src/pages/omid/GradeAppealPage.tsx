import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { DynamicForm } from "../../components/DynamicForm";
import { DataTable, isTableData } from "../../components/DataTable";
import { OperationResult } from "../../components/OperationResult";

export function GradeAppealPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const data = payload.data;
  const tables = Array.isArray(data.tables) ? data.tables.filter(isTableData) : [];
  const result = typeof data.operation_result === "object" && data.operation_result !== null
    ? data.operation_result as { heading?: string; message?: string; status?: string; created_at?: string; note?: string }
    : null;
  return <>
    {typeof data.notice === "string" && <div className="inline-notice" role="note"><p>{data.notice}</p></div>}
    {result && <OperationResult result={result} />}
    {tables.map((table, index) => <DataTable table={table} key={`${table.title || "table"}-${index}`} />)}
    {payload.form && <DynamicForm schema={payload.form} title="ثبت درخواست اعتراض به نمره" submitUrl={bootstrap.submitUrl} formClassName="live-form appeal-form" submitLabel="ثبت درخواست" />}
  </>;
}
