# ماتریس صفحه، مالکیت و API — تقسیم‌بندی جدید هفت‌گانه

وضعیت نگاشت هر مسیر به کامپوننت React و API آن در [گزارش مهاجرت React](REACT_PORTAL_MIGRATION.md) دنبال می‌شود؛ این ماتریس همچنان مرجع مالکیت و قرارداد دادهٔ صفحات است.

`API صفحه` در این ماتریس همان boundary عمومی هم‌مبدأ است: `GET|POST /api/portal/pages/<slug>/` با session و CSRF برای POST. GET پاسخ HTML صفحه را داخل JSON می‌دهد؛ POST فقط وقتی mutation می‌کند که فرم یا action مشخصی در ستون عملیات وجود داشته باشد. قرارداد کامل envelope، ورودی، status و خطا در [API_CONTRACTS.md](API_CONTRACTS.md) آمده است. URLهای مرورگر مطابق مسیرهای canonical هستند.

| slug | URL مرورگر | مالک جدید | قالب / selector | read و write واقعی |
|---|---|---|---|---|
| `enrollment` | `/portal/enrollment/` | Shaghayegh | `shaghayegh/enrollment.html` / `shaghayegh.selectors` | GET پرونده و ترم؛ بدون mutation. |
| `selected-courses` | `/portal/selected-courses/` | Shaghayegh | `shaghayegh/selected_courses.html` / همان | GET ثبت‌نام‌های فعال؛ GET offerings در modal گروه‌بندی‌شده بر اساس درس؛ ثبت گروه انتخابی با `POST /api/enrollment/register/<offering_id>/`. شمارهٔ گروه/تعرفه در مدل نیست. خطای واقعی `tuition_debt` modal صفحهٔ ۳۰ را باز می‌کند؛ مبلغ و حداکثر از پرونده‌اند، حداقل واحد تعریف نشده و پرداخت آنلاین درگاه ندارد. |
| `curriculum` | `/portal/curriculum/` | Omid | `omid/curriculum.html` / `omid.selectors` | GET چارت فعال رشته، پیش‌نیازهای تعریف‌شده و progress از Grade قبولی/Enrollment فعال همان دانشجو؛ فقط خواندن. |
| `add-drop` | `/portal/add-drop/` | Shaghayegh | `shaghayegh/course_changes.html` / selector شقایق | GET ثبت‌نام فعال با lesson/units/teacher/schedule/exam/status و فهرست offers از scheduling API؛ افزودن با `POST /api/enrollment/register/<offering_id>/` و حذف با `POST /api/enrollment/drop/<enrollment_id>/`; نتیجهٔ افزودن با `created` و `registration_id` فقط برای Enrollment فعال/مالک نمایش داده می‌شود؛ نتیجهٔ حذف با شناسهٔ رکورد حذف‌شده در همان scope خوانده می‌شود؛ بازپرداخت محاسبه/ثبت نمی‌شود. |
| `emergency-drop` | `/portal/emergency-drop/` | Shaghayegh | همان قالب/selector | GET ثبت‌نام؛ حذف از `POST /api/enrollment/emergency-drop/<id>/` که فقط پنجرهٔ emergency را می‌پذیرد و مالکیت backend را کنترل می‌کند؛ نتیجه فقط با ID رکورد dropped در scope Student/Term. حذف بازپرداخت ثبت نمی‌کند و حداقل واحد/قاعدهٔ رسمی unknown می‌ماند. |
| `registration-status` | `/portal/registration-status/` | Shaghayegh | `shaghayegh/registration_status.html` / selector شقایق | GET summary چهارمرحله‌ای؛ Enrollment فعال/واحد، بدهی Student و سقف واقعی. approval نهایی یا رسید پرداخت مدل نشده و وضعیت نامشخص اعلام می‌شود. |
| `grade-appeal` | `/portal/grade-appeal/` | Omid | `core/live_content.html` / `omid.selectors` | GET/POST صفحه؛ `GradeAppealForm` فقط enrollment متعلق به Student/Term که Grade دارای score دارد؛ status/date سروری؛ نتیجه با `request_id` به appeal همان پرونده/ترم وصل است و تغییر نمره را ادعا نمی‌کند. هشدار می‌دهد مهلت در API کنترل و فایل پیوست پشتیبانی نمی‌شود. |
| `evaluation` | `/portal/evaluation/` | Miri | `miri/evaluation.html` / `miri.selectors` | GET وضعیت survey برای enrollmentهای فعال پرونده/ترم؛ لینک درس‌های باز به فرم مختص همان enrollment؛ هر rating ۱–۵؛ survey به enrollment FK دارد، ناشناس‌بودن تضمین نیست. |
| `evaluation-form` | `/portal/evaluation-form/` (پنهان از منو) | Miri | `miri/evaluation_form.html` / `SurveyForm` | GET/POST پنج rating مستقل ۱–۵ و نظر اختیاری؛ فقط enrollment فعال همان پرونده/ترم؛ ثبت نهایی read-only و duplicate/foreign enrollment رد می‌شود. |
| `messages` | `/portal/messages/` | Miri | `miri/messages.html` / `miri.selectors` | GET استادهای Enrollment فعال همان Term و Communicationهای حساب؛ POST پیام به UserAccount فعال همان استاد/ترم؛ نتیجهٔ `request_id` فقط پیام ارسالی حساب جاری را می‌خواند؛ thread/delivery خارجی تضمین نشده است. |
| `guest-request` | `/portal/guest-request/` | Shahsvand | `shahsvand/guest_request.html` / `shahsvand.selectors` | GET/POST `TransferRequest`; فقط مقصد از client، تاریخچه و نتیجهٔ `request_id` owner-scoped و وضعیت review سروری؛ تأیید نهایی همچنان نیازمند review است و فیلدهای دیگر PDF در schema نیستند. |
| `graduation` | `/portal/graduation/` | Shahsvand | `shahsvand/graduation.html` / `shahsvand.selectors` | GET اطلاعات پرونده و GraduationAudit متعلق؛ POST=405 تا تعریف lookup معتبر؛ آستانهٔ GPA، کتابخانه و timeline فاقد منبع می‌مانند. |
| `academic-activities` | `/portal/academic-activities/` | Omid | `omid/academic_activities.html` / `omid.selectors` | GET enrollmentهای فعال همان Student/Term، حداکثر ۸ EducationalChangeLog همان Student، و چهار لینک داخلی. مدل log فاقد term FK است؛ تاریخچه را نمی‌توان برای term انتخاب‌شده جدا کرد. |
| `transcript` | `/portal/transcript/` | Omid | `omid/transcript.html` / selector امید | GET همهٔ Enrollmentهای فعال Student/Term با Lesson/units/status و آخرین Grade.score ثبت‌شده؛ درس بی‌نمره باقی می‌ماند. schema میان‌ترم/پایان‌ترم و معدل اختصاصی term ندارد؛ summary از current units و فیلدهای کل Student می‌آید؛ لینک اعتراض/چارت و چاپ. |
| `attendance` | `/portal/attendance/` | Niousha | `niousha/attendance.html` / `niousha.selectors` | GET Attendance برای enrollmentهای فعال پرونده/ترم؛ خلاصهٔ per-course؛ endpoint ثبت حضور کارمندی ندارد. |
| `exam-card` | `/portal/exam-card/` | Niousha | `niousha/exam_card.html` / selector نیوشا | GET درس‌ها/زمان‌های امتحان؛ seat number و صدور رسمی در مدل/provider نیست. |
| `requests` | `/portal/requests/` | Shahsvand | `core/live_content.html` / `shahsvand.selectors` | GET/POST `StudentServiceRequest`; lookup از Constant موجود و مالک/status سروری؛ notice نبود phone/attachment و ثبت محلی؛ نتیجه با `request_id` owner-scoped است و ارسال بیرونی را ادعا نمی‌کند. |
| `education-certificate` | `/portal/education-certificate/` | Shahsvand | `core/live_content.html` / `shahsvand.selectors` | GET/POST درخواست `employment_certificate` فقط با Constant فعال؛ notice نبود مخاطب/تعداد نسخه/روش تحویل و صدور؛ نتیجهٔ `request_id` owner-scoped است؛ صدور فایل رسمی خارج از API است. |
| `graduation-certificate` | `/portal/graduation-certificate/` | Shahsvand | `shahsvand/graduation_certificate.html` / `shahsvand.selectors` | GET read-only از Student/Curriculum/GraduationAudit و workflow توضیحی؛ پیوند graduation/curriculum؛ lookup نوع درخواست و provider صدور موجود نیست، POST غیرفعال است. |
| `student-card` | `/portal/student-card/` | Mobina | `mobina/student_card.html` / selector مبینا | GET اطلاعات Student واقعی و چاپ preview؛ serial/اعتبار رسمی تولید نمی‌شود. |
| `guide` | `/portal/guide/` | Miri | `miri/guide.html` / `miri.selectors` | GET راهنمای عملی با پیوندهای واقعی به routeها؛ Q&A رسمی یا write ندارد. |
| `support` | `/portal/support/` | Miri | `miri/support.html` / `miri.selectors` | GET root-ticketهای حساب جاری + reply آخر؛ POST JSON برای category فعال/subject/content، creator از session و status از lookup فعال `open`. موفقیت با `request_id` به Ticket مالک‌محور می‌رسد؛ پیوست، تحویل بیرونی و پاسخ agent از این صفحه پشتیبانی نمی‌شوند. |
| `payments` | `/portal/payments/` | Parsa | `parsa/finance.html` / `parsa.selectors` | GET Payment همان Student و Term؛ پرداخت/تکرار تراکنش ندارد. لینک مغایرت فقط فرم عمومی پشتیبانی را باز می‌کند؛ dispute مستقل مدل/API نشده. |
| `secure-payment` | `/portal/secure-payment/` | Parsa | همان | GET ماندهٔ Student، نام پرداخت‌کننده و شرح کلی؛ gateway وصل نیست، ادامه disabled و هیچ mutation یا pending Payment ندارد؛ لینک سوابق. |
| `financial-aid` | `/portal/financial-aid/` | Parsa | همان | GET/POST ScholarshipApplication متعلق به Student؛ فقط type/reason، owner و pending status سمت سرور؛ هشدار نبود amount/IBAN/attachment و عدم تأیید/پرداخت؛ نتیجه با `request_id` owner-scoped. |
| `tuition` | `/portal/tuition/` | Parsa | همان | GET بدهی Student و جمع Paymentهای successful هر term؛ تعرفه/line-item ثابت و متغیر در schema نیست؛ هشدار، لینک secure-payment disabled و payments دارد؛ فقط خواندن. |
| `internship` | `/portal/internship/` | Shahsvand | `shahsvand/internship.html` / `shahsvand.selectors` | GET/POST Internship؛ نوع از lookup فعال، duration مثبت، تاریخچه و نتیجهٔ `request_id` owner-scoped و owner/status سروری است؛ نتیجه ثبت داخلی را از ارسال دانشگاهی جدا می‌کند؛ استاد ناظر/تماس/نامه در schema نیست. |
| `notifications` | `/portal/notifications/` | Miri | `miri/notifications.html` / `miri.selectors` | GET اعلان‌های حساب با شمار فیلترهای `notification_type` واقعی؛ query اختیاری `notification_type`; POST فقط mark-read همان Notification متعلق به حساب. |
| `announcements` | `/portal/announcements/` | Miri | `miri/announcements.html` / `miri.selectors` | GET Communicationهای نوع announcement دریافتی حساب جاری؛ POST با `communication_id` فقط همان رکورد را read می‌کند. course/term link در مدل نیست؛ انتشار اطلاعیه در این UI/API نیست. |
| `calendar` | `/portal/calendar/` | Niousha | `niousha/calendar.html` / `niousha.selectors` | GET بازه‌های Term، امتحان CourseOffering و جلسات Attendance از enrollmentهای فعال همان دانشجو/ترم؛ تبدیل نمایش به شمسی؛ read-only. مناسبت عمومی و deadline شهریه مدل نشده‌اند. |
| `schedule` | `/portal/schedule/` | Niousha | `niousha/schedule.html` / `niousha.selectors` | GET Enrollment فعال، روز/ساعت/درس/استاد/کلاس و شمار واحد واقعی؛ شبکهٔ هفتگی و تشخیص overlap؛ چاپ مرورگر. |
| `settings` | `/portal/settings/` | Mobina | `mobina/settings.html` / `mobina.selectors` + `SettingsForm` | GET/POST Person حساب جاری؛ فیلدهای مجاز email/address/notification/language؛ نتیجهٔ `settings_saved=1` مقادیر ذخیره‌شده را نشان می‌دهد؛ فیلد اعلان فقط ذخیره می‌شود و اعمال نمی‌شود؛ phone، channel preferences و delivery provider خارج از پیاده‌سازی‌اند. |

## صفحه‌ها و اجزای غیر route

| مورد | URL/API و مالک | داده/محدودیت |
|---|---|---|
| ورود | Mobina؛ `/login/`, `POST /api/accounts/login/` | Person/UserAccount؛ CSRF، session و lockout؛ HTML fallback هم وجود دارد. |
| خروج/نشست | Mobina/shared; `GET /api/accounts/me/`, `POST /api/accounts/logout/` | احراز هویت session-based؛ POST با CSRF. |
| داشبورد | Mobina؛ `/`, `GET /api/portal/pages/home/` | خلاصهٔ پرونده، کلاس، اعلان و دادهٔ مالی واقعی؛ read-only. |
| انتخاب نیمسال | Niousha shared lead؛ dialog پوسته و `GET /api/scheduling/active-term/` | گزینه‌ها از Termهای ذخیره‌شده؛ query `term` صفحه را مشخص می‌کند. |
| منو و shell | مشترک؛ `portal_base.html`, `live_portal.js` | `NAV_GROUPS` فقط دسته‌بندی محصول است، نه مالک تیمی. |
| modalهای ثبت/حذف | Shaghayegh؛ screen docs `course-selection-dialog`, `course-group-dialog`, `drop-confirmation`, `emergency-drop-confirmation` | حالت‌های همان route؛ هر mutation به API واقعی دامنه وصل است. |

## مالکیت و شواهد

هفت گروه، صفحه‌های زیرمجموعه، مسیر README/ارائه و صفحه‌های PDF درج‌شده در [TEAM_OWNERSHIP.md](TEAM_OWNERSHIP.md) آمده‌اند. پوشش screen docs در [docs/screens/README.md](screens/README.md) است.

- دسترسی صفحه‌ها به session نیاز دارد؛ ورودی `student_code` فقط پروفایل متعلق به کاربر را می‌پذیرد. فرم‌های `OwnedModelForm` مالک و وضعیت اولیه را از server تعیین می‌کنند.
- Error envelope، methodها و payloadهای API صفحه در [API_CONTRACTS.md](API_CONTRACTS.md) است. APIهایی که از provider واقعی استفاده نمی‌کنند در جدول read-only/unavailable علامت خورده‌اند.
- تست‌های فعلی در فاز بعد اجرا و گزارش می‌شوند؛ این تغییر فعلاً نباید به‌عنوان evidence آزمون تلقی شود.
> React page-to-component coverage and current migration status: [REACT_PORTAL_MIGRATION.md](REACT_PORTAL_MIGRATION.md). This supplements the route/API ownership matrix below; it does not imply visual approval.
