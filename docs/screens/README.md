# پرونده‌های فنی صفحه‌ها

هر slug ثبت‌شده در `apps/core/frontend/registry.py` یک فایل هم‌نام در همین پوشه دارد؛ علاوه بر ۳۲ slug، login، dashboard، انتخاب نیمسال و navigation مشترک هم مستند شده‌اند. پنج فایل آخر، حالت‌های PDF/مودال/نتیجه‌ای را توضیح می‌دهند که route واقعی مستقل ندارند یا فقط بخشی از آن‌ها پیاده است.

## قرارداد مشترک

- shell مرورگر: `/portal/<slug>/`؛ دادهٔ صفحه: `GET /api/portal/pages/<slug>/` با session. برای dashboard مقدار `<slug>` برابر `home` است.
- queryهای انتخابی `student_code` و `term` در URL می‌مانند. دسترسی به پرونده فقط از رابطهٔ Person جاری resolve می‌شود.
- formهای پشتیبانی‌شده با POST JSON و CSRF در API صفحه ثبت می‌شوند؛ صفحهٔ بی‌فرم write ندارد. Exception مهم: ثبت/حذف درس endpointهای دامنه‌ای مشخص خودشان را دارند.
- خطاهای عمومی: session لازم (`401` برای API)، صفحه/term نامعتبر (`404`)، پروفایل متعلق به حساب دیگر (`403`)، فرم نامعتبر (`400` همراه HTML خطا)، DB unavailable (`503`). CSRF و method نامعتبر ممکن است خروجی پیش‌فرض Django باشند.
- جدول screen/API و مدل دقیق در [ماتریس](../SCREEN_API_MATRIX.md)؛ payloadها در [قرارداد API](../API_CONTRACTS.md)؛ وضعیت PDF مستقل در [نقشهٔ صفحه‌به‌صفحه](../PDF_PAGE_MAPPING.md).
- آزمون smoke مشترک: `apps/core/test_frontend.py`. فقط مواردی که suite دامنه‌ای در فایل ذکر می‌کند، آزمون اختصاصی دارند؛ baseline را در [TEST_REPORT.md](../TEST_REPORT.md) ببینید.

## Routeها

`login`, `dashboard`, سپس همهٔ ۳۲ صفحه:

`enrollment`, `selected-courses`, `curriculum`, `add-drop`, `emergency-drop`, `registration-status`, `grade-appeal`, `evaluation`, `evaluation-form`, `messages`, `guest-request`, `graduation`, `academic-activities`, `transcript`, `attendance`, `exam-card`, `requests`, `education-certificate`, `graduation-certificate`, `student-card`, `guide`, `support`, `payments`, `secure-payment`, `financial-aid`, `tuition`, `internship`, `notifications`, `announcements`, `calendar`, `schedule`, `settings`.

## اجزای مشترک و stateهای مرجع

- اجزا: [term-picker.md](term-picker.md)، [navigation.md](navigation.md).
- حالت‌های تصویری: [course-selection-dialog.md](course-selection-dialog.md)، [course-group-dialog.md](course-group-dialog.md)، [drop-confirmation.md](drop-confirmation.md)، [emergency-drop-confirmation.md](emergency-drop-confirmation.md)، [operation-results.md](operation-results.md).
