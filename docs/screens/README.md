# پرونده‌های فنی صفحه‌ها

وضعیت تبدیل همهٔ routeهای ثبت‌شده و crosswalk صفحه‌به‌صفحهٔ ۹۶ حالت PDF به کامپوننت React در [گزارش مهاجرت React](../REACT_PORTAL_MIGRATION.md) و [جدول نگاشت PDF](../PDF_PAGE_MAPPING.md) است؛ این نگاشت، جای capture یا تأیید بصری را نمی‌گیرد.

مالکیت فعال هفت‌گانه در [TEAM_OWNERSHIP.md](../TEAM_OWNERSHIP.md) تعریف شده؛ این گروه‌های کد را با دسته‌بندی کاربردی sidebar اشتباه نگیرید. مالکیت تیمی پنج‌گانهٔ قبلی superseded شده؛ دسته‌بندی محصولی منو موضوع جداگانه است.

هر slug ثبت‌شده در `apps/core/frontend/registry.py` یک فایل هم‌نام در همین پوشه دارد؛ علاوه بر ۳۲ slug، login، dashboard، انتخاب نیمسال و navigation مشترک هم مستند شده‌اند. پنج فایل آخر، حالت‌های PDF/مودال/نتیجه‌ای را توضیح می‌دهند که route واقعی مستقل ندارند یا فقط بخشی از آن‌ها پیاده است.

## قرارداد مشترک

- shell مرورگر: `/portal/<slug>/`؛ دادهٔ صفحه: `GET /api/portal/pages/<slug>/` با session. برای dashboard مقدار `<slug>` برابر `home` است.
- queryهای انتخابی `student_code` و `term` در URL می‌مانند؛ فرم ارزشیابی از `enrollment` نیز برای تعیین درس استفاده می‌کند. همهٔ این شناسه‌ها دوباره از رابطهٔ Person جاری resolve/scope می‌شوند.
- formهای پشتیبانی‌شده با POST JSON و CSRF در API صفحه ثبت می‌شوند؛ صفحهٔ بی‌فرم write ندارد. Exception مهم: ثبت/حذف درس endpointهای دامنه‌ای مشخص خودشان را دارند.
- خطاهای عمومی: session لازم (`401` برای API)، صفحه/term نامعتبر (`404`)، پروفایل متعلق به حساب دیگر (`403`)، فرم نامعتبر (`400` همراه HTML خطا)، DB unavailable (`503`). CSRF و method نامعتبر ممکن است خروجی پیش‌فرض Django باشند.
- جدول screen/API و مدل دقیق در [ماتریس](../SCREEN_API_MATRIX.md)؛ payloadها در [قرارداد API](../API_CONTRACTS.md)؛ وضعیت PDF مستقل در [نقشهٔ صفحه‌به‌صفحه](../PDF_PAGE_MAPPING.md).
- آزمون‌های قبلی در [TEST_REPORT.md](../TEST_REPORT.md) تاریخی‌اند؛ پس از بازتخصیص مالکیت این branch هنوز suite اجرا نشده و اجرای آن در فاز بعد برنامه‌ریزی شده است.

## Routeها

`login`, `dashboard`, سپس همهٔ ۳۲ صفحه:

`enrollment`, `selected-courses`, `curriculum`, `add-drop`, `emergency-drop`, `registration-status`, `grade-appeal`, `evaluation`, `evaluation-form`, `messages`, `guest-request`, `graduation`, `academic-activities`, `transcript`, `attendance`, `exam-card`, `requests`, `education-certificate`, `graduation-certificate`, `student-card`, `guide`, `support`, `payments`, `secure-payment`, `financial-aid`, `tuition`, `internship`, `notifications`, `announcements`, `calendar`, `schedule`, `settings`.

## اجزای مشترک و stateهای مرجع

- اجزا: [term-picker.md](term-picker.md)، [navigation.md](navigation.md)، [navigation-groups.md](navigation-groups.md).
- حالت‌های تصویری: [course-selection-dialog.md](course-selection-dialog.md)، [course-group-dialog.md](course-group-dialog.md)، [drop-confirmation.md](drop-confirmation.md)، [emergency-drop-confirmation.md](emergency-drop-confirmation.md)، [operation-results.md](operation-results.md)، [student-services-menu.md](student-services-menu.md)، [faculty-services-menu.md](faculty-services-menu.md).

## شواهد تطبیق ترتیبی PDF

فایل‌های `page-01-reference.png` تا `page-96-reference.png` مرجع PDF هستند؛ `page-NN-current.png` فقط وقتی capture رابط ثبت می‌شود که واقعاً گرفته شده باشد. وضعیت اختلاف و آدرس route/API هر شماره در [PDF_PAGE_MAPPING.md](../PDF_PAGE_MAPPING.md) آمده است. capture جاری احرازشدهٔ صفحهٔ ۱۹ در دسترس نیست؛ توالی تصویری طبق plan از صفحهٔ ۱۹ جلوتر نمی‌رود. صفحات ۲۰–۴۴ جداگانه از نظر PDF reference و سورس/داده/API بررسی شده‌اند، نه به‌عنوان تطبیق runtime تکمیل‌شده. جزئیات: [تقویم](calendar.md)، [اطلاعیه](announcements.md)، [فرم ارزشیابی](evaluation-form.md)، [مرکز اعلان‌ها](notifications.md)، [تنظیمات](settings.md)، [چارت درسی](curriculum.md)، [کارآموزی](internship.md)، [درخواست مهمانی](guest-request.md)، [فراغت از تحصیل](graduation.md)، [ارتباط با اساتید](messages.md)، [راهنمای سامانه](guide.md)، [مرکز پشتیبانی](support.md)، [نتیجه‌ها و منع عملیات](operation-results.md)، [فهرست ارزشیابی](evaluation.md).
