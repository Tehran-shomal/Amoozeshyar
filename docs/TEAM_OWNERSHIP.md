# تقسیم‌بندی اجرایی جدید هفت‌گانه

این فایل مرجع فعال مالکیت صفحه‌هاست و جایگزین گروه‌بندی پنج‌گانهٔ قدیمی در کد فرانت می‌شود. دسته‌بندی `NAV_GROUPS` در منو، دسته‌بندی محصول است و تغییر نمی‌کند.

## API و پوستهٔ مشترک

- route مرورگر: `/` برای داشبورد، `/portal/<slug>/` برای هر صفحه؛ ورود `/login/`.
- خواندن صفحه: `GET /api/portal/pages/<slug>/`؛ پاسخ JSON شامل HTML صفحه، پروفایل انتخاب‌شده و برچسب نیمسال است.
- ثبت فرم: `POST /api/portal/pages/<slug>/` با session و CSRF هم‌مبدأ. فقط صفحاتی که در جدول write دارند mutation می‌کنند.
- ترم فعال: `GET /api/scheduling/active-term/`; offerings: `GET /api/scheduling/offerings/?term=<term_code>`.
- ثبت/حذف درس: `POST /api/enrollment/register/<offering_id>/`, `POST /api/enrollment/drop/<enrollment_id>/`؛ backend شناسه، بازه و مالکیت را بررسی می‌کند.
- احراز هویت: `POST /api/accounts/login/`, `GET /api/accounts/me/`, `POST /api/accounts/logout/`.
- مسیرهای mutation دارای CSRF هستند. داده فقط از رکوردهای واقعی می‌آید؛ صفحهٔ خالی، provider غایب یا قانون نامعلوم success ساختگی نمی‌گیرد.

## مالکیت و URL تک‌تک صفحه‌ها

| مسئول | صفحه و URL | داده/API و عملیات |
|---|---|---|
| Mobina | ورود — `/login/` | ورود session؛ Accounts API و فرم HTML پشتیبان. |
| Mobina | داشبورد — `/` | `GET /api/portal/pages/home/`; خلاصهٔ پرونده، کلاس، اعلان و مالی؛ فقط خواندن. |
| Mobina | تنظیمات — `/portal/settings/` | صفحه API + `POST` همان route؛ فیلدهای مجاز Person حساب جاری. |
| Mobina | کارت دیجیتال — `/portal/student-card/` | صفحه API؛ چاپ پیش‌نمایش Student؛ کارت رسمی/سریال صادر نمی‌شود. |
| Shaghayegh | انتخاب واحد — `/portal/enrollment/` | صفحه API؛ نمایش پرونده و نیمسال واقعی. |
| Shaghayegh | دروس انتخاب‌شده — `/portal/selected-courses/` | صفحه API + offerings API؛ ثبت/حذف از Enrollment API. |
| Shaghayegh | حذف و اضافه — `/portal/add-drop/` | صفحه API و تأیید حذف؛ حذف از Enrollment API و افزودن از مرحلهٔ انتخاب. |
| Shaghayegh | حذف اضطراری — `/portal/emergency-drop/` | صفحه API و حذف با کنترل backend؛ قاعدهٔ رسمی منبع‌نداشته نامعلوم می‌ماند. |
| Shaghayegh | وضعیت ثبت‌نام — `/portal/registration-status/` | صفحه API؛ ثبت‌نام‌های همان Student و Term. |
| Parsa | سوابق پرداخت — `/portal/payments/` | صفحه API؛ Paymentهای Student و Term، فقط خواندن؛ «گزارش مغایرت» به پشتیبانی عمومی لینک است و Payment dispute مستقل ندارد. |
| Parsa | پرداخت امن — `/portal/secure-payment/` | صفحه API؛ read-only تا اتصال درگاه معتبر؛ پرداخت موفق ثبت نمی‌شود. |
| Parsa | تسهیلات — `/portal/financial-aid/` | صفحه API + `POST` همان route؛ ScholarshipApplication با مالک/status سروری. |
| Parsa | خلاصه شهریه — `/portal/tuition/` | صفحه API؛ بدهی و پرداخت موفق موجود، فقط خواندن. |
| Omid | فعالیت آموزشی — `/portal/academic-activities/` | صفحه API؛ Enrollment و EducationalChangeLog پرونده. |
| Omid | کارنامه — `/portal/transcript/` | صفحه API؛ Gradeهای واقعی ترم و خلاصهٔ Student. |
| Omid | چارت درسی — `/portal/curriculum/` | صفحه API؛ Curriculum فعال رشته، فقط خواندن. |
| Omid | اعتراض نمره — `/portal/grade-appeal/` | صفحه API + `POST`؛ فقط enrollment دارای نمرهٔ ثبت‌شده در پرونده/ترم جاری؛ status/date سروری. |
| Niousha | برنامه — `/portal/schedule/` | صفحه API؛ درس‌های فعال همان پرونده/ترم و چاپ مرورگر. |
| Niousha | تقویم — `/portal/calendar/` | صفحه API؛ تاریخ‌های Term؛ رویداد مستقلِ مدل‌نشده ساخته نمی‌شود. |
| Niousha | حضور و غیاب — `/portal/attendance/` | صفحه API؛ جلسه‌های ثبت‌شده؛ ثبت کارمندی ندارد. |
| Niousha | کارت امتحان — `/portal/exam-card/` | صفحه API؛ امتحان‌های موجود؛ شماره صندلی/صدور رسمی در دسترس نیست. |
| Shahsvand | کارآموزی — `/portal/internship/` | صفحه API + `POST`؛ نوع درخواست فعال، Internship پرونده، مدت مثبت و وضعیت سروری. |
| Shahsvand | مهمانی — `/portal/guest-request/` | صفحه API + `POST`؛ TransferRequest پرونده و وضعیت سروری. |
| Shahsvand | درخواست فارغ‌التحصیلی — `/portal/graduation/` | GET بررسی‌های GraduationAudit؛ نوع درخواست معتبر در lookup موجود نیست، بنابراین POST جدید غیرفعال است. |
| Shahsvand | درخواست عمومی — `/portal/requests/` | صفحه API + `POST`؛ StudentServiceRequest با نوع موجود. |
| Shahsvand | گواهی آموزشی — `/portal/education-certificate/` | صفحه API + `POST` درخواست؛ صدور فایل رسمی provider ندارد. |
| Shahsvand | گواهی دانش‌آموختگی — `/portal/graduation-certificate/` | GET با وضعیت unavailable؛ type lookup و فرایند رسمی موجود نیست، POST غیرفعال است. |
| Miri | ارزشیابی — `/portal/evaluation/` | صفحه API + `POST`؛ enrollmentهای خود دانشجو، امتیاز ۱–۵، جلوگیری از تکرار. |
| Miri | فرم ارزشیابی — `/portal/evaluation-form/` | همان API/form ارزشیابی؛ route پنهان از صفحهٔ والد. |
| Miri | پیام استاد — `/portal/messages/` | صفحه API + `POST`؛ گیرنده محدود به استادهای enrollmentهای خود دانشجو. |
| Miri | اطلاعیه‌ها — `/portal/announcements/` | صفحه API؛ `POST` فقط mark-read حساب جاری؛ انتشار ندارد. |
| Miri | اعلان‌ها — `/portal/notifications/` | صفحه API؛ `POST` فقط mark-read اعلان متعلق به حساب. |
| Miri | راهنما — `/portal/guide/` | صفحه API و topicهای راهنمای عملی با لینک routeهای موجود؛ Q&A رسمی پویا ندارد. |
| Miri | پشتیبانی — `/portal/support/` | صفحه API + `POST`؛ Ticket متعلق به حساب و فهرست همان حساب. |

## نقش، محدودهٔ PDF و فایل‌های مرجع

| عضو | مسئولیت / شماره‌های اشاره‌شده در MASTER | پوشهٔ کد | ارائه و راهنمای گروه |
|---|---|---|---|
| Mobina | ورود، داشبورد، shell مشترک، تنظیمات، کارت دیجیتال؛ صفحات ۱–۳، ۴–۸، ۱۹–۲۰ | `apps/core/frontend/mobina/` | [ارائه](presentation/01_Mobina.md) · [README](../apps/core/frontend/mobina/README.md) |
| Shaghayegh | انتخاب/تغییر درس، ظرفیت، تداخل و تأییدها؛ صفحات ۹–۱۳، ۵۲–۵۹، ۶۸–۹۶ | `apps/core/frontend/shaghayegh/` | [ارائه](presentation/02_Shaghayegh.md) · [README](../apps/core/frontend/shaghayegh/README.md) |
| Parsa | امور مالی؛ از جمله صفحهٔ ۳۰ و ۶۴–۶۶ | `apps/core/frontend/parsa/` | [ارائه](presentation/03_Parsa.md) · [README](../apps/core/frontend/parsa/README.md) |
| Omid | سوابق و پیشرفت؛ از جمله ۲۳ و ۶۰–۶۳ | `apps/core/frontend/omid/` | [ارائه](presentation/04_Omid.md) · [README](../apps/core/frontend/omid/README.md) |
| Niousha | برنامه و کلاس‌ها، Frontend Lead؛ صفحات ۱۴–۱۵ و ۲۱–۲۲ | `apps/core/frontend/niousha/` | [ارائه](presentation/05_Niousha.md) · [README](../apps/core/frontend/niousha/README.md) |
| Shahsvand | درخواست‌ها؛ از جمله صفحات ۲۴–۲۶، ۶۷ و ۷۲ | `apps/core/frontend/shahsvand/` | [ارائه](presentation/06_Shahsvand.md) · [README](../apps/core/frontend/shahsvand/README.md) |
| Miri | ارتباط و خدمات عمومی، Shared Lead؛ از جمله ۱۶–۱۸، ۲۷–۲۹، ۳۱–۳۷ | `apps/core/frontend/miri/` | [ارائه](presentation/07_Miri.md) · [README](../apps/core/frontend/miri/README.md) |

قالب مشترک: `apps/core/templates/core/portal_base.html`, `section.html`, `live_content.html`. API مشترک: `apps/core/frontend/api.py`; مالکیت route: `apps/core/frontend/registry.py`; رفتار fetch و فرم مرورگر: `static/core/portal_api.js`, `live_portal.js`.

## جزئیات screenها و وضعیت

صفحه‌به‌صفحه: [docs/screens](screens/README.md). ماتریس: [SCREEN_API_MATRIX.md](SCREEN_API_MATRIX.md). قرارداد envelope و خطا: [API_CONTRACTS.md](API_CONTRACTS.md). قوانین قطعی/نامعلوم: [BUSINESS_RULES.md](BUSINESS_RULES.md).

فایل PDF مرجع در clone پیدا نشد. [PDF_PAGE_MAPPING.md](PDF_PAGE_MAPPING.md) شماره‌ها را نگه می‌دارد اما تطبیق تصویری در این فاز تأییدنشده است. اجرای تست و QA طبق درخواست کاربر برای فاز بعد است؛ بنابراین جابه‌جایی مالک به تنهایی به معنی complete نیست.
