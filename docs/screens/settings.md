# تنظیمات زبان و اعلان‌ها

- مالک/route: Niousha/Pouya؛ `/portal/settings/`; shared `core/live_content.html`; `SettingsForm`.
- مرجع: PDF صفحهٔ ۱۹؛ toggle notification crop صفحهٔ ۵۰ و انتخاب زبان crop صفحهٔ ۵۱.
- هدف/کنترل: email/address، فعال‌بودن اعلان و preferred language حساب خود.
- داده/API: Person, Constant؛ GET/POST API صفحه؛ form instance صریحاً `request.user` است.
- اعتبارسنجی/مجوز: فقط فیلدهای `email,address,is_notification_enabled,preferred_language`; session لازم؛ هیچ person id از client انتخاب نمی‌شود.
- خطا: form errors 400 همراه HTML؛ DB unavailable 503؛ CSRF برای save.
- navigation: sidebar footer/settings؛ انتخاب زبان یا اعلان مستقل route ندارد.
- آزمون/وابستگی: `apps/core/test_frontend.py`; SettingsForm/OwnedModelForm.
- وضعیت: ذخیرهٔ DB-backed؛ screenshot crop مستقل و visual viewportهای جدید باز.
