# ارائهٔ گروه نیوشا — برنامه و تجربهٔ responsive

### 1. معرفی بخش

صفحه‌های زمان‌بندی و اعلان‌ها و بخشی از تنظیمات پرتال. نقش Frontend Lead در پیوست شامل هماهنگی UI و بررسی responsive تمام گروه‌هاست.

### 2. مسئولیت عضو

پیوست صفحات ۱۴–۱۵ و ۲۱–۲۲ را برای حضور، تقویم، کارت امتحان و برنامه هفتگی نام می‌برد. در کد فعلی گروه `neyousha_pouya` مشترک است و مالک `calendar`, `schedule`, `settings`, `internship`, `notifications`, و `announcements` است؛ `attendance` و `exam-card` در manifest Omid قرار دارند. گزارش responsive این شاخه در [TEST_REPORT.md](../TEST_REPORT.md) آمده است.

### 3. صفحات پیاده‌سازی‌شده

| صفحه | PDF | URL | مالکیت/وضعیت واقعی |
|---|---:|---|---|
| تقویم آموزشی | 15 | `/portal/calendar/` | گروه مشترک؛ فقط تاریخ‌های Term، نه grid رویداد PDF |
| برنامه هفتگی | 22 | `/portal/schedule/` | گروه مشترک؛ جدول Enrollmentهای فعال و چاپ مرورگر |
| اعلان‌ها | 18 | `/portal/notifications/` | گروه مشترک؛ read و mark-read متعلق به شخص |
| اطلاعیه‌ها | 16 | `/portal/announcements/` | گروه مشترک؛ feed مشترک Notification، انتشار ندارد |
| تنظیمات | 19 | `/portal/settings/` | گروه مشترک؛ ویرایش فیلدهای Person |
| انتخاب نیمسال | 3 | dialog در shell | جزء مشترک، query را در URL نگه می‌دارد |
| حضور و غیاب / کارت امتحان | 14 / 21 | `/portal/attendance/` / `/portal/exam-card/` | route واقعی اما manifest Omid؛ attendance فقط خواندنی، صدور رسمی نیست |

### 4. طراحی و عملکرد

صفحات زمان‌بندی از Term و Enrollment/Offering واقعی می‌خوانند. تقویم رویداد مستقل در schema وجود ندارد؛ دادهٔ خالی را به رویداد فرضی تبدیل نمی‌کنیم. اعلان فقط وقتی متعلق به Person جاری باشد خوانده علامت می‌خورد. تنظیمات فقط Person احرازشده را ویرایش می‌کند.

### 5. APIهای مرتبط

- `GET /api/portal/pages/calendar/`, `/schedule/`, `/notifications/`, `/announcements/`, `/settings/`
- `GET /api/scheduling/active-term/` برای نیمسال فعال
- `POST /api/portal/pages/notifications/` با شناسهٔ اعلان؛ فقط اعلان متعلق به همان حساب
- `POST /api/portal/pages/settings/` با `email`, `address`, `is_notification_enabled`, `preferred_language`

نمونهٔ قراردادی تنظیمات: `POST /api/portal/pages/settings/` پس از CSRF، JSON فیلدهای فرم؛ 200 با `{ "redirect": "/portal/settings/?…" }`. فرم نامعتبر 400 و دسترسی به شخص دیگر 403 است.

### 6. سناریوی عملکرد

session → portal shell → انتخاب نیمسال از dialog → API صفحه → selector و model query → render. تغییر نیمسال GET-only است؛ notification POST در transaction فقط حالت همان اعلان را تغییر می‌دهد. آزمون مرورگر شاخهٔ ممیزی term switching واقعی را با تغییر query مشاهده کرد.

### 7. ارتباط با سایر بخش‌ها

shell/term picker با تمام مالکان route مشترک است. schedule به ثبت‌نام‌های Mobina/Shaghayegh و Calendar به Term وابسته است؛ اعلان‌ها در dashboard نیز خلاصه می‌شوند. assignmentهای attendance و exam-card در کد با Omid است.

### 8. ساختار فنی

- `apps/core/frontend/neyousha_pouya/pages.py`, `selectors.py`, `forms.py`
- `apps/core/frontend/neyousha_pouya/templates/neyousha_pouya/notifications.html`
- `static/core/live_portal.js`, `apps/core/templates/core/portal_base.html`
- مدل‌ها: `Term`, `Enrollment`, `CourseOffering`, `Notification`, `Person`.

### 9. تست‌ها

در مرورگر محلی: ورود، dashboard، تغییر term از `14051` به `14052`، مسیر صفحهٔ دروس، خواندن API و logout اجرا شد. viewportهای هدف نیز capture شدند؛ در 768 پیکسل باگ قاب دوگانهٔ search اصلاح شد. اجرای کامل: ۱۰۱ تست Python و ۱۴ Node؛ هر دو پاس. جزئیات در [TEST_REPORT.md](../TEST_REPORT.md).

### 10. راهنمای ارائه به استاد

1. dialog نیمسال را باز و تغییر URL را نشان دهید.
2. برنامه هفتگی و تقویم را کنار هم باز کنید و منبع دادهٔ متفاوتشان را توضیح دهید.
3. اعلان را نشان دهید و مالکیت Person را در selector بررسی کنید.
4. نسخهٔ موبایل/تبلت و فایل responsive CSS را بازبینی کنید.
5. اعلام کنید چرا تقویم رویداد یا حضور کارمند بدون schema/API ساخته نشده است.
