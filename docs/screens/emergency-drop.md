# حذف اضطراری

- مالک/route: Shaghayegh؛ `/portal/emergency-drop/`; از همان template/selector و JS صفحهٔ حذف و اضافه.
- مرجع: PDF صفحهٔ ۵۴؛ نتیجه‌های جدا صفحات ۷۵–۷۸؛ تأییدها ۹۳–۹۶.
- هدف/کنترل: جدول enrollment فعال، action حذف اضطراری و مودال تأیید.
- داده/API: Student, Enrollment, CourseOffering, Term؛ GET page و `POST /api/enrollment/drop/<id>/`.
- قاعدهٔ موجود: service بازهٔ emergency-drop **یا** add/drop را می‌پذیرد؛ endpoint پارامتر «نوع حذف» دریافت نمی‌کند و تفاوت فقط label/UI است.
- اعتبارسنجی/مجوز: session/student و مالکیت Enrollment؛ زمان از Term واقعی؛ idempotent برای enrollment غیرفعال.
- خطا/نتیجه: خارج بازه `drop_window_closed`; نتیجه‌های مستقل PDF route ندارند؛ data unavailable پیام خطا.
- navigation: پس از تأیید reload؛ لینک‌های دیگر sidebar مشترک.
- آزمون/وابستگی: `apps/core/enrollment/test_services.py`, `apps/core/test_frontend.py`, `static/core/tests/portal_bindings.test.cjs`.
- وضعیت: حذف واقعی و dialog؛ سیاست مستقل متمایز از add/drop در backend اثبات نشده؛ viewport تازه باز.
