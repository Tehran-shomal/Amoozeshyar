import { useState, type FormEvent } from "react";
import { PortalApi } from "../api/client";

interface MarkReadFormProps {
  submitUrl: string;
  field: "communication_id" | "notification_id";
  id: number;
  label: string;
  ariaLabel: string;
}

export function MarkReadForm({ submitUrl, field, id, label, ariaLabel }: MarkReadFormProps) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const result = await PortalApi.submitPage(submitUrl, { [field]: id });
      if (result.redirect) {
        window.location.assign(result.redirect);
        return;
      }
      if (result.error) setError(result.error.message);
      else window.location.reload();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "ثبت وضعیت خواندن انجام نشد.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <form method="post" className="live-form" onSubmit={submit}>
        <button type="submit" className="button button--soft" aria-label={ariaLabel} disabled={busy}>
          {busy ? "در حال ثبت…" : label}
        </button>
      </form>
      {error && <div className="inline-notice" role="alert"><p>{error}</p></div>}
    </>
  );
}
