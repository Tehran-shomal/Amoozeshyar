interface OperationResultData {
  heading?: string;
  message?: string;
  status?: string;
  created_at?: string;
  note?: string;
}

export function OperationResult({ result }: { result: OperationResultData }) {
  return (
    <section className="panel operation-result" role="status">
      {result.heading && <h2>{result.heading}</h2>}
      {result.message && <p>{result.message}</p>}
      {(result.status || result.created_at) && (
        <dl className="key-value-list">
          {result.status && <div><dt>وضعیت</dt><dd>{result.status}</dd></div>}
          {result.created_at && <div><dt>تاریخ ثبت</dt><dd>{result.created_at}</dd></div>}
        </dl>
      )}
      {result.note && <small>{result.note}</small>}
    </section>
  );
}
