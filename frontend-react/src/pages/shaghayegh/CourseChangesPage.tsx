import { useEffect, useRef, useState } from "react";
import type { PagePayload } from "../../api/types";
import { PortalApi } from "../../api/client";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";
import { OfferingPicker } from "./OfferingPicker";
import { enrollmentErrorMessage, pageHrefWith, asList, asObject, text } from "./shared";

export function CourseChangesPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const [dropRow, setDropRow] = useState<Record<string, unknown> | null>(null);
  const [dropBusy, setDropBusy] = useState(false);
  const [dropError, setDropError] = useState("");
  const dropBusyRef = useRef(false);
  const dropDialogRef = useRef<HTMLElement>(null);
  const cancelDropButtonRef = useRef<HTMLButtonElement>(null);
  const dropOpenerRef = useRef<HTMLButtonElement | null>(null);
  const data = payload.data;
  const overview = asObject(data.course_overview);
  const table = asObject(data.course_change_table);
  const columns = asList(table.columns);
  const rows = asList(table.rows).map(asObject);
  const emergency = payload.page === "emergency-drop";
  const registrationResult = data.course_registration_result ? asObject(data.course_registration_result) : null;
  const dropResult = data.course_drop_result ? asObject(data.course_drop_result) : null;
  const studentCode = payload.profile.student_code;

  function closeDropDialog() {
    if (dropBusyRef.current) return;
    setDropRow(null);
    setDropError("");
    window.setTimeout(() => dropOpenerRef.current?.focus(), 0);
  }

  useEffect(() => {
    if (!dropRow) return;
    document.body.classList.add("modal-open");
    cancelDropButtonRef.current?.focus();
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && !dropBusyRef.current) {
        event.preventDefault();
        closeDropDialog();
        return;
      }
      if (event.key !== "Tab") return;

      const dialog = dropDialogRef.current;
      if (!dialog) return;
      const focusable = Array.from(dialog.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
      ));
      if (!focusable.length) {
        event.preventDefault();
        dialog.focus();
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      const active = document.activeElement;
      if (event.shiftKey && (active === first || !dialog.contains(active))) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && (active === last || !dialog.contains(active))) {
        event.preventDefault();
        first.focus();
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.classList.remove("modal-open");
    };
  }, [dropRow]);

  if (!payload.shell.current_profile || !Object.keys(overview).length) {
    return <section className="panel"><p className="empty-state">برای تغییر ثبت‌نام، ابتدا پروندهٔ دانشجویی را انتخاب کنید.</p></section>;
  }

  async function confirmDrop() {
    if (!dropRow || dropBusyRef.current) return;
    dropBusyRef.current = true;
    setDropBusy(true);
    setDropError("");
    try {
      const id = Number(dropRow.id);
      const response = emergency
        ? await PortalApi.emergencyDropEnrollment(id, studentCode)
        : await PortalApi.dropEnrollment(id, studentCode);
      if (!response.enrollment?.id) throw new Error("پاسخ حذف شناسهٔ ثبت‌نام را برنگرداند.");
      window.location.assign(pageHrefWith(payload.page, bootstrap, {
        student_code: studentCode,
        registration_id: null,
        dropped_enrollment_id: response.enrollment.id,
      }));
    } catch (error) {
      setDropError(enrollmentErrorMessage(error));
    } finally {
      dropBusyRef.current = false;
      setDropBusy(false);
    }
  }

  return <>
    <section className="panel student-course-summary"><dl className="summary-rows">
      <div><dt>نام و نام خانوادگی</dt><dd>{text(overview.full_name)}</dd></div><div><dt>شماره دانشجویی</dt><dd>{text(overview.student_code)}</dd></div>
      <div><dt>رشته و مقطع</dt><dd>{text(overview.field_name)} · {text(overview.educational_level)}</dd></div><div><dt>نیمسال و وضعیت</dt><dd>{text(payload.term.display_label)} · {text(overview.status)}</dd></div>
    </dl></section>
    <div className="course-warning-panel"><div>
      {Number(overview.tuition_debt) > 0 ? <p>در پروندهٔ دانشجو بدهی شهریهٔ {text(overview.tuition_debt_display)} ریال ثبت شده است.</p> : <p>{emergency ? "درخواست حذف طبق وضعیت نیمسال و پروندهٔ آموزشی در سامانه بررسی می‌شود." : "درخواست حذف طبق وضعیت نیمسال و پروندهٔ آموزشی در سامانه بررسی می‌شود."}</p>}
      <small>سقف مجاز: {text(overview.maximum_allowed_units, "۰")} واحد · زمان مجاز از تنظیمات نیمسال خوانده می‌شود؛ حداقل واحد در API تعریف نشده است.</small>
    </div>{!emergency && <OfferingPicker bootstrap={bootstrap} termCode={payload.term.term_code} studentCode={studentCode} shell={payload.shell} overview={overview} successSlug="add-drop" />}</div>

    {registrationResult && <section className="panel course-registration-result" role="status" aria-live="polite"><div className="panel-heading"><h2>نتیجهٔ ثبت درس</h2></div><p><strong>{text(registrationResult.lesson)}</strong> در برنامهٔ این نیمسال ثبت فعال دارد.</p><p>کد درس: {text(registrationResult.lesson_code)} · وضعیت: {text(registrationResult.status, "ثبت‌شده")}</p><a className="button button--soft" href={portalPageHref(payload.page, bootstrap)}>شروع دوباره سناریو</a></section>}
    {dropResult && <section className="panel course-drop-result" role="status" aria-live="polite"><div className="panel-heading"><h2>{emergency ? "نتیجهٔ حذف اضطراری" : "نتیجهٔ حذف درس"}</h2></div><p><strong>{text(dropResult.lesson)}</strong> ({text(dropResult.lesson_code)}) حذف‌شده ثبت شد.</p><p>وضعیت: {text(dropResult.status)}{dropResult.drop_date && dropResult.drop_date !== "—" ? ` · تاریخ حذف: ${text(dropResult.drop_date)}` : ""}</p><p>برای این حذف بازپرداخت مالی ثبت نشده است؛ این API فقط وضعیت ثبت‌نام را تغییر می‌دهد.</p><a className="button button--soft" href={portalPageHref(payload.page, bootstrap)}>شروع دوباره سناریو</a></section>}

    <section className="panel data-panel course-change-table"><div className="panel-heading"><h2>{emergency ? "دروس قابل حذف اضطراری" : "دروس ثبت‌شده"}</h2></div><div className="table-wrap"><table className="data-table">
      <thead><tr>{columns.map((column, index) => <th scope="col" key={index}>{text(column, "")}</th>)}</tr></thead>
      <tbody>{rows.length ? rows.map((row, index) => <tr key={text(row.id, String(index))}>{asList(row.cells).map((cell, cellIndex) => <td key={cellIndex}>{text(cell)}</td>)}<td><button className="table-action" type="button" onClick={(event) => { dropOpenerRef.current = event.currentTarget; setDropError(""); setDropRow(row); }}>{text(row.action_label, emergency ? "حذف اضطراری" : "حذف درس")}</button></td></tr>) : <tr><td colSpan={Math.max(columns.length, 1)} className="empty-state">برای این نیمسال ثبت‌نام فعالی وجود ندارد.</td></tr>}</tbody>
    </table></div></section>

    <section className="course-totals" aria-label="خلاصهٔ ثبت‌نام نیمسال"><div><span>مجموع واحدهای فعال</span><strong>{text(data.course_change_units, "۰")}</strong></div><div><span>سقف مجاز واحد</span><strong>{text(data.maximum_allowed_units, "۰")}</strong></div></section>
    <p className="action-note">{emergency ? "حذف اضطراری فقط در بازهٔ تعیین‌شده برای نیمسال پذیرفته می‌شود و درخواست استرداد وجه ایجاد نمی‌کند." : "پس از پاسخ API، جدول با وضعیت ثبت‌نام به‌روز می‌شود؛ قاعدهٔ حداقل واحد در سرویس ثبت‌نام وجود ندارد."}</p>
    <p className="course-totals-note">تعرفهٔ شهریه برای این نیمسال در داده‌های سامانه ثبت نشده است؛ مبلغی حدس زده نمی‌شود.</p>

    {dropRow && <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) closeDropDialog(); }}><section ref={dropDialogRef} className={`modal-dialog drop-confirm-dialog${emergency ? " drop-confirm-dialog--emergency" : ""}`} role="dialog" aria-modal="true" aria-labelledby="drop-dialog-title" aria-describedby="drop-dialog-description" tabIndex={-1}>
      <header className="modal-heading"><h2 id="drop-dialog-title">{emergency ? "تأیید حذف اضطراری" : "تأیید حذف درس"}</h2></header>
      <h3>{text(dropRow.course_name)}</h3><p className="course-modal-meta">کد درس: {text(dropRow.course_code)} · {text(dropRow.units, "۰")} واحد</p>
      <p id="drop-dialog-description">با تأیید، وضعیت ثبت‌نام این درس در نیمسال به «حذف‌شده» تغییر می‌کند.</p>
      {emergency ? <p className="emergency-drop-warning">حذف اضطراری بازپرداخت ثبت نمی‌کند؛ API فعلی فقط وضعیت ثبت‌نام را تغییر می‌دهد.</p> : <p>API فعلی مبلغ بازپرداخت را محاسبه یا ثبت نمی‌کند؛ تغییر شهریه از این صفحه تضمین نمی‌شود.</p>}
      {dropError && <div className="inline-notice" role="alert"><p>{dropError}</p></div>}
      <div className="page-actions"><button className="button button--primary" type="button" onClick={confirmDrop} disabled={dropBusy}>{dropBusy ? "در حال ثبت…" : "تأیید نهایی حذف"}</button><button ref={cancelDropButtonRef} className="button button--soft" type="button" onClick={closeDropDialog} disabled={dropBusy}>انصراف</button></div>
    </section></div>}
  </>;
}
