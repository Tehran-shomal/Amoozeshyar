# فهرست انتخاب درس در مودال (PDF reference state)

- مرجع: PDF صفحات ۷۹ و ۸۴؛ این‌ها state تصویری‌اند، نه route مستقل.
- صفحهٔ مرتبط/مالک: Shaghayegh؛ `/portal/selected-courses/` و `selected-courses.md`.
- رفتار جاری: دکمهٔ انتخاب در `/portal/selected-courses/` مودال قابل‌بستن باز می‌کند؛ فهرست از `GET /api/scheduling/offerings/?term=...` می‌آید و بر اساس `lesson_code/title` گروه‌بندی می‌شود. صفحات ۷۹ و ۸۴ دو state فهرست‌اند، نه endpoint جدا.
- وضعیت داده: کارت‌ها فقط درس‌های فعال واقعی را نشان می‌دهند؛ `CourseOffering`های همان درس گروه‌های قابل انتخاب می‌شوند. عنوان/کد/واحدها از API است. مبلغ شهریه و شمارهٔ رسمی گروه در schema/API نیستند و نمایش داده نمی‌شوند.
- تعامل/دسترسی: بستن با ×، کلیک پس‌زمینه یا Escape؛ focus به دکمهٔ بازکننده برمی‌گردد. حالت loading/empty/error متن دارد.
- ثبت: انتخاب گروه هنوز mutation نیست؛ دکمهٔ افزودن، `POST /api/enrollment/register/<offering_id>/` را با ID واقعی می‌زند و redirect موفق در صفحهٔ حذف‌واضافه نتیجهٔ enrollment مجاز را نشان می‌دهد.
- آزمون: assertions قالب در `apps/core/test_frontend.py` و binding/API event در `static/core/tests/portal_bindings.test.cjs` نوشته شده‌اند، اما اجرا نشده‌اند. Browser/focus verification نداریم.
- وضعیت: state API-driven پیاده شده؛ تطبیق runtime با capture جاری هنوز به‌علت توقف ترتیب visual روی صفحهٔ ۱۹ انجام نشده است.
