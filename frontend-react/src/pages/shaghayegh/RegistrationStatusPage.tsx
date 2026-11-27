import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";
import { asList, asObject, text } from "./shared";

export function RegistrationStatusPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  if (!payload.shell.current_profile) return <section className="panel"><p className="empty-state">برای نمایش وضعیت ثبت‌نام، ابتدا پروندهٔ دانشجویی را انتخاب کنید.</p></section>;
  const data = payload.data;
  const stages = asList(data.registration_status_stages).map(asObject);
  return <div className="registration-status-page">
    <div className="activity-summary-strip" aria-label="خلاصهٔ وضعیت نیمسال"><span>نیمسال {text(payload.term.display_label)} · {payload.shell.current_profile.full_name}</span><span>مقطع: {text(payload.shell.current_profile.educational_level)}</span><span>{text(data.registration_status_count, "۰")} درس ثبت‌شده · {text(data.registration_status_units, "۰")} واحد</span></div>
    <section className="panel registration-status-panel" aria-labelledby="registration-status-title"><div className="panel-heading"><h2 id="registration-status-title">مراحل و وضعیت ثبت‌نام</h2></div><div className="table-wrap"><table className="data-table registration-status-table">
      <thead><tr><th scope="col">مرحله</th><th scope="col">آخرین وضعیت</th><th scope="col">توضیح</th></tr></thead>
      <tbody>{stages.map((stage, index) => <tr key={`${stage.stage ?? index}`}><td>{text(stage.stage)}</td><td>{text(stage.status)}</td><td>{text(stage.description)}</td></tr>)}</tbody>
    </table></div></section>
    <p className="action-note registration-status-rules">سقف مجاز {text(data.registration_status_max_units, "۰")} واحد از پرونده و قواعد موجود خوانده شده است؛ حداقل واحد در سرویس ثبت‌نام تعریف نشده است. این صفحه تأیید نهایی یا تسویه را حدس نمی‌زند.</p>
    <nav className="page-actions registration-status-actions" aria-label="صفحه‌های مرتبط با ثبت‌نام"><a className="button button--primary" href={portalPageHref("secure-payment", bootstrap)}>مشاهدهٔ وضعیت بدهی</a><a className="button button--soft" href={portalPageHref("selected-courses", bootstrap)}>دروس ثبت‌شده</a><a className="button button--soft" href={portalPageHref("schedule", bootstrap)}>برنامهٔ هفتگی</a></nav>
  </div>;
}
