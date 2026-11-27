import { useState, type FormEvent } from "react";
import { PortalApi } from "../api/client";
import type { FormFieldSchema, FormSchema } from "../forms/types";

interface DynamicFormProps {
  schema: FormSchema;
  title?: string;
  submitUrl: string;
  sectionClassName?: string;
  formClassName?: string;
  fieldsClassName?: string;
  submitLabel?: string;
  submitDisabled?: boolean;
  disabledMessage?: string;
  disabledLabel?: string;
}

export function DynamicForm({
  schema: initialSchema,
  title,
  submitUrl,
  sectionClassName = "panel form-panel",
  formClassName = "demo-form",
  fieldsClassName = "",
  submitLabel = "ثبت اطلاعات",
  submitDisabled = false,
  disabledMessage = "",
  disabledLabel = "",
}: DynamicFormProps) {
  const [schema, setSchema] = useState(initialSchema);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const result = await PortalApi.submitPage(submitUrl, new FormData(event.currentTarget));
      if (result.form) setSchema(result.form);
      if (result.redirect) {
        window.location.assign(result.redirect);
        return;
      }
      if (result.error) setMessage(result.error.message);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "ثبت اطلاعات انجام نشد.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={sectionClassName}>
      <div className="panel-heading"><h2>{title || "ثبت اطلاعات"}</h2></div>
      {message && <div className="inline-notice" role="alert"><p>{message}</p></div>}
      {submitDisabled && disabledMessage && <p className="inline-notice" role="status">{disabledMessage}</p>}
      {schema.non_field_errors.length > 0 && (
        <div className="inline-notice" role="alert"><ul>{schema.non_field_errors.map((error, index) => <li key={index}>{error}</li>)}</ul></div>
      )}
      <form className={formClassName} onSubmit={submit} encType="multipart/form-data">
        {fieldsClassName
          ? <div className={fieldsClassName}>{schema.fields.map((field) => <FormField key={`${field.name}-${String(field.value ?? "")}`} field={field} />)}</div>
          : schema.fields.map((field) => <FormField key={`${field.name}-${String(field.value ?? "")}`} field={field} />)}
        <button className={`button button--primary${submitDisabled ? " button--disabled" : ""}`} type="submit" disabled={busy || submitDisabled || schema.fields.every((field) => field.disabled)}>
          {busy ? "در حال ثبت…" : submitDisabled ? (disabledLabel || submitLabel) : submitLabel}
        </button>
      </form>
    </section>
  );
}

function FormField({ field }: { field: FormFieldSchema }) {
  const errorId = `${field.id || field.name}-errors`;
  const common = {
    id: field.id || field.name,
    name: field.name,
    required: field.required,
    disabled: field.disabled,
    "aria-invalid": field.errors.length > 0,
    "aria-describedby": field.errors.length ? errorId : undefined,
  };

  if (field.type === "hidden") {
    return <input type="hidden" name={field.name} value={String(field.value ?? "")} />;
  }

  if (field.type === "checkbox-group" || field.type === "radio") {
    const selected = Array.isArray(field.value) ? field.value.map(String) : [String(field.value ?? "")];
    return (
      <fieldset className="form-field form-choice-group" disabled={field.disabled} aria-describedby={field.errors.length ? errorId : undefined}>
        <legend>{field.label}{field.required ? " *" : ""}</legend>
        {field.choices.map((choice, index) => (
          <label className="form-choice" key={`${choice.value}-${index}`}>
            <input
              type={field.type === "radio" ? "radio" : "checkbox"}
              name={field.name}
              value={choice.value}
              required={field.type === "radio" && field.required && index === 0}
              defaultChecked={selected.includes(choice.value)}
            />
            <span>{choice.label}</span>
          </label>
        ))}
        <FieldErrors id={errorId} errors={field.errors} />
      </fieldset>
    );
  }

  return (
    <div className="form-field">
      {field.type !== "checkbox" && <label htmlFor={common.id}>{field.label}{field.required ? " *" : ""}</label>}
      {field.type === "textarea" ? (
        <textarea {...common} defaultValue={String(field.value ?? "")} placeholder={field.placeholder || undefined} />
      ) : field.type === "select" || field.type === "select-multiple" ? (
        <select
          {...common}
          multiple={field.type === "select-multiple" || field.multiple}
          defaultValue={field.multiple || field.type === "select-multiple"
            ? (Array.isArray(field.value) ? field.value.map(String) : [])
            : String(field.value ?? "")}
        >
          {!field.required && !field.multiple && <option value="">انتخاب کنید</option>}
          {field.choices.map((choice, index) => <option key={`${choice.value}-${index}`} value={choice.value}>{choice.label}</option>)}
        </select>
      ) : field.type === "checkbox" ? (
        <label className="form-choice" htmlFor={common.id}>
          <input {...common} type="checkbox" value="on" defaultChecked={Boolean(field.value)} />
          <span>{field.label}{field.required ? " *" : ""}</span>
        </label>
      ) : (
        <input
          {...common}
          type={allowedInputType(field.type)}
          defaultValue={field.type === "file" ? undefined : String(field.value ?? "")}
          placeholder={field.placeholder || undefined}
          autoComplete="off"
        />
      )}
      {field.help_text && <small>{field.help_text}</small>}
      <FieldErrors id={errorId} errors={field.errors} />
    </div>
  );
}

function FieldErrors({ id, errors }: { id: string; errors: string[] }) {
  if (!errors.length) return null;
  return <ul className="field-errors" id={id} role="alert">{errors.map((error, index) => <li key={index}>{error}</li>)}</ul>;
}

function allowedInputType(type: string): string {
  const allowed = new Set(["text", "password", "email", "url", "number", "date", "time", "datetime-local", "file", "tel", "search"]);
  return allowed.has(type) ? type : "text";
}
