# ارائهٔ گروه میری — هماهنگی ارتباط و خدمات عمومی

### 1. معرفی بخش

نقش مشترک و cross-cutting برای هماهنگی ارتباط استاد و دانشجو، اعلان‌ها، راهنما، پشتیبانی و یکپارچگی API.

### 2. مسئولیت عضو

پیوست میری را Shared Lead معرفی می‌کند: بررسی هماهنگی جریان‌ها، اتصال frontend/backend، مستندات API و آمادگی ارائه. در repository هیچ manifest یا route مستقلی با مالک `Miri` وجود ندارد؛ سند حاضر مالکیت کدی را به او نسبت نمی‌دهد.

### 3. صفحات مرتبط در PDF

| موضوع | PDF | URL واقعی | مالک ثبت‌شده در کد |
|---|---:|---|---|
| اطلاعیه/اعلان | 16, 18 | `/portal/announcements/`, `/portal/notifications/` | Neyousha/Pouya |
| ارزشیابی | 17, 31–37 | `/portal/evaluation-form/`, `/portal/evaluation/` | Shahsavand در `academic_services` |
| ارتباط با استاد | 27 | `/portal/messages/` | Shahsavand |
| راهنمای سامانه | 28 | `/portal/guide/` | Omid؛ محتوای Q&A هنوز gap است |
| پشتیبانی | 29 | `/portal/support/` | Omid؛ Ticket lifecycle کامل نیست |

### 4. طراحی و عملکرد

تمام صفحات از shell/session مشترک استفاده می‌کنند. اعلان متعلق به Person فقط read/mark-read دارد؛ ارزشیابی رکورد survey می‌سازد؛ پیام، فرم داخلی Communication است؛ ticket فرم ثبت ابتدایی دارد. هیچ‌کدام به‌تنهایی اثبات‌کنندهٔ notification provider، پاسخ تیکت، Q&A کامل یا ارسال ایمیل بیرونی نیستند.

### 5. APIهای مرتبط

- `GET /api/portal/pages/announcements/` و `notifications/`
- `POST /api/portal/pages/notifications/` برای mark-read مالکانه
- `GET|POST /api/portal/pages/evaluation/`, `evaluation-form/`, `messages/`, `support/`
- `GET /api/accounts/me/` برای session جاری

نمونهٔ response مشترک GET: `{"page":"support","profile":{"student_code":"…"},"term":{"term_code":"…"},"html":"…"}`؛ writeهای page API پس از CSRF پاسخ redirect داخلی می‌دهند؛ فرم نامعتبر 400 و پروفایل غیرمجاز 403 است. endpoint مختص Miri وجود ندارد.

### 6. سناریوی عملکرد

هویت session → registry مالک route را انتخاب می‌کند → selector صفحه دادهٔ scoped می‌خواند → form validation و save در مدل واقعی → پاسخ و refresh. برای مرور بین صفحات، term/profile query حفظ می‌شود و owner/model در registry یا form class باقی می‌ماند؛ یک معماری جداگانه برای Shared Lead ساخته نشده است.

### 7. ارتباط با سایر بخش‌ها

Shared Lead نیازمند هماهنگی با Omid، شاهسوند و Neyousha/Pouya است. API عمومی page برای UI مشترک است، اما جای endpointهای دامنه‌ای کارکنان را نمی‌گیرد. مسئلهٔ assignment مهم برای تصمیم تیم: prompt هفت‌نفره Miri را جدا می‌کند ولی کد فعلی ownership را بین سه گروه تقسیم کرده است.

### 8. ساختار فنی

- `apps/core/frontend/registry.py` و گروه‌های `academic_services`, `neyousha_pouya`
- `apps/core/frontend/api.py`, `apps/core/frontend/forms.py` در ماژول‌های مالک
- `static/core/portal_api.js`, `static/core/live_portal.js`
- مدل‌های `Notification`, `Communication`, `TeacherSurvey`, `Ticket` در `apps/core/models.py`.

### 9. تست‌ها

`apps/core/test_frontend.py`, `apps/core/requests/test_services.py` و تست‌های client در `static/core/tests/` شواهد اصلی‌اند. آخرین اجرای کامل: ۱۰۱ Python و ۱۴ Node، پاس؛ وضعیت pageهای ناقص و browser smoke در [TEST_REPORT.md](../TEST_REPORT.md) درج شده است.

### 10. راهنمای ارائه به استاد

1. صفحه‌های اعلان، پیام و پشتیبانی را باز و مالک واقعی هرکدام را از matrix نشان دهید.
2. flow یک POST داخلی را تا model ذخیره‌شده دنبال کنید.
3. تفاوت ثبت داخلی با ارسال بیرونی یا lifecycle کامل را توضیح دهید.
4. guide را نشان دهید و اعلام کنید محتوای Q&A هنوز پیاده نشده.
5. نقش Miri را به‌عنوان هماهنگی/بازبینی ارائه دهید، نه مالک feature یا endpoint مستقل.
