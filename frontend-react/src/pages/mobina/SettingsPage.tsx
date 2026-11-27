import { useState, type FormEvent } from "react";
import type { FormFieldSchema, FormSchema } from "../../forms/types";
import type { PagePayload } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { PortalApi } from "../../api/client";
import { portalPageHref } from "../../app/navigation";

function field(schema: FormSchema, name: string): FormFieldSchema | undefined {
  return schema.fields.find((item) => item.name === name);
}

function LanguageField({ item }: { item: FormFieldSchema }) {
  const selected = String(item.value ?? "");
  return <>
    <div className="settings-language-options" role="radiogroup" aria-label={item.label}>
      {item.choices.map((choice) => <label className={`settings-language-option${selected === choice.value ? " is-selected" : ""}`} key={choice.value}>
        <input type="radio" name={item.name} value={choice.value} defaultChecked={selected === choice.value} required={item.required} disabled={item.disabled} />
        <span>{choice.label}</span>
      </label>)}
    </div>
    <FieldErrors errors={item.errors} />
  </>;
}

function FieldErrors({ errors }: { errors: string[] }) {
  return errors.length ? <ul className="field-errors" role="alert">{errors.map((error, index) => <li key={index}>{error}</li>)}</ul> : null;
}

function AccountField({ item, multiline = false }: { item: FormFieldSchema; multiline?: boolean }) {
  return <div className="form-field">
    <label htmlFor={item.id || item.name}>{item.label}{item.required ? " *" : ""}</label>
    {multiline
      ? <textarea id={item.id || item.name} name={item.name} defaultValue={String(item.value ?? "")} required={item.required} disabled={item.disabled} placeholder={item.placeholder || undefined} />
      : <input id={item.id || item.name} name={item.name} type={item.type === "email" ? "email" : "text"} defaultValue={String(item.value ?? "")} required={item.required} disabled={item.disabled} placeholder={item.placeholder || undefined} autoComplete={item.name === "email" ? "email" : "street-address"} />}
    <FieldErrors errors={item.errors} />
  </div>;
}

function checked(value: unknown): boolean {
  return value === true || value === "on" || value === "true" || value === "True" || value === 1;
}

export function SettingsPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const [schema, setSchema] = useState(payload.form);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [revision, setRevision] = useState(0);
  if (!schema) return <section className="panel"><p className="empty-state">فرم تنظیمات در دسترس نیست.</p></section>;

  const language = field(schema, "preferred_language");
  const notifications = field(schema, "is_notification_enabled");
  const email = field(schema, "email");
  const address = field(schema, "address");
  const categories = Array.isArray(payload.data.notification_categories) ? payload.data.notification_categories : [];

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const result = await PortalApi.submitPage(bootstrap.submitUrl, new FormData(event.currentTarget));
      if (result.form) {
        setSchema(result.form);
        setRevision((value) => value + 1);
      }
      if (result.redirect) window.location.assign(result.redirect);
      else if (result.error) setError(result.error.message);
      else window.location.reload();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "ذخیرهٔ تنظیمات انجام نشد.");
    } finally {
      setBusy(false);
    }
  }

  return <div className="settings-page">
    {payload.data.settings_save_result === true && <section className="panel settings-save-result" role="status" aria-live="polite">
      <div className="panel-heading"><h2>نتیجهٔ عملیات</h2></div>
      <p>تنظیمات در حساب شما ذخیره شد.</p>
      <p>زبان انتخابی: {String(language?.choices.find((choice) => choice.value === String(language.value ?? ""))?.label || "—")} · ترجیح کلی اعلان: {checked(notifications?.value) ? "فعال" : "غیرفعال"}</p>
      <p className="settings-channel-notice">این صفحه تنظیمات را در حساب محلی ذخیره می‌کند؛ ترجیح اعلان فقط ذخیره شده و سرویس اعلان فعلی آن را اعمال نمی‌کند. کانال پیامک/رایانامه تنظیم‌پذیر نیست.</p>
      <a className="button button--primary" href={portalPageHref("settings", bootstrap)}>متوجه شدم</a>
    </section>}

    <form key={revision} method="post" className="settings-form live-form" onSubmit={submit}>
      {error && <div className="inline-notice" role="alert"><p>{error}</p></div>}
      {schema.non_field_errors.length > 0 && <div className="inline-notice" role="alert"><ul>{schema.non_field_errors.map((item, index) => <li key={index}>{item}</li>)}</ul></div>}

      <section className="panel settings-language-panel">
        <div className="panel-heading"><h2>زبان و نمایش</h2></div>
        <div className="settings-language-row"><strong>زبان رابط کاربری</strong>{language && <LanguageField item={language} />}</div>
        <p>زبان انتخاب‌شده پس از ذخیره در حساب کاربری ثبت می‌شود.</p>
      </section>

      <section className="panel settings-notifications-panel">
        <div className="panel-heading"><h2>روش دریافت اعلان‌ها</h2></div>
        <div className="settings-notification-grid" role="table" aria-label="وضعیت پشتیبانی کانال‌های اعلان">
          <div className="settings-notification-header" role="row"><span role="columnheader">دستهٔ اعلان</span><span role="columnheader">داخل سامانه</span><span role="columnheader">پیامک</span><span role="columnheader">رایانامه</span></div>
          {categories.map((category, index) => <div className="settings-notification-row" role="row" key={`${String(category)}-${index}`}>
            <strong role="cell">{String(category)}</strong><span role="cell">ترجیح کلی ذخیره‌شده</span><span className="settings-channel-unavailable" role="cell">تنظیم‌پذیر نیست</span><span className="settings-channel-unavailable" role="cell">تنظیم‌پذیر نیست</span>
          </div>)}
        </div>
        {notifications && <div className="settings-notification-toggle"><input id={notifications.id || notifications.name} type="checkbox" name={notifications.name} value="on" defaultChecked={checked(notifications.value)} disabled={notifications.disabled} /><label htmlFor={notifications.id || notifications.name}>{notifications.label}</label><FieldErrors errors={notifications.errors} /></div>}
        <p className="settings-channel-notice" role="note">این گزینه فقط در اطلاعات حساب ذخیره می‌شود و فعلاً سرویس اعلان آن را اعمال نمی‌کند. تنظیم جداگانهٔ پیامک/رایانامه و شمارهٔ همراه در مدل فعلی وجود ندارد؛ ارسال بیرونی فعال یا تضمین نمی‌شود.</p>
      </section>

      <section className="panel settings-contact-panel">
        <div className="panel-heading"><h2>اطلاعات حساب</h2></div>
        <div className="settings-contact-grid">{email && <AccountField item={email} />}{address && <AccountField item={address} />}</div>
        <p className="settings-channel-notice" role="note">شمارهٔ همراه در مدل فعلی قابل ثبت یا ویرایش نیست.</p>
      </section>

      <div className="page-actions settings-page-actions">
        <button className="button button--primary" type="submit" disabled={busy}>{busy ? "در حال ذخیره…" : "ذخیره تنظیمات"}</button>
        <a className="button button--soft" href={portalPageHref("notifications", bootstrap)}>مرکز اعلان‌ها</a>
      </div>
    </form>
  </div>;
}
