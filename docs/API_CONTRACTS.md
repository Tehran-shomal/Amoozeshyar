# قرارداد API آموزشیار

این سند فقط routeهایی را توصیف می‌کند که در `config/urls.py` و URLConfهای feature واقعاً mount شده‌اند. «API صفحه» یک endpoint عمومی برای رندر/ارسال فرم است و جای API تخصصی دامنه‌ای یا مجوز سازمانی را نمی‌گیرد.

## قرارداد مشترک

- احراز هویت با session جنگو و cookie هم‌مبدأ است؛ bearer token یا CORS در این checkout تعریف نشده است.
- همهٔ درخواست‌های تغییردهنده به CSRF معتبر نیاز دارند. کلاینت مرورگر ابتدا `GET /api/accounts/csrf/` می‌زند و مقدار `X-CSRFToken` را روی درخواست بعدی می‌فرستد. CSRF rotation پس از ورود، token بعدی را دوباره bootstrap می‌کند.
- JSON ورودی باید object باشد. خطاهای برنامه‌ای با `{"error":{"code":"…","message":"…"}}` برمی‌گردند. خطای CSRF و methodهای غیرمجاز ممکن است پاسخ پیش‌فرض Django باشند و الزاماً این envelope را ندارند.
- نشست API به‌صورت پیش‌فرض ۹۰۰ ثانیه idle timeout دارد؛ گزینهٔ `remember_me=false` نشست را تا پایان مرورگر نگه می‌دارد.
- صفحه‌های دامنه فقط پروندهٔ متعلق به `request.user` را resolve می‌کنند. `student_code` ارسالی صرفاً می‌تواند یکی از پرونده‌های همان حساب را انتخاب کند؛ شناسهٔ دانشجوی دیگر مجوز دسترسی ایجاد نمی‌کند.

## Routeهای پیاده‌شده

| روش و مسیر | ورود/CSRF | payload / پاسخ موفق | خطاهای مهم و رفتار |
|---|---|---|---|
| `GET /api/accounts/csrf/` | بدون ورود؛ cookie را تنظیم می‌کند | `{"csrf_token":"…"}` — 200 | فقط GET؛ پاسخ CSRF برای درخواست‌های نوشتنی بعدی است. |
| `POST /api/accounts/login/` | بدون session؛ CSRF لازم | `username`, `password`, اختیاری `remember_me` (boolean، پیش‌فرض `true`)؛ 200 با `user:{id,username,full_name,roles}` | 400 `invalid_json`, `missing_credentials`, `invalid_remember_preference`; 401 `invalid_credentials`; 403 `account_inactive`; 423 `account_locked`; 503 `database_unavailable`. پنج تلاش ناموفق و ۹۰۰ ثانیه قفل، تنظیم پیش‌فرض سرویس است. |
| `POST /api/accounts/logout/` | session لازم؛ CSRF لازم | `{"success":true}` — 200 و session پاک می‌شود | 401 `authentication_required`. |
| `GET /api/accounts/me/` | session لازم | `{"user":{"id","username","full_name","roles"}}` — 200 | 401 `authentication_required`. |
| `GET /api/scheduling/active-term/` | session لازم | `{"term":null}` یا `term:{id,term_code,academic_year,start_date,end_date,registration_open,add_drop_open,emergency_drop_open}` — 200 | 401 `authentication_required`. این endpoint فقط نیمسال فعال را می‌خواند. |
| `GET /api/scheduling/offerings/?term=<term_code>` | session لازم | `{"offerings":[{id,term_id,lesson_code,title,theory_units,practical_units,total_units,teacher,day_of_week,start_time,end_time,classroom,capacity,remaining_capacity,exam_date,exam_time}]}` — 200 | بدون `term` نیمسال فعال خوانده می‌شود؛ کد ناموجود 404 `term_not_found`; بدون نیمسال/ارائه، آرایهٔ خالی. |
| `POST /api/enrollment/register/<offering_id>/` | role `student`؛ CSRF لازم | body اختیاری `{student_code}`؛ `{"enrollment":{id,student_code,offering_id,lesson_code,lesson_title,status,enrollment_date,drop_date}}`; 201 برای رکورد جدید، 200 برای ثبت موجود/فعال‌سازی مجدد | 400 برای profile مبهم، بازه بسته یا قواعد آموزشی؛ 401 بدون session؛ 403 role/مالکیت؛ 404 offering یا student؛ 500 status lookup پیکربندی‌نشده. کدهای business در بخش ثبت‌نام پایین آمده‌اند. |
| `POST /api/enrollment/drop/<enrollment_id>/` | role `student`؛ CSRF لازم | body اختیاری `{student_code}`؛ همان envelope `enrollment` — 200 | 400 `drop_window_closed`; 401 بدون session؛ 403 `permission_denied`/`enrollment_not_owned`; 404 enrollment/student؛ وضعیت حذف‌شده idempotent است. |
| `POST /api/requests/<request_type>/<request_id>/review/` | session و role مخصوص نوع درخواست؛ CSRF لازم | `{target_status:"in_review"|"approved"|"rejected"}`؛ `{"request":{"id,type,status}}` — 200 | 400 `invalid_json`, `missing_target_status`, `invalid_transition`; 401 `authentication_required`; 403 `permission_denied`; 404 نوع/درخواست ناموجود؛ 500 `request_status_unavailable` اگر Constant فعال موجود نباشد. جدول نقش‌ها پایین آمده است. |
| `GET|POST /api/portal/pages/<slug>/` | session لازم؛ POST علاوه بر آن CSRF | GET: `{"page":slug,"html":"…","profile":{"student_code":"…"},"term":{"term_code":…,"display_label":"…"}}` — 200. POST: JSON scalar یا list از فیلدهای فرم؛ پس از موفقیت `{"redirect":"/portal/<slug>/?..."}` — 200 | 401 `authentication_required`; 403 پروندهٔ انتخابی متعلق به حساب نیست؛ 404 `page_not_found`, `page_data_not_found`; 503 `database_unavailable`. فرم نامعتبر 400 با `error.code=validation_error` و HTML مجدداً renderشده. ارسال nested object، فایل، یا POST صفحهٔ بدون فرم پذیرفته نیست؛ صفحهٔ بدون فرم 405. |
| `GET|POST /api/portal/pages/home/` | session لازم | GET همان envelope صفحه با `page:"home"`؛ فقط GET مجاز است | POST داشبورد 405 `method_not_allowed`; 401 بدون session؛ 503 در قطع DB. |

### ثبت‌نام و حذف درس

اعتبارسنجی در `apps/core/enrollment/services.py` و داخل transaction انجام می‌شود. کدهای قابل مشاهدهٔ پیاده‌سازی: `offering_not_found`, `student_not_found`, `inactive_offering`, `term_not_active`, `registration_window_closed`, `student_not_eligible`, `tuition_debt`, `corequisite_not_met`, `prerequisite_not_met`, `schedule_conflict`, `exam_conflict`, `credit_limit_exceeded`, `offering_full`, `enrollment_status_unavailable`, `enrollment_not_found`, `enrollment_not_owned`, `drop_window_closed`. هر خطا به envelope مشترک `error` تبدیل می‌شود.

Body ثبت/حذف می‌تواند خالی باشد؛ اگر فرد چند پرونده داشته باشد باید `student_code` متعلق به خودش را بفرستد. enrollment id و offering id، شناسهٔ رکورد دیتابیس‌اند؛ عنوان/کد درس به‌تنهایی برای mutation پذیرفته نمی‌شود.

### بازبینی درخواست‌ها

| `request_type` | نقش‌های مجاز در کد فعلی |
|---|---|
| `student-service`, `transfer`, `credit-transfer`, `refund` | `education_officer`, `admin` |
| `scholarship-application` | `scholarship_officer`, `admin` |
| `proposal`, `thesis-progress-report` | `professor`, `education_officer`, `admin` |
| `internship`, `internship-request` | `student_affairs_officer`, `admin` |
| `grade-appeal` | `education_officer`, `professor`, `admin` |

کدهای مجاز مقصد `in_review`, `approved`, `rejected` هستند. از `submitted` فقط `in_review`؛ از `in_review` فقط `approved` یا `rejected`؛ دادهٔ legacy با `pending` هر سه مقصد را می‌پذیرد. این transition در `apps/core/requests/services.py` است و مجوز product owner مستقلاً تأیید نشده است.

## Browser routes (غیر API)

- `GET /login/` و `POST /login/`: فرم HTML و fallback؛ ورود از طریق `authenticate_person`.
- `GET /`: shell داشبورد؛ داده با `GET /api/portal/pages/home/` بارگیری می‌شود.
- `GET /portal/<slug>/`: shell صفحه؛ محتوای واقعی از API صفحه دریافت می‌شود.
- `POST /logout/`: fallback HTML؛ در مرورگر معمولاً `POST /api/accounts/logout/` مصرف می‌شود.
- `/admin/`: Django admin، جدا از API پرتال.

## Routeهای خالی

در ۱۴ namespace آدرس‌های مستقل دامنه‌ای تعریف نشده‌اند: `attendance`, `grading`, `counseling`, `classroom`, `tuition`, `tickets`, `student_services`, `thesis`, `scholarships`, `people`, `reports`, `online_exam`, `internship`, `notifications`. برخی selectorهای UI همین مدل‌ها را از طریق API عمومی صفحه می‌خوانند؛ این معادل API تخصصی برای actorها/مجوزهای آن دامنه نیست. سایر namespaceها در `config/urls.py` عبارت‌اند از `accounts`, `enrollment`, `requests`, `scheduling`.

## قراردادهای بیرونیِ موجود نیستند

درگاه پرداخت، صدور رسمی کارت/گواهی، ارسال ایمیل/SMS، task queue و API سرویس دانشگاهی در checkout تنظیم نشده‌اند. هیچ route یا UI موجود نباید برای این اقدام‌ها موفقیت بیرونی را وانمود کند.

## شواهد آزمون

- endpointها: `apps/core/accounts/test_services.py`, `apps/core/enrollment/test_services.py`, `apps/core/scheduling/test_services.py`, `apps/core/requests/test_services.py`.
- API صفحه و مالکیت داده: `apps/core/test_frontend.py`, `apps/core/test_architecture.py`.
- browser client: `static/core/tests/portal_api.test.cjs`, `static/core/tests/portal_bindings.test.cjs`.
