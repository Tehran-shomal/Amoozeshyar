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
| `GET /api/scheduling/offerings/?term=<term_code>` | session لازم | `{"offerings":[{id,term_id,lesson_code,title,theory_units,practical_units,total_units,teacher,day_of_week,start_time,end_time,classroom,capacity,remaining_capacity,exam_date,exam_time}]}` — 200 | بدون `term` نیمسال فعال خوانده می‌شود؛ کد ناموجود 404 `term_not_found`; بدون نیمسال/ارائه، آرایهٔ خالی. مدل/API شمارهٔ رسمی گروه و تعرفه ندارد. |
| `POST /api/enrollment/register/<offering_id>/` | role `student`؛ CSRF لازم | body اختیاری `{student_code}`؛ `{"enrollment":{id,student_code,offering_id,lesson_code,lesson_title,status,enrollment_date,drop_date},"created":boolean}`؛ 201 برای رکورد جدید، 200 برای ثبت موجود/فعال‌سازی مجدد | `created` سمت سرور تفاوت ایجاد تازه را از ثبت موجود مشخص می‌کند؛ 400 برای profile مبهم، بازه بسته یا قواعد آموزشی؛ 401 بدون session؛ 403 role/مالکیت؛ 404 offering یا student؛ 500 status lookup پیکربندی‌نشده. کدهای business در بخش ثبت‌نام پایین آمده‌اند. |
| `POST /api/enrollment/drop/<enrollment_id>/` | role `student`؛ CSRF لازم | body اختیاری `{student_code}`؛ همان envelope `enrollment` — 200 | 400 `drop_window_closed`; 401 بدون session؛ 403 `permission_denied`/`enrollment_not_owned`; 404 enrollment/student؛ وضعیت حذف‌شده idempotent است. |
| `POST /api/enrollment/emergency-drop/<enrollment_id>/` | role `student`؛ CSRF لازم | body اختیاری `{student_code}`؛ همان envelope `enrollment` — 200 | فقط `Term.emergency_drop_start/end`; خارج بازه 400 `emergency_drop_window_closed`; 401/403/404 مثل حذف عادی. |
| `POST /api/requests/<request_type>/<request_id>/review/` | session و role مخصوص نوع درخواست؛ CSRF لازم | `{target_status:"in_review"|"approved"|"rejected"}`؛ `{"request":{"id,type,status}}` — 200 | 400 `invalid_json`, `missing_target_status`, `invalid_transition`; 401 `authentication_required`; 403 `permission_denied`; 404 نوع/درخواست ناموجود؛ 500 `request_status_unavailable` اگر Constant فعال موجود نباشد. جدول نقش‌ها پایین آمده است. |
| `GET|POST /api/portal/pages/<slug>/` | session لازم؛ POST علاوه بر آن CSRF | GET: `{"page":slug,"html":"…","profile":{"student_code":"…"},"term":{"term_code":…,"display_label":"…"}}` — 200. POST: JSON scalar یا list از فیلدهای فرم؛ پس از موفقیت `{"redirect":"/portal/<slug>/?..."}` — 200؛ مسیر UI canonical است، نه `/api/...`، و query برگشتی حفظ می‌شود. | 401 `authentication_required`; 403 پروندهٔ انتخابی متعلق به حساب نیست؛ 404 `page_not_found`, `page_data_not_found`; 503 `database_unavailable`. فرم نامعتبر 400 با JSON شامل `error.code=validation_error` و قطعهٔ HTML فرم در `html`. ارسال nested object، فایل، یا POST صفحهٔ بدون فرم پذیرفته نیست؛ صفحهٔ بدون فرم 405. |
| `GET /api/portal/ui/pages/<slug>/` | session لازم؛ پاسخ `private, no-store` | React view-model نسخهٔ ۱: `schema_version`, `page`, `title`, `subtitle`, `owner`, `profile`, `term`, `shell`, `data`, `form`, `omitted_fields` — 200. `data` فقط کلیدهای allowlist‌شده دارد؛ فرم شامل metadata/choices/errors/value است و مدل Django خام برگردانده نمی‌شود. | همان scope و خطاهای 401/403/404/503 صفحهٔ معمولی. فیلدهای پیچیده‌ای که هنوز adapter امن ندارند در `omitted_fields` گزارش می‌شوند و تا مهاجرت همان صفحه نباید از React نمایش داده شوند. |
| `GET|POST /api/portal/pages/home/` | session لازم | GET همان envelope صفحه با `page:"home"`؛ فقط GET مجاز است | POST داشبورد 405 `method_not_allowed`; 401 بدون session؛ 503 در قطع DB. |

### Page API — query و payload به تفکیک صفحه

تمام slugهای فهرست‌شده در [SCREEN_API_MATRIX.md](SCREEN_API_MATRIX.md) با همین boundary خوانده می‌شوند؛ هیچ URL اختصاصی برای گروه تیمی ایجاد نشده است. queryهای عمومی `student_code` و `term` هستند؛ `student_code` باید متعلق به کاربر باشد و `term` باید به Term موجود اشاره کند. فرم ارزشیابی علاوه بر آن `enrollment` را برای انتخاب درس می‌گیرد و مالکیت/نیمسال/فعال‌بودن آن را مجدداً کنترل می‌کند؛ مرکز اعلان‌ها `notification_type` را فقط از نوع‌های واقعی همان حساب می‌پذیرد. صفحهٔ `add-drop` query اختیاری `registration_id` را فقط در scope Enrollment فعال همان Student/Term resolve می‌کند؛ `add-drop` و `emergency-drop` query اختیاری `dropped_enrollment_id` را فقط به رکورد واقعاً حذف‌شدهٔ همان Student/Term resolve می‌کنند. حذف در API فعلی مبلغ بازپرداخت را محاسبه یا ثبت نمی‌کند. POSTهای زیر JSON scalar/list به API صفحه می‌فرستند؛ فیلد owner، status، timestamp و sender که ذکر نشده‌اند از client پذیرفته نمی‌شوند.

| صفحه | POST path | JSON keys و اعتبارسنجی سمت server |
|---|---|---|
| `settings` (Mobina) | `/api/portal/pages/settings/` | `email`, `address`, `is_notification_enabled`, `preferred_language`; فقط Person حساب جاری. POST موفق با `settings_saved=1` redirect می‌کند و GET مقادیر واقعی ذخیره‌شده را نشان می‌دهد. `is_notification_enabled` ذخیره می‌شود اما سرویس اعلان فعلی آن را اعمال نمی‌کند؛ ارسال SMS/email در این endpoint نیست. |
| `financial-aid` (Parsa) | `/api/portal/pages/financial-aid/` | `scholarship_type`, `scholarship_reason`; owner و `pending` status از server. POST موفق با `request_id` redirect می‌کند؛ GET نتیجه فقط ScholarshipApplication متعلق به Student جاری را می‌خواند و اعطای تسهیلات را تضمین نمی‌کند. |
| `grade-appeal` (Omid) | `/api/portal/pages/grade-appeal/` | `enrollment`, `appeal_reason`; enrollment فقط از Student/Term جاری و دارای Grade واقعی با score غیرخالی، `appeal_date` و status از server. POST موفق با `request_id` redirect می‌کند؛ GET نتیجه فقط appeal همان Student/Term را می‌خواند و تغییر نمره/تأیید را ادعا نمی‌کند. |
| `evaluation-form` (Miri) | `/api/portal/pages/evaluation-form/` | `enrollment`, `content_mastery_rating`, `explanation_clarity_rating`, `class_organization_rating`, `student_interaction_rating`, `assessment_alignment_rating`, `comment`; پنج امتیاز اجباری ۱–۵؛ `overall_rating` سمت سرور از میانگین گرد‌شده محاسبه می‌شود؛ enrollment باید فعال و متعلق به پرونده/ترم باشد؛ duplicate رد می‌شود. فیلدهای legacy `teaching_quality` و `behavior` در POST جدید پذیرفته نمی‌شوند. |
| `evaluation` (Miri) | `/api/portal/pages/evaluation/` | GET وضعیت واقعی TeacherSurvey برای enrollmentهای فعال پرونده/ترم؛ این route فرم ثبت نمی‌پذیرد. |
| `messages` (Miri) | `/api/portal/pages/messages/` | `receiver`, `subject`, `message_body`; receiver باید حساب فعال استاد مرتبط با enrollment دانشجو باشد؛ sender سروری است. POST موفق، redirect دارای `request_id` می‌دهد؛ GET نتیجه فقط Communicationی را می‌خواند که sender آن حساب جاری باشد. نتیجهٔ DB به‌معنی اتصال استاد واقعی/تحویل بیرونی نیست. |
| `guest-request` (Shahsvand) | `/api/portal/pages/guest-request/` | `destination_university`; owner Student و وضعیت review سروری. پس از POST موفق، redirect query شامل `request_id` رکورد TransferRequest است؛ GET نتیجه فقط رکورد متعلق به Student مجاز را نشان می‌دهد و تأیید نهایی را ادعا نمی‌کند. |
| `requests` (Shahsvand) | `/api/portal/pages/requests/` | `service_request_kind` اجباری و باید Constant فعال `service_request_type` باشد؛ `service_request_data`؛ requester/status سروری. POST موفق redirect دارای `request_id` می‌دهد؛ GET نتیجه فقط رکورد Student جاری را نشان می‌دهد. مدل timestamp ندارد؛ اطلاعات به سامانهٔ بیرونی ارسال نشده است. |
| `education-certificate` (Shahsvand) | `/api/portal/pages/education-certificate/` | همان دو key درخواست؛ `service_request_kind` اجباری و فقط Constant فعال `employment_certificate`، آن هم وقتی در DB وجود داشته باشد. POST موفق با `request_id` redirect می‌کند؛ GET نتیجه فقط درخواست مالک را نشان می‌دهد. این POST درخواست است، صدور رسمی نیست. |
| `internship` (Shahsvand) | `/api/portal/pages/internship/` | `request_type` اجباری و باید lookup فعال `internship_request_type` باشد؛ `company_name`, `intern_start_date`, `duration_hours`; duration بیشتر از صفر، Student/status سروری. پس از ثبت موفق، redirect query شامل `request_id` رکورد ساخته‌شده است؛ GET نتیجه را فقط در scope Student مجاز می‌یابد و ثبت محلی را ارسال به دانشگاه معرفی نمی‌کند. |
| `support` (Miri) | `/api/portal/pages/support/` | `category`, `subject`, `content`; category فعال، creator از account session؛ Student الزامی نیست. POST موفق redirect JSON دارای `request_id` می‌دهد؛ GET نتیجه فقط Ticket ریشهٔ همان creator را می‌خواند و کد/status/time واقعی را نشان می‌دهد. فایل پیوست در مدل/این API پشتیبانی نمی‌شود و ثبت محلی تأیید تحویل agent نیست. |
| `notifications` (Miri) | `/api/portal/pages/notifications/` | GET query اختیاری `notification_type=<Constant.code>`؛ گزینه/count فقط از اعلان‌های حساب جاری. POST `notification_id`; فقط Notification متعلق به `request.user` mark-read می‌شود و فیلتر انتخاب‌شده حفظ می‌شود. |
| `announcements` (Miri) | `/api/portal/pages/announcements/` | `communication_id`; فقط Communication دریافتی با type=`announcement` متعلق به receiver حساب جاری mark-read می‌شود. `notification_id` ورودی سازگاری است. |
| ثبت درس (Shaghayegh) | `/api/enrollment/register/<offering_id>/` | body خالی یا `student_code` متعلق به حساب؛ شناسهٔ path، رکورد Offering است. |
| حذف درس (Shaghayegh) | `/api/enrollment/drop/<enrollment_id>/` | body خالی یا `student_code` متعلق به حساب؛ شناسهٔ path، enrollment متعلق به همان Student است. |
| حذف اضطراری (Shaghayegh) | `/api/enrollment/emergency-drop/<enrollment_id>/` | همان مالکیت/role؛ فقط پنجرهٔ emergency-drop، نه پنجرهٔ عادی add/drop. |

`graduation`, `graduation-certificate`, `secure-payment` و همهٔ صفحه‌های read-only POST کاربردی ندارند؛ پاسخ 405 برمی‌گردد. Graduation و graduation-certificate به علت نبود نوع lookup معتبر write-disabled هستند؛ هیچ `certificate` نامرتبطی جایگزین نمی‌شود. تمام صفحه‌های دیگر read-only نیز از GET همان API صفحه استفاده می‌کنند. فرم invalid، HTML خطا و `400 validation_error` می‌دهد؛ پس از موفقیت page API redirect را در JSON برمی‌گرداند تا مرورگر دوباره load کند. نتیجه‌های POST با `request_id` فقط از رکورد مجاز و متعلق به همان کاربر/پرونده ساخته می‌شوند؛ این شامل تیکت ذخیره‌شده است، اما تحویل پشتیبانی، پرداخت بانکی یا صدور رسمی گواهی را ادعا نمی‌کند.

### React UI API (مهاجرت تدریجی)

`GET /api/portal/ui/pages/<slug>/` داده را از همان `PortalView.context` و selectorهای فعلی می‌سازد و فقط shell، فرم و کلیدهای page-data ثبت‌شده در `apps/core/frontend/react_payloads.py` را برمی‌گرداند. Serializer بازگشتی دلخواه مدل‌ها ندارد: کلیدهای page-data خارج از adapter وارد پاسخ نمی‌شوند؛ اگر مقدار یک کلید allowlist‌شده مدل یا نوع پشتیبانی‌نشده باشد، مقدار حذف و نام کلید در `omitted_fields` ثبت می‌شود. این قرارداد در طول مهاجرت با adapterهای مشخص هر صفحه گسترش می‌یابد؛ تا وقتی کلیدهای لازم صفحه کامل نشده‌اند، route روی UI قدیمی می‌ماند.

برای پاسخ JSON خطای اعتبارسنجی از POST موجود، React هدر `Accept: application/vnd.amoozeshyar.react+json` می‌فرستد؛ پاسخ 400 شامل `{error:{code,message}, form:{fields,non_field_errors}}` است. بدون این media type، پاسخ HTML legacy تغییر نمی‌کند. همهٔ POSTها همچنان CSRF، فرم Django، مالکیت پرونده و اعتبارسنجی سمت سرور را رعایت می‌کنند.

### نمونهٔ درخواست و پاسخ

شناسه‌ها و مقدارهای این مثال‌ها قراردادی‌اند و به دادهٔ واقعی/seed اشاره ندارند. `html` در پاسخ GET، خروجی کامل template همان صفحه است و اینجا برای خوانایی کوتاه شده است.

**CSRF، ورود و بازیابی نشست:**

```http
GET /api/accounts/csrf/
Accept: application/json
```

```json
{"csrf_token":"<csrf-token>"}
```

```http
POST /api/accounts/login/
Content-Type: application/json
X-CSRFToken: <csrf-token>

{"username":"S10001","password":"<user-provided-password>","remember_me":true}
```

پاسخ ورود موفق HTTP 200 شامل `{"user":{"id":12,"username":"S10001","full_name":"نام نمونه","roles":["student"]}}` است. پس از login، CSRF در Django چرخش می‌کند؛ هر write بعدی باید token تازه را دریافت کند. `GET /api/accounts/me/` همین ساختار user را در نشست فعلی برمی‌گرداند.

**خواندن کارنامه:**

```http
GET /api/portal/pages/transcript/?student_code=S10001&term=TERM-1
Accept: application/json
Cookie: sessionid=<session>
```

```json
{
  "page": "transcript",
  "html": "<section class=\"panel transcript-summary-panel\">…</section>",
  "profile": {"student_code": "S10001"},
  "term": {"term_code": "TERM-1", "display_label": "1405"}
}
```

**ثبت اعتراض برای enrollment دارای نمره:**

```http
POST /api/portal/pages/grade-appeal/?student_code=S10001&term=TERM-1
Content-Type: application/json
X-CSRFToken: <csrf-token>
Cookie: sessionid=<session>; csrftoken=<csrf-token>

{"enrollment": 31, "appeal_reason": "لطفاً نمره بررسی شود"}
```

```json
{"redirect": "/portal/grade-appeal/?student_code=S10001&term=TERM-1"}
```

در صورت enrollment نامعتبر/بی‌نمره یا ورودی ناقص، پاسخ `400` با `error.code=validation_error` و HTML فرم دارای خطا می‌آید؛ اگر `student_code` متعلق به session نباشد، پاسخ `403 permission_denied` است.

**خواندن ارائه‌های یک نیمسال و ثبت واقعی offering:**

```http
GET /api/scheduling/offerings/?term=TERM-1
Accept: application/json
Cookie: sessionid=<session>
```

```json
{
  "offerings": [{
    "id": 27, "term_id": 4, "lesson_code": "C-101", "title": "عنوان درس",
    "theory_units": 2, "practical_units": 0, "total_units": 2,
    "teacher": "استاد نمونه", "day_of_week": "saturday",
    "start_time": "08:00:00", "end_time": "10:00:00",
    "classroom": "ساختمان ۱ / ۱۰۱", "capacity": 30,
    "remaining_capacity": 4, "exam_date": null, "exam_time": null
  }]
}
```

```http
POST /api/enrollment/register/27/
Content-Type: application/json
X-CSRFToken: <csrf-token>
Cookie: sessionid=<session>; csrftoken=<csrf-token>

{"student_code": "S10001"}
```

پاسخ موفق شامل `enrollment:{id,student_code,offering_id,lesson_code,lesson_title,status,enrollment_date,drop_date}` است؛ status HTTP بسته به ثبت جدید/تکراری `201` یا `200` است. ظرفیت/بازه/پیش‌نیاز/تداخل و مالکیت در service دامنه بررسی می‌شوند، نه در مثال UI.

حذف نیز با `POST /api/enrollment/drop/31/`، CSRF و body اختیاری `{"student_code":"S10001"}` انجام می‌شود؛ موفقیت HTTP 200 همان envelope `enrollment` را با وضعیت و `drop_date` به‌روز می‌دهد. خارج از بازه پاسخ `400` با `error.code=drop_window_closed` است؛ شناسهٔ ثبت‌نام شخص دیگر `403` می‌گیرد.

**ثبت اعلان به‌عنوان خوانده‌شده:**

```http
POST /api/portal/pages/notifications/
Content-Type: application/json
X-CSRFToken: <csrf-token>
Cookie: sessionid=<session>; csrftoken=<csrf-token>

{"notification_id": 42}
```

```json
{"redirect": "/portal/notifications/"}
```

همین payload برای اعلان متعلق به حساب دیگر پذیرفته نمی‌شود؛ API فقط رکورد متعلق به session را تغییر می‌دهد.

**علامت‌گذاری اطلاعیهٔ استاد به‌عنوان خوانده‌شده:**

```http
POST /api/portal/pages/announcements/
Content-Type: application/json
X-CSRFToken: <csrf-token>
Cookie: sessionid=<session>; csrftoken=<csrf-token>

{"communication_id": 73}
```

```json
{"redirect": "/portal/announcements/"}
```

شناسه باید متعلق به Communication دریافتی حساب جاری و نوع آن `announcement` باشد؛ رکورد خوانده می‌شود، `read_at` ثبت و status فعال `read` نیز در صورت وجود تنظیم می‌شود. رکورد نوع دیگر یا حساب دیگر `404` می‌گیرد. برای سازگاری، `notification_id` قدیمی هم در این route پذیرفته می‌شود. Communication به course/term FK ندارد.

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
