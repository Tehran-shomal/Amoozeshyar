# برنامهٔ هفتگی کامل

- مالک/route: Niousha؛ `/portal/schedule/`; `niousha/schedule.html`; `niousha.selectors`.
- مرجع: [PDF صفحهٔ ۲۲](page-22-reference.png).
- هدف/کنترل: چهار خلاصهٔ نیمسال/واحد/جلسات/تداخل و جدول ماتریسی روز×بازهٔ ساعت با چاپ مرورگر.
- داده/API: GET `/api/portal/pages/schedule/`; فقط Enrollment فعال پرونده/ترم جاری و CourseOffering/Lesson/Teacher/Classroom واقعی.
- نوشتن/اعتبارسنجی: read-only؛ تغییر برنامه از ثبت‌نام API است.
- دسترسی/خطا: session و پروندهٔ جاری؛ روز نامشخص جداگانه اعلام می‌شود؛ ترم بی‌ثبت‌نام empty state؛ فقط active enrollmentها.
- navigation: پیوند واقعی به دروس انتخاب‌شده و تقویم؛ print button `window.print()`.
- آزمون/وابستگی: `apps/core/test_frontend.py::test_schedule_page_renders_owned_enrollments_in_a_weekly_grid`; regression افزوده شد اما به درخواست کاربر اجرا نشده.
- وضعیت: source/API و مرجع بررسی شدند؛ generic table با شبکهٔ داده‌محور جایگزین شد. capture احرازشدهٔ فعلی در دسترس نیست و تطبیق بصری runtime باز است.
