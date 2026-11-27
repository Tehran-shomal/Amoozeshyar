import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";
import { MarkReadForm } from "../../components/MarkReadForm";

type Row = Record<string, unknown>;

function object(value: unknown): Row { return typeof value === "object" && value !== null ? value as Row : {}; }
function list(value: unknown): Row[] { return Array.isArray(value) ? value.map(object) : []; }
function text(value: unknown, fallback = "—"): string { return value === null || value === undefined || value === "" ? fallback : String(value); }

function filterHref(code: string, bootstrap: PortalBootstrap): string {
  const url = new URL(portalPageHref("notifications", bootstrap), window.location.origin);
  if (code) url.searchParams.set("notification_type", code);
  else url.searchParams.delete("notification_type");
  return `${url.pathname}${url.search}`;
}

export function NotificationsPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const filters = list(payload.data.notification_type_filters);
  const notifications = list(payload.data.notifications);
  const selected = text(payload.data.notification_filter_code, "");
  return (
    <>
      <nav className="notification-filters" aria-label="فیلتر اعلان‌ها">
        <a className={`notification-filter${selected ? "" : " is-active"}`} href={filterHref("", bootstrap)} aria-current={!selected ? "page" : undefined}>همه ({text(payload.data.notification_count, "0")})</a>
        {filters.map((item, index) => {
          const code = text(item.code, "");
          return <a className={`notification-filter${selected === code ? " is-active" : ""}`} href={filterHref(code, bootstrap)} aria-current={selected === code ? "page" : undefined} key={`${code}-${index}`}>{text(item.label)} ({text(item.count, "0")})</a>;
        })}
      </nav>

      <section className="notification-center-list" aria-label="فهرست اعلان‌های حساب شما">
        {notifications.length ? notifications.map((item) => {
          const id = Number(item.notification_id);
          const isRead = Boolean(item.is_read);
          const title = text(item.title, "");
          return (
            <article className={`notification-center-card${isRead ? " is-read" : ""}`} key={id}>
              <div className="notification-center-copy">
                <strong className="notification-center-type">{text(item.type_label, "بدون نوع")}{!isRead && <span> · خوانده‌نشده</span>}</strong>
                <h2>{title}</h2>
                <p>{text(item.message, "")}</p>
              </div>
              <div className="notification-center-actions">
                {isRead ? <span className="notification-read-label">خوانده‌شده</span> : Number.isSafeInteger(id) && id > 0
                  ? <MarkReadForm submitUrl={bootstrap.submitUrl} field="notification_id" id={id} label="مشاهده" ariaLabel={`مشاهده و علامت‌گذاری اعلان ${title}`} />
                  : null}
              </div>
            </article>
          );
        }) : <div className="panel notification-center-empty">{selected ? "اعلانی با این نوع در حساب شما ثبت نشده است." : "اعلانی برای حساب شما ثبت نشده است."}</div>}
      </section>

      <div className="page-actions notification-center-footer">
        <a className="button button--primary" href={portalPageHref("settings", bootstrap)}>تنظیمات اعلان‌ها</a>
      </div>
    </>
  );
}
