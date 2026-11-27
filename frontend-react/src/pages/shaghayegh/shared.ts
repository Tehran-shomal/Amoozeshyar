export type Row = Record<string, unknown>;

export function asObject(value: unknown): Row {
  return typeof value === "object" && value !== null ? value as Row : {};
}

export function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export function text(value: unknown, fallback = "—"): string {
  return value === null || value === undefined || value === "" ? fallback : String(value);
}

export function pageHrefWith(slug: string, bootstrap: { sectionUrlTemplate: string; homeUrl: string }, params: Record<string, string | number | null | undefined>): string {
  const target = new URL(slug ? bootstrap.sectionUrlTemplate.replace("__slug__", encodeURIComponent(slug)) : bootstrap.homeUrl, window.location.origin);
  const current = new URLSearchParams(window.location.search);
  for (const key of ["student_code", "term", "react"]) {
    const value = current.get(key);
    if (value) target.searchParams.set(key, value);
  }
  Object.entries(params).forEach(([key, value]) => {
    if (value === null || value === undefined || value === "") target.searchParams.delete(key);
    else target.searchParams.set(key, String(value));
  });
  return `${target.pathname}${target.search}`;
}

export function enrollmentErrorMessage(error: unknown): string {
  const code = typeof error === "object" && error !== null && "code" in error ? String((error as { code?: unknown }).code) : "";
  const messages: Record<string, string> = {
    authentication_required: "نشست پایان یافته است؛ دوباره وارد شوید.",
    permission_denied: "حساب شما اجازهٔ انجام این عملیات را ندارد.",
    student_profile_not_found: "پروندهٔ دانشجویی پیدا نشد.",
    student_profile_ambiguous: "ابتدا پروندهٔ دانشجویی را انتخاب کنید.",
    registration_window_closed: "بازهٔ انتخاب واحد باز نیست.",
    drop_window_closed: "بازهٔ حذف درس باز نیست.",
    emergency_drop_window_closed: "بازهٔ حذف اضطراری باز نیست.",
    tuition_debt: "بدهی شهریه مانع انتخاب واحد است.",
    offering_full: "ظرفیت درس تکمیل شده است.",
    credit_limit_exceeded: "انتخاب این درس از سقف مجاز واحد بیشتر است.",
    schedule_conflict: "زمان درس با برنامهٔ شما تداخل دارد.",
    exam_conflict: "زمان امتحان این درس با امتحان دیگری تداخل دارد.",
    prerequisite_not_met: "پیش‌نیاز درس گذرانده نشده است.",
    corequisite_not_met: "هم‌نیاز این درس ثبت نشده است.",
    term_not_active: "این نیمسال فعال نیست.",
    student_not_eligible: "وضعیت تحصیلی اجازهٔ انتخاب واحد نمی‌دهد.",
    enrollment_not_owned: "این ثبت‌نام متعلق به شما نیست.",
    enrollment_not_found: "ثبت‌نام موردنظر پیدا نشد.",
    database_unavailable: "پایگاه داده در دسترس نیست.",
  };
  if (messages[code]) return messages[code];
  return error instanceof Error ? `عملیات انجام نشد. ${error.message}` : "عملیات انجام نشد؛ دوباره تلاش کنید.";
}
