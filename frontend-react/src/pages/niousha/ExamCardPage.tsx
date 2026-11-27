import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";
import { asList, asObject, displayText } from "./display";

export function ExamCardPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const student = asObject(payload.data.exam_student);
  if (!payload.shell.current_profile || !Object.keys(student).length) {
    return <section className="panel"><p className="empty-state">برای مشاهدهٔ برنامهٔ امتحانات، پروندهٔ دانشجویی را انتخاب کنید.</p></section>;
  }

  const card = asObject(payload.data.exam_card);
  const blockers = asList(card.blockers).map((item) => displayText(item, ""));
  const enrollments = asList(card.enrollments).map(asObject);
  return <>
    <div className="inline-notice exam-card-warning" role="status"><span aria-hidden="true">{blockers.length ? "!" : "i"}</span><p>{blockers.length ? blockers.join("، ") : "این برنامه از درس‌های ثبت‌شده خوانده شده است؛ برای حضور در جلسه، کارت رسمی و مدرک شناسایی لازم است."}</p></div>

    <section className="panel exam-card-student">
      <h2>{displayText(student.full_name)}</h2>
      <dl>
        <div><dt>شماره دانشجویی</dt><dd>{displayText(student.student_code)}</dd></div>
        <div><dt>رشته و مقطع</dt><dd>{displayText(student.field_name)} / {displayText(student.educational_level)}</dd></div>
        <div><dt>نیمسال</dt><dd>{displayText(student.term_display_code, payload.term.display_label || "—")}</dd></div>
        <div><dt>وضعیت تحصیلی</dt><dd>{displayText(student.status)}</dd></div>
      </dl>
    </section>

    <section className="panel data-panel exam-card-table">
      <div className="panel-heading"><h2>برنامهٔ امتحان‌های ثبت‌شده</h2></div>
      <div className="table-wrap"><table className="data-table">
        <thead><tr><th scope="col">درس</th><th scope="col">تاریخ / ساعت</th><th scope="col">محل / صندلی</th><th scope="col">وضعیت</th></tr></thead>
        <tbody>{enrollments.length ? enrollments.map((row, index) => <tr key={`${row.lesson ?? "exam"}-${index}`}>
          <td>{displayText(row.lesson)}</td>
          <td>{row.exam_date ? `${displayText(row.exam_date)}${row.exam_time ? `، ${displayText(row.exam_time)}` : ""}` : "ثبت نشده"}</td>
          <td>{displayText(row.classroom)} • شماره صندلی: در سامانه ثبت نشده</td>
          <td>{displayText(row.status, "ثبت‌شده")}</td>
        </tr>) : <tr><td colSpan={4} className="empty-state">برای این نیمسال ثبت‌نام فعالی وجود ندارد.</td></tr>}</tbody>
      </table></div>
    </section>

    <p className="action-note exam-card-note">برای ورود به جلسه، کارت معتبر و مدرک شناسایی همراه داشته باشید و ۳۰ دقیقه پیش از شروع آزمون در محل حاضر شوید. شمارهٔ صندلی یا صدور کارت رسمی از سرویس دانشگاه در دسترس نیست.</p>
    <div className="page-actions exam-card-actions">
      <a className="button button--primary" href={portalPageHref("secure-payment", bootstrap)}>پرداخت بدهی</a>
      <a className="button button--primary" href={portalPageHref("evaluation", bootstrap)}>تکمیل ارزشیابی</a>
      <button className="button button--disabled" type="button" disabled>صدور کارت رسمی در دسترس نیست</button>
    </div>
  </>;
}
