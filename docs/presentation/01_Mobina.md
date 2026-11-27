# ارائهٔ ۰۱ — مبینا: ورود و چارچوب مشترک

### 1. معرفی بخش

ورود دانشجو، داشبورد و اجزای مشترک پنل در گروه مبینا هستند. shell، sidebar و header میان همهٔ صفحه‌ها مشترک‌اند؛ انتخاب نیمسال مؤلفهٔ مشترک است و توسط لید فرانت‌اند هماهنگ می‌شود.

### 2. مسئولیت عضو

ورود/احراز هویت، داشبورد، کارت‌های دسترسی، shell، تنظیمات حساب و کارت دانشجویی دیجیتال. اشارهٔ پرامپت: صفحات PDF ۱–۳، ۴–۸ و ۱۹–۲۰. فایل PDF در clone پیدا نشد؛ این شماره‌ها فعلاً تأیید بصری نشده‌اند.

### 3. صفحه‌ها و URLها

| صفحه | URL | API | وضعیت فعلی |
|---|---|---|---|
| ورود | `/login/` | `POST /api/accounts/login/`; `GET /api/accounts/csrf/`, `/api/accounts/me/` | session واقعی و فرم HTML پشتیبان |
| داشبورد | `/` | `GET /api/portal/pages/home/` | خلاصه از ORM، برای پروفایل انتخابی |
| تنظیمات | `/portal/settings/` | GET/POST `/api/portal/pages/settings/` | قالب PDF صفحهٔ ۱۹؛ Person حساب واردشده؛ کانال پیامک/ایمیل و موبایل فاقد مدل/provider |
| کارت دانشجویی | `/portal/student-card/` | `GET /api/portal/pages/student-card/` | preview از دادهٔ واقعی، نه کارت رسمی |

### 4. طراحی و جریان

فرم ورود داده را به Accounts API می‌فرستد، session ساخته می‌شود و کاربر به dashboard می‌رود. هر صفحهٔ داخلی اول shell را می‌گیرد و سپس HTML داده‌محور از API صفحه دریافت می‌کند. انتخاب نیمسال query `term` را نگه می‌دارد. تغییر تنظیمات با refresh/redirect از همان endpoint انجام می‌شود.

### 5. API و داده

ورودی login شامل username/password و اختیاری remember_me است؛ CSRF از `/api/accounts/csrf/` bootstrap می‌شود. داشبورد از Student، Enrollment، Notification و Paymentهای موجود می‌خواند. تنظیمات Person جاری را update می‌کند؛ فرم اختصاصی فقط email/address/is_notification_enabled/preferred_language را می‌پذیرد و محدودیت کانال‌های بیرونی را اعلام می‌کند. کارت فقط Person/Student/Field/Term را نمایش می‌دهد.

نمونهٔ قراردادی (مقدارها ساختگی و صرفاً نمایشی‌اند):

```http
POST /api/portal/pages/settings/?student_code=S10001&term=TERM-1
Content-Type: application/json
X-CSRFToken: <csrf-token>

{"email":"student@example.test","address":"آدرس نمونه","is_notification_enabled":true,"preferred_language":"fa"}
```

پاسخ موفق: `{"redirect":"/portal/settings/?student_code=S10001&term=TERM-1"}` با HTTP 200؛ دادهٔ تازه پس از redirect از GET همان صفحه خوانده می‌شود. نمونهٔ login و خطاها در [قرارداد API](../API_CONTRACTS.md) است.

### 6. مجوز و محدودیت

همهٔ APIها به session وابسته‌اند. `student_code` ورودی فقط وقتی پذیرفته می‌شود که Student متعلق به حساب باشد. تنظیمات بر اساس `request.user` است. کارت دیجیتال شماره سریال، اعتبارنامه یا صدور رسمی جعل نمی‌کند. reset password محلی و provider کارت موجود نیستند.

### 7. فایل‌های فنی

- `apps/core/frontend/mobina/pages.py`, `selectors.py`, `forms.py`
- `apps/core/frontend/mobina/templates/mobina/{home.html,login.html,student_card.html}`
- `apps/core/frontend/mobina/static/mobina/login.js`
- پوسته: `apps/core/templates/core/portal_base.html`; API مرورگر: `static/core/portal_api.js`, `live_portal.js`
- [Screen docs](../screens/login.md), [dashboard](../screens/dashboard.md), [settings](../screens/settings.md), [student-card](../screens/student-card.md)

### 8. ارتباط بین بخش‌ها

پوسته برای تمام هفت گروه استفاده می‌شود. انتخاب نیمسال از Termهای موجود می‌آید و مقدار انتخاب‌شده برای enrollment، مالی، کارنامه و برنامه قابل استفاده است. logout از `/api/accounts/logout/` انجام می‌شود.

### 9. تست و وضعیت QA

تست و مرورگر بنا به درخواست صاحب پروژه برای فاز بعد نگه داشته شده؛ پس این ارائه نتیجهٔ اجرای آزمون جدید ادعا نمی‌کند. مسیرهای test مرتبط بعداً `apps/core/test_frontend.py`, `apps/core/accounts/test_services.py` و Node tests هستند. تطبیق PDF نیز تا قرارگرفتن فایل مرجع معلق است.

### 10. سناریوی ارائه

۱) `/login/` را باز کنید و session را بسازید. ۲) داشبورد و داده‌های خوانده‌شده را نشان دهید. ۳) انتخاب نیمسال را باز کنید. ۴) تنظیمات حساب و scope آن را مرور کنید. ۵) کارت دیجیتال را به‌عنوان پیش‌نمایش، نه سند رسمی، معرفی کنید.

برای آدرس همهٔ routeها و محدودیت‌ها: [TEAM_OWNERSHIP](../TEAM_OWNERSHIP.md)؛ API: [قراردادها](../API_CONTRACTS.md).
