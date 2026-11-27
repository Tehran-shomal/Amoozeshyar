import { useState, type FormEvent } from "react";
import type { PagePayload, SubmitResult } from "../../api/types";
import { PortalApi } from "../../api/client";
import { portalPageHref } from "../../app/navigation";
import { asList, asObject, displayText } from "../niousha/display";
import type { FormFieldSchema, FormSchema } from "../../forms/types";
import type { PortalBootstrap } from "../../types";

export function EvaluationFormPage({ payload, bootstrap }: { payload: PagePayload; bootstrap: PortalBootstrap }) {
  const data = payload.data;
  const notice = payload.shell.profile_notice;
  const selected = data.evaluation_selected_enrollment ? asObject(data.evaluation_selected_enrollment) : null;
  const survey = data.evaluation_selected_survey ? asObject(data.evaluation_selected_survey) : null;
  const options = asList(data.evaluation_enrollment_options).map(asObject);
  if (notice) return <div className="inline-notice" role="status"><p>{notice}</p></div>;

  if (!selected) {
    if (!options.length) return <section className="panel evaluation-empty-panel"><p>برای این نیمسال ارزشیابی تکمیل‌نشده‌ای ثبت نشده است.</p><a className="button button--soft" href={portalPageHref("evaluation", bootstrap)}>بازگشت به فهرست</a></section>;
    return <section className="panel evaluation-list-panel" aria-labelledby="evaluation-select-title">
      <div className="panel-heading"><h2 id="evaluation-select-title">درس موردنظر را انتخاب کنید</h2></div>
      <div className="evaluation-course-list">{options.map((enrollment, index) => {
        const target = new URL(portalPageHref("evaluation-form", bootstrap), window.location.origin);
        target.searchParams.set("enrollment", String(enrollment.id ?? ""));
        return <article className="evaluation-course-row" key={`${enrollment.id ?? index}`}>
          <div className="evaluation-course-copy"><strong>{displayText(enrollment.lesson)}</strong><small>{displayText(enrollment.teacher)}</small></div>
          <span className="evaluation-course-status">تکمیل‌نشده</span>
          <a className="button button--primary" href={`${target.pathname}${target.search}`}>انتخاب درس</a>
        </article>;
      })}</div>
    </section>;
  }

  return <>
    <div className="evaluation-course-info" aria-label="اطلاعات درس و ارزشیابی">
      <span>{displayText(selected.lesson)}</span><span>{displayText(selected.teacher)}</span>
      <span>نیمسال {displayText(payload.term.display_label)}</span><span>پاسخ‌ها محرمانه هستند.</span>
    </div>
    {survey ? <SubmittedEvaluation survey={survey} bootstrap={bootstrap} /> : payload.form
      ? <EvaluationSubmissionForm schema={payload.form} bootstrap={bootstrap} />
      : <section className="panel"><p className="empty-state">فرم ارزشیابی برای این درس در دسترس نیست.</p></section>}
  </>;
}

function SubmittedEvaluation({ survey, bootstrap }: { survey: Record<string, unknown>; bootstrap: PortalBootstrap }) {
  const ratings = asObject(survey.ratings);
  const criteria: Array<[string, string]> = [
    ["teaching_quality", "کیفیت تدریس"],
    ["behavior", "رفتار استاد"],
  ];
  const hasRatings = criteria.some(([key]) => ratings[key] !== null && ratings[key] !== undefined && ratings[key] !== "");
  return <section className="panel evaluation-submitted-panel">
    <h2>ارزشیابی نهایی ثبت شده است</h2>
    <p className="evaluation-submitted-summary">امتیاز کلی ثبت‌شده: {displayText(survey.overall_rating)} از ۵</p>
    {hasRatings ? <dl className="evaluation-submitted-ratings">{criteria.map(([key, label]) => <div key={key}><dt>{label}</dt><dd>{displayText(ratings[key])}</dd></div>)}</dl> : null}
    {survey.comment ? <p className="evaluation-submitted-comment">{displayText(survey.comment, "")}</p> : null}
    <div className="page-actions"><a className="button button--soft" href={portalPageHref("evaluation", bootstrap)}>بازگشت به فهرست</a></div>
  </section>;
}

function EvaluationSubmissionForm({ schema: initialSchema, bootstrap }: { schema: FormSchema; bootstrap: PortalBootstrap }) {
  const [schema, setSchema] = useState(initialSchema);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const fields = new Map(schema.fields.map((field) => [field.name, field]));
  const ratings = schema.fields.filter((field) => field.type === "radio");
  const enrollment = fields.get("enrollment");
  const comment = fields.get("comment");

  function updateField(name: string, value: string) {
    setSchema((previous) => ({
      ...previous,
      fields: previous.fields.map((field) => field.name === name ? { ...field, value, errors: [] } : field),
    }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const result: SubmitResult = await PortalApi.submitPage(bootstrap.submitUrl, new FormData(event.currentTarget));
      if (result.form) setSchema(result.form);
      if (result.redirect) {
        window.location.assign(result.redirect);
        return;
      }
      if (result.error) setMessage(result.error.message);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "ثبت ارزشیابی انجام نشد.");
    } finally {
      setBusy(false);
    }
  }

  return <section className="panel evaluation-form-panel">
    {message && <div className="inline-notice" role="alert"><p>{message}</p></div>}
    {schema.non_field_errors.length > 0 && <div className="inline-notice" role="alert"><ul>{schema.non_field_errors.map((error, index) => <li key={index}>{error}</li>)}</ul></div>}
    <form method="post" className="live-form evaluation-live-form" onSubmit={submit}>
      {enrollment && <input type="hidden" name={enrollment.name} value={String(enrollment.value ?? "")} />}
      <div className="evaluation-questions">
        <header className="evaluation-panel-heading"><h2>میزان موافقت خود را مشخص کنید</h2><p className="evaluation-rating-key">۱ بسیار کم&nbsp;&nbsp; ۲ کم&nbsp;&nbsp; ۳ متوسط&nbsp;&nbsp; ۴ زیاد&nbsp;&nbsp; ۵ بسیار زیاد</p></header>
        {ratings.map((field, index) => <RatingQuestion field={field} index={index} onChange={updateField} key={field.name} />)}
      </div>
      {comment && <label className="evaluation-comment" htmlFor={comment.id || comment.name}>
        <span>{comment.label} (اختیاری)</span>
        <textarea id={comment.id || comment.name} name={comment.name} value={String(comment.value ?? "")} onChange={(event) => updateField(comment.name, event.currentTarget.value)} aria-invalid={comment.errors.length > 0} aria-describedby={comment.errors.length ? `${comment.id || comment.name}-errors` : undefined} />
        {comment.errors.map((error, index) => <small className="field-error" id={`${comment.id || comment.name}-errors`} key={index}>{error}</small>)}
      </label>}
      <p className="evaluation-action-note">✓ پاسخ‌ها محرمانه هستند. پس از ثبت نهایی، ویرایش امکان‌پذیر نیست.</p>
      <div className="page-actions evaluation-form-actions">
        <button className="button button--primary" type="submit" disabled={busy}>{busy ? "در حال ثبت…" : "ثبت نهایی ارزشیابی"}</button>
        <a className="button button--soft" href={portalPageHref("evaluation", bootstrap)}>بازگشت به فهرست</a>
      </div>
    </form>
  </section>;
}

function RatingQuestion({ field, index, onChange }: { field: FormFieldSchema; index: number; onChange: (name: string, value: string) => void }) {
  const selected = String(field.value ?? "");
  const errorId = `${field.id || field.name}-errors`;
  return <fieldset className="evaluation-question" aria-describedby={field.errors.length ? errorId : undefined}>
    <legend><span className="evaluation-question-number">{index + 1}</span>{field.label}</legend>
    <div className="evaluation-rating-options">{field.choices.map((choice, choiceIndex) => <label className="evaluation-rating-option" key={`${choice.value}-${choiceIndex}`}>
      <input type="radio" name={field.name} value={choice.value} required={field.required && choiceIndex === 0} checked={selected === choice.value} onChange={() => onChange(field.name, choice.value)} />
      <span>{choice.label}</span>
    </label>)}</div>
    {field.errors.length > 0 && <ul className="field-errors" id={errorId} role="alert">{field.errors.map((error, errorIndex) => <li key={errorIndex}>{error}</li>)}</ul>}
  </fieldset>;
}
