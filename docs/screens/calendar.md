# تقویم آموزشی ترم

- مالک/route: Niousha/Pouya؛ `/portal/calendar/`; shared `core/live_content.html`; Niousha/Pouya selector.
- مرجع: PDF صفحهٔ ۱۵.
- هدف مرجع: grid تقویم رویدادهای ترم؛ دادهٔ کد فعلی محدودتر است.
- داده/API: Term.start/end, registration, add_drop, emergency_drop dates؛ GET API صفحه.
- نوشتن/اعتبارسنجی: read-only؛ رویداد جدا، برچسب امتحان و model calendar ندارد.
- دسترسی/خطا: session + term انتخاب‌شده؛ نبود term notice؛ تاریخ‌ها از رکورد Term موجود.
- navigation: group آموزشی/term picker.
- آزمون/وابستگی: `apps/core/test_frontend.py`; selector, Term.
- وضعیت: بازه‌های term نمایش داده می‌شوند، اما grid و رویدادهای کامل PDF در selector فعلی تأیید نشده؛ screenshot تازه باز.
