# ارائهٔ گروه امید — سوابق آموزشی و خدمات دانشجویی

### 1. معرفی بخش

نمایش سوابق و وضعیت آموزشی دانشجو و چند سرویس درخواست/پشتیبانی که در schema موجود قابل ثبت‌اند.

### 2. مسئولیت عضو

پیوست گروه امید را برای سوابق، نمره‌ها، چارت و اعتراض نمره تعیین می‌کند. در manifest واقعی Omid مالک ده route از جمله `academic-activities`, `transcript`, `attendance`, `exam-card`, `requests`, مدارک، کارت، راهنما و پشتیبانی است. `curriculum` در کد Mobina و `grade-appeal` در Shaghayegh است؛ این اختلاف در این سند مطابق واقع گزارش شده است.

### 3. صفحات پیاده‌سازی‌شده

| صفحه | PDF | URL | وضعیت |
|---|---:|---|---|
| حضور و غیاب | 14 | `/portal/attendance/` | نمایش رکوردها؛ endpoint ورود حضور کارمند ندارد |
| کارت امتحان | 21 | `/portal/exam-card/` | قالب/چاپ؛ شمارهٔ صندلی و صدور رسمی غایب |
| راهنمای سامانه | 28 | `/portal/guide/` | shell هست؛ محتوای Q&A در selector نیست |
| پشتیبانی | 29 | `/portal/support/` | ثبت Ticket؛ lifecycle کامل نیست |
| چارت درسی | 23 | `/portal/curriculum/` | route واقعی اما مالک کدی Mobina |
| اعتراض نمره | 60 | `/portal/grade-appeal/` | route واقعی اما مالک کدی Shaghayegh |
| فعالیت آموزشی | 61 | `/portal/academic-activities/` | selector/template اختصاصی |
| کارنامه | 62 | `/portal/transcript/` | دادهٔ Grade/Enrollment موجود |
| کارت دانشجویی | 20 | `/portal/student-card/` | کارت دیجیتال/چاپ؛ صدور رسمی ادعا نمی‌شود |
| درخواست/گواهی | 67, 72–73 | `/portal/requests/`, `/portal/education-certificate/`, `/portal/graduation-certificate/` | ثبت درخواست موجود؛ فایل رسمی صادر نمی‌شود |

### 4. طراحی و عملکرد

صفحه‌های خواندنی از Enrollment، Grade، Attendance و Term انتخابی ساخته می‌شوند. فرم درخواست، owner و وضعیت را سرور تعیین می‌کند. Ticket از دسته‌های فعال استفاده می‌کند و ایجادکننده از session می‌آید. صفحهٔ راهنما و صدور رسمی گواهی/کارت ناقص‌اند و به‌عنوان complete معرفی نمی‌شوند.

### 5. APIهای مرتبط

صفحه‌ها از `GET /api/portal/pages/<slug>/` استفاده می‌کنند. درخواست‌های موجود از `POST /api/portal/pages/requests/`، `education-certificate/` یا `support/` با CSRF استفاده می‌کنند. نمونهٔ عمومی response موفق GET: `{"page":"transcript","profile":{"student_code":"…"},"term":{"term_code":"…"},"html":"…"}`؛ POST موفق پس از redirect داخلی، `{ "redirect": "/portal/<slug>/?…" }` برمی‌گرداند؛ فرم نامعتبر 400 با `validation_error` و HTML خطا می‌دهد.

### 6. سناریوی عملکرد

session → resolve پروفایل متعلق → selector صفحه → ORM read → render. برای فرم: JSON scalarها → Django Form → تعیین owner/status از سمت سرور → save → پاسخ redirect → refresh. ثبت درخواست از نظر داده با صدور فایل رسمی یا تأیید نهایی یکی نیست.

### 7. ارتباط با سایر بخش‌ها

به هستهٔ مدل‌های Person/Student/Term/Enrollment/Grade و API عمومی صفحه وابسته است. کارت امتحان به CourseOffering و Exam نیاز دارد؛ اعتراض نمره workflow reviewer جدا دارد؛ Ticket به دسته و lifecycle پشتیبانی نیاز دارد.

### 8. ساختار فنی

- `apps/core/frontend/academic_services/pages.py`, `selectors.py`, `forms.py`
- `apps/core/frontend/academic_services/templates/academic_services/academic_activities.html`, `transcript.html`, `exam_card.html`, `student_card.html`
- `apps/core/templates/core/live_content.html`
- `apps/core/models.py`: Student، Enrollment، Grade، Attendance، Ticket، StudentServiceRequest و Constant.

### 9. تست‌ها

`apps/core/test_frontend.py` همهٔ page slugها را render/API-read می‌کند، مالکیت را می‌سنجد و write مربوط به درخواست را به دانشجوی session نسبت می‌دهد. آخرین اجرای کامل ثبت‌شده ۱۰۱ Python و ۱۴ Node پاس؛ ۲۰ هشدار datetime از fixtureها باقی است. جزئیات و محدودیت‌ها در [TEST_REPORT.md](../TEST_REPORT.md).

### 10. راهنمای ارائه به استاد

1. `academic-activities` و `transcript` را باز کنید و منبع دادهٔ selector را توضیح دهید.
2. صفحهٔ Attendance را نشان دهید و روشن کنید route فعلی فقط خواندن است.
3. Ticket آزمایشی را فقط در دیتابیس test ثبت کنید؛ owner را از payload کاربر نپذیرید.
4. کارت/مدرک را با caveat رسمی نشان دهید؛ شماره یا سند صادرشده را جعل نکنید.
5. اختلاف page ownership مربوط به curriculum و grade appeal را توضیح دهید.
