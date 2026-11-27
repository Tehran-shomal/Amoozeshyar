import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";

type Row = Record<string, unknown>;
function object(value: unknown): Row { return typeof value === "object" && value !== null ? value as Row : {}; }
function list(value: unknown): unknown[] { return Array.isArray(value) ? value : []; }
function text(value: unknown, fallback = "—"): string { return value === null || value === undefined || value === "" ? fallback : String(value); }
function pairs(value: unknown): Array<[string, unknown]> {
  return list(value).flatMap((row): Array<[string, unknown]> => Array.isArray(row) && row.length > 1 ? [[text(row[0], ""), row[1]]] : []);
}

export function AcademicPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const data = payload.data;
  const profile = payload.shell.current_profile;
  if (!profile) return <section className="panel"><p className="empty-state">پروندهٔ دانشجویی انتخاب نشده است.</p></section>;

  if (payload.page === "academic-activities") {
    const activitySummary = pairs(data.activity_summary);
    const links = list(data.activity_links).map(object);
    const activities = list(data.recent_activities).map(object);
    return <>
      <div className="activity-summary-strip">
        <span>خلاصهٔ فعالیت‌های نیمسال {text(payload.term.display_label)}</span>
        {activitySummary.map(([name, value], index) => <span key={`${name}-${index}`}>{name}: {text(value)}</span>)}
      </div>
      <nav className="activity-links-grid" aria-label="فعالیت‌های آموزشی">
        {links.map((item, index) => <a className="activity-link-card" href={portalPageHref(text(item.slug, ""), bootstrap)} key={`${item.slug}-${index}`}><strong>{text(item.title)}</strong><span>{text(item.text, "")}</span><span className="text-link">مشاهده</span></a>)}
      </nav>
      <section className="panel data-panel activity-history-panel">
        <div className="panel-heading"><h2>آخرین فعالیت</h2></div>
        <div className="table-wrap"><table className="data-table">
          <thead><tr><th scope="col">عنوان</th><th scope="col">تاریخ</th><th scope="col">وضعیت</th></tr></thead>
          <tbody>{activities.length ? activities.map((activity, index) => <tr key={index}><td>{text(activity.change_type)}</td><td>{text(activity.changed_at_display, "")}</td><td>{text(activity.description, "ثبت‌شده")}</td></tr>) : <tr><td colSpan={3} className="empty-state">فعالیت آموزشی‌ای برای این پرونده ثبت نشده است.</td></tr>}</tbody>
        </table></div>
      </section>
    </>;
  }

  if (payload.page === "transcript") {
    const summary = pairs(data.transcript_summary);
    const rows = list(data.transcript_rows).map(object);
    return <>
      <section className="panel transcript-summary-panel" data-current-units={text(data.current_units, "0")}>
        <div className="panel-heading"><h2>خلاصهٔ کارنامه</h2></div>
        <dl className="key-value-list">
          <div><dt>نام و نام خانوادگی</dt><dd>{profile.full_name}</dd></div>
          <div><dt>شماره دانشجویی</dt><dd>{profile.student_code}</dd></div>
          <div><dt>نیمسال</dt><dd>{text(payload.term.display_label)}</dd></div>
          {summary.map(([name, value], index) => <div key={`${name}-${index}`}><dt>{name}</dt><dd>{text(value)}</dd></div>)}
        </dl>
      </section>
      <section className="panel data-panel transcript-table-panel">
        <div className="panel-heading"><h2>کارنامهٔ نیمسال جاری</h2><button className="button button--soft" type="button" onClick={() => window.print()}>چاپ / ذخیره PDF</button></div>
        <div className="table-wrap"><table className="data-table">
          <thead><tr><th scope="col">درس</th><th scope="col">واحد</th><th scope="col">نمرهٔ ثبت‌شده</th><th scope="col">وضعیت</th></tr></thead>
          <tbody>{rows.length ? rows.map((row, index) => <tr key={`${row.lesson_code}-${index}`}><td>{text(row.lesson)}</td><td>{text(row.units)}</td><td>{text(row.score)}</td><td>{text(row.status)}</td></tr>) : <tr><td colSpan={4} className="empty-state">برای این نیمسال درسی ثبت نشده است.</td></tr>}</tbody>
        </table></div>
      </section>
      <div className="inline-notice transcript-data-notice" role="note"><p>{text(data.notice, "")}</p></div>
      <div className="page-actions transcript-actions"><a className="button button--primary" href={portalPageHref("grade-appeal", bootstrap)}>اعتراض به نمره</a><a className="button button--soft" href={portalPageHref("curriculum", bootstrap)}>چارت دروس</a></div>
    </>;
  }

  if (payload.page === "curriculum") {
    const summary = object(data.curriculum_summary);
    const rows = list(data.curriculum_rows).map(object);
    const summaryCards: Array<[string, unknown]> = [
      ["واحد مصوب رشته", summary.total],
      ["گذرانده", summary.passed],
      [`جاری در نیمسال ${text(payload.term.display_label)}`, summary.current],
      ["باقی‌مانده", summary.remaining],
    ];
    return <>
      <section className="curriculum-summary" aria-label="خلاصهٔ چارت درسی" data-curriculum-total={text(summary.total, "0")} data-curriculum-passed={text(summary.passed, "0")} data-curriculum-current={text(summary.current, "0")} data-curriculum-remaining={text(summary.remaining, "0")}>
        {summaryCards.map(([name, value]) => <article className="curriculum-summary-card" key={name}><span>{name}</span><strong>{text(value, "0")} واحد</strong></article>)}
      </section>
      <section className="panel curriculum-panel">
        <div className="panel-heading"><h2>مسیر دروس {profile.field_name}</h2></div>
        <div className="curriculum-table-wrap"><table className="curriculum-table" aria-label="چارت درسی رشتهٔ دانشجو">
          <thead><tr><th scope="col">درس</th><th scope="col">واحد</th><th scope="col">پیش‌نیاز</th><th scope="col">وضعیت</th><th scope="col">گروه</th></tr></thead>
          <tbody>{rows.length ? rows.map((row, index) => <tr key={`${row.lesson}-${index}`}>
            <th scope="row">{text(row.lesson)}</th><td>{text(row.units)}</td><td>{list(row.prerequisites).map((item) => text(item, "")).join("، ") || "—"}</td>
            <td><span className={`curriculum-status curriculum-status--${text(row.status_code, "remaining")}`}>{text(row.status)}</span></td><td>{text(row.group)}</td>
          </tr>) : <tr><td colSpan={5} className="empty-state">برای رشتهٔ این پرونده چارت فعالی ثبت نشده است.</td></tr>}</tbody>
        </table></div>
      </section>
      <div className="inline-notice curriculum-notice" role="note"><p>وضعیت درس‌ها از انتخاب‌واحد همین پرونده و نمره‌های ثبت‌شده محاسبه می‌شود. گروه و پیش‌نیاز فقط در صورت تعریف در اطلاعات چارت نمایش داده می‌شود.</p></div>
      <div className="page-actions curriculum-actions"><a className="button button--primary" href={portalPageHref("enrollment", bootstrap)}>انتخاب واحد</a><a className="button button--soft" href={portalPageHref("internship", bootstrap)}>کارآموزی</a></div>
    </>;
  }

  return null;
}
