# ارائهٔ یکپارچهٔ تیم آموزشیار

## معرفی سامانه

این checkout یک پورتال دانشجویی Django برای ورود، داشبورد، مشاهدهٔ داده‌های آموزشی و ثبت چند فرم واقعی است. PDF مرجع ۹۶ صفحه دارد. route یا تصویر مشابه به‌تنهایی به معنی workflow کامل یا تأیید قواعد دانشگاه نیست.

## معماری و جریان داده

```text
مرورگر RTL
   │ same-origin session + CSRF
   ├── GET /, /portal/<slug>/ ──> shell + page API ──> owner selector ──> ORM
   └── POST page/API ──> Django Form/service ──> permission + validation
                                             └── transaction/DB ──> response + refresh
```

مدل‌ها در `apps/core/models.py` و adminها در `apps/core/admin.py` متمرکزند؛ پنج گروه frontend در registry صفحه‌ها را مالک می‌شوند. endpoint عمومی `GET|POST /api/portal/pages/<slug>/` پاسخ HTML/فرم صفحه است، نه جایگزین API دامنه‌ای یا نقش‌های staff.

## تقسیم مسئولیت

| ارائه | مسئولیت پیوست | مالکیت واقعی در repository |
|---|---|---|
| مبینا | ورود، dashboard و shell | login/dashboard/enrollment/selected-courses/curriculum؛ shell و term picker مشترک |
| شقایق | ثبت‌نام و تغییر دروس | add-drop/emergency-drop/registration-status/grade-appeal؛ دو صفحهٔ انتخاب واحد در Mobina |
| پارسا | امور مالی | payments/secure-payment/financial-aid/tuition |
| امید | سوابق و خدمات آموزشی | activity/transcript/attendance/exam-card/requests/certificates/student-card/guide/support؛ curriculum و grade appeal مالک دیگری دارند |
| نیوشا | زمان‌بندی و Frontend Lead | calendar/schedule/settings/notifications/internship/announcements در گروه مشترک Neyousha/Pouya؛ attendance/exam-card متعلق به Omid |
| شاهسوند | درخواست‌های دانشجویی | evaluation/messages/guest-request/graduation در academic_services؛ چند درخواست پیوست در گروه‌های دیگر است |
| میری | Shared Lead | مالک مستقل در manifest ندارد؛ صفحه‌ها بین Omid، شاهسوند و Neyousha/Pouya تقسیم‌اند |

این جدول اختلاف دو مرجع را آشکار نگه می‌دارد: تقسیم جدید پیوست برای ارائه و مالکیت واقعی registry برای کد. فایل‌های فردی در همین پوشه جزئیات route، PDF، API و caveat هر عضو را دارند.

## سناریوی ارائهٔ تیمی

1. ورود session-based و مشاهدهٔ داشبورد دانشجوی واردشده.
2. تغییر نیمسال در dialog و مشاهدهٔ query به‌روزشده.
3. ورود از انتخاب واحد به دروس انتخاب‌شده، مشاهدهٔ offering واقعی و اشاره به شناسهٔ دیتابیسی.
4. نمایش حذف با modal تأیید و کد server-side مالکیت/بازه.
5. بازکردن کارنامه و فعالیت آموزشی، سپس پرداخت‌ها و تسهیلات.
6. نمایش یک فرم درخواست و توضیح اینکه owner/status از server تعیین می‌شود.
7. خروج و نمایش بازگشت به login.

در browser seed فعلی، term فعال بیرون از registration window و term دیگر فاقد offering است؛ پس ثبت واقعی در demo بدون آماده‌سازی test DB با term/offer معتبر اجرا نمی‌شود. suite Python قواعد register/drop و persistence را با دادهٔ test کنترل‌شده بررسی می‌کند. دادهٔ واقعی یا seed اصلی دست‌کاری نشود.

## وضعیت فنی و شواهد

- اجرای نهایی: ۱۰۱ تست Python، ۱۴ تست Node؛ همه پاس.
- `manage.py check`: پاک؛ `makemigrations --check --dry-run`: بدون تغییر.
- ۲۰ هشدار `RuntimeWarning` datetime naive در fixture/seed هنوز باقی است.
- browser smoke شامل login/logout، dashboard، انتخاب نیمسال، route دروس، API ارائه و رد دسترسی به پروندهٔ دیگر است.
- هفت viewport هدف بررسی شدند؛ document-level horizontal overflow دیده نشد. در 768px قاب دوتایی search رفع شد؛ جزئیات در [TEST_REPORT.md](../TEST_REPORT.md).

## محدودیت‌هایی که باید در دفاع گفته شوند

درگاه پرداخت، صدور رسمی کارت/گواهی، APIهای مستقل ۱۴ namespace، ثبت حضور کارمند، تقویم رویداد مستقل، guide Q&A، lifecycle کامل Ticket/درخواست، result screenهای PDF و منبع رفتار رسمی (`نیازمندی_های_آموزشیار.md`) موجود نیستند. این موارد mock یا completed معرفی نشده‌اند.
