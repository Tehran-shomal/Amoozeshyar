# انتخاب نیمسال (جزء مشترک)

- مالک: لید مشترک Neyousha/Pouya؛ در `portal_base.html` و `static/core/live_portal.js`.
- مرجع: PDF صفحهٔ ۳؛ component است و URL مستقل ندارد.
- هدف/کنترل‌ها: انتخاب رکورد Term و reload محتوای صفحه با `?term=<term_code>`؛ کد کامل برای query حفظ و label نمایشی کوتاه می‌شود.
- داده/API: فهرست `Term` در payload HTML صفحه؛ `GET /api/scheduling/active-term/` فقط فعال‌بودن/tooltip را می‌دهد؛ offeringها در صفحه‌های مرتبط از scheduling API می‌آیند.
- ورودی/اعتبارسنجی: term code باید در DB موجود باشد؛ term ناموجود در API صفحه 404 `page_data_not_found` و در offerings 404 `term_not_found`.
- مجوز/خطا: session لازم؛ CSRF برای عمل تغییردهنده‌ای در خود picker نیست؛ خطای خواندن از پیام مشترک UI.
- مسیر: انتخاب نیمسال همان صفحه را با query جدید بارگیری می‌کند؛ رکورد یا داده‌ای را تغییر نمی‌دهد.
- آزمون/وابستگی: `apps/core/test_frontend.py`, `apps/core/scheduling/test_services.py`, `static/core/tests/portal_bindings.test.cjs`; Term model و shell JS.
- وضعیت: انتخاب query-backed؛ فهرست term ثابت یا route مستقل نیست؛ تست viewport تازه باز است.
