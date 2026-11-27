import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";
import { DynamicForm } from "../../components/DynamicForm";

type Row = Record<string, unknown>;
function object(value: unknown): Row { return typeof value === "object" && value !== null ? value as Row : {}; }
function list(value: unknown): Row[] { return Array.isArray(value) ? value.map(object) : []; }
function text(value: unknown, fallback = "—"): string { return value === null || value === undefined || value === "" ? fallback : String(value); }

export function MessagesPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const data = payload.data;
  const teachers = list(data.message_teachers);
  const messages = list(data.message_history);
  const result = data.message_submission_result ? object(data.message_submission_result) : null;
  if (!payload.shell.current_profile) return <section className="panel"><p className="empty-state">برای ارتباط با استادان، پروندهٔ دانشجویی را انتخاب کنید.</p></section>;

  return <>
    {result && <section className="panel message-submission-result" role="status" aria-live="polite">
      <div className="panel-heading"><h2>نتیجهٔ عملیات</h2></div>
      <p>پیام «{text(result.subject)}» برای {text(result.receiver_name)} در سوابق مکاتبات حساب شما ثبت شد.</p>
      <p className="message-storage-note">این محیط به حساب واقعی استاد متصل نیست؛ ثبت پیام در این سامانه تحویل بیرونی را تأیید نمی‌کند.</p>
      <a className="button button--primary" href={portalPageHref("messages", bootstrap)}>متوجه شدم</a>
    </section>}

    <div className="content-columns messages-layout">
      <section className="panel message-list-panel" aria-label="استادان نیمسال انتخاب‌شده">
        <div className="panel-heading"><h2>استادان نیمسال {text(payload.term.display_label)}</h2></div>
        <div className="demo-card-list">
          {teachers.length ? teachers.map((teacher, index) => <article className="demo-card" key={`${teacher.teacher_name}-${index}`}>
            <div className="demo-card-copy"><strong>{text(teacher.teacher_name)}</strong>
              {list(teacher.lessons).map((lesson, lessonIndex) => <div key={lessonIndex}>
                <small>{text(lesson.title)} / {text(lesson.day)} / {text(lesson.start)}–{text(lesson.end)}</small>
                <small>{text(lesson.classroom)}</small>
              </div>)}
            </div>
          </article>) : <p className="empty-state">برای این پرونده در نیمسال انتخاب‌شده استاد فعالی ثبت نشده است.</p>}
        </div>
      </section>

      {payload.form && <DynamicForm
        schema={payload.form}
        title="ارسال پیام آموزشی"
        submitUrl={bootstrap.submitUrl}
        sectionClassName="panel form-panel message-form-panel"
        formClassName="live-form message-composer"
        submitLabel="ارسال پیام"
        submitDisabled={data.message_can_send !== true}
        disabledMessage="استاد دریافت‌کنندهٔ فعال برای این نیمسال در دسترس نیست."
        disabledLabel="ارسال پیام در دسترس نیست"
      />}
    </div>

    <div className="page-actions messages-page-actions"><a className="button button--soft" href={portalPageHref("announcements", bootstrap)}>اطلاعیه‌های استادان</a></div>

    <section className="panel latest-message">
      <div className="panel-heading"><h2>آخرین مکاتبات · {text(data.message_count, "0")}</h2></div>
      <div className="message-history-list">
        {messages.length ? messages.map((message, index) => {
          const sentByCurrent = message.sender_is_current_user === true;
          const sentAt = object(message.sent_at);
          return <article className="message-history-item" key={`${message.subject}-${index}`}>
            <header><strong>{text(message.subject)}</strong><time dateTime={text(sentAt.iso, "")}>{text(sentAt.display)}</time></header>
            <small>{sentByCurrent ? `شما → ${text(message.receiver_name)}` : `${text(message.sender_name)} → شما`}</small>
            <p>{text(message.message_body, "")}</p>
            <span className="message-storage-note">ثبت‌شده در سامانه؛ تحویل بیرونی از این داده قابل تأیید نیست.</span>
          </article>;
        }) : <p className="empty-state">مکاتبه‌ای برای حساب شما ثبت نشده است.</p>}
      </div>
      <p className="message-scope-note">{text(data.message_scope_note, "")}</p>
    </section>
  </>;
}
