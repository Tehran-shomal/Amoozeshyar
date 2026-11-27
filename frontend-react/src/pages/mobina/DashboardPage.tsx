import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";

type Row = Record<string, unknown>;

function object(value: unknown): Row {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? value as Row
    : {};
}

function array(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function label(value: unknown, fallback = "—"): string {
  return value === null || value === undefined || value === "" ? fallback : String(value);
}

function entries(value: unknown): Array<[string, unknown]> {
  return array(value).flatMap((item): Array<[string, unknown]> => {
    if (Array.isArray(item) && item.length >= 2) return [[label(item[0], ""), item[1]]];
    return [];
  });
}

export function DashboardPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const data = object(payload.data.dashboard);
  const student = payload.shell.student;
  const details = entries(data.student_details);
  const academic = entries(data.academic_summary);
  const classes = array(data.classes).map(object);
  const notices = array(data.notices).map(object);
  const financial = array(data.financial_summary).map(object);
  const quickActions = array(data.quick_actions).map(object);
  const columns = array(data.classes_columns).map((item) => label(item, ""));

  return (
    <>
      <section className="dashboard-hero" aria-labelledby="dashboard-title">
        <div className="welcome-copy">
          <h1 id="dashboard-title">{label(data.welcome, "داشبورد")}</h1>
          <p>{label(data.intro, "")}</p>
        </div>
        <div className="welcome-art" aria-hidden="true">
          <span className="welcome-orbit welcome-orbit--one" />
          <span className="welcome-orbit welcome-orbit--two" />
          <span className="welcome-book">◧</span>
        </div>
        <div className="welcome-university">{label(data.university, "")}</div>
      </section>

      <nav className="dashboard-quick-links quick-grid" aria-label="دسترسی سریع">
        {quickActions.map((action, index) => (
          <a className="quick-card" href={portalPageHref(label(action.slug, ""), bootstrap)} key={`${action.slug}-${index}`}>
            <span className="quick-icon quick-icon--blue" aria-hidden="true">{label(action.icon, "•")}</span>
            <span className="quick-copy"><strong>{label(action.title, "")}</strong></span>
            <span className="quick-arrow" aria-hidden="true">←</span>
          </a>
        ))}
      </nav>

      <div className="dashboard-layout">
        <aside className="dashboard-side-column" aria-label="خلاصه پرونده">
          <section className="student-summary-card" aria-labelledby="student-summary-title">
            <div className="student-summary-head">
              <h2 id="student-summary-title">سلام {label(student.name, "دانشجو")}!</h2>
              <span className="avatar avatar--large" aria-hidden="true">{label(student.avatar_initials, "د")}</span>
            </div>
            <dl className="student-summary-details">
              {details.length ? details.map(([name, value], index) => (
                <div key={`${name}-${index}`}><dt>{name}</dt><dd>{label(value)}</dd></div>
              )) : <div><dt>پرونده</dt><dd>پروندهٔ دانشجویی در دسترس نیست.</dd></div>}
            </dl>
          </section>
        </aside>

        <div className="dashboard-content-column">
          <div className="home-overview-grid">
            <section className="panel home-table-panel" aria-labelledby="classes-title">
              <div className="panel-heading">
                <h2 id="classes-title">{label(data.classes_title, "برنامهٔ کلاس‌ها")}</h2>
                <a className="text-link" href={portalPageHref("schedule", bootstrap)}>{label(data.classes_link, "مشاهده برنامه")} <span aria-hidden="true">←</span></a>
              </div>
              <div className="table-wrap">
                <table className="data-table dashboard-class-table">
                  <thead><tr>{columns.map((column, index) => <th scope="col" key={`${column}-${index}`}>{column}</th>)}</tr></thead>
                  <tbody>
                    {classes.length ? classes.map((row, index) => (
                      <tr key={index}><td>{label(row.day_time)}</td><td>{label(row.name)}</td><td>{label(row.teacher)}</td><td>{label(row.room)}</td></tr>
                    )) : <tr><td colSpan={Math.max(columns.length, 1)} className="empty-state">برای این نیمسال کلاسی ثبت نشده است.</td></tr>}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="panel home-notices-panel" aria-labelledby="notices-title">
              <div className="panel-heading">
                <h2 id="notices-title">{label(data.notices_title, "اطلاعیه‌ها")}</h2>
                <a className="text-link" href={portalPageHref("announcements", bootstrap)}>{label(data.notices_link, "مشاهده همه")} <span aria-hidden="true">←</span></a>
              </div>
              <div className="home-notice-list">
                {notices.length ? notices.map((notice, index) => (
                  <article className="home-notice-row" key={index}><strong>{label(notice.title, "")}</strong><time>{label(notice.date, "")}</time></article>
                )) : <p className="empty-state">اعلانی برای نمایش ثبت نشده است.</p>}
              </div>
            </section>
          </div>
        </div>
      </div>

      <div className="home-summary-grid">
        <section className="panel home-financial-panel" aria-labelledby="financial-title">
          <div className="panel-heading">
            <h2 id="financial-title">{label(data.financial_title, "وضعیت مالی")}</h2>
            <a className="text-link" href={portalPageHref("tuition", bootstrap)}>سوابق پرداخت <span aria-hidden="true">←</span></a>
          </div>
          <div className="financial-summary-list">
            {financial.length ? financial.map((item, index) => (
              <div className="financial-summary-row" key={index}>
                <div><span>{label(item.label, "")}</span><strong>{label(item.value)}</strong></div>
                <span className={`financial-status financial-status--${label(item.state, "muted")}`}>{label(item.status, "")}</span>
              </div>
            )) : <p className="empty-state">برای این پرونده اطلاعات مالی ثبت نشده است.</p>}
          </div>
          <p className="financial-summary-note">{label(data.financial_note, "")}</p>
        </section>

        <section className="panel home-academic-panel" aria-labelledby="academic-title">
          <div className="panel-heading">
            <h2 id="academic-title">{label(data.academic_title, "وضعیت تحصیلی")}</h2>
            <a className="text-link" href={portalPageHref("transcript", bootstrap)}>{label(data.academic_link, "مشاهده کارنامه")} <span aria-hidden="true">←</span></a>
          </div>
          <div className="academic-summary-content">
            {academic.length ? <>
              <div className="average-ring"><strong>{label(academic[0][1])}</strong><small>{label(data.academic_average_label, "معدل کل")}</small></div>
              <dl className="summary-rows">{academic.map(([name, value], index) => <div key={`${name}-${index}`}><dt>{name}</dt><dd>{label(value)}</dd></div>)}</dl>
            </> : <p className="empty-state">اطلاعات تحصیلی پرونده در دسترس نیست.</p>}
          </div>
        </section>
      </div>
    </>
  );
}
