# گزارش نهایی ممیزی و بازسازی آموزشیار

تاریخ: ۲۰۷۶-۰۵-۰۷ — branch: `codex/full-system-audit`

## نتیجهٔ کلی

**وضعیت پروژه: Partially Completed.** این شاخه ممیزی کامل، قراردادها و نقشهٔ صفحات را مستند کرده، دو defect قابل‌بازتولید را با تست اصلاح کرده و بستهٔ ارائه را تولید کرده است؛ اما همهٔ workflowهای PDF یا همهٔ screenها به معیار سخت‌گیرانهٔ UI/API/persistence/permission/error/test نرسیده‌اند. این branch برای مرور فنی و نمایش جریان‌های تأییدشده مناسب است، نه معرفی به‌عنوان سامانهٔ دانشگاهی آمادهٔ production.

## دامنه و شمارش‌های قابل‌اثبات

| معیار | نتیجه |
|---|---|
| صفحات PDF بررسی‌شده و mapشده | ۹۶/۹۶؛ هر شماره یک ردیف در `PDF_PAGE_MAPPING.md` دارد |
| routeهای پرتال ثبت‌شده | ۳۲ slug؛ همه screen doc، matrix و GET render smoke دارند؛ این عدد به معنی کامل‌بودن workflow هر screen نیست |
| APIهای جدید در این شاخه | ۰؛ APIهای موجود بررسی/مستند شدند و رفتار endpoint جدید اضافه نشد |
| قراردادهای API مستندشده | accounts، scheduling، enrollment، review و page API؛ تعداد endpoint/روش‌ها در جدول دقیق `API_CONTRACTS.md` |
| presentationهای فارسی | ۷ عضو + master؛ هر سند عضو ۱۰ بخش دارد |
| Python tests | ۱۰۱ پاس، ۰ شکست |
| JavaScript tests | ۱۴ پاس، ۰ شکست |
| Django system check | پاک |
| migration check | `No changes detected` |
| لینک محلی Markdown | ۱۰۶ فایل بررسی؛ ۰ لینک شکسته |

## وضعیت حوزه‌ها

| حوزه | وضعیت | شاهد/مانده |
|---|---|---|
| Git isolation، audit، API contracts، screen docs و PDF map | Completed (مستندات) | چهار checkpoint و ۹۶ صفحه/۳۲ route ثبت شدند |
| ورود، dashboard، term switching، route navigation و logout | Partially Completed | browser smoke واقعی گذشت؛ تمام دسترس‌پذیری/حالت‌های UI ممیزی نشده‌اند |
| انتخاب واحد و حذف | Partially Completed | serviceهای register/drop و persistence در تست‌ها؛ browser write اجرا نشد چون seed term/offer واجد شرایط ندارد |
| مالی | Partially Completed | پرداخت/شهریه/تسهیلات موجود؛ درگاه بانکی و چند مدل مالی غایب‌اند؛ موفقیت بیرونی جعل نمی‌شود |
| زمان‌بندی، درخواست و خدمات عمومی | Partially Completed | route و فرم‌های موجود؛ lifecycle و APIهای کارکنان کامل نیستند |
| responsive و visual match | Partially Completed | ۷ viewport بررسی و ۴ صفحه با PDF مقایسه شد؛ pixel match همهٔ ۹۶ صفحه انجام نشده |
| APIهای مستقل ۱۴ namespace دامنه‌ای | Not Implemented / Blocked | actor، schema، permission و lifecycle معتبر در منبع موجود نیست |
| gateway، صدور رسمی، SMS/email، task queue | Blocked | provider و قرارداد اتصال موجود نیست |
| guide Q&A، تقویم رویداد، پاسخ کامل Ticket و result stateهای PDF | Partially/Not Implemented | content/schema/workflow کافی در repository نیست |

## تغییرهای کد و بررسی مرورگر

1. `finance.html` از shell مستقل به fragment تبدیل شد؛ تست می‌سنجد `payments`, `secure-payment`, و `tuition` فقط یک `portal-shell` داشته باشند.
2. border داخلی input جست‌وجوی جدول در responsive stylesheet حذف شد؛ wrapper قاب را نگه می‌دارد. تست Node با RED/GREEN و browser computed style در `768×1024` تأیید شد.
3. browser smoke شامل login، dashboard، term `14051→14052`، ادامه از enrollment به selected-courses، دریافت دو offering واقعی برای term `14051`، رد دسترسی به profile دیگر با 403 و logout بود.
4. حساب QA مرورگر فقط در SQLite کلون ایجاد و پس از تست پاک شد. دیتابیس و source اصلی تغییر نکردند.
5. viewportهای `1920×1080`, `1536×864`, `1366×768`, `1280×720`, `1024×768`, `768×1024`, `390×844` بازبینی شدند؛ document-level horizontal overflow مشاهده نشد. captureها در temp هستند و به مخزن اضافه نشده‌اند.

## آزمون‌ها و هشدارهای باقی‌مانده

اجرای نهایی روی کد پس از تغییرهای source: `manage.py test` — ۱۰۱ تست در ۱۳۷٫۷۱۶ ثانیه، PASS؛ Node — ۱۴ تست، PASS؛ `manage.py check` و `makemigrations --check --dry-run` نیز PASS. دقیقاً ۲۰ `RuntimeWarning` برای datetimeهای naive با `USE_TZ=True` باقی ماند: ۶ `Term`، یک `Payment`، سه `CounselingAppointment` و ۱۰ `OnlineClass`. این‌ها failure نبودند، اما اصلاحشان به timezone مرجع seed وابسته است.

## محدودیت‌های محیط

- پروژه در clone مستقل `C:\Users\repair\Downloads\Amoozeshyar-audit-clone-3` روی branch بالا تغییر کرد؛ checkout اصلی `C:\Users\repair\Documents\یونی` و دیتابیسش دست‌نخورده ماند.
- اجرای تست از venv موجود با Django 5.2.18 انجام شد. ساخت venv تازه ممکن شد ولی PyPI به‌علت TLS/date محیط پاسخ نداد؛ verification TLS دور زده نشد و dependency جدید نصب نشد.
- Git `2.56.0.windows.4` هنگام commit/ref write معمول crash می‌کند؛ checkpointهای این clone با `hash-object` و `update-ref` شرطی ثبت و سپس با log/status بررسی شدند. config/ref مخزن اصلی دستکاری نشد.
- `نیازمندی_های_آموزشیار.md` در repository نیست؛ فرض‌ها و unknownها در `BUSINESS_RULES.md` و `DECISIONS.md` مشخص‌اند.

## تصمیم‌ها و فرض‌های مهم

- مدل/endpoint تازه از تصویر PDF یا ۱۵۲ شناسهٔ SDD اختراع نشد.
- همهٔ صفحه‌ها به session جاری و Student متعلق محدود می‌مانند؛ ID ارسالی مجوز نیست.
- درخواست داخلی معادل صدور رسمی، پرداخت واقعی یا ارسال بیرونی نیست.
- مالکیت هفت‌نفرهٔ پیوست با پنج گروه و registry واقعی متفاوت است؛ ارائه‌ها اختلاف را صریح ثبت می‌کنند. Miri در کد manifest route ندارد.
- browser ثبت درس انجام نشد چون seed فعلی ترم/ارائهٔ مجاز ندارد؛ بازه برای تست دست‌کاری نشد.

## Git و handoff

Branch اختصاصی: `codex/full-system-audit`؛ base: `dbe34c558df41517fe262a13e4af90eb75d2937e`. checkpointهای شاخه پیش از این گزارش:

- `05b98eb900aa8214cc494a86991107e65428f237` — audit checkpoint
- `db6dae31652865f6789a9f19073552563e11e679` — API/screen matrix
- `228fb833be06e1764300c40ab46bd6d09e7caa59` — PDF mapping/screens
- `8e796fe011053acc3417abf8cd0e85feb34e0593` — رفع دو defect و regression tests

این گزارش در checkpoint مستندات انتهایی همین branch نگهداری می‌شود؛ `git log -1` آن را نشان می‌دهد. پس از commit، `git status --short --branch` بررسی شد و working tree تمیز بود. Push، merge و PR انجام نشده‌اند.

## آمادگی ارائه

**Partial.** می‌توان login، dashboard، تغییر term، خواندن داده، منع دسترسی بین پروفایل‌ها، نمایش مالی بدون gateway، و تست‌های backend را ارائه کرد. ثبت browser write باید فقط با test fixture معتبر اجرا شود. صفحات/عملیات ناقص و محدودیت‌های provider باید در ارائه به استاد آشکارا گفته شوند.
