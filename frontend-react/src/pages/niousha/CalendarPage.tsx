import type { PagePayload } from "../../api/types";
import { asList, asObject, displayText } from "./display";

export function CalendarPage({ payload }: { payload: PagePayload }) {
  const data = payload.data;
  const notice = payload.shell.profile_notice || displayText(data.notice, "");
  if (notice) return <div className="inline-notice" role="status"><p>{notice}</p></div>;

  const days = asList(data.calendar_days);
  const events = asList(data.calendar_events).map(asObject);
  const summary = asList(data.calendar_summary).flatMap((item): Array<[string, unknown]> =>
    Array.isArray(item) && item.length >= 2 ? [[displayText(item[0], ""), item[1]]] : [],
  );
  const deadline = data.calendar_next_deadline ? asObject(data.calendar_next_deadline) : null;

  return <>
    <section className="calendar-overview-grid" aria-label="خلاصهٔ تقویم ترم">
      <article className="calendar-overview-card"><span>نیمسال تحصیلی</span><strong>{displayText(data.calendar_term_code)}</strong><small>{payload.term.display_label}</small></article>
      <article className="calendar-overview-card"><span>بازهٔ کلاس‌ها</span><strong>{displayText(data.calendar_term_range)}</strong><small>بر اساس تاریخ‌های ثبت‌شدهٔ ترم</small></article>
      <article className="calendar-overview-card"><span>مهلت پیش‌رو</span>{deadline ? <><strong>{displayText(deadline.date_label)}</strong><small>{displayText(deadline.title, "")}{deadline.time_label ? ` • ${displayText(deadline.time_label)}` : ""}</small></> : <><strong>—</strong><small>مهلت آینده‌ای ثبت نشده است</small></>}</article>
    </section>

    <div className="calendar-layout">
      <section className="panel calendar-month-panel" aria-labelledby="calendar-month-heading">
        <div className="panel-heading"><h2 id="calendar-month-heading">{displayText(data.calendar_month_label)}</h2><span className="calendar-calendar-note">هجری شمسی</span></div>
        <div className="calendar-weekdays" aria-hidden="true">{["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"].map((day) => <span key={day}>{day}</span>)}</div>
        <div className="calendar-month-grid" role="grid" aria-label={`روزهای ماه ${displayText(data.calendar_month_label, "")}`}>
          {days.map((item, index) => {
            if (!item || typeof item !== "object") return <div className="calendar-day" aria-hidden="true" key={`empty-${index}`} />;
            const day = asObject(item);
            const className = ["calendar-day", day.is_event_day ? "is-event-day" : "", day.is_today ? "is-today" : ""].filter(Boolean).join(" ");
            return <div className={className} role="gridcell" data-calendar-day={displayText(day.number, "")} data-date={displayText(day.iso_date, "")} aria-label={displayText(day.iso_date, "")} key={displayText(day.iso_date, String(index))}>{displayText(day.number, "")}</div>;
          })}
        </div>
      </section>

      <section className="panel calendar-events-panel" aria-labelledby="calendar-events-heading">
        <div className="panel-heading"><h2 id="calendar-events-heading">رویدادهای آموزشی</h2></div>
        <div className="calendar-event-list">{events.length ? events.map((event, index) => <article key={`${event.iso_date ?? index}-${event.title ?? "event"}`}>
          <strong>{displayText(event.date_label)}{event.time_label ? ` • ${displayText(event.time_label)}` : ""}</strong>
          <span>{displayText(event.title, "")}{event.detail ? ` — ${displayText(event.detail)}` : ""}</span>
        </article>) : <p className="calendar-empty-state">برای این ماه رویدادی در پروندهٔ ترم ثبت نشده است.</p>}</div>
      </section>
    </div>

    <section className="panel calendar-summary-panel" aria-labelledby="calendar-summary-heading">
      <div className="panel-heading"><h2 id="calendar-summary-heading">خلاصهٔ نیمسال {displayText(data.calendar_term_code)}</h2></div>
      <dl className="calendar-summary-list">{summary.map(([label, value], index) => <div key={`${label}-${index}`}><dt>{label}</dt><dd>{displayText(value)}</dd></div>)}</dl>
    </section>
    <p className="calendar-data-note">رویدادها فقط از تاریخ‌های ترم، امتحان‌های درس‌های فعال و جلسات ثبت‌شده استخراج می‌شوند؛ تقویم مناسبت‌های عمومی در دادهٔ سامانه موجود نیست.</p>
  </>;
}
