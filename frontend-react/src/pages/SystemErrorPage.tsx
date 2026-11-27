interface SystemErrorPageProps {
  status?: number;
  title: string;
  message: string;
  onRetry: () => void;
}

export function SystemErrorPage({ status, title, message, onRetry }: SystemErrorPageProps) {
  return (
    <main className="portal-page-loading" role="alert" data-error-status={status || undefined}>
      <section className="panel">
        <h1>{title}</h1>
        <p>{message}</p>
        <button className="button button--soft" type="button" onClick={onRetry}>تلاش دوباره</button>
      </section>
    </main>
  );
}
