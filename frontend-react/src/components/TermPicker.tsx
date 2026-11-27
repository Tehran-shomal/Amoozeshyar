import { useEffect, useRef, useState, type FormEvent } from "react";
import type { PortalShellData } from "../api/types";

export function TermPicker({ shell, termLabel }: { shell: PortalShellData; termLabel: string }) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const current = shell.term_options.find((option) => option.selected)?.value || "";
  const [value, setValue] = useState(current);

  useEffect(() => setValue(current), [current]);
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (dialog.open) dialog.close();
  }, []);

  function apply(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!value) return;
    const url = new URL(window.location.href);
    url.searchParams.set("term", value);
    window.location.assign(`${url.pathname}${url.search}`);
  }

  function open() {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) dialog.showModal();
  }

  function close() {
    const dialog = dialogRef.current;
    if (dialog?.open) dialog.close();
  }

  return (
    <>
      <div className="term-picker" aria-label="نیمسال تحصیلی">
        <span className="term-picker-current"><small>نیمسال تحصیلی:</small><strong>{termLabel || "—"}</strong></span>
        <button className="term-picker-button" type="button" onClick={open} disabled={!shell.term_options.length}>انتخاب نیمسال</button>
      </div>
      <dialog className="term-selection-dialog" ref={dialogRef} aria-labelledby="term-dialog-title" onCancel={(event) => { event.preventDefault(); close(); }}>
        <div className="term-dialog-heading">
          <h2 id="term-dialog-title">انتخاب نیمسال تحصیلی</h2>
          <button className="term-dialog-close" type="button" aria-label="بستن" onClick={close}>×</button>
        </div>
        <form className="term-selection-form" onSubmit={apply}>
          {shell.current_profile && <input type="hidden" name="student_code" value={shell.current_profile.student_code} />}
          {new URLSearchParams(window.location.search).get("react") === "1" && <input type="hidden" name="react" value="1" />}
          {new URLSearchParams(window.location.search).get("legacy") === "1" && <input type="hidden" name="legacy" value="1" />}
          <fieldset className="term-option-list">
            <legend className="sr-only">نیمسال موردنظر را انتخاب کنید</legend>
            {shell.term_options.length ? shell.term_options.map((option) => (
              <label className="term-option" key={option.value}>
                <input type="radio" name="term" value={option.value} checked={value === option.value} onChange={() => setValue(option.value)} required />
                <span>{option.display_label}</span>
              </label>
            )) : <p className="empty-state">نیمسالی برای انتخاب ثبت نشده است.</p>}
          </fieldset>
          <p className="term-selection-note">داده‌های این پیش‌نمایش تنها برای نیمسال انتخاب‌شده بارگذاری می‌شوند.</p>
          <button className="term-picker-submit" type="submit" disabled={!shell.term_options.length}>انتخاب و بستن</button>
        </form>
      </dialog>
    </>
  );
}
