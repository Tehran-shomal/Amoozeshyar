# آخرین وضعیت ثبت‌نام

- مالک/route: Shaghayegh؛ `/portal/registration-status/`; shared `core/live_content.html`; Shaghayegh selector.
- مرجع: PDF صفحهٔ ۵۵؛ در comparison قبلی ثبت شده اما visual review آن ناتمام بود.
- هدف/کنترل: خلاصهٔ پرونده و enrollmentهای فعال، سپس جدول چهارمرحله‌ای مشابه PDF.
- داده/API: GET `/api/portal/pages/registration-status/`; داده از Person/Student/Term/Enrollment واقعی می‌آید؛ شمار درس/واحد از enrollmentهای فعال، بدهی از Student.tuition_debt و سقف از قواعد جاری محاسبه می‌شود.
- نتیجهٔ ممیزی: مدل هیچ گردش/وضعیت تأیید نهایی یا رسید تسویه نگه نمی‌دارد؛ مرحلهٔ تأیید صریحاً «ثبت نشده» است. صفر بودن بدهی به‌عنوان رسید پرداخت تعبیر نمی‌شود؛ secure-payment هم provider ندارد. حداقل واحد PDF در enrollment service تعریف نشده است.
- نوشتن/اعتبارسنجی: mutation ندارد؛ status از DB خوانده می‌شود، client status تازه نمی‌سازد.
- دسترسی/خطا: session؛ پروندهٔ متعلق؛ profile/term نامعتبر و DB unavailable طبق قرارداد مشترک.
- navigation: sidebar ثبت‌نام؛ term-picker در پوسته.
- آزمون/وابستگی: `test_registration_status_summarizes_persisted_stages_without_claiming_final_approval` در `apps/core/test_frontend.py` اضافه شد؛ اجرا نشده.
- وضعیت: قالب اختصاصی read-only بر مبنای دادهٔ پرونده ساخته شد؛ capture احرازشدهٔ جدید نداریم و داده‌های نمونهٔ PDF seed نشده‌اند.
