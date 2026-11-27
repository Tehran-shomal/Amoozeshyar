# نگاشت canonical صفحات Amoozeshyar.pdf

فایل `Amoozeshyar.pdf` در مسیر محلی `C:\Users\repair\Downloads\Amoozeshyar.pdf` موجود است؛ PNG مرجع همهٔ صفحات ۱–۹۶ در `docs/screens/page-NN-reference.png` ذخیره‌اند. بازبینی سورس/API به‌ترتیب صفحه‌ها ادامه دارد؛ stateهای crop/menu/modal به route والد یا «بازنمایی‌نشده» نگاشت می‌شوند. screenshotهای قدیمی متعلق به نسخهٔ قبل از بازتخصیص گروه‌ها هستند و شاهد UI جاری محسوب نمی‌شوند. هیچ statusی به‌معنی تطبیق پیکسلی کامل یا پذیرش responsive نیست.

وضعیت‌ها: **route موجود**، **جزء مشترک**، **state بخشی**، **بازنمایی‌نشده**. مالکیت جاری را [TEAM_OWNERSHIP.md](TEAM_OWNERSHIP.md) تعیین می‌کند؛ شرح route در [docs/screens](screens/README.md) و API در [API_CONTRACTS.md](API_CONTRACTS.md) است. PDF بیرون clone می‌ماند؛ تطبیق پیکسلی، همهٔ viewportها و تست‌های workflow پس از تکمیل بازبینی ترتیبی در فاز QA انجام می‌شوند.

## مالک مسئول شماره‌های PDF بر اساس تقسیم جدید

این نگاشت شمارهٔ PDF را به مالک workflow وصل می‌کند؛ شماره‌های state/modal/result مالک جداگانهٔ endpoint نیستند و از مالک route والد پیروی می‌کنند. نتیجه‌های عمومی عملیات (۳۸–۴۸) مؤلفهٔ مشترک‌اند: Miri هماهنگ‌کنندهٔ مشترک است و مالک عملیات نهایی همان مالک workflow آغازکننده است. صفحات ۴–۸ عنوان گروه‌های محصولی sidebar هستند، نه گروه مالکیت تیمی.

| PDF | مالک مسئول | مبنای تخصیص |
|---|---|---|
| ۱–۲ | Mobina | ورود و داشبورد |
| ۳ | Niousha | انتخاب نیمسال مشترک، تحت هماهنگی Frontend Lead |
| ۴–۸ | Mobina (پوستهٔ مشترک) | رندر sidebar؛ نام گروه‌ها فقط دسته‌بندی محصولی است |
| ۹–۱۳ | Shaghayegh | انتخاب درس و stateهای آن |
| ۱۴–۱۵ | Niousha | حضور و تقویم |
| ۱۶–۱۸ | Miri | اطلاعیه، ارزشیابی و اعلان |
| ۱۹–۲۰ | Mobina | تنظیمات و کارت دانشجویی |
| ۲۱–۲۲ | Niousha | کارت امتحان و برنامهٔ هفتگی |
| ۲۳ | Omid | چارت درسی |
| ۲۴–۲۶ | Shahsvand | کارآموزی، مهمانی و فراغت از تحصیل |
| ۲۷–۲۹ | Miri | پیام، راهنما و پشتیبانی |
| ۳۰ | Shaghayegh | منع ثبت‌نام ناشی از وضعیت مالی در workflow انتخاب واحد |
| ۳۱–۳۷ | Miri | فرم و stateهای ارزشیابی استاد |
| ۳۸–۴۸ | Miri (مؤلفهٔ نتیجهٔ مشترک) | هماهنگی نمایش؛ mutation به مالک workflow route والد تعلق دارد |
| ۴۹ | Miri | کنترل امتیاز ارزشیابی |
| ۵۰–۵۱ | Mobina | تنظیم اعلان و زبان حساب |
| ۵۲–۵۹ | Shaghayegh | مراحل ثبت‌نام، حذف‌واضافه و نتیجه‌های وابسته |
| ۶۰–۶۲ | Omid | اعتراض نمره، فعالیت و کارنامه |
| ۶۳–۶۶ | Parsa | پرداخت، درگاه، تسهیلات و شهریه |
| ۶۷ | Shahsvand | درخواست‌های دانشجویی |
| ۶۸–۷۱ | Shaghayegh | stateهای حذف‌واضافه |
| ۷۲–۷۳ | Shahsvand | گواهی آموزشی و دانش‌آموختگی |
| ۷۴ | Miri | فهرست ارزشیابی |
| ۷۵–۹۶ | Shaghayegh | حالت‌های فهرست حذف اضطراری، مودال انتخاب/جزئیات ارائه، و تأیید حذف عادی/اضطراری |

این انتساب‌ها از موضوع/route موجود و تقسیم مالکیت Master مشتق شده‌اند؛ چون PDF در clone حاضر نیست، تطبیق تصویر به تصویر و هر ابهام در شماره‌گذاری تأیید بصری نشده است.

| PDF | route/جزء و موضوع تصویر | وضعیت در checkout و شاهد |
|---:|---|---|
| 1 | ورود `/login/` | تطبیق فعلی انجام شد؛ ابعاد/جای کارت با مرجع هم‌خوان است و گرادیان دکمه اصلاح شد. کد `POST /api/accounts/login/` بازبینی و GETهای CSRF (۲۰۰) و حساب ناشناس (۴۰۱) بررسی شدند؛ آزمون ورود واقعی و تست خودکار اجرا نشده‌اند. شاهد capture محلی در `docs/screens/login.md` ثبت است. |
| 2 | داشبورد `/` | **بازبینی شد**: template/view/selector و API؛ درخواست ناشناس ۴۰۱ و درخواست احراز‌شدهٔ `GET /api/portal/pages/home/` برابر ۲۰۰. در capture ۱۴۴۰×۹۰۰، هندسهٔ اصلی با PDF ۱۰۸۰×۶۷۵ (مقیاس ۴/۳) هم‌تراز شد؛ grid ردیف پایین و ارتفاع کارت‌ها در `responsive.css` اصلاح شد. شاهد: `%TEMP%\amoozeshyar-dashboard-page02-final.png` و [شرح داشبورد](screens/dashboard.md). تست خودکار اجرا نشده است. |
| 3 | انتخاب نیمسال | **بازبینی شد**: رندر ۷۵۶×۴۴۱ با [مرجع](screens/page-03-reference.png) و [UI](screens/page-03-current.png) مقایسه شد؛ قاب/سایه/× حذف، اندازه و جای دکمه تنظیم، و ترم فعال در ترتیب نمایش اول شد. API: valid 14051/14052 → 200 و query درست؛ invalid → 404 `page_data_not_found`; active-term با session → 200 و ناشناس → 401. DB محلی دو ترم دارد (PDF یکی) و برچسب نیمسال متفاوت است؛ رکوردها دست‌نخورده ماندند. جزئیات در [screen doc](screens/term-picker.md). |
| 4 | گروه منوی «سیستم دروس دانشجو» | [مرجع](screens/page-04-reference.png) و capture تازهٔ route احراز‌شدهٔ `/portal/enrollment/` در [صفحهٔ جاری](screens/page-04-current.png) (۷۵۶×۴۴۱). ۱۳ مقصد به ترتیب PDF و دو کپسول عنوان مطابقت دارند؛ API/route احراز‌شده `200`، ناشناس API `401` و route `302`. تفکیک مالکیت تیمی بدون تغییر مانده است. جزئیات گروه‌ها در [navigation-groups.md](screens/navigation-groups.md). |
| 5 | گروه منوی «خدمات مالی» | [مرجع](screens/page-05-reference.png) و capture تازهٔ route احراز‌شدهٔ `/portal/payments/` در [صفحهٔ جاری](screens/page-05-current.png) (۵۳۲×۲۲۸). چهار مقصد PDF در همان ترتیب و ظاهر دوکپسولی قرار گرفتند؛ چهار API مالی احراز‌شده پیش‌تر `200` داده‌اند؛ ناشناس API `401` و route `302`. رفتار POST اجرا نشده است. جزئیات در [پروندهٔ مالی](screens/financial-services.md). |
| 6 | گروه منوی «درخواست مجوز» | [مرجع](screens/page-06-reference.png) و capture تازهٔ route احراز‌شدهٔ `/portal/requests/` در [صفحهٔ جاری](screens/page-06-current.png) (۵۳۲×۲۷۸). عنوان، پنج مقصد و دو کپسول با PDF همسان شدند؛ پنج route/API احراز‌شده `200` داده‌اند. رفتار POST فقط از source بررسی شد. جزئیات در [پروندهٔ درخواست‌ها](screens/request-permissions-menu.md). |
| 7 | گروه منوی «خدمات دانشجویی» | [مرجع](screens/page-07-reference.png) و capture تازهٔ route احراز‌شدهٔ `/portal/student-card/` در [صفحهٔ جاری](screens/page-07-current.png) (۵۳۲×۲۷۸). گروه جاری دقیقاً پنج مقصد PDF دارد؛ هر پنج route و API احراز‌شده `200` دادند. لینک‌های استادان از گروه سابق خارج شدند. [جزئیات مالکیت و API](screens/student-services-menu.md). |
| 8 | گروه منوی «اساتید» | [مرجع](screens/page-08-reference.png) و capture تازهٔ route احراز‌شدهٔ `/portal/evaluation/` در [صفحهٔ جاری](screens/page-08-current.png) (۵۳۲×۱۷۸). سه مقصد مطابق PDF؛ هر سه route/API احراز‌شده `200` دادند. فرم ارزشیابی `evaluation-form` همچنان route پنهان است. [جزئیات مالکیت و API](screens/faculty-services-menu.md). |
| 9 | دروس انتخاب‌شده | [مرجع](screens/page-09-reference.png) و [UI جاری 1440×900](screens/page-09-current.png)؛ [موبایل 390×844](screens/page-09-mobile-current.png). route و GETهای صفحه، active-term و offerings همگی `200`؛ جدول هفت‌ستونی و خلاصهٔ واحد پیاده‌اند. clone یک درس ثبت‌شده دارد در برابر چهار درس/۱۲ واحد PDF؛ اطلاعات پرونده، بدهی و سقف واحد هم از داده/قواعد clone می‌آیند و با نمونه فرق دارند. تعرفهٔ شهریه موجود نیست و جعل نشده. مقایسهٔ تصویر موجود، عنوان نیم‌عرض منو، دکمه‌های کوچک‌تر (حدود 101/125 در برابر 160/180px) و سایه/گردی اضافهٔ کارت را یافت؛ CSS route-specific اصلاح شد و asset `200` می‌گیرد، اما route بدون نشست به login redirect می‌کند و capture تأییدی تازه نداریم. هیچ داده‌ای تغییر نکرد؛ POST و تست خودکار اجرا نشده‌اند. جزئیات در [screen doc](screens/selected-courses.md). |
| 10 | همان فهرست دروس، state داده‌ای متفاوت | [مرجع](screens/page-10-reference.png)؛ همان route و APIهای صفحهٔ ۹، بنابراین capture جاری [صفحهٔ ۹](screens/page-09-current.png) فقط layout مشترک را نشان می‌دهد، نه state دقیق. PDF پنج درس/۱۵ واحد و «شروع دوباره سناریو» دارد؛ clone یک ثبت فعال دارد و این state جداگانه بازنمایی نشده. |
| 11 | همان فهرست دروس، ارائهٔ پنجم متفاوت | [مرجع](screens/page-11-reference.png)؛ پنج درس/۱۵ واحد و همان خلاصه/route؛ ردیف پنجم نسبت به صفحهٔ ۱۰ تغییر کرده است. clone این مجموعه را ندارد؛ endpoint همان GET صفحهٔ ۹ است و capture جاری فقط layout مشترک را شاهد است. |
| 12 | همان فهرست دروس، درس پنجم متفاوت | [مرجع](screens/page-12-reference.png)؛ پنج درس/۱۵ واحد، ردیف پنجم «سیستم‌های عامل»؛ route/API مستقل نیست و دادهٔ متناظر در clone وجود ندارد. |
| 13 | همان فهرست دروس، ارائهٔ متفاوت درس پنجم | [مرجع](screens/page-13-reference.png)؛ همان پنج درس و ۱۵ واحد صفحهٔ ۱۲ با تفاوت اطلاعات ارائه/مدرس ردیف پنجم؛ دادهٔ مستقل/fixture در clone موجود نیست. برای صفحات ۱۰–۱۳ هیچ رکوردی جهت تقلید PDF ساخته نشد؛ جزئیات در [screen doc](screens/selected-courses.md). |
| 14 | حضور و غیاب `/portal/attendance/` | [مرجع](screens/page-14-reference.png)، [UI جاری 1440×900](screens/page-14-current.png)، [موبایل 390×844](screens/page-14-mobile-current.png). قالب summary و جدول تجمیعی درس‌ها با PDF هم‌تراز شد. GET صفحه `200`، ناشناس `401` و پروندهٔ غیرمجاز `403`. clone یک درس/سه واحد و یک سابقهٔ حضور دارد، در برابر چهار درس/۱۲ واحد و ۳۲ جلسهٔ PDF؛ حد مجاز غیبت معلوم نیست و اخطار عددی جعل نشده. تست regression نوشته شده ولی اجرا نشده؛ جزئیات در [screen doc](screens/attendance.md). |
| 15 | تقویم آموزشی `/portal/calendar/` | [مرجع](screens/page-15-reference.png)؛ قالب اختصاصی با grid هجری شمسی، رویدادهای ماه از Term/امتحان/Attendance فعال و summary واقعی اضافه شد. مدل مناسبت عمومی یا deadline شهریه نداریم و دادهٔ PDF جعل نشد. clone تاریخ ترم 14051 را با مقادیر سال میلادی 2076 دارد؛ API ناشناس `401`، اما API احرازشده/capture جاری بازتولید نشده، پس تطبیق بصری کامل تأیید نشده. regression نوشته شد و اجرا نشده؛ [screen doc](screens/calendar.md). |
| 16 | اطلاعیه استادان `/portal/announcements/` | [مرجع](screens/page-16-reference.png)؛ selector از Communication نوع announcement و دریافت‌کنندهٔ حساب جاری؛ قالب کارت title/author/date/body و POST mark-read برای همان شناسه. API ناشناس `401`؛ دادهٔ مدل به درس/ترم وصل نیست و CTA «بخش مرتبط» منبع ندارد. capture جاری و API مجاز pending؛ regression نوشته و اجرا نشده؛ [screen doc](screens/announcements.md). |
| 17 | فرم ارزشیابی `/portal/evaluation-form/` | [مرجع](screens/page-17-reference.png)؛ قالب اختصاصی راست‌چین، پنج معیار مستقل رادیویی ۱–۵، نظر اختیاری و وضعیت پس از ثبت read-only اضافه شد. POST پنج معیار را در `TeacherSurvey` نگه می‌دارد؛ `overall_rating` میانگین گرد‌شده است. فرم از فهرست درس‌ها به enrollment مشخص وصل شد؛ enrollment غیرمتعلق رد می‌شود. migration افزوده شد اما روی DB محلی اجرا نشده؛ API مجاز/capture و suite خودکار به درخواست کاربر اجرا نشده‌اند. کد گروه و گزینه‌های ۴ انتخاب‌شدهٔ نمونه در مدل/فرم جعل نشدند؛ [screen doc](screens/evaluation-form.md). |
| 18 | مرکز اعلان‌ها `/portal/notifications/` | [مرجع](screens/page-18-reference.png)؛ قالب اختصاصی کارت‌ها/فیلترهای شمارشی، GET فیلترشونده با lookup واقعی و POST mark-read مالک‌محور پیاده شد؛ query فیلتر بعد از POST حفظ می‌شود. PDF پنج اعلان در سه دسته دارد؛ کل DB محلی فقط ۲ رکورد (announcement=1, grade=1) دارد و حساب احرازشده بررسی نشده. lookup چهار code از جمله financial/request ندارد، پس دسته‌بندی PDF جعل نشد. GET ناشناس `401`، تست NOT RUN و capture جاری احرازشده pending؛ [screen doc](screens/notifications.md). |
| 19 | تنظیمات `/portal/settings/` | [مرجع](screens/page-19-reference.png)؛ قالب اختصاصی زبان/ترجیح اعلان کلی/اطلاعات حساب از GET صفحه و POST به `SettingsForm` متصل به Person جاری. چهار دستهٔ PDF با محدودیت واقعی کانال‌ها نمایش داده می‌شوند؛ شمارهٔ موبایل، ترجیح تفکیکی کانال و provider پیامک/ایمیل در schema/service موجود نیست و ساخته نشد. فیلد اعلان ذخیره می‌شود اما سرویس فعلی آن را اعمال نمی‌کند. regression source نوشته شد و اجرا نشده؛ API مجاز/capture جاری احرازشده pending است، پس تطبیق بصری کامل تأیید نشده؛ [screen doc](screens/settings.md). |
| 20 | کارت دانشجویی `/portal/student-card/` | [مرجع PDF](screens/page-20-reference.png) ثبت شد؛ سورس template/CSS، selector و GET page API بررسی شد؛ کارت فقط Person/Student/Field/Term واقعی پروندهٔ متعلق به حساب را مصرف می‌کند. شناسهٔ سریال، QR و تاریخ اعتبار رسمی در مدل/service نیستند و جعل نمی‌شوند؛ markup فعلی دکمهٔ چاپ هم ندارد. کد API برای GET ناشناس `401` می‌دهد؛ regression موجود است اما در این فاز اجرا نشده. capture احرازشدهٔ تازه نداریم؛ بررسی منبع به‌معنای تکمیل بصری نیست و توالی بصری همچنان روی صفحهٔ ۱۹ متوقف است؛ [screen doc](screens/student-card.md). |
| 21 | کارت امتحان `/portal/exam-card/` | [مرجع PDF](screens/page-21-reference.png) بررسی شد؛ selector از enrollmentهای فعال همان Student/Term، تاریخ/ساعت/کلاس، TeacherSurvey و بدهی واقعی `Student.tuition_debt` استفاده می‌کند. هشدار اکنون مبلغ واقعی را با واحد ریال نشان می‌دهد و یادآوری همراه‌داشتن کارت/مدرک و حضور ۳۰ دقیقه پیش از آزمون اضافه شد. صندلی و صدور رسمی موجود نیست و کنترل رسمی غیرفعال می‌ماند. regression جدید نوشته شده اما اجرا نشده؛ capture جاری احرازشده در دسترس نیست، پس تطبیق بصری runtime تأیید نشده؛ [screen doc](screens/exam-card.md). |
| 22 | برنامه هفتگی `/portal/schedule/` | [مرجع PDF](screens/page-22-reference.png) بررسی شد؛ selector قبلی به‌اشتباه generic list table می‌داد و چهار خلاصه/شبکهٔ روز×زمان PDF را نداشت. قالب اختصاصی `niousha/schedule.html` با Enrollment فعال، CourseOffering و Constant روز هفته ساخته شد؛ واحد/جلسه/تداخل از دادهٔ واقعی محاسبه می‌شوند، روز بدون مقدار جداگانه گزارش می‌شود، و پیوندهای مسیرهای موجود/چاپ نگه داشته شدند. تست regression نوشته شد اما اجرا نشده؛ capture جاری احرازشده نداریم و visual runtime تأیید نشده؛ [screen doc](screens/schedule.md). |
| 23 | چارت درسی `/portal/curriculum/` | قالب اختصاصی چهار شاخص پیشرفت و جدول درس/واحد/پیش‌نیاز/وضعیت/گروه؛ GET فقط‌خواندنی و scoped به Curriculum رشته، Grade قبولی، Enrollment فعال و Prerequisite واقعی. گروه از `requirement_type` است چون مدل گروه مستقل ندارد. تست regression نوشته و اجرا نشده؛ capture جاری احرازشده نداریم و توالی بصری هنوز روی صفحهٔ ۱۹ متوقف است؛ [screen doc](screens/curriculum.md). |
| 24 | کارآموزی `/portal/internship/` | قالب اختصاصی برای چهار فیلد واقعی Internship، فرم/تاریخچهٔ پرونده‌محور و GET/POST API؛ status و owner سمت سرور. استاد ناظر، تماس/نشانی، فعالیت و فایل نامه در schema نیستند؛ جعل نشدند. Regression نوشته اما اجرا نشده؛ capture جاری احرازشده نداریم؛ [screen doc](screens/internship.md). |
| 25 | درخواست مهمانی `/portal/guest-request/` | قالب اختصاصی برای ثبت مقصد و جدول تاریخچهٔ owner-scoped؛ GET/POST API فقط داده‌های مدل TransferRequest را می‌پذیرد. فیلدهای PDF مبدأ/نوع/تماس/دلیل/مدرک و timeline مرحله‌ای در schema نیستند و ساخته نشدند. Regression نوشته اما اجرا نشده؛ capture جاری احرازشده نداریم؛ [screen doc](screens/guest-request.md). |
| 26 | درخواست بررسی فراغت از تحصیل `/portal/graduation/` | قالب اختصاصی واقعیت‌های Student و GraduationAudit scoped؛ eligibility فقط از property مدل، معدل/بدهی بدون تبدیل به شرط رسمی، کتابخانه unavailable؛ CTA ثبت disabled و POST=405 چون lookup درخواست موجود نیست. Regression نوشته اما اجرا نشده؛ capture احرازشده نداریم؛ [screen doc](screens/graduation.md). |
| 27 | ارتباط با استادان `/portal/messages/` | قالب دوپنلی استادهای ثبت‌نام فعال همان نیمسال + فرم/تاریخچه؛ گیرنده به UserAccount فعال همان استاد scope شد. هشت رکورد اخیر account نمایش داده می‌شود؛ thread/delivery/SMS/email منبع ندارد. Regression نوشته اما اجرا نشده؛ capture جاری احرازشده نداریم؛ [screen doc](screens/messages.md). |
| 28 | راهنمای سامانه `/portal/guide/` | UI چهار کارت Q&A و CTA پشتیبانی مطابق مرجع ساخته شد؛ لینک‌ها به enrollment، registration-status، emergency-drop، messages و support متصل‌اند. API حذف اضطراری حداقل واحد را کنترل نمی‌کند (در کارت/مستندات آشکار شده) و صفحهٔ وضعیت علت انسداد را تشخیص نمی‌دهد. تست regression نوشته شد ولی طبق درخواست اجرا نشده؛ capture جاری مجاز برای تطبیق runtime نداریم؛ [screen doc](screens/guide.md). |
| 29 | مرکز پشتیبانی `/portal/support/` | قالب اختصاصی فرم category/subject/content و جدول root-ticket/آخرین reply واقعی؛ POST JSON، سازنده از session و status اولیه از lookup فعال `open`. PDF پیوست دارد اما Ticket/API فایل را پشتیبانی نمی‌کنند؛ UI این gap را اعلام می‌کند. پاسخ/تغییر status فقط از این صفحه در دسترس نیست. Regression نوشته شده اما اجرا نشده؛ capture جاری نداریم؛ [screen doc](screens/support.md). |
| 30 | منع ثبت‌نام به علت بدهی | modal در `/portal/selected-courses/` به خطای واقعی `tuition_debt` از `POST /api/enrollment/register/<id>/` متصل شد؛ مبلغ بدهی و سقف مجاز پرونده را می‌خواند و مسیر مالی واقعی را لینک می‌کند. حداقل واحد در مدل/API تعریف نشده و در modal به‌عنوان gap گفته می‌شود؛ پرداخت آنلاین هم درگاه ندارد. Regression نوشته شده اما اجرا نشده؛ [screen doc](screens/operation-results.md). |
| 31 | فرم ارزشیابی استاد | قالب پنج rating مستقل، نظر اختیاری، اطلاعات درس/استاد/ترم و read-only بعد از ثبت موجود است. POST فقط Enrollment فعال متعلق به Student/Term جاری را می‌پذیرد و survey تکراری را رد می‌کند. گروه کلاس در schema نیست؛ مقدارهای ۴ PDF به‌عنوان پاسخ پیش‌فرض جعل نشدند. Regression نوشته اما اجرا نشده؛ [screen doc](screens/evaluation-form.md). |
| 32 | فرم ارزشیابی درس دوم | همان route/API با `enrollment` متفاوت؛ فرم در انتخاب هر enrollment فعال همین پرونده باز می‌شود. رکورد تصویری نمونه در DB ساخته نشده؛ گروه کلاس در schema نیست و فرم خالی می‌ماند تا دانشجو پاسخ دهد. Regression مشترک نوشته اما اجرا نشده؛ [screen doc](screens/evaluation-form.md). |
| 33 | ارزشیابی برای درس سوم | همان فرم/API با `enrollment` متعلق به درس سوم؛ دادهٔ نمونه به DB اضافه نشده؛ پاسخ‌های پیش‌فرض PDF جعل نمی‌شوند و group code در schema نیست. |
| 34 | فهرست ارزشیابی `/portal/evaluation/` | selector همهٔ Enrollmentهای فعال همان پرونده/ترم را با TeacherSurvey واقعی به تکمیل‌شده/نشده تقسیم می‌کند؛ موردهای باز به فرم همان enrollment لینک دارند. تعداد/نام نمونهٔ PDF در DB تزریق نشده. Regression برای scope/وضعیت نوشته اما اجرا نشده؛ [screen doc](screens/evaluation.md). |
| 35 | فهرست با وضعیت تکمیل متفاوت | همان route/API؛ state از وجود/عدم وجود TeacherSurvey برای Enrollmentهای فعال ساخته می‌شود و نیاز به route یا وضعیت hard-code ندارد. ردیف‌های خاص PDF در دیتابیس نمونه‌سازی نشده‌اند؛ regression اجرا نشده. |
| 36 | فهرست با وضعیت تکمیل متفاوت | همان route/API و منطق داده‌محور صفحهٔ ۳۴؛ state متفاوت فقط با survey واقعی روی enrollment متفاوت شکل می‌گیرد؛ دادهٔ PDF به DB نوشته نشده. |
| 37 | فهرست پس از ثبت ارزشیابی دیگر | همان route/API؛ وضعیت هر درس از survey واقعی همان Enrollment می‌آید؛ فرمِ تکمیل‌شده لینک submit ندارد و قابل ویرایش نیست. دادهٔ PDF seed نشده. |
| 38 | نتیجهٔ عملیات پس از ثبت کارآموزی | پس از ذخیرهٔ موفق Internship، API به صفحه با `request_id` همان رکورد redirect می‌کند؛ صفحه نتیجه را فقط از میان رکوردهای متعلق به Student جاری پیدا می‌کند و وضعیت/شناسه را نشان می‌دهد. متن روشن می‌کند که ارسال دانشگاهی یا تأیید رسمی انجام نشده است. regression نوشته شده ولی اجرا نشده؛ [کارآموزی](screens/internship.md) و [نتیجه‌ها](screens/operation-results.md). |
| 39 | نتیجهٔ عملیات پس از ثبت درخواست مهمانی | نتیجه از `TransferRequest` ذخیره‌شده با شناسه، دانشگاه مقصد و وضعیت review واقعی ساخته می‌شود؛ فقط رکورد متعلق به Student جاری نمایش داده می‌شود و تأیید نهایی را منوط به بررسی می‌داند. ارسال خودکار دانشگاهی ادعا نمی‌شود. regression نوشته شده ولی اجرا نشده؛ [درخواست مهمانی](screens/guest-request.md) و [نتیجه‌ها](screens/operation-results.md). |
| 40 | نتیجهٔ عملیات پس از ارسال پیام آموزشی | نتیجه از Communication واقعیِ فرستاده‌شده توسط حساب جاری ساخته می‌شود؛ فقط رکورد sender جاری با `request_id` می‌آید. UI مطابق مرجع یادآوری می‌کند حساب واقعی استاد متصل نیست و تحویل بیرونی قابل تأیید نیست. regression مالکیت/ذخیره نوشته شده ولی اجرا نشده؛ [پیام‌ها](screens/messages.md) و [نتیجه‌ها](screens/operation-results.md). |
| 41 | نتیجهٔ ذخیرهٔ تنظیمات | GET صفحه پس از redirect موفق، مقادیر ذخیره‌شده در Person حساب جاری را تأیید می‌کند. برخلاف نمونهٔ PDF، این برنامه واقعاً در دیتابیس محلی تغییر می‌دهد؛ ترجیح اعلان ذخیره می‌شود اما سرویس فعلی آن را اعمال نمی‌کند. regression نوشته شده ولی اجرا نشده؛ [تنظیمات](screens/settings.md) و [نتیجه‌ها](screens/operation-results.md). |
| 42 | نتیجهٔ ثبت اعتراض نمره | پس از ثبت GradeAppeal، `request_id` به route برمی‌گردد؛ فقط اعتراض همان Enrollment/Student/Term پیدا می‌شود و وضعیت موجود نمایش داده می‌شود. متن نتیجه تصریح می‌کند ثبت اعتراض به معنی تغییر نمره یا تأیید نیست. regression نوشته شده ولی اجرا نشده؛ [اعتراض نمره](screens/grade-appeal.md) و [نتیجه‌ها](screens/operation-results.md). |
| 43 | نتیجهٔ ثبت درخواست وام/تسهیلات | نتیجه از ScholarshipApplication ذخیره‌شده، شناسه، نوع و status واقعی ساخته می‌شود؛ پیام می‌گوید ثبت درخواست به معنی تخصیص/تأیید نهایی نیست و بررسی به مدارک/منابع وابسته است. regression نوشته شده ولی اجرا نشده؛ [تسهیلات](screens/financial-aid.md) و [نتیجه‌ها](screens/operation-results.md). |
| 44 | نتیجهٔ ثبت درخواست دانشجویی | پس از POST موفق، `request_id` به صفحه برمی‌گردد؛ نتیجه نوع درخواست و status واقعی StudentServiceRequest را از رکورد همان Student می‌خواند و صریحاً می‌گوید به سامانهٔ دانشگاهی ارسال نشده است. برای این مدل timestamp نداریم، پس تاریخ ساخته نمی‌شود. regression نوشته شده ولی اجرا نشده؛ [درخواست‌ها](screens/requests.md) و [نتیجه‌ها](screens/operation-results.md). |
| 45 | نتیجهٔ ثبت درخواست گواهی آموزشی | نتیجهٔ StudentServiceRequest با نوع فعال `employment_certificate`, شناسه و status واقعی نمایش داده می‌شود؛ اعلام می‌کند درخواست ثبت شده، اما مدرک رسمی صادر نشده و باید از سامانهٔ رسمی دریافت شود. regression نوشته شده ولی اجرا نشده؛ [گواهی آموزشی](screens/education-certificate.md) و [نتیجه‌ها](screens/operation-results.md). |
| 46 | نتیجهٔ ثبت تیکت پشتیبانی | POST همان API تیکت را ذخیره و `request_id` برمی‌گرداند؛ صفحه فقط Ticket ریشهٔ متعلق به همان حساب را با کد/موضوع/status/زمان نشان می‌دهد. ثبت محلی به معنی تحویل/پاسخ واحد پشتیبانی نیست و پیوست در schema/API پشتیبانی نمی‌شود. regression مالکیت نتیجه نوشته شد، اجرا نشده؛ [پشتیبانی](screens/support.md). |
| 47 | نتیجه/بازگشت از پرداخت | معادل امن موجود `/portal/secure-payment/` فقط بدهی واقعی را می‌خواند؛ gateway و POST پرداخت وجود ندارند، Payment جدید ثبت یا بدهی تسویه نمی‌شود. state موفق PDF جعل نمی‌شود؛ [نتیجه‌ها](screens/operation-results.md). |
| 48 | پیش‌نمایش گواهی اشتغال به تحصیل | محتوای نام/شماره/ترم PDF صرفاً نمونه است؛ صفحهٔ `education-certificate` فقط درخواست محلی را ثبت/پیگیری می‌کند و صدور یا فایل رسمی provider ندارد. گواهی نمونه به‌عنوان سند معتبر بازتولید نمی‌شود؛ [گواهی آموزشی](screens/education-certificate.md). |
| 49 | مقیاس و state پاسخ ارزشیابی | مرجع پنج کنترل رادیویی ۱–۵ دارد؛ همان پنج معیار API مستقل و اجباری‌اند و پس از POST scoreهای واقعی read-only می‌شوند. scoreهای انتخاب‌شدهٔ PDF پیش‌فرض فرم نیستند؛ تست موجود ۵،۴،۳،۲،۱ را ثبت و نمایش هر پنج score را پوشش می‌دهد، اما اجرا نشده؛ [فرم ارزشیابی](screens/evaluation-form.md). |
| 50 | تنظیم کانال اعلان | مرجع حالت‌های روشن/خاموش SMS و رایانامه را جدا نشان می‌دهد؛ clone فقط `Person.is_notification_enabled` کلی را ذخیره می‌کند و phone، ترجیح کانالی و provider ندارد. UI این شکاف را به‌جای نمایش toggle ساختگی اعلام می‌کند؛ [تنظیمات](screens/settings.md). |
| 51 | انتخاب زبان | مرجع دو گزینهٔ فارسی/English را در stateهای متفاوت نشان می‌دهد؛ UI گزینه‌های `Constant(language)` موجود را رادیویی render و POST آن‌ها را فقط برای Person جاری ذخیره می‌کند. regression render فارسی/English و ذخیرهٔ فارسی نوشته شده اما اجرا نشده؛ [تنظیمات](screens/settings.md). |
| 52 | مرحلهٔ اول انتخاب واحد `/portal/enrollment/` | دادهٔ Person/Student/Term و بدهی/سقف واقعی؛ مرحله‌نما و لینک `selected-courses`. PDF عدد حداقل واحد هم دارد اما در مدل/API rule فعالش نیست، پس clone آن را اختراع نمی‌کند؛ regression مالکیت/ترم/بدهی/CTA نوشته شده، اجرا نشده؛ [صفحه](screens/enrollment.md). |
| 53 | حذف و اضافه `/portal/add-drop/` | صفحهٔ واحد هر دو عملیات را دارد: حذف Enrollment با مودال و افزودن از offering table همان مسیر، هر دو به API واقعی. gap false-fix شد: API حداقل واحد را بررسی نمی‌کند؛ صفحه آن را شفاف اعلام می‌کند. بدهی modal دارد؛ تعرفهٔ شهریه نیست. regression جدید نوشته/اجرا نشده؛ [screen doc](screens/add-drop.md). |
| 54 | حذف اضطراری `/portal/emergency-drop/` | actionها به endpoint مجزای emergency وصل شدند که فقط پنجرهٔ emergency را می‌پذیرد؛ add/drop دیگر به‌تنهایی اجازه نمی‌دهد. فیلد حداقل واحد در PDF در service موجود نیست و جعل نمی‌شود. regressionهای service/API/template نوشته شده، اجرا نشده؛ [صفحه](screens/emergency-drop.md). |
| 55 | آخرین وضعیت ثبت‌نام `/portal/registration-status/` | قالب اختصاصی چهارمرحله‌ای از Student/Enrollment/debt می‌خواند؛ مرحلهٔ نهایی نامشخص می‌ماند چون مدل approval ندارد، بدهی صفر رسید پرداخت نیست، و حداقل واحد تعریف نشده است. regression نوشته/اجرا نشده؛ [screen doc](screens/registration-status.md). |
| 56 | نتیجهٔ موفق افزودن درس | API نتیجهٔ `created=true` و Enrollment می‌دهد؛ UI به add-drop با `registration_id` می‌رود و نتیجه فقط رکورد فعال متعلق را نمایش می‌دهد؛ state/offerings دیگر PDF جعل نشده؛ regression نوشته، اجرا نشده؛ [حذف و اضافه](screens/add-drop.md). |
| 57 | نتیجهٔ افزودن با offering متفاوت | همان result مالک‌محور ۵۶؛ دادهٔ استاد/درس PDF در DB ساخته نشده. |
| 58 | نتیجهٔ افزودن با offering متفاوت | همان result مالک‌محور ۵۶؛ تعرفهٔ شهریه و fixture PDF موجود نیست. |
| 59 | نتیجهٔ افزودن با offering متفاوت | همان result مالک‌محور ۵۶؛ offering مرجع seed نشده و تست اجرا نشده. |
| 60 | اعتراض نمره `/portal/grade-appeal/` | PDF فرم درسِ نمره‌دار، دلیل، پیوست و رعایت مهلت را نشان می‌دهد. route/form واقعی فقط enrollment همان Student/Term با score ثبت‌شده را می‌پذیرد؛ مدل/API مهلت را اعتبارسنجی نمی‌کند و پیوست ندارد، پس هشدار صریح نمایش داده می‌شود. نتیجه به درخواست واقعی و وضعیت بازبینی‌نشده وصل است؛ capture جاری احرازشده موجود نیست. |
| 61 | فعالیت آموزشی `/portal/academic-activities/` | PDF چهار کارت برنامه/حضور/امتحان/تقویم، خلاصهٔ پرونده و جدول آخرین فعالیت را نشان می‌دهد. clone همین مقصدها را به routeهای واقعی وصل می‌کند و خلاصهٔ enrollment فعال/واحد را از Student/Term می‌خواند؛ تاریخچه owner-scoped است اما مدل EducationalChangeLog ترم ندارد. رگرسیون مقصد لینک‌ها و عدم افشای تاریخچهٔ حساب دیگر نوشته شد، اجرا نشده؛ capture جاری نداریم. |
| 62 | کارنامه `/portal/transcript/` | PDF همهٔ درس‌های نیمسال را با واحد/میان‌ترم/پایان‌ترم/وضعیت، خلاصه و دو action نشان می‌دهد. clone اکنون همهٔ Enrollmentهای فعال همان Student/Term را می‌آورد؛ یک `Grade.score` موجود یا «ثبت نشده»، واحد و status را نمایش می‌دهد و به اعتراض/چارت لینک می‌دهد. مدل نمره را به دو بخش یا معدل term جدا نمی‌کند؛ آن محدودیت شفاف است. regression مالکیت و درس بی‌نمره نوشته، اجرا نشده؛ capture جاری نداریم. |
| 63 | پرداخت‌ها `/portal/payments/` | PDF ستون شرح دارد اما Payment آن را ندارد؛ UI ستون را با «شرح در مدل پرداخت ثبت نشده» پر می‌کند، term در عنوان است؛ خلاصهٔ موفق/بدهی واقعی و تراکنش‌های owner/term نمایش داده می‌شوند و failed در جمع نیست. تست مبلغ/شرح/مالکیت تقویت شد، اجرا نشده؛ capture جاری احرازشده نداریم. |
| 64 | پرداخت امن `/portal/secure-payment/` | چیدمان preview شامل ماندهٔ Student، شرح کلی، نام Person و unavailable بودن درگاه؛ ادامهٔ پرداخت disabled و لینک سوابق واقعی است. مدل Payment pending transaction ندارد و بدهی term-specific نیست؛ هیچ کارت/درگاه/POST/موفقیت جعل نمی‌شود. regression نوشته، اجرا نشده؛ capture جاری احرازشده نداریم. |
| 65 | تسهیلات `/portal/financial-aid/` | PDF مبلغ، شبا و مدرک می‌خواهد؛ ScholarshipApplication فقط type/reason/status/date دارد. فرم موجود فقط همین دو ورودی را می‌گیرد و بالایش روشن می‌کند مبلغ/شبا/پیوست و پرداخت/تأیید پشتیبانی نمی‌شود؛ applicant/status سروری و tracking owner-scoped است. assertion نوشته، اجرا نشده؛ capture جاری نداریم. |
| 66 | شهریه `/portal/tuition/` | خلاصهٔ بدهی پرونده و جمع Paymentهای successful از دادهٔ واقعی؛ breakdown شهریهٔ ثابت/متغیر و بدهی term-specific در schema نیست، پس هشدار داده می‌شود. مبالغ با واحد portal (ریال) نمایش داده می‌شوند، نه تبدیل حدسی از تومان PDF. پیوندهای پرداخت/سوابق وصل‌اند؛ regression نوشته، اجرا نشده؛ capture جاری احرازشده نداریم. |
| 67 | درخواست‌ها `/portal/requests/` | فرم واقعی فقط نوع و توضیحات می‌گیرد؛ `StudentServiceRequest` contact phone/attachment ندارد و API به سامانهٔ دانشگاهی ارسال نمی‌کند، محدودیت کنار فرم می‌آید. owner/status سروری و history/result scoped است. assertion نوشته، اجرا نشده؛ capture جاری احرازشده نداریم. |
| 68 | state حذف‌و‌اضافه با دادهٔ دیگر | route والد جدول ثبت‌نام فعال با زمان/امتحان/status و حذف واقعی را نشان می‌دهد؛ status به ردیف افزوده شد. stateهای متفاوت دادهٔ PDF در DB نیستند و breakdown شهریه مدل نشده؛ regression نوشته، اجرا نشده؛ capture جاری احرازشده نداریم. |
| 69 | state حذف‌و‌اضافه با دادهٔ دیگر | route والد موجود؛ data set PDF-specific بازنمایی‌نشده. |
| 70 | state حذف‌و‌اضافه با دادهٔ دیگر | route والد موجود؛ data set PDF-specific بازنمایی‌نشده. |
| 71 | state حذف‌و‌اضافه با دادهٔ دیگر | route والد موجود؛ data set PDF-specific بازنمایی‌نشده. |
| 72 | مدرک آموزشی `/portal/education-certificate/` | ثبت محلی فقط با active `employment_certificate`; مخاطب/تعداد نسخه/روش تحویل در schema نیست و پیام محدودیت کنار فرم می‌آید؛ نتیجه ثبت را از status واقعی می‌خواند ولی مدرک صادر نمی‌کند. assertion نوشته، اجرا نشده؛ capture جاری احرازشده نداریم. |
| 73 | مدرک دانش‌آموختگی `/portal/graduation-certificate/` | صفحهٔ read-only اختصاصی از پرونده، واحدهای Student و جمع چارت فعال، آخرین GraduationAudit، نبود وضعیت کتابخانه/مدارک و مسیر چهارمرحله‌ای استفاده می‌کند؛ به بررسی فراغت/چارت وصل است. request type و provider صدور موجود نیست، POST ندارد. regression نوشته، اجرا نشده؛ capture جاری نداریم. |
| 74 | فهرست ارزشیابی `/portal/evaluation/` | چهار درس/وضعیت تکمیل/پیوند فرم از Enrollmentهای فعال و TeacherSurvey همان Student/Term ساخته می‌شود؛ هر معیار ۱–۵ است. PDF پاسخ‌ها را محرمانه می‌خواند، ولی مدل Survey به Enrollment دانشجو FK دارد و ناشناس‌بودن تضمین نمی‌شود؛ همین تفاوت اعلام می‌شود. آزمون scope موجود تقویت شد، اجرا نشده؛ capture جاری نداریم. |
| 75–78 | فهرست حذف اضطراری `/portal/emergency-drop/` | چهار state فهرست/ردیف‌اند، نه نتیجهٔ عملیات یا route جدا. همان صفحه دادهٔ Enrollment جاری را می‌خواند. پس از حذف موفق، نتیجهٔ همان رکورد فقط در scope Student/Term مالک نشان داده می‌شود؛ API استرداد وجه ندارد. آزمون مالکیت نتیجه نوشته، اجرا نشده. |
| 79 و 84 | فهرست درس در مودال انتخاب `/portal/selected-courses/` | مودال API-driven به `GET /api/scheduling/offerings/` وصل است؛ کارت‌های درس از lesson code/title واقعی گروه‌بندی می‌شوند. گروه شماره‌گذاری/شهریه که schema ندارد جعل نمی‌شود. Regression markup/binding نوشته، اجرا نشده. |
| 80–83 و 85–88 | جزئیات و انتخاب ارائهٔ درس در همان مودال | استاد، روز/ساعت، واحد، ظرفیت و زمان امتحان از CourseOffering واقعی می‌آیند؛ انتخاب رادیویی صرفاً UI است، و افزودن فقط با `POST /api/enrollment/register/<offering_id>/` انجام می‌شود. group number/تعرفه در مدل نیست. آزمون‌ها نوشته، اجرا نشده. |
| 89–92 | تأیید حذف عادی `/portal/add-drop/` | dialog دادهٔ درس را از Enrollment واقعی می‌گیرد و فقط پس از تأیید `POST /api/enrollment/drop/<id>/` را می‌زند. سرویس status را تغییر می‌دهد؛ بازپرداخت را محاسبه/ثبت نمی‌کند. |
| 93–96 | تأیید حذف اضطراری `/portal/emergency-drop/` | همان dialog با متن محدودیت مالی روشن؛ عملیات از endpoint emergency-only می‌گذرد و فقط در پنجرهٔ اضطراری معتبر است. بازپرداخت ثبت نمی‌شود. آزمون‌ها نوشته، اجرا نشده. |

مرجع تصویری ۷۵–۹۶ دیده شد؛ capture جاری این بازه در این نوبت گرفته نشد. این یادداشت مقدم بر بازبینی مجدد صفحهٔ ۹ است؛ وضعیت ترتیبی فعلی و علت نیاز به capture تازه در `docs/PROGRESS.md` ثبت شده است.

## اختلاف inventory تصویر و محدودیت بازبینی

سند قبلی `docs/portal-pdf-comparison.md` ۵۸ حالت رابط ثبت‌شده را گزارش می‌کند و پوشهٔ موقت ۷۵ screenshot دارد؛ تعریف این دو شمارش یکسان نیست. ۹۶ تصویر مرجع PDF در contact sheet مرور و صفحه‌های ۲، ۹، ۵۳ و ۶۳ با capture فعلی به‌طور نماینده مقایسه شدند. هفت viewport هدف capture شدند و در هیچ‌کدام document-level horizontal overflow دیده نشد. این بررسی، pixel matching یا مرور جداگانهٔ تمام routeها/stateها نیست؛ محدودیت و فایل‌های موقت در `docs/TEST_REPORT.md` ثبت‌اند.

## نگاشت صفحه‌به‌صفحه به کامپوننت React

این crosswalk همهٔ شماره‌های PDF را به مسیر/state جاری و کامپوننتی که در `PageRenderer` رندر می‌شود وصل می‌کند. برای stateهای چندصفحه‌ای، یک route و کامپوننت مشترک عمداً تکرار شده است؛ دادهٔ خاص PDF در clone جعل نمی‌شود. این جدول فقط مالکیت رندر را مستند می‌کند و هیچ‌یک از وضعیت‌های تصویری/پذیرش جدول بالا را تغییر نمی‌دهد.

| PDF | route/state فعلی | React component |
|---:|---|---|
| 1 | ورود `/login/` | `LoginPage` |
| 2 | داشبورد `/` | `DashboardPage` |
| 3 | انتخاب نیمسال؛ dialog مشترک پوسته | `PortalShell + TermPicker` |
| 4 | گروه‌های منوی کناری؛ stateهای Sidebar | `PortalShell + Sidebar` |
| 5 | گروه‌های منوی کناری؛ stateهای Sidebar | `PortalShell + Sidebar` |
| 6 | گروه‌های منوی کناری؛ stateهای Sidebar | `PortalShell + Sidebar` |
| 7 | گروه‌های منوی کناری؛ stateهای Sidebar | `PortalShell + Sidebar` |
| 8 | گروه‌های منوی کناری؛ stateهای Sidebar | `PortalShell + Sidebar` |
| 9 | دروس انتخاب‌شده `/portal/selected-courses/`؛ state داده‌ای PDF | `SelectedCoursesPage` |
| 10 | دروس انتخاب‌شده `/portal/selected-courses/`؛ state داده‌ای PDF | `SelectedCoursesPage` |
| 11 | دروس انتخاب‌شده `/portal/selected-courses/`؛ state داده‌ای PDF | `SelectedCoursesPage` |
| 12 | دروس انتخاب‌شده `/portal/selected-courses/`؛ state داده‌ای PDF | `SelectedCoursesPage` |
| 13 | دروس انتخاب‌شده `/portal/selected-courses/`؛ state داده‌ای PDF | `SelectedCoursesPage` |
| 14 | حضور و غیاب `/portal/attendance/` | `AttendancePage` |
| 15 | تقویم آموزشی `/portal/calendar/` | `CalendarPage` |
| 16 | اطلاعیه‌ها `/portal/announcements/` | `AnnouncementsPage` |
| 17 | فرم ارزشیابی `/portal/evaluation-form/` | `EvaluationFormPage` |
| 18 | اعلان‌ها `/portal/notifications/` | `NotificationsPage` |
| 19 | تنظیمات `/portal/settings/` | `SettingsPage` |
| 20 | کارت دانشجویی `/portal/student-card/` | `StudentCardPage` |
| 21 | کارت امتحان `/portal/exam-card/` | `ExamCardPage` |
| 22 | برنامه هفتگی `/portal/schedule/` | `SchedulePage` |
| 23 | چارت درسی `/portal/curriculum/` | `AcademicPage` |
| 24 | کارآموزی `/portal/internship/` | `StudentServicePage` |
| 25 | درخواست مهمانی `/portal/guest-request/` | `StudentServicePage` |
| 26 | بررسی فراغت `/portal/graduation/` | `StudentServicePage` |
| 27 | پیام به استاد `/portal/messages/` | `MessagesPage` |
| 28 | راهنمای سامانه `/portal/guide/` | `GuidePage` |
| 29 | پشتیبانی `/portal/support/` | `SupportPage` |
| 30 | هشدار بدهی در مودال انتخاب ارائه `/portal/selected-courses/` | `OfferingPicker` |
| 31 | فرم ارزشیابی؛ انتخاب Enrollmentهای متفاوت | `EvaluationFormPage` |
| 32 | فرم ارزشیابی؛ انتخاب Enrollmentهای متفاوت | `EvaluationFormPage` |
| 33 | فرم ارزشیابی؛ انتخاب Enrollmentهای متفاوت | `EvaluationFormPage` |
| 34 | فهرست ارزشیابی؛ stateهای تکمیل متفاوت `/portal/evaluation/` | `EvaluationPage` |
| 35 | فهرست ارزشیابی؛ stateهای تکمیل متفاوت `/portal/evaluation/` | `EvaluationPage` |
| 36 | فهرست ارزشیابی؛ stateهای تکمیل متفاوت `/portal/evaluation/` | `EvaluationPage` |
| 37 | فهرست ارزشیابی؛ stateهای تکمیل متفاوت `/portal/evaluation/` | `EvaluationPage` |
| 38 | نتیجهٔ کارآموزی با `request_id` | `StudentServicePage` |
| 39 | نتیجهٔ درخواست مهمانی با `request_id` | `StudentServicePage` |
| 40 | نتیجهٔ پیام آموزشی با scope فرستنده | `MessagesPage` |
| 41 | نتیجهٔ ذخیرهٔ تنظیمات | `SettingsPage` |
| 42 | نتیجهٔ اعتراض نمره | `GradeAppealPage` |
| 43 | نتیجهٔ تسهیلات `/portal/financial-aid/` | `StudentServicePage` |
| 44 | نتیجهٔ درخواست دانشجویی `/portal/requests/` | `StudentServicePage` |
| 45 | نتیجهٔ درخواست گواهی آموزشی | `StudentServicePage` |
| 46 | نتیجهٔ تیکت پشتیبانی | `SupportPage` |
| 47 | بازگشت از پرداخت؛ بدون gateway یا تراکنش | `FinancePage` |
| 48 | گواهی اشتغال؛ درخواست محلی، بدون فایل رسمی | `StudentServicePage` |
| 49 | مقیاس امتیازدهی ارزشیابی | `EvaluationFormPage` |
| 50 | ترجیح اعلان و زبان `/portal/settings/` | `SettingsPage` |
| 51 | ترجیح اعلان و زبان `/portal/settings/` | `SettingsPage` |
| 52 | مرحلهٔ اول انتخاب واحد `/portal/enrollment/` | `EnrollmentPage` |
| 53 | حذف و اضافه `/portal/add-drop/` | `CourseChangesPage + OfferingPicker` |
| 54 | حذف اضطراری `/portal/emergency-drop/` | `CourseChangesPage` |
| 55 | وضعیت ثبت‌نام `/portal/registration-status/` | `RegistrationStatusPage` |
| 56 | نتیجهٔ افزودن درس؛ offeringهای متفاوت در `/portal/add-drop/` | `CourseChangesPage` |
| 57 | نتیجهٔ افزودن درس؛ offeringهای متفاوت در `/portal/add-drop/` | `CourseChangesPage` |
| 58 | نتیجهٔ افزودن درس؛ offeringهای متفاوت در `/portal/add-drop/` | `CourseChangesPage` |
| 59 | نتیجهٔ افزودن درس؛ offeringهای متفاوت در `/portal/add-drop/` | `CourseChangesPage` |
| 60 | اعتراض نمره `/portal/grade-appeal/` | `GradeAppealPage` |
| 61 | فعالیت آموزشی و کارنامه | `AcademicPage` |
| 62 | فعالیت آموزشی و کارنامه | `AcademicPage` |
| 63 | پرداخت‌ها، پرداخت امن و شهریه | `FinancePage` |
| 64 | پرداخت‌ها، پرداخت امن و شهریه | `FinancePage` |
| 65 | تسهیلات `/portal/financial-aid/` | `StudentServicePage` |
| 66 | پرداخت‌ها، پرداخت امن و شهریه | `FinancePage` |
| 67 | درخواست‌های دانشجویی `/portal/requests/` | `StudentServicePage` |
| 68 | حذف و اضافه؛ stateهای ثبت‌نام `/portal/add-drop/` | `CourseChangesPage` |
| 69 | حذف و اضافه؛ stateهای ثبت‌نام `/portal/add-drop/` | `CourseChangesPage` |
| 70 | حذف و اضافه؛ stateهای ثبت‌نام `/portal/add-drop/` | `CourseChangesPage` |
| 71 | حذف و اضافه؛ stateهای ثبت‌نام `/portal/add-drop/` | `CourseChangesPage` |
| 72 | گواهی آموزشی و دانش‌آموختگی | `StudentServicePage` |
| 73 | گواهی آموزشی و دانش‌آموختگی | `StudentServicePage` |
| 74 | فهرست ارزشیابی `/portal/evaluation/` | `EvaluationPage` |
| 75 | فهرست حذف اضطراری `/portal/emergency-drop/` | `CourseChangesPage` |
| 76 | فهرست حذف اضطراری `/portal/emergency-drop/` | `CourseChangesPage` |
| 77 | فهرست حذف اضطراری `/portal/emergency-drop/` | `CourseChangesPage` |
| 78 | فهرست حذف اضطراری `/portal/emergency-drop/` | `CourseChangesPage` |
| 79 | فهرست offeringها در مودال `/portal/selected-courses/` | `OfferingPicker` |
| 80 | جزئیات و انتخاب offering در مودال | `OfferingPicker` |
| 81 | جزئیات و انتخاب offering در مودال | `OfferingPicker` |
| 82 | جزئیات و انتخاب offering در مودال | `OfferingPicker` |
| 83 | جزئیات و انتخاب offering در مودال | `OfferingPicker` |
| 84 | فهرست offeringها در مودال `/portal/selected-courses/` | `OfferingPicker` |
| 85 | جزئیات و انتخاب offering در مودال | `OfferingPicker` |
| 86 | جزئیات و انتخاب offering در مودال | `OfferingPicker` |
| 87 | جزئیات و انتخاب offering در مودال | `OfferingPicker` |
| 88 | جزئیات و انتخاب offering در مودال | `OfferingPicker` |
| 89 | تأیید حذف عادی `/portal/add-drop/` | `CourseChangesPage` |
| 90 | تأیید حذف عادی `/portal/add-drop/` | `CourseChangesPage` |
| 91 | تأیید حذف عادی `/portal/add-drop/` | `CourseChangesPage` |
| 92 | تأیید حذف عادی `/portal/add-drop/` | `CourseChangesPage` |
| 93 | تأیید حذف اضطراری `/portal/emergency-drop/` | `CourseChangesPage` |
| 94 | تأیید حذف اضطراری `/portal/emergency-drop/` | `CourseChangesPage` |
| 95 | تأیید حذف اضطراری `/portal/emergency-drop/` | `CourseChangesPage` |
| 96 | تأیید حذف اضطراری `/portal/emergency-drop/` | `CourseChangesPage` |

بررسی منبع در این مرحله تأیید می‌کند هر ۳۳ slug رجیستری Django در `routes.ts` و dispatch صفحهٔ React وجود دارد. این پوشش کد است، نه تأیید capture یا تطبیق بصری ۹۶ صفحه؛ cursor ترتیبی visual همچنان صفحهٔ ۹ است.
