# تأیید حذف اضطراری (PDF reference state)

- مرجع: PDF صفحات ۹۳–۹۶.
- صفحهٔ مرتبط/مالک: Shaghayegh؛ `/portal/emergency-drop/`; همان modal و JS حذف عادی.
- رفتار موجود: نام/کد/واحد از ردیف Enrollment؛ confirm فقط `POST /api/enrollment/emergency-drop/<id>/` را صدا می‌زند، مستقل از حذف عادی. مودال روشن می‌کند حذف اضطراری بازپرداخت ثبت نمی‌کند.
- اعتبارسنجی/خطا: مالکیت و فقط پنجرهٔ `Term.emergency_drop_start/end` در backend؛ خارج پنجره `emergency_drop_window_closed`; پس از موفقیت همان Enrollment در scope مالک/Term به‌عنوان نتیجه نمایش داده می‌شود.
- آزمون: `apps/core/enrollment/test_services.py`, `apps/core/test_frontend.py`, `static/core/tests/portal_api.test.cjs` و `portal_bindings.test.cjs`; همه **NOT RUN**؛ چهار variation PDF و focus/viewport بصری باید جداگانه بررسی شوند.
- وضعیت: endpoint و result واقعی جداست؛ مقایسهٔ runtime تصویری هنوز به ترتیب صفحهٔ ۱۹ متوقف است.
