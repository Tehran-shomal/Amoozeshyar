# ارائهٔ گروه شقایق — تغییر دروس

### 1. معرفی بخش

صفحه‌های حذف‌واضافه، حذف اضطراری، وضعیت ثبت‌نام و اعتراض نمره. هدف، حفظ ارتباط کنترل‌های مرورگر با سرویس‌های ثبت‌نام و دادهٔ متعلق به دانشجو است.

### 2. مسئولیت عضو

پیوست صفحات ۹–۱۳، ۵۲–۵۹ و ۶۸–۹۶ را در دامنهٔ گروه قرار می‌دهد. در manifest واقعی، `selected-courses` و `enrollment` متعلق به Mobina هستند؛ Shaghayegh مالک `add-drop`, `emergency-drop`, `registration-status`, و `grade-appeal` است. modalهای تأیید حذف در صفحات مالکانهٔ Shaghayegh قرار دارند؛ نتیجه‌های مستقل PDF کامل نیستند.

### 3. صفحات پیاده‌سازی‌شده

| صفحه/حالت | PDF | URL | وضعیت |
|---|---:|---|---|
| دروس انتخاب‌شده/گروه‌ها | 9–13 | `/portal/selected-courses/` | route واقعی، مالک Mobina؛ چند state تصویری مستقل موجود نیست |
| شروع انتخاب واحد | 52 | `/portal/enrollment/` | route واقعی، مالک Mobina |
| حذف و اضافه | 53 | `/portal/add-drop/` | route و حذف واقعی؛ افزودن از مسیر انتخاب واحد |
| حذف اضطراری | 54 | `/portal/emergency-drop/` | route واقعی، پنجرهٔ قواعد در service |
| وضعیت ثبت‌نام | 55 | `/portal/registration-status/` | نمایش DB-backed |
| اعتراض نمره | 60 | `/portal/grade-appeal/` | فرم موجود؛ مهلت رسمی در منبع رفتاری نیست |
| modalهای حذف | 89–96 | داخل add-drop/emergency-drop | تأیید پیش از POST؛ result page مستقل وجود ندارد |

صفحات 56–59 و 68–88 و 75–78 در mapping به‌عنوان state/modal یا دادهٔ PDF که route مستقل ندارد ثبت شده‌اند؛ به‌جای دادهٔ ساختگی همان وضعیت صریحاً gap می‌ماند.

### 4. طراحی و عملکرد

جدول ثبت‌نام وضعیت فعلی را از صفحه API می‌خواند. حذف از modal تأیید به `enrollment_id` دیتابیسی وصل است؛ service مالکیت پرونده، بازهٔ مجاز و وضعیت را بررسی می‌کند. انتخاب درس در صفحهٔ والد انجام می‌شود. ثبت تکراری و درس دارای تداخل/ظرفیت/پیش‌نیاز نامعتبر باید از پاسخ service منعکس شود.

### 5. APIهای مرتبط

| مسیر | روش | داده و نتیجه |
|---|---|---|
| `/api/portal/pages/add-drop/` | GET | جدول و context صفحه |
| `/api/scheduling/offerings/?term=<code>` | GET | فهرست ارائه‌ها/ظرفیت |
| `/api/enrollment/drop/<enrollment_id>/` | POST | body اختیاری `{student_code}`؛ پاسخ enrollment تازه‌وضعیت‌یافته |
| `/api/enrollment/register/<offering_id>/` | POST | endpoint ثبت که از صفحهٔ مالک Mobina فراخوانی می‌شود |
| `/api/portal/pages/grade-appeal/` | GET/POST | POST دادهٔ فرم؛ خطای اعتبارسنجی 400، دسترسی نامعتبر 403 |

نمونهٔ قراردادی حذف: `POST /api/enrollment/drop/<enrollment_id>/`، JSON اختیاری `{ "student_code": "<کد متعلق به session>" }`؛ پاسخ موفق `{"enrollment":{"id":"…","status":"dropped",…}}`. خطای بسته‌بودن پنجره 400 و شناسهٔ متعلق‌نبودن 403 است.

### 6. سناریوی عملکرد

dashboard → enrollment → selected-courses → offerings API → انتخاب گروه → service ثبت‌نام → transaction دیتابیس → refresh صفحه؛ برای حذف، جدول → modal → service drop → refresh. قواعد در `apps/core/enrollment/services.py` است. ثبت مرورگر روی seed فعلی قابل اجرا نیست: term فعال پنجره‌اش بسته است و term دیگر ارائهٔ ثبت‌شده ندارد؛ suite Python قواعد را با زمان کنترل‌شده آزموده است.

### 7. ارتباط با سایر بخش‌ها

به Mobina برای مسیر enrollment/selected courses، به scheduling برای offering و به مدل‌های مشترک `Enrollment`, `CourseOffering`, `Term`, `Grade`, `Prerequisite` وابسته است. اعتراض نمره با نقش reviewer در API بررسی درخواست، workflow کارمند کامل محسوب نمی‌شود.

### 8. ساختار فنی

- `apps/core/frontend/shaghayegh/pages.py`, `selectors.py`
- `apps/core/frontend/shaghayegh/templates/shaghayegh/course_changes.html`
- `apps/core/frontend/shaghayegh/static/shaghayegh/section.js`
- `apps/core/enrollment/services.py`, `apps/core/enrollment/views.py`
- `apps/core/models.py`: Enrollment/GradeAppeal/Term/Constant.

### 9. تست‌ها

`apps/core/enrollment/test_services.py` بر قواعد ثبت/حذف، ظرفیت، تداخل، مالکیت، بازه و اعتبارسنجی تمرکز دارد؛ `apps/core/test_frontend.py` رندر و فرم‌ها را می‌سنجد. آخرین اجرای کامل گزارش‌شده: ۱۰۱ Python و ۱۴ Node پاس؛ جزئیات در [گزارش آزمون](../TEST_REPORT.md).

### 10. راهنمای ارائه به استاد

1. صفحهٔ حذف‌واضافه و جدول را باز کنید.
2. modal حذف را باز کنید و نشان دهید درخواست فقط پس از تأیید ارسال می‌شود.
3. در `section.js` شناسهٔ `data-record-id` و فراخوانی `PortalApi.drop` را دنبال کنید.
4. در service قواعد بازه و مالکیت را نشان دهید.
5. ثبت درس را فقط در test database با term باز انجام دهید؛ seed فعلی به‌عمد خارج از بازه است.
