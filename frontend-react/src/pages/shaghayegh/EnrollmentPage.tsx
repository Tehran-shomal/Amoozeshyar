import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";
import { asObject, text } from "./shared";

export function EnrollmentPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const overview = asObject(payload.data.course_overview);
  const term = payload.data.course_term ? asObject(payload.data.course_term) : null;
  if (!payload.shell.current_profile || !Object.keys(overview).length) {
    return <section className="panel"><p className="empty-state">برای نمایش مرحلهٔ انتخاب واحد، ابتدا پروندهٔ دانشجویی را انتخاب کنید.</p></section>;
  }
  return <>
    <section className="enrollment-steps" aria-label="مراحل ثبت‌نام"><span className="is-current">۱ · اطلاعات دانشجو و تحصیلی</span><span>۲ · دروس انتخاب‌شده</span></section>
    <div className="content-columns enrollment-columns">
      <section className="panel"><div className="panel-heading"><h2>اطلاعات دانشجو</h2></div><dl className="key-value-list">
        <div><dt>شماره دانشجویی</dt><dd>{text(overview.student_code)}</dd></div><div><dt>نام و نام خانوادگی</dt><dd>{text(overview.full_name)}</dd></div>
        <div><dt>مقطع تحصیلی</dt><dd>{text(overview.educational_level)}</dd></div><div><dt>رشته تحصیلی</dt><dd>{text(overview.field_name)}</dd></div>
        <div><dt>وضعیت آموزشی</dt><dd>{text(overview.status)}</dd></div>
      </dl></section>
      <section className="panel"><div className="panel-heading"><h2>اطلاعات آموزشی</h2></div>{term ? <dl className="key-value-list">
        <div><dt>سال تحصیلی</dt><dd>{text(term.academic_year)}</dd></div><div><dt>نیمسال تحصیلی</dt><dd>{text(term.semester)} · {payload.term.display_label}</dd></div>
        <div><dt>سقف مجاز واحد</dt><dd>{text(overview.maximum_allowed_units, "۰")}</dd></div>
      </dl> : <p className="empty-state">برای این حساب نیمسال تحصیلی ثبت نشده است.</p>}</section>
    </div>
    {Number(overview.tuition_debt) > 0 && <div className="inline-notice enrollment-warning" role="status"><span aria-hidden="true">!</span><p>در پروندهٔ دانشجو بدهی شهریهٔ {text(overview.tuition_debt_display)} ریال ثبت شده است. شرایط ثبت‌نام هنگام ارسال درخواست از سوی سامانه بررسی می‌شود.</p></div>}
    <p className="action-note">سقف واحد و زمان مجاز انتخاب واحد از پرونده و تنظیمات نیمسال خوانده می‌شوند.</p>
    <div className="page-actions enrollment-actions"><a className="button button--soft" href={portalPageHref("", bootstrap)}>بازگشت به داشبورد</a>{payload.data.enrollment_can_continue === true && <a className="button button--primary" href={portalPageHref("selected-courses", bootstrap)}>ادامه</a>}</div>
  </>;
}
