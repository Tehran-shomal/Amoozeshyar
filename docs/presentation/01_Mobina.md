# ارائهٔ گروه مبینا — ورود و چارچوب پرتال

> این سند مسئولیت‌های ذکرشده در پیوست را با مالکیت واقعی `registry.py` تطبیق می‌دهد. صفحه‌ای که در PDF کنار این گروه آمده الزاماً در manifest فعلی کد متعلق به این گروه نیست.

### 1. معرفی بخش

ورود، داشبورد و مسیر ورود دانشجو به جریان انتخاب واحد. shell، header و sidebar بین همهٔ صفحات مشترک‌اند و به یک صفحهٔ Mobina محدود نیستند.

### 2. مسئولیت عضو

طبق پیوست: ورود و احراز هویت، داشبورد، کارت‌های دسترسی، اجزای مشترک، انتخاب نیمسال، تنظیمات و کارت دیجیتال. در کد فعلی Mobina مالک `login`, `dashboard`, `enrollment`, `selected-courses`, و `curriculum` است؛ `settings` در گروه مشترک Neyousha/Pouya و `student-card` در manifest امید ثبت شده‌اند. مالکیت واقعی نباید در ارائه جابه‌جا یا پنهان شود.

### 3. صفحات پیاده‌سازی‌شده

| صفحه/حالت | PDF | URL | وضعیت مالکیت در کد |
|---|---:|---|---|
| ورود | 1 | `/login/` | Mobina؛ فرم HTML و API ورود |
| داشبورد | 2 | `/` | Mobina؛ دادهٔ حساب جاری |
| انتخاب نیمسال | 3 | در shell همهٔ صفحات | جزء مشترک Neyousha/Pouya؛ query در URL |
| sidebar گروهی | 4–8 | shell همهٔ صفحات | navigation مشترک، نه route مستقل |
| انتخاب واحد | 52 | `/portal/enrollment/` | Mobina |
| دروس انتخاب‌شده و انتخاب گروه | 9–13 | `/portal/selected-courses/` | Mobina؛ بخشی از حالت‌های PDF غایب است |
| چارت درسی | 23 | `/portal/curriculum/` | Mobina |
| تنظیمات / کارت | 19 / 20 | `/portal/settings/` / `/portal/student-card/` | به‌ترتیب Neyousha/Pouya و Omid؛ در این گروه نیستند |

### 4. طراحی و عملکرد

فرم ورود نام کاربری و گذرواژه را می‌گیرد، CSRF را برای API هم‌مبدأ تأمین می‌کند و پس از ایجاد session به داشبورد می‌رود. داشبورد و صفحه‌های داخلی از API صفحه HTML داده‌محور می‌گیرند. انتخاب نیمسال در dialog انجام می‌شود و `student_code` و `term` را در query حفظ می‌کند. ثبت درس در صفحهٔ دروس انتخاب‌شده با شناسهٔ رکورد ارائه انجام می‌شود، نه با عنوان درس.

### 5. APIهای مرتبط

| مسیر | روش | ورودی/خروجی اصلی |
|---|---|---|
| `/api/accounts/csrf/` | GET | cookie و token برای درخواست نوشتنی |
| `/api/accounts/login/` | POST | `{username,password,remember_me?}`؛ پاسخ 200 با `user`، خطای اعتبارسنجی/ورود با envelope `error` |
| `/api/accounts/me/` | GET | هویت و نقش‌های session جاری |
| `/api/portal/pages/home/` | GET | `page`, `html`, `profile`, `term` |
| `/api/scheduling/offerings/?term=<code>` | GET | فهرست ارائه‌ها؛ بدون ارائه آرایهٔ خالی |
| `/api/enrollment/register/<offering_id>/` | POST | body اختیاری `{student_code}`؛ 201 برای ثبت تازه |

نمونهٔ قراردادی: `POST /api/accounts/login/` با JSON دارای `username` و `password` پس از `GET /api/accounts/csrf/`؛ پاسخ موفق `{"user":{"id":"…","username":"…","full_name":"…","roles":[]}}`. جزئیات status و CSRF در [قرارداد API](../API_CONTRACTS.md) است.

### 6. سناریوی عملکرد

مرورگر → CSRF/login → احراز هویت در `Person` و `UserAccount` → session → dashboard selector → دریافت نیمسال/دروس → بررسی مجوز و قواعد در service ثبت‌نام → نوشتن Enrollment در transaction → نمایش دوباره از API صفحه. آزمون‌های دامنه‌ای ثبت و حذف را با بازه‌های کنترل‌شده اجرا می‌کنند؛ seed مرورگر فعلی ارائهٔ قابل‌ثبت در بازهٔ باز ندارد.

### 7. ارتباط با سایر بخش‌ها

shell و `term_picker` برای همه مشترک‌اند؛ انتخاب درس به service مشترک enrollment و زمان‌بندی وابسته است. پروفایل دانشجو از session resolve می‌شود و شناسهٔ دانشجوی دیگر مجوز محسوب نمی‌شود.

### 8. ساختار فنی

- `apps/core/frontend/mobina/pages.py`, `selectors.py`, `views.py`
- `apps/core/frontend/mobina/templates/mobina/login.html`, `home.html`, `enrollment.html`, `selected_courses.html`
- `apps/core/frontend/mobina/static/mobina/section.js`
- `apps/core/accounts/`, `apps/core/enrollment/`, `apps/core/scheduling/`
- مدل‌ها: `Person`, `Student`, `Term`, `CourseOffering`, `Enrollment` در `apps/core/models.py`.

### 9. تست‌ها

در اجرای کامل branch ممیزی: ۱۰۱ تست Python و ۱۴ تست Node پاس شدند؛ suite ورود/مالکیت در `apps/core/accounts/test_services.py` و render صفحه‌ها در `apps/core/test_frontend.py` است. سناریوی مرورگر محلی ورود، dashboard، تغییر نیمسال، رسیدن از «ادامه» به دروس و خروج را گذراند. وضعیت نهایی آزمون‌ها در [TEST_REPORT.md](../TEST_REPORT.md) نگهداری می‌شود.

### 10. راهنمای ارائه به استاد

1. فرم `/login/` را باز و با حساب تست محلی وارد شوید؛ هیچ رمز seed را در اسلاید یا مخزن منتشر نکنید.
2. dashboard را نشان دهید و توضیح دهید محتوا از session و selector می‌آید.
3. dialog نیمسال را باز کنید و تغییر query را نشان دهید.
4. از «ادامه» وارد `/portal/selected-courses/` شوید؛ API ارائه‌ها و شناسهٔ ارائه را در کد دنبال کنید.
5. به `portal_api.js`، `mobina/section.js` و service ثبت‌نام اشاره کنید؛ ثبت واقعی فقط وقتی داده و بازهٔ معتبر وجود دارد اجرا شود.
