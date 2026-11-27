import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { MarkReadForm } from "../../components/MarkReadForm";

type Announcement = {
  communication_id: number;
  subject: string;
  sender_name: string;
  message_body: string;
  sent_at: { iso: string | null; display: string };
  is_read: boolean;
};

function list(value: unknown): Announcement[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is Announcement => typeof item === "object" && item !== null && "communication_id" in item && "subject" in item);
}

function text(value: unknown, fallback = "—"): string {
  return value === null || value === undefined || value === "" ? fallback : String(value);
}

export function AnnouncementsPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const announcements = list(payload.data.announcements);
  if (payload.shell.profile_notice) return null;
  return (
    <>
      <>
        <section className="announcement-summary-strip" aria-label="خلاصهٔ اطلاعیه‌ها">
          <div><span>اطلاعیه‌های دریافت‌شده</span><strong>{text(payload.data.announcement_count, "0")}</strong></div>
          <div><span>خوانده‌نشده</span><strong>{text(payload.data.announcement_unread_count, "0")}</strong></div>
          <div><span>نیمسال انتخاب‌شده</span><strong>{text(payload.data.announcement_term_code)}</strong></div>
        </section>
        <p className="announcement-scope-note">{text(payload.data.announcement_scope_note, "")}</p>
        <section className="announcement-list" aria-label="فهرست اطلاعیه‌های استادان">
          {announcements.length ? announcements.map((item) => (
            <article className={`announcement-card${item.is_read ? " is-read" : ""}`} key={item.communication_id}>
              <header className="announcement-card-header">
                <div className="announcement-card-title"><h2>{text(item.subject)}</h2><span>{text(item.sender_name)}</span></div>
                <time dateTime={item.sent_at?.iso || undefined}>{text(item.sent_at?.display, "")}</time>
              </header>
              <p className="announcement-card-message">{text(item.message_body, "")}</p>
              <footer className="announcement-card-actions">
                {item.is_read
                  ? <span className="announcement-read-label">خوانده‌شده</span>
                  : <MarkReadForm submitUrl={bootstrap.submitUrl} field="communication_id" id={item.communication_id} label="خواندم" ariaLabel={`علامت‌گذاری اطلاعیهٔ ${item.subject} به‌عنوان خوانده‌شده`} />}
              </footer>
            </article>
          )) : <div className="panel announcement-empty-state">اطلاعیه‌ای برای حساب شما ثبت نشده است.</div>}
        </section>
      </>
    </>
  );
}
