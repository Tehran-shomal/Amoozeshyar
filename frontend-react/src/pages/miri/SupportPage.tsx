import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { DynamicForm } from "../../components/DynamicForm";
import { portalPageHref } from "../../app/navigation";

type Row = Record<string, unknown>;
function object(value: unknown): Row { return typeof value === "object" && value !== null ? value as Row : {}; }
function list(value: unknown): Row[] { return Array.isArray(value) ? value.map(object) : []; }
function text(value: unknown, fallback = "—"): string { return value === null || value === undefined || value === "" ? fallback : String(value); }

export function SupportPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const data = payload.data;
  const tickets = list(data.support_tickets);
  const result = data.support_submission_result ? object(data.support_submission_result) : null;
  const resultDate = object(result?.created_at);

  return <>
    {result && <section className="panel support-submission-result" id="support-submission-result" role="status" aria-labelledby="support-result-title">
      <div className="panel-heading"><h2 id="support-result-title">نتیجهٔ ثبت تیکت</h2></div>
      <p>تیکت زیر در سامانه ثبت شده است؛ این پیام به‌تنهایی تأیید دریافت یا پاسخ‌گویی واحد پشتیبانی نیست.</p>
      <dl className="support-result-details">
        <div><dt>کد تیکت</dt><dd>{text(result.id)}</dd></div><div><dt>موضوع</dt><dd>{text(result.subject)}</dd></div>
        <div><dt>وضعیت</dt><dd>{text(result.status, "ثبت‌شده")}</dd></div><div><dt>زمان ثبت</dt><dd>{text(result.created_at_display, text(resultDate.display, ""))}</dd></div>
      </dl>
      <p className="support-attachment-note">{text(data.support_attachment_note, "")}</p>
      <a className="button button--secondary" href={portalPageHref("support", bootstrap)}>متوجه شدم</a>
    </section>}

    {payload.form && <DynamicForm
      schema={payload.form}
      title="ثبت تیکت پشتیبانی"
      submitUrl={bootstrap.submitUrl}
      sectionClassName="panel form-panel support-form-panel"
      formClassName="live-form support-form"
      submitLabel="ارسال تیکت"
    />}
    <p className="support-attachment-note">{text(data.support_attachment_note, "")}</p>

    <section className="panel support-history-panel" aria-labelledby="support-history-title">
      <div className="panel-heading"><h2 id="support-history-title">تیکت‌های اخیر</h2></div>
      <div className="table-wrap"><table className="data-table support-ticket-list">
        <thead><tr><th scope="col">کد</th><th scope="col">موضوع</th><th scope="col">آخرین پاسخ</th><th scope="col">وضعیت</th></tr></thead>
        <tbody>{tickets.length ? tickets.map((ticket, index) => {
          const reply = ticket.latest_reply ? object(ticket.latest_reply) : null;
          return <tr key={`${ticket.id}-${index}`}>
            <td>{text(ticket.id)}</td><td>{text(ticket.subject)}</td>
            <td>{reply ? <><span>{text(reply.content, "")}</span><small className="support-reply-date">{text(reply.created_at_display, "")}</small></> : "پاسخی ثبت نشده"}</td>
            <td>{text(ticket.status)}</td>
          </tr>;
        }) : <tr><td colSpan={4} className="empty-state">تیکتی برای حساب شما ثبت نشده است.</td></tr>}</tbody>
      </table></div>
    </section>
    <p className="support-privacy-warning">اطلاعات کارت بانکی و گذرواژه را در پیام یا پیوست ارسال نکنید.</p>
  </>;
}
