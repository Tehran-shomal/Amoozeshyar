import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";

type Row = Record<string, unknown>;
function object(value: unknown): Row { return typeof value === "object" && value !== null ? value as Row : {}; }
function list(value: unknown): Row[] { return Array.isArray(value) ? value.map(object) : []; }
function text(value: unknown, fallback = "—"): string { return value === null || value === undefined || value === "" ? fallback : String(value); }

export function FinancePage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const data = payload.data;
  const student = payload.shell.current_profile;
  const summary = list(data.finance_summary);
  const actions = list(data.finance_actions);

  if (!student) return <section className="panel"><p className="empty-state">برای مشاهدهٔ اطلاعات مالی، پروندهٔ دانشجویی را انتخاب کنید.</p></section>;

  return (
    <>
      <div className="finance-summary-strip" aria-label="خلاصهٔ وضعیت مالی">
        {summary.map((item, index) => <span key={index}><strong>{text(item.label)}:</strong> {text(item.value)}</span>)}
        <span><strong>نیمسال:</strong> {text(data.finance_term_label)}</span>
      </div>

      {payload.page === "payments" && <>
        <section className="panel data-panel finance-transactions-panel">
          <div className="panel-heading"><h2>تراکنش‌های نیمسال {text(data.finance_term_label)}</h2></div>
          <div className="table-wrap"><table className="data-table">
            <thead><tr><th scope="col">شناسه</th><th scope="col">شرح</th><th scope="col">تاریخ</th><th scope="col">مبلغ</th><th scope="col">وضعیت</th></tr></thead>
            <tbody>
              {list(data.payment_rows).length ? list(data.payment_rows).map((payment, index) => {
                const date = object(payment.payment_date);
                return <tr key={`${payment.tracking_code}-${index}`}>
                  <td>{text(payment.tracking_code)}</td><td>شرح در مدل پرداخت ثبت نشده</td><td>{text(date.display)}</td>
                  <td>{text(payment.amount)} ریال</td><td>{text(payment.status, "نامشخص")}</td>
                </tr>;
              }) : <tr><td colSpan={5} className="empty-state">برای این نیمسال سابقهٔ پرداختی ثبت نشده است.</td></tr>}
            </tbody>
          </table></div>
        </section>
        {data.failed_payment ? <div className="inline-notice finance-reconciliation-note" role="status"><span aria-hidden="true">!</span><p>تراکنش {text(object(data.failed_payment).tracking_code)} ناموفق ثبت شده و در جمع پرداخت‌های موفق محاسبه نشده است. برای پیگیری با پشتیبانی ارتباط بگیرید.</p></div>
          : <div className="finance-reconciliation-note">مبلغ‌ها از رکوردهای پرداخت همین پرونده محاسبه شده‌اند. وضعیت بدهی از پروندهٔ آموزشی خوانده می‌شود.</div>}
      </>}

      {payload.page === "secure-payment" && <>
        <div className="inline-notice finance-gateway-note" role="status"><span aria-hidden="true">!</span><p>{text(data.finance_notice, "")}</p></div>
        <section className="panel finance-debt-panel">
          <div className="panel-heading"><h2>اطلاعات پرداخت</h2></div>
          <dl className="key-value-list finance-payment-review">
            <div><dt>شرح پرداخت</dt><dd>ماندهٔ شهریهٔ ثبت‌شده در پرونده</dd></div>
            <div><dt>مبلغ (ریال)</dt><dd>{text(data.finance_debt_display)}</dd></div>
            <div><dt>پرداخت‌کننده</dt><dd>{text(student.full_name)}</dd></div>
            <div><dt>درگاه بانکی</dt><dd>به سامانه متصل نیست</dd></div>
          </dl>
          <p>این فقط پیش‌نمایش اطلاعات پرونده است؛ تا اتصال درگاه رسمی هیچ پرداخت یا تراکنشی ثبت نمی‌شود.</p>
        </section>
        <div className="page-actions finance-actions">
          <button className="button button--primary" type="button" disabled aria-disabled="true" title="درگاه پرداخت متصل نیست">ادامه پرداخت</button>
          <a className="button button--soft" href={portalPageHref("payments", bootstrap)}>سوابق پرداخت</a>
        </div>
      </>}

      {payload.page === "tuition" && <>
        <section className="panel data-panel finance-transactions-panel">
          <div className="panel-heading"><h2>پرداخت‌های موفق هر نیمسال</h2></div>
          <div className="table-wrap"><table className="data-table">
            <thead><tr><th scope="col">نیمسال</th><th scope="col">سال تحصیلی</th><th scope="col">نوع نیمسال</th><th scope="col">جمع پرداخت‌های موفق</th></tr></thead>
            <tbody>{list(data.tuition_rows).length ? list(data.tuition_rows).map((row, index) => <tr key={`${row.term_code}-${index}`}><td>{text(row.term_code)}</td><td>{text(row.academic_year)}</td><td>{text(row.semester)}</td><td>{text(row.total)}</td></tr>)
              : <tr><td colSpan={4} className="empty-state">پرداخت موفقی برای این پرونده ثبت نشده است.</td></tr>}</tbody>
          </table></div>
        </section>
        <div className="inline-notice tuition-detail-note" role="note"><p>{text(data.notice, "")}</p></div>
      </>}

      {actions.length > 0 && <div className="page-actions finance-actions">
        {actions.map((item, index) => {
          const slug = text(item.slug, "");
          return <a className={`button${index === 0 ? " button--primary" : " button--soft"}`} href={portalPageHref(slug, bootstrap)} key={`${slug}-${index}`}>{text(item.label, "")}</a>;
        })}
      </div>}
    </>
  );
}
