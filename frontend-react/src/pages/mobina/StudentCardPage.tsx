import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";

function text(value: unknown, fallback = "—"): string {
  return value === null || value === undefined || value === "" ? fallback : String(value);
}

export function StudentCardPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const card = payload.data.student_card as Record<string, unknown> | null;
  if (!card) {
    return <section className="panel"><p className="empty-state">اطلاعات کارت برای پروندهٔ انتخاب‌شده در دسترس نیست.</p></section>;
  }

  return (
    <>
      <section className="digital-card" aria-label="کارت دانشجویی دیجیتال">
        <div className="digital-card-top"><strong>دانشگاه آزاد اسلامی</strong><small>کارت دانشجویی دیجیتال</small></div>
        <strong className="digital-card-name">{text(card.full_name)}</strong>
        <strong className="digital-card-number">شماره دانشجویی: {text(card.student_code)}</strong>
        <div className="digital-card-facts">
          <span>رشته / مقطع / وضعیت: {text(card.field_name)} / {text(card.educational_level)} / {text(card.status)}</span>
          <span>نیمسال: {text(card.term_display_code)}</span>
        </div>
        <strong className="digital-card-check">وضعیت پرونده: {text(card.status)}</strong>
      </section>

      <div className="student-card-warning">این کارت پیش‌نمایش اطلاعات پرونده است و جایگزین کارت رسمی دانشگاه نیست. برای احراز هویت از کارت معتبر دانشگاه استفاده کنید.</div>
      <section className="panel student-card-meta-panel">
        <div><strong>آخرین وضعیت پرونده: {text(card.status)}</strong><span>تاریخ شروع تحصیل: {text(card.application_date)}</span></div>
        <p>در صورت مغایرت نام یا رشته، درخواست اصلاح اطلاعات ثبت کنید.</p>
      </section>
      <div className="page-actions student-card-actions">
        <a className="button button--primary" href={portalPageHref("requests", bootstrap)}>درخواست اصلاح اطلاعات</a>
        <a className="button button--soft" href={portalPageHref("support", bootstrap)}>مرکز پشتیبانی</a>
        {payload.data.printable === true && <button className="button button--soft" type="button" onClick={() => window.print()}>چاپ</button>}
      </div>
    </>
  );
}
