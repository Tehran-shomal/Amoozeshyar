import { useEffect, useMemo, useRef, useState } from "react";
import { PortalApi, PortalApiError } from "../../api/client";
import type { CourseOffering, PortalShellData } from "../../api/types";
import type { PortalBootstrap } from "../../types";
import { portalPageHref } from "../../app/navigation";
import { enrollmentErrorMessage, pageHrefWith, text, type Row } from "./shared";

interface PickerProps {
  bootstrap: PortalBootstrap;
  termCode: string | null;
  studentCode: string | null;
  shell: PortalShellData;
  overview: Row;
  successSlug: string;
}

const dayLabels: Record<string, string> = {
  saturday: "شنبه", sunday: "یکشنبه", monday: "دوشنبه", tuesday: "سه‌شنبه",
  wednesday: "چهارشنبه", thursday: "پنجشنبه", friday: "جمعه",
};

export function OfferingPicker({ bootstrap, termCode, studentCode, shell, overview, successSlug }: PickerProps) {
  const [open, setOpen] = useState(false);
  const [offerings, setOfferings] = useState<CourseOffering[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [selectedGroupKey, setSelectedGroupKey] = useState("");
  const [selectedOfferingId, setSelectedOfferingId] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [showDebt, setShowDebt] = useState(false);
  const closeButton = useRef<HTMLButtonElement>(null);
  const openerButton = useRef<HTMLButtonElement>(null);
  const dialogRef = useRef<HTMLElement>(null);
  const debtDialogRef = useRef<HTMLElement>(null);
  const debtBackButtonRef = useRef<HTMLButtonElement>(null);

  const groups = useMemo(() => {
    const grouped = new Map<string, CourseOffering[]>();
    offerings.forEach((offering) => {
      if (!Number.isInteger(offering.id) || offering.id <= 0) return;
      const key = `${offering.lesson_code}\u0000${offering.title}`;
      grouped.set(key, [...(grouped.get(key) || []), offering]);
    });
    return [...grouped.entries()];
  }, [offerings]);

  const selectedGroup = groups.find(([key]) => key === selectedGroupKey)?.[1] || [];
  const selectedOffering = selectedGroup.find((offering) => offering.id === selectedOfferingId) || null;

  useEffect(() => {
    if (!open) {
      document.body.classList.remove("modal-open");
      return;
    }
    document.body.classList.add("modal-open");
    if (showDebt) debtBackButtonRef.current?.focus();
    else closeButton.current?.focus();
    return () => document.body.classList.remove("modal-open");
  }, [open, showDebt, selectedGroupKey]);

  useEffect(() => {
    if (!open || offerings.length) return;
    let active = true;
    setLoading(true);
    setLoadError("");
    PortalApi.getOfferings(termCode).then((result) => {
      if (active) setOfferings(result.offerings || []);
    }).catch((error: unknown) => {
      if (active) setLoadError(enrollmentErrorMessage(error));
    }).finally(() => {
      if (active) setLoading(false);
    });
    return () => { active = false; };
  }, [open, termCode]);

  function close() {
    setOpen(false);
    setSelectedGroupKey("");
    setSelectedOfferingId(null);
    setMessage("");
    setShowDebt(false);
    window.setTimeout(() => openerButton.current?.focus(), 0);
  }

  function dismissDebt() {
    setShowDebt(false);
    window.setTimeout(() => closeButton.current?.focus(), 0);
  }

  useEffect(() => {
    if (!open) return;
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        if (showDebt) dismissDebt();
        else close();
        return;
      }
      if (event.key !== "Tab") return;

      const dialog = showDebt ? debtDialogRef.current : dialogRef.current;
      if (!dialog) return;
      const focusable = Array.from(dialog.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
      ));
      if (!focusable.length) {
        event.preventDefault();
        dialog.focus();
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      const active = document.activeElement;
      if (event.shiftKey && (active === first || !dialog.contains(active))) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && (active === last || !dialog.contains(active))) {
        event.preventDefault();
        first.focus();
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, showDebt]);

  async function register() {
    if (!selectedOffering || busy) return;
    setBusy(true);
    setMessage("");
    try {
      const result = await PortalApi.registerOffering(selectedOffering.id, studentCode);
      const enrollmentId = result.enrollment?.id;
      if (!enrollmentId) throw new Error("پاسخ ثبت‌نام شناسهٔ پرونده را برنگرداند.");
      window.location.assign(pageHrefWith(successSlug, bootstrap, {
        student_code: studentCode,
        registration_id: enrollmentId,
        dropped_enrollment_id: null,
      }));
    } catch (error) {
      if (error instanceof PortalApiError && error.code === "tuition_debt") setShowDebt(true);
      else setMessage(enrollmentErrorMessage(error));
    } finally {
      setBusy(false);
    }
  }

  return <>
    <button ref={openerButton} className="button button--primary" type="button" onClick={() => setOpen(true)} aria-expanded={open} aria-haspopup="dialog">انتخاب درس‌ها</button>
    {open && <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget && !showDebt) close(); }}>
      <section ref={dialogRef} className="modal-dialog" role="dialog" aria-modal="true" aria-labelledby="course-modal-title">
        {!selectedGroup.length ? <section className="course-modal-list">
          <header className="modal-heading"><div><h2 id="course-modal-title">انتخاب درس‌ها</h2><p>نیمسال {text(termCode)} · {text(shell.current_profile?.field_name, "رشتهٔ دانشجو")}</p></div><button ref={closeButton} type="button" onClick={close} aria-label="بستن پنجرهٔ انتخاب درس">بستن ×</button></header>
          <p className="modal-instruction">برای مشاهدهٔ استادان و زمان‌های ارائه، گروه درس را انتخاب کنید.</p>
          <div className="course-choice-list" aria-live="polite">
            {loading && <p className="empty-state">دروس نیمسال در حال دریافت است…</p>}
            {loadError && <p className="empty-state" role="alert">{loadError}</p>}
            {!loading && !loadError && !groups.length && <p className="empty-state">برای این نیمسال درسی ارائه نشده است.</p>}
            {groups.map(([key, group]) => {
              const offering = group[0];
              return <article className="course-choice" key={key}>
                <div><h3>{offering.title || "عنوان درس ثبت نشده"}</h3><p>کد {offering.lesson_code || "—"} · {offering.total_units} واحد</p><small>{group.length} ارائهٔ فعال</small></div>
                <button className="button button--primary" type="button" onClick={() => { setSelectedGroupKey(key); setSelectedOfferingId(group[0]?.id ?? null); setMessage(""); }}>انتخاب گروه</button>
              </article>;
            })}
          </div>
          <p className="action-note">ثبت نهایی هر درس پس از بررسی قوانین آموزشی و ظرفیت توسط API انجام می‌شود.</p>
        </section> : <section aria-labelledby="course-detail-title">
          <header className="modal-heading"><div><h2 id="course-detail-title">{selectedGroup[0]?.title || "عنوان درس ثبت نشده"}</h2><p className="course-modal-meta">کد درس: {selectedGroup[0]?.lesson_code || "—"} · {selectedGroup[0]?.total_units ?? 0} واحد</p></div><button ref={closeButton} type="button" onClick={close} aria-label="بستن پنجرهٔ انتخاب درس">بستن ×</button></header>
          <p className="course-modal-meta">شهریهٔ هر درس در اطلاعات سامانه ثبت نشده است.</p>
          {selectedOffering?.exam_date && <p className="course-modal-meta">زمان امتحان: {selectedOffering.exam_date}{selectedOffering.exam_time ? ` · ${selectedOffering.exam_time.slice(0, 5)}` : ""}</p>}
          <p className="course-totals-note">شمارهٔ گروه در داده‌های سامانه ثبت نشده است؛ ارائه را بر اساس استاد و زمان انتخاب کنید.</p>
          <div className="course-group-options" aria-label="ارائه‌های قابل انتخاب">{selectedGroup.map((offering) => {
            const remaining = offering.remaining_capacity;
            const disabled = remaining <= 0;
            const id = `offering-${offering.id}`;
            const day = offering.day_of_week ? dayLabels[offering.day_of_week.toLowerCase()] || "روز نامشخص" : "روز نامشخص";
            return <label className="course-group-option" htmlFor={id} key={offering.id}>
              <input id={id} type="radio" name="course-offering-choice" value={offering.id} checked={selectedOfferingId === offering.id} onChange={() => { setSelectedOfferingId(offering.id); setMessage(""); }} />
              <span><strong>ارائه با {offering.teacher || "استاد ثبت‌نشده"}</strong><small>{day} {offering.start_time.slice(0, 5)}–{offering.end_time.slice(0, 5)} · ظرفیت باقی‌مانده: {remaining} نفر</small><small>کلاس {offering.classroom?.building || "—"} · {offering.classroom?.room || "—"}{disabled ? " · ظرفیت تکمیل است" : ""}</small></span>
            </label>;
          })}</div>
          <p className="selected-group-note" role="status" aria-live="polite">{message || (selectedOffering?.remaining_capacity === 0 ? "ظرفیت این ارائه تکمیل است؛ ارائهٔ دیگری را انتخاب کنید." : "")}</p>
          <div className="page-actions">
            <button className="button button--primary" type="button" onClick={register} disabled={busy || !selectedOffering || selectedOffering.remaining_capacity <= 0}>{busy ? "در حال ثبت…" : "افزودن درس"}</button>
            <button className="button button--soft" type="button" onClick={() => { setSelectedGroupKey(""); setSelectedOfferingId(null); setMessage(""); }}>بازگشت به فهرست</button>
          </div>
        </section>}
      </section>
    </div>}
    {showDebt && <div className="tuition-debt-modal" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) dismissDebt(); }}>
      <section ref={debtDialogRef} className="tuition-debt-dialog" role="dialog" aria-modal="true" aria-labelledby="tuition-debt-title" aria-describedby="tuition-debt-description">
        <h2 id="tuition-debt-title">عملیات ثبت‌نام مجاز نیست</h2><p id="tuition-debt-description">بدهی شهریهٔ ثبت‌شده مانع ادامهٔ ثبت‌نام است. پس از تسویه، محدودیت‌های انتخاب واحد دوباره بررسی می‌شوند.</p>
        <div className="tuition-debt-facts"><div><span>حداقل واحد</span><strong>حداقل واحد در قوانین جاری سامانه تعریف نشده است</strong></div><div><span>حداکثر واحد مجاز</span><strong>{text(overview.maximum_allowed_units, "۰")} واحد</strong></div><div><span>بدهی شهریه</span><strong>{text(overview.tuition_debt_display)}</strong></div></div>
        <p className="tuition-debt-note">API فعلی بدهی و سقف حداکثر را کنترل می‌کند؛ قاعدهٔ حداقل واحد در مدل/سرویس تعریف نشده است.</p>
        <div className="tuition-debt-actions"><a className="button button--primary" href={portalPageHref("secure-payment", bootstrap)}>پرداخت بدهی</a><button ref={debtBackButtonRef} className="button button--soft" type="button" onClick={dismissDebt}>بازگشت</button></div>
      </section>
    </div>}
  </>;
}
