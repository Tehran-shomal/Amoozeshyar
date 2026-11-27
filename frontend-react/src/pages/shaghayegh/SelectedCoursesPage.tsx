import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";
import { OfferingPicker } from "./OfferingPicker";
import { asList, asObject, text } from "./shared";

export function SelectedCoursesPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const overview = asObject(payload.data.course_overview);
  const tables = asList(payload.data.tables).map(asObject);
  const courseTable = tables[0] || {};
  const columns = asList(courseTable.columns);
  const rows = asList(courseTable.rows).map(asObject);
  if (!payload.shell.current_profile || !Object.keys(overview).length) {
    return <section className="panel"><p className="empty-state">برای نمایش دروس، پروندهٔ دانشجویی را از نوار بالای صفحه انتخاب کنید.</p></section>;
  }
  return <>
    <section className="panel student-course-summary"><dl className="summary-rows">
      <div><dt>نام و نام خانوادگی</dt><dd>{text(overview.full_name)}</dd></div><div><dt>شماره دانشجویی</dt><dd>{text(overview.student_code)}</dd></div>
      <div><dt>رشته و مقطع</dt><dd>{text(overview.field_name)} · {text(overview.educational_level)}</dd></div><div><dt>نیمسال و وضعیت</dt><dd>{text(payload.term.display_label)} · {text(overview.status)}</dd></div>
    </dl></section>

    <div className="course-warning-panel"><div>
      {Number(overview.tuition_debt) > 0 ? <p>در پروندهٔ دانشجو بدهی شهریهٔ {text(overview.tuition_debt_display)} ریال ثبت شده است.</p> : <p>ثبت نهایی هر درس پس از بررسی قوانین آموزشی و ظرفیت از سوی سامانه انجام می‌شود.</p>}
      <small>سقف مجاز این نیمسال: {text(overview.maximum_allowed_units, "۰")} واحد · وضعیت ثبت‌نام از دادهٔ سامانه خوانده می‌شود.</small>
    </div><OfferingPicker bootstrap={bootstrap} termCode={payload.term.term_code} studentCode={payload.profile.student_code} shell={payload.shell} overview={overview} successSlug="add-drop" /></div>

    <section className="panel data-panel course-list-panel course-current-panel"><div className="panel-heading"><h2>{text(courseTable.title, "دروس ثبت‌نام‌شده")}</h2></div>
      <div className="table-wrap"><table className="data-table"><thead><tr>{columns.map((column, index) => <th scope="col" key={index}>{text(column, "")}</th>)}</tr></thead>
        <tbody>{rows.length ? rows.map((row, rowIndex) => <tr key={rowIndex}>{asList(row.cells).map((cell, cellIndex) => <td key={cellIndex}>{text(cell)}</td>)}</tr>) : <tr><td colSpan={Math.max(columns.length, 1)} className="empty-state">برای این نیمسال درس ثبت‌شده‌ای وجود ندارد.</td></tr>}</tbody>
      </table></div>
    </section>

    <section className="course-totals" aria-label="خلاصه واحدهای انتخاب‌شده">
      <div><span>مجموع واحدها</span><strong>{text(payload.data.selected_units, "۰")}</strong></div><div><span>شهریه ثابت (تومان)</span><strong>—</strong></div>
      <div><span>شهریه متغیر (تومان)</span><strong>—</strong></div><div><span>جمع کل (تومان)</span><strong>—</strong></div>
      {payload.data.tuition_breakdown_available !== true && <p className="course-totals-note">تعرفهٔ شهریه برای این نیمسال در داده‌های سامانه ثبت نشده است؛ مبلغی حدس زده نمی‌شود.</p>}
    </section>
    <div className="page-actions course-page-actions"><a className="button button--soft" href={portalPageHref("enrollment", bootstrap)}>بازگشت به اطلاعات</a></div>
  </>;
}
