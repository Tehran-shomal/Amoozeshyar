# تأیید حذف عادی (PDF reference state)

- مرجع: PDF صفحات ۸۹–۹۲.
- صفحهٔ مرتبط/مالک: Shaghayegh؛ `/portal/add-drop/`; template `course_changes.html` و `static/shaghayegh/section.js`.
- رفتار موجود: مودال در همان صفحه، نام/کد/واحد را از ردیف واقعی می‌گیرد؛ بستن، backdrop و Escape؛ confirm endpoint حذف را صدا می‌زند.
- API/data: `POST /api/enrollment/drop/<enrollment_id>/`; enrollment id و profile در backend مالکیت‌سنجی می‌شوند.
- اعتبارسنجی/خطا: بازهٔ drop و status؛ خطا در همان dialog نمایش داده و دکمه دوباره فعال می‌شود؛ موفقیت صفحه را reload می‌کند.
- آزمون: `apps/core/enrollment/test_services.py`, `static/core/tests/portal_bindings.test.cjs`; pixel layout of all four PDFs not asserted.
- وضعیت: interaction واقعی موجود؛ چهار variation PDF و viewport تازه هنوز به‌صورت تصویری تأیید نشده‌اند.
