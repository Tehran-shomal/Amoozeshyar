# ماتریس صفحه، مالکیت و API

در جدول، «API صفحه» یعنی `GET /api/portal/pages/<slug>/` با session احرازشده؛ همان پاسخ HTML را از template موجود می‌سازد. POST فقط در ردیف‌هایی عمل می‌کند که فرم/کنترل نوشته‌شده در ستون آخر وجود دارد. قرارداد دقیق envelope، CSRF و خطاها در [API_CONTRACTS.md](API_CONTRACTS.md) است. URLهای مرورگر صفحه‌ها `/portal/<slug>/` هستند.

| slug | مالک ثبت‌شده در registry | template / selector | مدل‌ها و دادهٔ اصلی | Read / write واقعی |
|---|---|---|---|---|
| `enrollment` | Mobina | `mobina/enrollment.html` / `mobina.selectors.build` | Student, Term, Field, Constant | API صفحه؛ لینک مرحله بعد؛ انتخاب درس از صفحهٔ بعدی، نه ثبت mutation در این فرم. |
| `selected-courses` | Mobina | `mobina/selected_courses.html` / همان selector | Enrollment, CourseOffering, Lesson, Student | API صفحه + `GET /api/scheduling/offerings/`; انتخاب از `POST /api/enrollment/register/<offering_id>/`; حذف فعال از `POST /api/enrollment/drop/<enrollment_id>/`. |
| `curriculum` | Mobina | `core/live_content.html` / Mobina | Curriculum, Lesson, Constant | API صفحه فقط خواندن؛ فرم/write ندارد. |
| `add-drop` | Shaghayegh | `shaghayegh/course_changes.html` / `shaghayegh.selectors.build` | Enrollment, CourseOffering, Lesson, Student | API صفحه + offerings API؛ حذف با مودال و `POST /api/enrollment/drop/<id>/`; لینک به enrollment برای افزودن. |
| `emergency-drop` | Shaghayegh | همان template و selector | Enrollment, Term, Student | API صفحه + حذف با همان endpoint؛ service بازهٔ emergency یا add/drop را می‌پذیرد. |
| `registration-status` | Shaghayegh | `core/live_content.html` / Shaghayegh | Enrollment, CourseOffering, Term | API صفحه فقط خواندن؛ فرم ندارد. |
| `grade-appeal` | Shaghayegh | `core/live_content.html` / Shaghayegh | GradeAppeal, Enrollment, Constant | API صفحه؛ POST فرم اعتراض (درس، دلیل)؛ مالکیت enrollment، وضعیت اولیه و تاریخ در سمت سرور. |
| `evaluation` | Shahsavand | `core/live_content.html` / `academic_services.selectors` | TeacherSurvey, Enrollment, Teacher, Lesson | API صفحه و POST فرم ارزشیابی؛ ثبت تکراری برای enrollment رد می‌شود. |
| `evaluation-form` | Shahsavand | `core/live_content.html` / همان | TeacherSurvey, Enrollment | همان داده/فرم ارزشیابی؛ slug پنهان منویی است و فرم مستقل چندمرحله‌ای اثبات نشده است. |
| `messages` | Shahsavand | `core/live_content.html` / همان | Communication, UserAccount, Person, Enrollment | API صفحه + POST فرم استاد/موضوع/متن؛ گیرنده به استاد مرتبط با enrollmentهای خود محدود می‌شود. |
| `guest-request` | Shahsavand | `core/live_content.html` / همان | TransferRequest, Student, Constant | API صفحه + POST مقصد دانشگاه؛ مالک Student و وضعیت از سرور. |
| `graduation` | Shahsavand | `core/live_content.html` / همان | GraduationAudit, StudentServiceRequest, Constant | API صفحه + POST درخواست review در مدل StudentServiceRequest؛ پاسخ درخواست، تأیید رسمی فارغ‌التحصیلی نیست. |
| `academic-activities` | Omid | `academic_services/academic_activities.html` / academic services | Enrollment, EducationalChangeLog, Student, Term | API صفحه فقط خواندن؛ لینک به برنامه/حضور/کارت/تقویم. |
| `transcript` | Omid | `academic_services/transcript.html` / همان | Grade, Enrollment, Lesson, Student | API صفحه فقط خواندن؛ معدل/واحدهای تجمیعی و نمره‌های موجود. |
| `attendance` | Omid | `core/live_content.html` / همان | Attendance, Enrollment, Lesson, Constant | API صفحه فقط خواندن؛ هیچ endpoint ثبت حضور برای کارمند در این route وجود ندارد. |
| `exam-card` | Omid | `academic_services/exam_card.html` / همان | Enrollment, CourseOffering, Exam, TeacherSurvey, Payment/Student fields | API صفحه؛ چاپ مرورگر موجود؛ شماره صندلی/صدور رسمی در مدل موجود نیست. |
| `requests` | Omid | `core/live_content.html` / همان | StudentServiceRequest, Constant | API صفحه + POST فرم درخواست عمومی با دو فیلد مدل موجود. |
| `education-certificate` | Omid | `core/live_content.html` / همان | StudentServiceRequest, Constant | API صفحه + POST همان نوع درخواست certificate؛ صدور فایل رسمی انجام نمی‌شود. |
| `graduation-certificate` | Omid | `core/live_content.html` / همان | StudentServiceRequest, Constant | API صفحه + POST همان مدل/نوع certificate؛ وضعیت صدور رسمی در این checkout نیست. |
| `student-card` | Omid | `academic_services/student_card.html` / همان | Person, Student, Field, Term | API صفحه و چاپ؛ سریال/اعتبار یا کارت رسمیِ ثبت‌نشده جعل نمی‌شود. |
| `guide` | Omid | `core/live_content.html` / همان | محتوای ثابت/notice | API صفحه؛ برای حساب بدون پرونده هم در PortalView مجاز به render است؛ write ندارد. |
| `support` | Omid | `core/live_content.html` / همان | Ticket, TicketCategory, Person, Constant | API صفحه + POST ساخت Ticket؛ category از گزینه‌های فعال و creator از session می‌آید. |
| `payments` | Parsa | `parsa/finance.html` / `parsa.selectors.build` | Payment, Term, Student, Constant | API صفحه فقط خواندن؛ paymentها برای دانشجوی جاری/نیمسال انتخابی؛ تکرار پرداخت واقعی ندارد. |
| `secure-payment` | Parsa | `parsa/finance.html` / همان | Student, Payment | API صفحه فقط خواندن؛ پیام صریحِ نبود gateway؛ هیچ مبلغ/تراکنشی ثبت نمی‌کند. |
| `financial-aid` | Parsa | `parsa/finance.html` / همان | ScholarshipApplication, Student, Constant | API صفحه + POST فرم نوع/دلیل؛ مبلغ، حساب یا پیوست مدل نشده است. |
| `tuition` | Parsa | `parsa/finance.html` / همان | Payment, Term, Student | API صفحه فقط خواندن؛ جمع پرداخت‌های موفق واقعی هر نیمسال و بدهی پرونده. |
| `internship` | Niousha/Pouya (گروه مشترک) | `core/live_content.html` / `neyousha_pouya.selectors` | Internship, Student, Constant, UserAccount | API صفحه + POST شرکت/شروع/مدت/نوع؛ مدت باید بیشتر از صفر و status/owner سروری است. |
| `notifications` | Niousha/Pouya | `neyousha_pouya/notifications.html` / همان | Notification, UserAccount, Person | API صفحه؛ POST با `notification_id` فقط اعلان متعلق به همان Person را خوانده علامت می‌زند. |
| `announcements` | Niousha/Pouya | `neyousha_pouya/notifications.html` / همان | Notification, UserAccount, Person | همان selector اعلان؛ write فقط mark-read در مالکیت جاری، نه انتشار اطلاعیه. |
| `calendar` | Niousha/Pouya | `core/live_content.html` / همان | Term dates | API صفحه فقط خواندن بازه‌های Term؛ تقویم رویدادِ مستقل در مدل نیست. |
| `schedule` | Niousha/Pouya | `core/live_content.html` / همان | Enrollment, CourseOffering, Lesson, Teacher, Classroom | API صفحه و چاپ؛ فقط ثبت‌نام فعال نیمسال جاری. |
| `settings` | Niousha/Pouya | `core/live_content.html` / همان | Person, Constant | API صفحه + POST تغییر email/address/notification/language برای `request.user`. |

## صفحه‌ها و اجزای مشترک

| سطح | مالک/فایل | URL/API | داده، مجوز و قابلیت |
|---|---|---|---|
| ورود | Mobina؛ `mobina/login.html`, `LoginPreviewView`, `mobina/static/mobina/section.js` | `/login/`; `POST /api/accounts/login/` | Person/UserAccount/Role؛ فرم fallback HTML و API؛ CSRF، lockout و session. بازیابی گذرواژهٔ محلی پیاده نیست. |
| داشبورد | Mobina؛ `mobina/home.html`, `mobina.selectors.dashboard` | `/`; `GET /api/portal/pages/home/` | پروفایل متعلق، کلاس‌های فعال، اعلان‌های همان حساب، بدهی و پرداخت واقعی؛ POST ندارد. |
| انتخاب نیمسال | لید مشترک Niousha/Pouya؛ `portal_base.html`, `live_portal.js` | query `?term=<term_code>` و API صفحه؛ `GET /api/scheduling/active-term/` وضعیت فعال | picker فقط رکوردهای Term را می‌گیرد؛ code کامل در URL می‌ماند و برچسب کوتاه نمایشی است؛ route مستقل ندارد. |
| منو/پوسته | registry و metadata مشترک | `GET /`, `/portal/<slug>/` | پنج گروه منو و جست‌وجوی client-side؛ session لازم؛ مالکیت/صفحه از registry کنترل می‌شود. |

## آزمون در برابر پوشش واقعی

- `apps/core/test_frontend.py` صفحه‌های registry را به‌صورت عمومی render/API-read smoke می‌کند و مالکیت پروفایل، session، POST نامعتبر و مسیر notification را می‌سنجد؛ این به معنی تست اختصاصی هر edge case همهٔ ۳۲ فرم نیست.
- جزئیات ثبت‌نام/حذف، ورود، زمان‌بندی و transition review در چهار suite دامنه‌ای ثبت‌شده در [API_CONTRACTS.md](API_CONTRACTS.md) است.
- قابلیت بیرونی یا صفحه/نتیجهٔ PDF که در این ماتریس write واقعی ندارد «کامل‌شده» محسوب نمی‌شود.
