import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";
import { asList, asObject, displayText } from "../niousha/display";

export function EvaluationPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const data = payload.data;
  const entries = asList(data.evaluation_course_entries).map(asObject);
  if (payload.shell.profile_notice) return <div className="inline-notice" role="status"><p>{payload.shell.profile_notice}</p></div>;

  return <>
    <div className="inline-notice evaluation-info">
      <p>ارزشیابی نیمسال {displayText(data.evaluation_term_code)}؛ {displayText(data.evaluation_course_count, "۰")} درس ثبت‌شده و {displayText(data.evaluation_completed_count, "۰")} ارزشیابی تکمیل‌شده</p>
      <p className="evaluation-privacy-note">{displayText(data.evaluation_notice, "")}</p>
    </div>
    <section className="panel evaluation-list-panel" aria-labelledby="evaluation-course-list-title">
      <div className="panel-heading"><h2 id="evaluation-course-list-title">وضعیت ارزشیابی درس‌های ثبت‌شده</h2></div>
      <div className="evaluation-course-list">
        {entries.length ? entries.map((entry, index) => {
          const enrollment = asObject(entry.enrollment);
          const completed = entry.completed === true;
          const formUrl = new URL(portalPageHref("evaluation-form", bootstrap), window.location.origin);
          formUrl.searchParams.set("enrollment", String(enrollment.id ?? ""));
          return <article className="evaluation-course-row" key={`${enrollment.id ?? index}`}>
            <div className="evaluation-course-copy"><strong>{displayText(enrollment.lesson)}</strong><small>{displayText(enrollment.teacher)}</small></div>
            <span className="evaluation-course-status">{completed ? "ثبت‌شده" : "تکمیل‌نشده"}</span>
            {completed ? <span className="evaluation-complete-badge">ثبت‌شده</span> : <a className="button button--primary" href={`${formUrl.pathname}${formUrl.search}`}>تکمیل فرم</a>}
          </article>;
        }) : <p className="empty-state">برای نیمسال انتخاب‌شده درسی برای ارزشیابی ثبت نشده است.</p>}
      </div>
    </section>
    <p className="evaluation-footer-notice">پس از ثبت نهایی، ویرایش پاسخ‌ها امکان‌پذیر نیست. تکمیل ارزشیابی ممکن است یکی از شرایط دریافت کارت امتحان باشد.</p>
    <div className="page-actions evaluation-page-actions"><a className="button button--soft" href={portalPageHref("exam-card", bootstrap)}>مشاهده شرایط کارت امتحان</a></div>
  </>;
}
