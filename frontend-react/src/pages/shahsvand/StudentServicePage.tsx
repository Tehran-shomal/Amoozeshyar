import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";
import { DynamicForm } from "../../components/DynamicForm";
import { DataTable, isTableData } from "../../components/DataTable";
import { OperationResult } from "../../components/OperationResult";
import { asList, asObject, text } from "../shaghayegh/shared";

export function StudentServicePage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const data = payload.data;
  const tables = asList(data.tables).filter(isTableData);
  const result = data.operation_result && typeof data.operation_result === "object"
    ? data.operation_result as { heading?: string; message?: string; status?: string; created_at?: string; note?: string }
    : null;
  const profile = payload.shell.current_profile;

  if (payload.page === "graduation") return <GraduationPage payload={payload} bootstrap={bootstrap} tables={tables} />;
  if (payload.page === "graduation-certificate") return <GraduationCertificatePage payload={payload} bootstrap={bootstrap} tables={tables} />;
  if (!profile) return <section className="panel"><p className="empty-state">برای ثبت یا پیگیری این درخواست، ابتدا پروندهٔ دانشجویی را انتخاب کنید.</p></section>;

  const submission = data.service_submission_result ? asObject(data.service_submission_result) : null;
  if (payload.page === "internship") return <>
    {submission && <section className="panel internship-submission-result" role="status" aria-live="polite"><div className="panel-heading"><h2>نتیجهٔ عملیات</h2></div>
      <p>درخواست کارآموزی «{text(submission.company_name)}» با شناسهٔ {text(submission.id)} در سامانه ثبت شد.</p>
      <p>وضعیت فعلی: {text(submission.status)} · تاریخ ثبت: {text(submission.created_at)}</p>
      <p className="internship-form-note">این فقط ثبت داخلی درخواست است؛ ارسال به سامانهٔ دانشگاه انجام نشده و به‌معنی تأیید رسمی نیست.</p>
      <a className="button button--primary" href={portalPageHref("internship", bootstrap)}>متوجه شدم</a>
    </section>}
    {payload.form ? <DynamicForm schema={payload.form} title={`اطلاعات کارآموزی / نیمسال ${payload.term.display_label}`} submitUrl={bootstrap.submitUrl} sectionClassName="panel internship-form-panel" formClassName="live-form internship-application-form" fieldsClassName="internship-form-grid" submitLabel="ارسال برای بررسی" />
      : <section className="panel internship-form-panel"><p className="empty-state">فرم کارآموزی برای این پرونده در دسترس نیست.</p></section>}
    <p className="internship-form-note" role="note">در مدل فعلی فقط نوع درخواست، نام سازمان، تاریخ شروع و مدت به ساعت ذخیره می‌شود؛ اطلاعات استاد ناظر، تماس/نشانی و فایل نامهٔ پذیرش در این پایگاه داده قابل ثبت نیست.</p>
    {tables.map((table, index) => <DataTable table={table} key={`internship-${index}`} />)}
  </>;

  if (payload.page === "guest-request") return <>
    {submission && <section className="panel guest-request-submission-result" role="status" aria-live="polite"><div className="panel-heading"><h2>نتیجهٔ عملیات</h2></div>
      <p>درخواست مهمانی با شناسهٔ {text(submission.id)} برای «{text(submission.destination)}» در سامانه ثبت شد.</p>
      <p>وضعیت بررسی: {text(submission.status)} · تاریخ ثبت: {text(submission.created_at)}</p>
      <p className="guest-request-note">این ثبت داخلی است؛ تأیید نهایی پس از بررسی انجام می‌شود و ارسال خودکار به دانشگاه مقصد صورت نگرفته است.</p>
      <a className="button button--primary" href={portalPageHref("guest-request", bootstrap)}>متوجه شدم</a>
    </section>}
    {payload.form ? <DynamicForm schema={payload.form} title={`درخواست جدید / نیمسال ${payload.term.display_label}`} submitUrl={bootstrap.submitUrl} sectionClassName="panel guest-request-form-panel" formClassName="live-form guest-request-application-form" fieldsClassName="guest-request-form-grid" submitLabel="ثبت درخواست مهمانی" />
      : <section className="panel guest-request-form-panel"><p className="empty-state">فرم درخواست برای این پرونده در دسترس نیست.</p></section>}
    <div className="page-actions guest-request-actions"><p className="guest-request-note" role="note">فرم فعلی فقط دانشگاه مقصد را ذخیره می‌کند؛ مبدأ، نوع مهمانی، تماس، دلیل و فایل مدرک در مدل موجود نیست.</p></div>
    {tables.map((table, index) => <DataTable table={table} key={`guest-${index}`} />)}
  </>;

  return <>
    {typeof data.notice === "string" && <div className="inline-notice" role="note"><p>{data.notice}</p></div>}
    {result && <OperationResult result={result} />}
    {tables.map((table, index) => <DataTable table={table} key={`${payload.page}-${index}`} />)}
    {payload.form && <DynamicForm schema={payload.form} title={formTitle(payload.page)} submitUrl={bootstrap.submitUrl} submitLabel={submitLabel(payload.page)} />}
  </>;
}

function GraduationPage({ payload, bootstrap, tables }: { payload: PagePayload; bootstrap: PortalBootstrap; tables: Array<{ title?: string; columns?: unknown[]; rows?: Array<{ cells?: unknown[] }> }> }) {
  if (!payload.shell.current_profile) return <section className="panel"><p className="empty-state">برای مشاهدهٔ وضعیت فارغ‌التحصیلی، پروندهٔ دانشجویی را انتخاب کنید.</p></section>;
  const checks = asList(payload.data.graduation_checks).map(asObject);
  return <>
    {typeof payload.data.notice === "string" && <div className="inline-notice graduation-warning" role="status"><p>{payload.data.notice}</p></div>}
    <section className="panel graduation-checklist-panel" data-graduation-audits={text(payload.data.graduation_audit_count, "0")}>
      <div className="panel-heading"><h2>چک‌لیست اطلاعات قابل بررسی</h2></div>
      <div className="graduation-check-list">{checks.map((check, index) => <article className={`graduation-check-row graduation-check-row--${text(check.state, "review")}`} key={`${check.label ?? index}`}>
        <strong>{text(check.label)}</strong><span>{text(check.value)}</span><small>{text(check.status)}</small>
      </article>)}</div>
    </section>
    {tables.map((table, index) => <ServiceTable table={table} className="graduation-history-panel" tableClassName="graduation-audit-table" emptyLabel="بررسی آموزشی برای این پرونده ثبت نشده است." key={index} />)}
    <div className="page-actions graduation-actions"><a className="button button--primary" href={portalPageHref("curriculum", bootstrap)}>مشاهدهٔ چارت دروس</a><a className="button button--soft" href={portalPageHref("tuition", bootstrap)}>بررسی مالی</a><button className="button button--disabled" type="button" disabled aria-describedby="graduation-submit-reason">ثبت نهایی در این نسخه ممکن نیست</button></div>
    <p id="graduation-submit-reason" className="graduation-submit-note">نوع درخواست معتبر و اتصال شرط معدل/کتابخانه به سامانه تعریف نشده است؛ این صفحه نتیجهٔ رسمی فارغ‌التحصیلی صادر نمی‌کند.</p>
  </>;
}

function GraduationCertificatePage({ payload, bootstrap, tables }: { payload: PagePayload; bootstrap: PortalBootstrap; tables: Array<{ title?: string; columns?: unknown[]; rows?: Array<{ cells?: unknown[] }> }> }) {
  const student = payload.data.certificate_student ? asObject(payload.data.certificate_student) : null;
  if (!payload.shell.current_profile || !student) return <section className="panel"><p className="empty-state">برای مشاهدهٔ وضعیت مدرک، ابتدا پروندهٔ دانشجویی را انتخاب کنید.</p></section>;
  const steps = asList(payload.data.certificate_steps).map(asObject);
  return <>
    {typeof payload.data.notice === "string" && <div className="inline-notice graduation-warning" role="status"><p>{payload.data.notice}</p></div>}
    <section className="panel graduation-certificate-summary"><div className="panel-heading"><h2>وضعیت پروندهٔ {text(student.full_name)}</h2></div><dl className="key-value-list">
      <div><dt>شماره دانشجویی</dt><dd>{text(student.student_code)}</dd></div><div><dt>رشته و مقطع</dt><dd>{text(student.field_name)} · {text(student.educational_level)}</dd></div>
      <div><dt>وضعیت فعلی</dt><dd>{text(student.status)}</dd></div><div><dt>واحد گذرانده در پرونده</dt><dd>{text(student.passed_units, "0")} واحد</dd></div>
      <div><dt>واحدهای چارت فعال</dt><dd>{text(payload.data.certificate_curriculum_units)}</dd></div><div><dt>ماندهٔ بدهی پرونده</dt><dd>{text(student.tuition_debt_display)} ریال</dd></div>
    </dl><p>شرط‌های رسمی فراغت و تسویهٔ کتابخانه در این صفحه به‌طور مستقل قابل تأیید نیستند؛ برای ارزیابی معتبر به آموزش مراجعه کنید.</p></section>
    <section className="panel graduation-certificate-documents"><div className="panel-heading"><h2>مدارک و شرایط</h2></div><p>فهرست مدارک لازم و بارگذاری تصویر/رسید در مدل فعلی ثبت نمی‌شود. پس از احراز شرایط، نوع مدرک قابل دریافت باید از آموزش تأیید شود.</p>
      {tables[0]?.rows?.length ? <ServiceTable table={tables[0]} /> : <p className="empty-state">بررسی رسمی برای این پرونده ثبت نشده است.</p>}
    </section>
    <div className="page-actions graduation-certificate-actions"><a className="button button--primary" href={portalPageHref("graduation", bootstrap)}>بررسی شرایط فراغت</a><a className="button button--soft" href={portalPageHref("curriculum", bootstrap)}>چارت دروس</a></div>
    <section className="panel graduation-certificate-workflow" aria-labelledby="graduation-certificate-workflow-title"><div className="panel-heading"><h2 id="graduation-certificate-workflow-title">مسیر صدور مدرک</h2></div><ol>
      {steps.map((step, index) => <li key={`${step.title ?? index}`}><strong>{text(step.title)}</strong><span>{text(step.status)}</span></li>)}
    </ol><p>هیچ مرحله‌ای با نمایش این مسیر تأیید نمی‌شود؛ درخواست معتبر صدور و سرویس رسمی متصل نیست.</p></section>
  </>;
}

function ServiceTable({ table, className = "", tableClassName = "", emptyLabel }: { table: { title?: string; columns?: unknown[]; rows?: Array<{ cells?: unknown[] }> }; className?: string; tableClassName?: string; emptyLabel?: string }) {
  const columns = table.columns || [];
  const rows = table.rows || [];
  return <section className={`panel data-panel ${className}`}><div className="panel-heading"><h2>{table.title || "اطلاعات"}</h2></div><div className="table-wrap"><table className={`data-table ${tableClassName}`}>
    <thead><tr>{columns.map((column, index) => <th scope="col" key={index}>{text(column, "")}</th>)}</tr></thead>
    <tbody>{rows.length ? rows.map((row, rowIndex) => <tr key={rowIndex}>{(row.cells || []).map((cell, cellIndex) => <td key={cellIndex}>{text(cell)}</td>)}</tr>) : <tr><td colSpan={Math.max(columns.length, 1)} className="empty-state">{emptyLabel || "اطلاعاتی برای نمایش ثبت نشده است."}</td></tr>}</tbody>
  </table></div></section>;
}

function formTitle(slug: string): string {
  return ({
    "financial-aid": "ثبت درخواست تسهیلات",
    requests: "ثبت درخواست دانشجویی",
    "education-certificate": "ثبت درخواست گواهی آموزشی",
  } as Record<string, string>)[slug] || "ثبت اطلاعات";
}

function submitLabel(slug: string): string {
  return ({
    "financial-aid": "ثبت درخواست تسهیلات",
    requests: "ثبت درخواست",
    "education-certificate": "ثبت درخواست گواهی",
  } as Record<string, string>)[slug] || "ثبت اطلاعات";
}
