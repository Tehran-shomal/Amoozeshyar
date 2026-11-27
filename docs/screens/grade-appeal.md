# اعتراض به نمره

- مالک/route: Omid؛ `/portal/grade-appeal/`; shared `core/live_content.html`; `omid.forms.GradeAppealForm`.
- مرجع: PDF صفحهٔ ۶۰؛ نتیجهٔ ثبت متناظر در PDF صفحهٔ ۴۲ است.
- هدف/کنترل: نمایش اعتراض‌های قبلی و فرم انتخاب درس/ثبت دلیل اعتراض.
- داده/API: GradeAppeal, Enrollment, CourseOffering, Lesson, Constant؛ GET page و POST page API. نتیجهٔ موفق با `request_id` فقط appeal همان Student/Term را می‌خواند.
- اعتبارسنجی/مجوز: فهرست enrollment محدود به همان Student و Term و فقط enrollmentهای دارای Grade با score غیرخالی؛ `appeal_date` و status اولیه `appeal_status/pending` سمت سرور؛ lookup ناموجود خطای فرم. مدل/API فعلی پنجرهٔ مجاز اعتراض را کنترل نمی‌کند و پیوست فایل ندارد؛ هشدار این محدودیت بالای فرم نمایش داده می‌شود.
- دادهٔ نوشته‌شده: owner مستقیماً از فیلد enrollment تعیین نمی‌شود، اما enrollment choice در form محدود است؛ review بعدی endpoint مستقل `requests/grade-appeal/.../review/` دارد.
- خطا/navigation: validation errors در HTML بازگشتی؛ نتیجهٔ عملیات وضعیت واقعی appeal را نشان می‌دهد و اعلام می‌کند درخواست برای رسیدگی ثبت شده، نه اینکه نمره تغییر کرده یا اعتراض پذیرفته شده باشد؛ sidebar ثبت‌نام؛ profile/term/session بر اساس قرارداد مشترک.
- آزمون/وابستگی: `apps/core/test_frontend.py`, `apps/core/requests/test_services.py`; model GradeAppeal و review service.
- وضعیت: صفحهٔ PDF ۶۰ با فرم و مسیر واقعی تطبیق داده شد؛ فرم و پیگیری موجود است، اما پنجرهٔ مجاز اعتراض و پیوست پشتیبانی نمی‌شوند و قاعدهٔ دقیق مهلت در source موجود نیست. مرجع در `page-60-reference.png` است؛ capture جاری احرازشده در دسترس نیست.
