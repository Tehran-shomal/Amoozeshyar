# برنامهٔ هفتگی کامل

- مالک/route: Niousha/Pouya؛ `/portal/schedule/`; shared `core/live_content.html`; Niousha/Pouya selector.
- مرجع: PDF صفحهٔ ۲۲.
- هدف/کنترل: جدول درس/استاد/روز/شروع/پایان/کلاس و چاپ مرورگر.
- داده/API: active Enrollment، CourseOffering، Lesson، Teacher، Classroom فیلترشده به Student/Term؛ GET API page.
- نوشتن/اعتبارسنجی: read-only؛ تغییر برنامه از ثبت‌نام API است.
- دسترسی/خطا: session و پروندهٔ جاری؛ term خالی state؛ query فقط active enrollmentها.
- navigation: ترم و فعالیت آموزشی؛ print button `window.print()`.
- آزمون/وابستگی: `apps/core/test_frontend.py`; `active_enrollment_rows`, common live content.
- وضعیت: دادهٔ واقعی و print UI؛ اختلاف‌های typography/منو در comparison و viewport تازه باز.
