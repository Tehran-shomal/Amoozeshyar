# تنظیمات زبان و اعلان‌ها

- مالک/route: Mobina؛ `/portal/settings/`; قالب اختصاصی `mobina/settings.html` و فرم `mobina.forms.SettingsForm`.
- مرجع: [PDF صفحهٔ ۱۹](page-19-reference.png)، نتیجهٔ ذخیره در صفحهٔ ۴۱، [صفحهٔ ۵۰](page-50-reference.png) برای کانال اعلان و [صفحهٔ ۵۱](page-51-reference.png) برای زبان.
- هدف/کنترل: انتخاب زبان از lookupهای `language` موجود، ایمیل، نشانی پستی، و ترجیح کلی اعلان حساب.
- داده/API: `Person`, `Constant`; GET/POST `/api/portal/pages/settings/`. فرم همیشه به `request.user` متصل است و `person_id` ارسالی از مرورگر را نمی‌پذیرد.
- اعتبارسنجی/مجوز: فقط `email,address,is_notification_enabled,preferred_language`; انتخاب زبان از Constantهای دستهٔ `language`؛ session و CSRF لازم.
- تطبیق/شکاف: انتخاب فارسی/English از گزینه‌های واقعی `Constant(language)` می‌آید و فقط در Person جاری ذخیره می‌شود؛ regression وجود هر دو گزینه و ذخیرهٔ فارسی را پوشش می‌دهد. صفحهٔ ۵۰ مرجع، روشن/خاموش مستقل پیامک و رایانامه را نشان می‌دهد؛ مدل فقط یک Boolean کلی اعلان دارد، سرویس آن را اعمال نمی‌کند، شمارهٔ موبایل و provider ارسال SMS/email هم نیست. برای کانال‌های جداگانه کنترل ذخیره‌شونده یا ارسال موفق جعل نمی‌شود و محدودیت در خود صفحه اعلام شده است.
- خطا: خطای فرم با HTTP 400 و پاسخ JSON شامل `error` و قطعهٔ HTML فرم؛ DB unavailable با 503؛ پس از ذخیره redirect به `/portal/settings/?settings_saved=1` و حفظ query صفحه. صفحهٔ نتیجه مقادیر ذخیره‌شده از Person جاری را نشان می‌دهد.
- navigation: گروه «خدمات دانشجویی»؛ لینک واقعی به مرکز اعلان‌ها؛ تنظیمات در footer تکرار نمی‌شود.
- آزمون/وابستگی: `test_settings_page_renders_only_profile_backed_preferences` و `test_settings_post_updates_only_the_logged_in_person` در `apps/core/test_frontend.py` نوشته شده‌اند اما به درخواست کاربر اجرا نشده‌اند؛ تست دوم نتیجهٔ ذخیرهٔ صفحهٔ ۴۱ را هم بررسی می‌کند.
- وضعیت: پیاده‌سازی source و reference ثبت شد؛ GET ناشناس `401` است. capture جاری احرازشده در دسترس نیست، پس تطبیق runtime و viewportها هنوز تأیید نشده‌اند.
