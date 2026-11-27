import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";
import { asList, asObject, displayCount, displayText } from "./display";

export function AttendancePage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const data = payload.data;
  if (!payload.shell.current_profile) {
    return <section className="panel attendance-empty-panel"><p className="empty-state">برای مشاهدهٔ حضور و غیاب، پروندهٔ دانشجویی را از سربرگ انتخاب کنید.</p></section>;
  }

  const rows = asList(data.attendance_rows).map(asObject);
  const metrics: Array<[string, string]> = [
    ["نیمسال تحصیلی", displayText(data.attendance_term)],
    ["درس فعال", `${displayCount(data.attendance_active_course_count)} درس / ${displayCount(data.attendance_active_units)} واحد`],
    ["غیبت ثبت‌شده", `${displayCount(data.attendance_absence_count)} جلسه`],
    ["حضور ثبت‌شده", `${displayCount(data.attendance_present_count)} از ${displayCount(data.attendance_session_count)} جلسه`],
  ];

  return <>
    <section className="attendance-metrics" aria-label="خلاصه حضور و غیاب"
      data-attendance-total={displayCount(data.attendance_session_count)}
      data-attendance-absences={displayCount(data.attendance_absence_count)}
      data-attendance-active-courses={displayCount(data.attendance_active_course_count)}>
      {metrics.map(([label, value]) => <div className="attendance-metric" key={label}><span>{label}</span><strong>{value}</strong></div>)}
    </section>

    <section className="panel data-panel attendance-table-panel">
      <div className="panel-heading"><h2>وضعیت حضور در درس‌ها</h2></div>
      <div className="table-wrap"><table className="data-table attendance-table">
        <thead><tr><th scope="col">نام درس / استاد</th><th scope="col">جلسات ثبت‌شده</th><th scope="col">حاضر</th><th scope="col">غیبت</th><th scope="col">وضعیت ثبت‌نام</th></tr></thead>
        <tbody>{rows.length ? rows.map((row, index) => <tr data-enrollment-id={displayText(row.enrollment_id, "")} key={`${row.enrollment_id ?? index}`}>
          <td className="attendance-course-copy"><strong>{displayText(row.lesson)}</strong><small>{displayText(row.teacher)}</small></td>
          <td>{displayCount(row.session_count)}</td>
          <td>{displayCount(row.present_count)}{Number(row.late_count) || Number(row.unclassified_count) ? <small className="attendance-secondary-count">تأخیر {displayCount(row.late_count)} · نامشخص {displayCount(row.unclassified_count)}</small> : null}</td>
          <td>{displayCount(row.absent_count)}</td><td>{displayText(row.enrollment_status)}</td>
        </tr>) : <tr><td colSpan={5} className="empty-state">برای این نیمسال درس فعال یا سابقهٔ حضوری ثبت نشده است.</td></tr>}</tbody>
      </table></div>
    </section>

    <aside className="attendance-warning" role="note">حد مجاز غیبت مطابق مقررات هر درس محاسبه می‌شود؛ این صفحه فقط سابقه‌های ثبت‌شده را نمایش می‌دهد. برای اصلاح سابقه با استاد درس ارتباط بگیرید.</aside>
    <footer className="attendance-footer">
      <p className="attendance-update">آخرین ثبت: {displayText(data.attendance_last_updated, "ثبت نشده")} · تأخیر ثبت‌شده: {displayCount(data.attendance_late_count)} · وضعیت نامشخص: {displayCount(data.attendance_unclassified_count)}</p>
      <a className="button button--primary" href={portalPageHref("messages", bootstrap)}>ارتباط با استاد</a>
    </footer>
  </>;
}
