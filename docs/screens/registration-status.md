# آخرین وضعیت ثبت‌نام

- مالک/route: Shaghayegh؛ `/portal/registration-status/`; shared `core/live_content.html`; Shaghayegh selector.
- مرجع: PDF صفحهٔ ۵۵؛ در comparison قبلی ثبت شده اما visual review آن ناتمام بود.
- هدف/کنترل: نمایش جدول enrollmentهای پرونده در term انتخابی و statusهای ذخیره‌شده.
- داده/API: Enrollment, CourseOffering, Lesson, Term, Constant؛ GET API صفحه.
- نوشتن/اعتبارسنجی: mutation ندارد؛ status از DB خوانده می‌شود، client status تازه نمی‌سازد.
- دسترسی/خطا: session؛ پروندهٔ متعلق؛ profile/term نامعتبر و DB unavailable طبق قرارداد مشترک.
- navigation: sidebar ثبت‌نام؛ term-picker در پوسته.
- آزمون/وابستگی: `apps/core/test_frontend.py`; selector مشترک enrollment rows و `display`.
- وضعیت: read-only render؛ screenshot/مقایسهٔ branch فعلی و تست statusهای مختلف باز است.
