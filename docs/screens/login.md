# ورود

- مالک/مسیر: Mobina؛ `GET|POST /login/`، API نوشتنی `POST /api/accounts/login/`؛ template: `mobina/login.html`.
- مرجع: PDF صفحهٔ ۱.
- هدف/کنترل‌ها: شروع session؛ نام کاربری، گذرواژه، remember-me و پیام وضعیت خطا.
- ورودی: `username`, `password`, `remember_me`; browser API JSON و fallback HTML هر دو موجودند.
- داده: `Person`, `UserAccount`, `Role`; رمز با Django password hasher روی Person سنجیده می‌شود.
- اعتبارسنجی/مجوز: CSRF؛ حساب/role فعال؛ قفل پس از ۵ شکست برای ۹۰۰ ثانیه؛ در ورود موفق redirect به `/`.
- خطا: نامعتبر 401 در API، inactive 403، locked 423، DB 503؛ فرم HTML پیام فارسی می‌دهد.
- مسیر بعدی: dashboard؛ بازیابی گذرواژه در UI copy دارد اما flow/backend محلی ندارد.
- آزمون/وابستگی: `apps/core/accounts/test_services.py`, `static/core/tests/portal_api.test.cjs`, Mobina JS، session/CSRF middleware.
- وضعیت: ورود session-backed پیاده است؛ recovery پیاده نیست؛ تطبیق بصری screenshot تازهٔ این branch هنوز انجام نشده.
