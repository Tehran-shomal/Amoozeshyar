# اعتراض به نمره

- مالک/route: Shaghayegh؛ `/portal/grade-appeal/`; shared `core/live_content.html`; `GradeAppealForm`.
- مرجع: PDF صفحهٔ ۶۰؛ صفحه در مقایسه «ثبت‌شده، بازبینی‌نشده» است.
- هدف/کنترل: نمایش اعتراض‌های قبلی و فرم انتخاب درس/ثبت دلیل اعتراض.
- داده/API: GradeAppeal, Enrollment, CourseOffering, Lesson, Constant؛ GET page و POST page API.
- اعتبارسنجی/مجوز: فهرست enrollment محدود به همان Student و Term؛ `appeal_date` و status اولیه `appeal_status/pending` سمت سرور؛ lookup ناموجود خطای فرم.
- دادهٔ نوشته‌شده: owner مستقیماً از فیلد enrollment تعیین نمی‌شود، اما enrollment choice در form محدود است؛ review بعدی endpoint مستقل `requests/grade-appeal/.../review/` دارد.
- خطا/navigation: validation errors در HTML بازگشتی؛ sidebar ثبت‌نام؛ profile/term/session بر اساس قرارداد مشترک.
- آزمون/وابستگی: `apps/core/test_frontend.py`, `apps/core/requests/test_services.py`; model GradeAppeal و review service.
- وضعیت: فرم و پیگیری موجود؛ شرط‌های محصولی اعتراض (مهلت/فایل/ویرایش) ناشناخته؛ visual تازه باز.
