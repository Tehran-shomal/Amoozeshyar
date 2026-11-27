import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";
import { asList, asObject, displayText, displayTime } from "./display";

export function SchedulePage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  if (!payload.shell.current_profile) {
    return <section className="panel"><p className="empty-state">برای مشاهدهٔ برنامهٔ هفتگی، پروندهٔ دانشجویی را انتخاب کنید.</p></section>;
  }

  const data = payload.data;
  const summary = asObject(data.schedule_summary);
  const days = asList(data.schedule_days).map(asObject);
  const slots = asList(data.schedule_slots).map(asObject);
  const unassigned = asList(data.schedule_unassigned).map(asObject);
  const columnCount = typeof data.schedule_column_count === "number" ? data.schedule_column_count : days.length + 1;

  return <>
    <section className="schedule-summary" aria-label="خلاصهٔ برنامهٔ هفتگی"
      data-schedule-units={displayText(summary.units, "0")}
      data-schedule-sessions={displayText(summary.sessions, "0")}
      data-schedule-conflicts={summary.has_conflicts ? "true" : "false"}>
      <article className="schedule-summary-card"><span>نیمسال</span><strong>{displayText(summary.term)}</strong></article>
      <article className="schedule-summary-card"><span>واحد ثبت‌شده</span><strong>{displayText(summary.units, "0")} واحد</strong></article>
      <article className="schedule-summary-card"><span>جلسات هفتگی</span><strong>{displayText(summary.sessions, "0")} جلسه</strong></article>
      <article className={`schedule-summary-card${summary.has_conflicts ? " schedule-summary-card--warning" : ""}`}><span>تداخل زمانی</span><strong>{displayText(summary.conflict_label)}</strong></article>
    </section>

    {unassigned.length > 0 && <div className="inline-notice schedule-unassigned" role="status"><p>روز این درس‌ها در اطلاعات ثبت‌شده مشخص نشده است: {unassigned.map((item) => `${displayText(item.lesson)} (${displayTime(item.start_time)}–${displayTime(item.end_time)})`).join("، ")}</p></div>}

    <section className="panel schedule-panel">
      <div className="schedule-wrap weekly-schedule-grid"><table className="schedule-table" aria-label="برنامهٔ هفتگی بر اساس روز و ساعت">
        <thead><tr><th scope="col">روز / ساعت</th>{days.map((day, index) => <th scope="col" key={`${day.code ?? day.label ?? index}`}>{displayText(day.label)}</th>)}</tr></thead>
        <tbody>{slots.length ? slots.map((slot, slotIndex) => {
          const cells = asList(slot.cells).map(asObject);
          return <tr key={`${slot.start_time ?? "time"}-${slot.end_time ?? slotIndex}`}>
            <th scope="row">{displayTime(slot.start_time)}–{displayTime(slot.end_time)}</th>
            {cells.map((cell, cellIndex) => {
              const courses = asList(cell.courses).map(asObject);
              return <td key={cellIndex}>{courses.length ? courses.map((course, courseIndex) => <div className="schedule-class" key={`${course.lesson ?? "course"}-${courseIndex}`}>
                <strong>{displayText(course.lesson)}</strong><small>{displayText(course.teacher)}</small><small>{displayText(course.room)}</small>
              </div>) : <span className="schedule-empty-cell" aria-label="بدون کلاس">—</span>}</td>;
            })}
          </tr>;
        }) : <tr><td colSpan={columnCount} className="empty-state">برای این نیمسال برنامهٔ ثبت‌شده‌ای وجود ندارد.</td></tr>}</tbody>
      </table></div>
    </section>

    <div className="inline-notice schedule-notice" role="note"><p>این برنامه از ثبت‌نام‌های فعال و زمان‌های ثبت‌شدهٔ درس‌ها ساخته شده است؛ فقط اطلاعات موجود در پرونده نمایش داده می‌شود.</p></div>
    <div className="page-actions schedule-actions">
      <a className="button button--primary" href={portalPageHref("selected-courses", bootstrap)}>مشاهده دروس انتخاب‌شده</a>
      <a className="button button--soft" href={portalPageHref("calendar", bootstrap)}>تقویم آموزشی</a>
      <button className="button button--soft" type="button" onClick={() => window.print()}>چاپ / ذخیره PDF</button>
    </div>
  </>;
}
