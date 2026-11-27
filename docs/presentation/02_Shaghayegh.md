# ارائهٔ ۰۲ — شقایق: ثبت‌نام و تغییر دروس

### 1. معرفی بخش

مسیر انتخاب واحد و تغییر برنامهٔ درسی. مالکیت شامل مرحلهٔ اطلاعات، جدول انتخاب گروه، حذف و اضافه، حذف اضطراری و مشاهدهٔ وضعیت ثبت‌نام است.

### 2. مسئولیت عضو

ظرفیت، تداخل و تأییدهای عملیات در مسئولیت این بخش‌اند. بازه‌های PDF در پرامپت: ۹–۱۳، ۵۲–۵۹ و ۶۸–۹۶؛ PDF در workspace حاضر نیست و mapping تصویری تأیید نشده است.

### 3. صفحه‌ها و URLها

| صفحه/حالت | URL | API | وضعیت |
|---|---|---|---|
| انتخاب واحد | `/portal/enrollment/` | GET API صفحه | اطلاعات واقعی دانشجو/ترم |
| دروس انتخاب‌شده | `/portal/selected-courses/` | GET صفحه، GET offerings، POST register | شناسهٔ واقعی offering به service می‌رود |
| حذف و اضافه | `/portal/add-drop/` | GET صفحه، POST drop | افزودن از مرحلهٔ انتخاب واحد؛ حذف با dialog |
| حذف اضطراری | `/portal/emergency-drop/` | GET صفحه، POST drop | backend بازه و مالکیت را بررسی می‌کند |
| وضعیت ثبت‌نام | `/portal/registration-status/` | GET API صفحه | خواندن وضعیت‌های ثبت‌شده |
| dialogs | داخل route والد | همان API دامنه | تأیید انتخاب گروه/حذف، نه URL مستقل |

### 4. جریان رابط کاربر

داشبورد → `enrollment` → `selected-courses` → بارگیری offeringها → انتخاب offering یکتا → ثبت → refresh. برای حذف، جدول ثبت‌نام → dialog → تأیید → درخواست حذف → refresh. دکمه‌ها تا دریافت پاسخ غیرفعال می‌شوند.

### 5. API و قرارداد

- `GET /api/scheduling/offerings/?term=<term_code>` فهرست و ظرفیت باقیمانده را می‌دهد.
- `POST /api/enrollment/register/<offering_id>/` ثبت را انجام می‌دهد.
- `POST /api/enrollment/drop/<enrollment_id>/` حذف را انجام می‌دهد.
- صفحه‌ها از `GET /api/portal/pages/<slug>/` خوانده می‌شوند. تغییرات فرم‌محور، اگر در صفحه تعریف شده باشند، با POST همین path هستند.

نمونهٔ قراردادی ثبت (شناسه‌ها نمایشی‌اند):

```http
POST /api/enrollment/register/27/
Content-Type: application/json
X-CSRFToken: <csrf-token>

{"student_code":"S10001"}
```

پاسخ موفق شامل `{"enrollment":{"id":31,"student_code":"S10001","offering_id":27,"lesson_code":"C-101","lesson_title":"عنوان درس","status":"active","enrollment_date":"2026-01-01","drop_date":null}}` است؛ HTTP 201 برای ایجاد و 200 برای نتیجهٔ موجود/idempotent. خطاهای ظرفیت، بازه، پیش‌نیاز و تداخل با کد JSON در API برمی‌گردند.

### 6. اعتبارسنجی و مجوز

backend مالکیت Student، وضعیت فعال، ظرفیت، بازه، پیش‌نیاز و تداخل را کنترل می‌کند. شناسهٔ معتبر دیتابیسی لازم است؛ نام درس برای mutation استفاده نمی‌شود. قواعدی که منبع رفتاری رسمی ندارند در `BUSINESS_RULES.md` نامعلوم می‌مانند.

### 7. فایل‌های فنی

- `apps/core/frontend/shaghayegh/{pages.py,selectors.py,forms.py}`
- `templates/shaghayegh/{enrollment.html,selected_courses.html,course_changes.html}`
- `static/shaghayegh/section.js`
- Backend: `apps/core/enrollment/`, `apps/core/scheduling/`; API client: `static/core/portal_api.js`
- [Screens](../screens/enrollment.md), [selected courses](../screens/selected-courses.md), [add/drop](../screens/add-drop.md), [dialog](../screens/drop-confirmation.md)

### 8. وابستگی بین بخش‌ها

Term از shell مشترک می‌آید؛ offeringها به scheduling و تغییر وضعیت به enrollment service وابسته‌اند. Omid برای grade appeal از همان Enrollmentهای پرونده در صفحه‌ای جدا استفاده می‌کند.

### 9. تست و QA

اجرای تست‌ها طبق درخواست کاربر به فاز بعد موکول است. آزمون‌های دامنه‌ای بعداً باید capacity/window/conflict/ownership و ثبت مجدد را پوشش دهند. از دادهٔ دیتابیس اصلی برای نمایش آزمایشی تغییر وضعیت استفاده نشود.

### 10. سناریوی ارائه

۱) دو مرحلهٔ انتخاب را باز کنید. ۲) درخواست offerings را در Network نشان دهید. ۳) شناسهٔ offering را از JS تا API دنبال کنید. ۴) dialog حذف را باز و بدون تأیید ببندید؛ سپس در محیط تست تأیید کنید. ۵) پاسخ service و refresh صفحه را نشان دهید.

ماتریس routeها: [TEAM_OWNERSHIP](../TEAM_OWNERSHIP.md)؛ قراردادها: [API_CONTRACTS](../API_CONTRACTS.md).
