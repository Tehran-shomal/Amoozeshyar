# آموزشیار (Amoozeshyar)

سامانهٔ آموزشیار یک پروژهٔ Django برای مدیریت فرایندهای دانشگاهی است. این شاخه زیرساخت backend و رابط کاربری سروررندرشدهٔ فارسی/راست‌چین را فراهم می‌کند.

## وضعیت فعلی

پروژه یک Django monolith است. مدل‌ها در `apps/core/models.py` و ثبت‌های پنل مدیریت در `apps/core/admin.py` نگهداری می‌شوند. برای ۱۸ حوزهٔ سامانه app و مسیر API ایجاد شده است؛ منطق backend فعلاً در این حوزه‌ها پیاده‌سازی شده:

- **حساب‌ها:** ورود و خروج مبتنی بر session، CSRF، نقش‌ها و قفل حساب پس از پنج ورود ناموفق برای ۱۵ دقیقه.
- **زمان‌بندی:** خواندن ترم فعال و ارائه‌های فعال.
- **ثبت‌نام:** ثبت و حذف درس با بررسی بازهٔ مجاز، وضعیت دانشجو، بدهی، پیش‌نیاز، تداخل برنامه و امتحان، سقف واحد و ظرفیت.
- **درخواست‌ها:** تغییر وضعیت بازبینی برای مدل‌های درخواست موجود؛ ثبت درخواست و فهرست وضعیت‌ها هنوز پیاده‌سازی نشده‌اند.

بقیهٔ feature appها فعلاً عمدتاً namespace و مسیر خالی دارند. جزئیات شکاف‌های مدل و قابلیت‌ها در [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) آمده است.

صفحه‌های پرتال به APIها و رکوردهای دیتابیس متصل‌اند؛ ورود و خروج با session انجام می‌شود و عملیات انتخاب/حذف درس از APIهای موجود می‌گذرد. دادهٔ صفحه از selectorهای Django خوانده می‌شود و برای صفحهٔ بدون رکورد، نتیجهٔ خالی نمایش داده می‌شود.

پنج گروه منوی محصول از پنج گروه کد فرانت جدا هستند. هر گروه در `apps/core/frontend/<group>/`، فهرست صفحه‌ها را در `pages.py`، خواندن داده را در `selectors.py` و فرم‌ها را در `forms.py` نگه می‌دارد. قالب عمومی جدول/فرم در `apps/core/templates/core/live_content.html` مشترک است؛ قالب یا اسکریپت اختصاصی فقط کنار صفحه‌ای نگه داشته می‌شود که واقعاً به آن نیاز دارد. هر گروه README مالکیت و توضیح کوتاه منطق اصلی خود را دارد.

| گروه کد | صفحه‌ها |
| --- | --- |
| [مبینا](apps/core/frontend/mobina/README.md) | ورود، داشبورد، انتخاب واحد، دروس انتخاب‌شده، چارت انتخاب واحد |
| [شقایق](apps/core/frontend/shaghayegh/README.md) | حذف و اضافه، حذف اضطراری، وضعیت ثبت‌نام، اعتراض به نمره |
| [خدمات آموزشی (شاهسوند و امید)](apps/core/frontend/academic_services/README.md) | شاهسوند: ارزشیابی استاد، فرم ارزشیابی، ارتباط با استاد، درخواست مهمانی، فارغ‌التحصیلی؛ امید: فعالیت‌های آموزشی، کارنامه، حضور و غیاب، کارت امتحان، درخواست‌های دانشجو و مدارک |
| [پارسا](apps/core/frontend/parsa/README.md) | سوابق پرداخت، پرداخت امن، تسهیلات، مالی نیمسال‌ها |
| [پویا و نیوشا (لید فرانت)](apps/core/frontend/neyousha_pouya/README.md) | کارآموزی، اعلان‌ها، اطلاعیه‌ها، تقویم و برنامهٔ ترم، تنظیمات، انتخاب نیمسال |

## فناوری‌ها

- Python و Django 5.2.18
- SQLite برای توسعهٔ محلی
- Django sessions، `JsonResponse` و middleware داخلی CSRF؛ بدون REST framework یا وابستگی ثالث جدید
- زبان و timezone محلی: `fa-ir` و `Asia/Tehran`؛ ذخیره‌سازی `DateTimeField` با `USE_TZ=True`

## راه‌اندازی محلی در Windows / PowerShell

فرمان‌ها را از ریشهٔ مخزن اجرا کنید:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

اگر `.env` از قبل وجود دارد، آن را نگه دارید؛ نمونهٔ محیط در `.env.example` برای توسعهٔ محلی است. پیش از استفاده در محیط واقعی، `SECRET_KEY`, `DEBUG` و `ALLOWED_HOSTS` را با مقادیر امن و مناسب همان محیط تنظیم کنید.

دادهٔ نمونه را می‌توان با فرمان `python manage.py seed` ساخت. این فرمان فقط در حالت `DEBUG=True` مجاز است و برای دادهٔ توسعه است.

## دیتابیس و timezone

برای دیتابیس خالی، `manage.py migrate` کافی است. مهاجرت `0004_legacy_datetime_utc` داده‌های قدیمی و بدون timezone را به UTC تبدیل می‌کند؛ اگر دیتابیس پیش از فعال‌کردن `USE_TZ` تاریخ‌هایی داشته باشد، باید timezone واقعی مبدأ آن داده‌ها را در `.env` مشخص کنید:

```dotenv
LEGACY_DATETIME_TIME_ZONE=Asia/Tehran
```

این مقدار را فقط وقتی بگذارید که timezone واقعی داده‌های دیتابیس را تأیید کرده باشید؛ آن را حدس نزنید. پیش از مهاجرت دیتابیس موجود، نسخهٔ پشتیبان بگیرید. اگر ردیف‌های قدیمی وجود داشته باشند و timezone تعیین نشده باشد، مهاجرت پیش از تغییر داده متوقف می‌شود. مهاجرت تبدیل timezone برگشت‌پذیر نیست؛ برای بازگردانی باید نسخهٔ پیش از مهاجرت را بازیابی کرد.

## API

همهٔ مسیرها با `/api/` آغاز می‌شوند. خطاها به شکل JSON زیر برمی‌گردند:

```json
{"error": {"code": "...", "message": "..."}}
```

| روش و مسیر | دسترسی و کاربرد |
|---|---|
| `GET /api/accounts/csrf/` | عمومی؛ cookie و token مربوط به CSRF را آماده می‌کند. |
| `POST /api/accounts/login/` | CSRF-protected؛ JSON شامل `username` و `password`؛ session می‌سازد. |
| `POST /api/accounts/logout/` | نیازمند session؛ خروج از حساب. |
| `GET /api/accounts/me/` | نیازمند session؛ خلاصهٔ امن کاربر فعلی. |
| `GET /api/scheduling/active-term/` | عمومی؛ ترم فعال و وضعیت بازه‌های ثبت‌نام. |
| `GET /api/scheduling/offerings/` | عمومی؛ ارائه‌های فعال ترم جاری. |
| `POST /api/enrollment/register/<offering_id>/` | نیازمند session دانشجو؛ در صورت داشتن چند پروفایل، JSON اختیاری `{ "student_code": "..." }` می‌پذیرد. ثبت جدید `201` و ثبت تکراری `200` می‌دهد. |
| `POST /api/enrollment/drop/<enrollment_id>/` | نیازمند session مالک ثبت‌نام؛ در صورت نیاز همان `student_code` اختیاری را می‌پذیرد. |
| `POST /api/requests/<request_type>/<request_id>/review/` | نیازمند نقش بازبین؛ JSON شامل `target_status` با یکی از مقادیر `in_review`, `approved`, `rejected`. |

برای درخواست‌های مرورگر، ابتدا `GET /api/accounts/csrf/` را بزنید، cookie مربوط را نگه دارید و مقدار token را در header `X-CSRFToken` درخواست‌های تغییردهنده بفرستید. پس از ورود، cookie مربوط به session را هم نگه دارید. ارتباط cross-origin پیکربندی نشده است؛ درخواست‌ها باید same-origin باشند.

قواعد ثبت‌نام در `apps/core/enrollment/services.py` پیاده‌سازی شده‌اند. وضعیت مشروط سقف ۱۴ واحد دارد؛ کد قدیمی `student_status.suspended` نیز به‌عنوان alias وضعیت مشروط پذیرفته می‌شود. جزئیات قرارداد API و نقش‌ها در [SSOT](docs/SSOT.md) آمده است.

## آزمون‌ها و بررسی‌های توسعه

```powershell
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

برای بررسی تنظیمات استقرار:

```powershell
.\.venv\Scripts\python.exe manage.py check --deploy
```

محیط استقرار باید HTTPS را مطابق معماری واقعی خود تنظیم کند؛ در تنظیم توسعهٔ فعلی، `check --deploy` دربارهٔ HSTS و redirect به SSL هشدار می‌دهد. SQLite نیز تضمین قفل ردیفی `select_for_update()` را برای آزمون هم‌زمانی فراهم نمی‌کند.

## مستندات و محدودهٔ کار

- [SSOT](docs/SSOT.md): قراردادها، ساختار و سطح API.
- [ADR](docs/ADR.md): تصمیم‌های معماری، فرض‌ها و محدودیت‌ها.
- [SDD](docs/SDD.md): نگاشت نیازمندی‌ها به حوزه‌ها؛ جدول‌ها در `docs/sdd/traceability/` جدا شده‌اند.
- [AGENT_INSTRUCTIONS](docs/AGENT_INSTRUCTIONS.md): قواعد نگهداری ساختار مخزن.
- [PROJECT_STRUCTURE](PROJECT_STRUCTURE.md): وضعیت واقعی مدل‌ها، appها، مسیرها و شکاف‌ها.

فایل اصلی شرح رفتاری نیازمندی‌ها که SSOT به آن ارجاع می‌دهد در این مخزن موجود نیست. جدول‌های SDD شناسه‌ها و حوزه‌ها را نگاشت می‌کنند، اما جایگزین شرح رفتار کامل نیستند؛ برای تکمیل featureهای باقی‌مانده باید متن اصلی نیازمندی‌ها بازیابی و قواعد نامشخص تأیید شوند.
