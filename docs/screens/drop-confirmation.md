# تأیید حذف عادی (PDF reference state)

- مرجع: PDF صفحات ۸۹–۹۲.
- صفحهٔ مرتبط/مالک: Shaghayegh؛ `/portal/add-drop/`; template `course_changes.html` و `static/shaghayegh/section.js`.
- رفتار موجود: مودال در همان صفحه، نام/کد/واحد را از ردیف واقعی می‌گیرد؛ بستن، backdrop و Escape؛ confirm endpoint حذف عادی را صدا می‌زند. متن مودال می‌گوید این API مبلغ بازپرداخت را محاسبه/ثبت نمی‌کند.
- API/data: `POST /api/enrollment/drop/<enrollment_id>/`; enrollment id و profile در backend مالکیت‌سنجی می‌شوند.
- اعتبارسنجی/خطا: مالکیت و بازهٔ add/drop؛ خطا در همان dialog نمایش داده و دکمه دوباره فعال می‌شود؛ پس از موفقیت همان Enrollment با `dropped_enrollment_id` و scope مالک/ترم بازخوانی می‌شود.
- آزمون: `apps/core/enrollment/test_services.py`, `apps/core/test_frontend.py`, `static/core/tests/portal_bindings.test.cjs`; همه **NOT RUN**؛ pixel layout چهار مرجع assert نشده.
- وضعیت: interaction و result واقعی موجود؛ چهار variation PDF و capture جاری هنوز به‌صورت تصویری تأیید نشده‌اند.
