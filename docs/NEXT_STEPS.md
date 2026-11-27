# ادامهٔ کار — تکمیل واقعی صفحه‌ها و APIها

> وضعیت جدید ۲۰۲۶-۱۱-۲۷: یادداشت‌های checkpoint پایین‌تر ممکن است قبل از بازبینی اخیر باشند. فرم ارزشیابی فقط ستون‌های موجود `overall_rating`, `teaching_quality`, `behavior` را ذخیره می‌کند؛ migration پنج معیار PDF حذف شد تا schema تغییر نکند. همچنین serializer تاریخ، خطاهای فرم React و سازگاری پنجرهٔ حذف قدیمی اصلاح شده‌اند. Regressionها نوشته/به‌روز شده‌اند ولی بنا به درخواست، اجرا نشده‌اند.

این فهرست با تقسیم‌بندی هفت‌گانه جایگزین برنامهٔ مالکیت قبلی است. ترتیب کار: اول تمام پیاده‌سازی‌های قابل‌استناد؛ تست رسمی بعد از اتمام این مرحله، مطابق درخواست صاحب پروژه.

## وضعیت تطبیق ترتیبی PDF

یادداشت ادامهٔ تاریخی: سورس صفحه‌های ۲۰–۴۰ بررسی/اصلاح شده، اما آن بررسی جای capture/API مجاز صفحهٔ ۱۹ را نگرفت. این checkpoint پیش از بازبینی دوبارهٔ صفحهٔ ۹ ثبت شده است. صفحات ۲۳ تا ۲۹ قالب اختصاصی، صفحهٔ ۳۰ modal نتیجهٔ API، صفحات ۳۱–۳۳ فرم ارزشیابی، ۳۴–۳۷ حالت‌های فهرست داده‌محور، و صفحات ۳۸–۴۰ نتیجه‌های ثبت داخلی کارآموزی، درخواست مهمانی و پیام را دارند؛ regressionهای نوشته‌شده هنوز اجرا نشده‌اند.

وضعیت جاریِ افزوده: مرور مرجع و trace سورس/API تا صفحهٔ ۹۶ رسیده. صفحه‌های ۷۵–۷۸ فهرست emergency-drop، ۷۹–۸۸ مودال API-driven انتخاب ارائه، ۸۹–۹۲ حذف عادی و ۹۳–۹۶ حذف اضطراری‌اند. رگرسیون‌ها نوشته شده‌اند اما اجرا نشده‌اند. **توالی visual فعلی به صفحهٔ ۹ برگشته**: اصلاح عرض عنوان sidebar انجام شده اما capture موجود پیش از اصلاح است. سرور clone اکنون روی `http://127.0.0.1:8000/` فعال است؛ صفحهٔ ورود GET=200 و APIهای صفحهٔ ۹/ارائه برای ناشناس GET=401 می‌دهند. CDP در ۹۲۲۲ در دسترس نیست و credential seed با DB فعلی تطبیق ندارد؛ هیچ ورود اجباری، reset رمز یا تغییر DB انجام نمی‌شود. قدم بعد پس از ورود عادیِ مجاز، capture تازهٔ صفحهٔ ۹ و سپس ادامه از صفحهٔ ۱۰ است.

PDF اصلی در `C:\Users\repair\Downloads\Amoozeshyar.pdf` موجود است؛ مرجع‌های تصویری همهٔ صفحه‌های ۱ تا ۹۶ در `docs/screens/page-NN-reference.png` رندر و ذخیره‌اند. صفحات ۱ تا ۱۴ به‌ترتیب با مرجع و UI بررسی شده‌اند؛ captureهای موجود فعلاً قدیمی‌اند و صفحهٔ ۹ پس از اصلاح CSS به capture مجدد نیاز دارد. source صفحات ۱۵–۳۷ توسعه/بازبینی شده اما capture جاری/API مجاز آن‌ها pending است. صفحات ۱۵–۳۷ طبق جزئیات ثبت‌شده در `docs/PROGRESS.md` و `docs/PDF_PAGE_MAPPING.md` بررسی شده‌اند. صفحهٔ ۲۸ چهار FAQ و CTA پشتیبانی دارد؛ API حذف اضطراری حداقل واحد را کنترل نمی‌کند و وضعیت ثبت‌نام علت انسداد را اعلام نمی‌کند. صفحهٔ ۲۹ فرم/جدول پشتیبانی را به Ticket/reply واقعی وصل می‌کند؛ پیوست و پاسخ agent از portal API پشتیبانی نمی‌شود. صفحهٔ ۳۰ خطای بدهی ثبت‌نام را با دادهٔ پرونده در modal نشان می‌دهد؛ حداقل واحد رسمی تعریف نشده و درگاه پرداخت فعال نیست. صفحات ۳۱–۳۳ به فرم ارزشیابی پنج‌معیاری متصل‌اند؛ گروه کلاس در schema وجود ندارد و گزینهٔ ۴ پیش‌فرض نیست. صفحات ۳۴–۳۷ حالت‌های لیست را از surveyهای واقعی، نه stateهای ثابت، می‌سازند. فیلدهای PDF که در schema نیستند پنهان از ادعای ثبت می‌مانند. رویداد عمومی تقویم منبع ندارد؛ term clone سال میلادی ۲۰۷۶ دارد، نه ۱۴۰۵ PDF. صفحات ۱۰–۱۳ همچنان state پنج‌درسی مفقودند؛ حد قانونی غیبت صفحهٔ ۱۴ معلوم نیست. بررسی منبع ۲۰–۳۷ جای capture احرازشدهٔ جاری را نمی‌گیرد؛ توالی visual مطابق وضعیت تازه در صفحهٔ ۹ متوقف است.

## فاز جاری: API و صفحه‌ها

۱. از [ماتریس صفحه/API](SCREEN_API_MATRIX.md) هر slug را با registry، template، selector، form و `GET|POST /api/portal/pages/<slug>/` تطبیق بده؛ تمام ۳۲ route، login، dashboard، term picker و دو state پنهان را یکی‌یکی بررسی کن.
۲. برای هر فرم یا کنترل، payload سمت browser تا view/form/service/DB را trace کن؛ scope حساب/Student، CSRF، validation، خطا و refresh را ثبت کن.
۳. هر ناسازگاری واقعی را اصلاح کن. به‌خصوص lookupهای request؛ نوع‌هایی که در `seed.py` نیستند نباید با certificate یا نوع نزدیک جایگزین شوند.
۴. stateهای loading/empty/error/success و accessibility/RTL را در هر صفحه مرور کن. modal یا stateی که منبع PDF ندارد را اختراع نکن؛ آن را gap مستند کن. سورس/API تا PDF صفحهٔ ۹۶ ردیابی شده؛ مانع فعلی، capture جاری برای ادامهٔ تطبیق تصویری از صفحهٔ ۱۹ است.
۵. APIهای دامنه‌ای موجود را به صفحهٔ مناسب وصل نگه‌دار: accounts برای login، scheduling برای term/offerings، enrollment برای register/drop و requests/review برای نقش‌های staff. صفحه‌هایی که از page API داده می‌گیرند نیازمند API اختصاصی جعلی نیستند.

## محدودیت‌های واقعی که با کدنویسی حدس‌زدنی حل نمی‌شوند

- فایل PDF داخل clone نیست و از مسیر محلی بالا استفاده می‌شود؛ تطبیق تصویری کامل تا صفحهٔ ۱۴ انجام شده و source صفحات ۱۵–۳۷ بررسی شده است، ولی capture احرازشدهٔ جاری صفحهٔ ۱۹ در دسترس نیست. stateهای داده‌ای مفقود باید به‌عنوان gap بمانند؛ seed برای شبیه‌سازی PDF نساز.
- `نیازمندی_های_آموزشیار.md` در source نیست؛ ruleهای رسمی، actorها و lifecycleهای نامعلوم را از روی اسم صفحه نساز.
- ۱۴ feature namespace دامنه در `config/urls.py` URLConf خالی دارند. فقط وقتی قرارداد actor/schema/permission مشخص شد API جدید اضافه کن؛ API عمومی صفحه آن‌ها را به‌عنوان API کارمندی جا نزن.
- درگاه پرداخت، ارسال SMS/email، صدور رسمی مدرک/کارت و task queue provider ندارند؛ وضعیت unavailable بماند.
- seed موجود `employment_certificate` دارد اما type جدا برای graduation/graduation-certificate ندارد؛ تا دریافت lookup معتبر، write این دو صفحه خاموش است.

## فاز بعد: تست و QA (فعلاً اجرا نشده)

- Python/Django: تمام tests، `check` و `makemigrations --check --dry-run` روی clone/test DB؛ دیتابیس اصلی ممنوع.
- JavaScript: تمام Node tests، API binding و ثبت/حذف واقعی فقط روی test fixture.
- Browser: login/logout، همهٔ ۳۲ page API، formهای success/validation/error، CSRF، دیگر-profile 403، term picker و stateهای modal.
- Viewportها: 1920×1080، 1536×864، 1366×768، 1280×720، 1024×768، 768×1024 و 390×844؛ RTL، focus، overflow، sidebar و table.
- لینک‌های Markdown، پوشش ۹۶ شماره، coverage دقیق ۳۲ slug، `git diff --check` و working-tree safety را دوباره بررسی کن.
- نتیجه را در `docs/TEST_REPORT.md`, `PROGRESS.md` و `FINAL_REPORT.md` با عبارت دقیق PASS/FAIL/NOT RUN ثبت کن.

## تحویل مستندات و آدرس‌ها

- تقسیم هفت‌گانه و URL هر screen: `docs/TEAM_OWNERSHIP.md`
- API و مالکیت route: `docs/SCREEN_API_MATRIX.md`, `docs/API_CONTRACTS.md`
- جزئیات جداگانهٔ صفحه: `docs/screens/<slug>.md`
- ارائه‌های جداگانه: `docs/presentation/01_Mobina.md` تا `07_Miri.md`
- ارائهٔ کلی: `docs/presentation/MASTER_PRESENTATION.md`
- وضعیت کار: `docs/PROGRESS.md`; نتایج آزمون فعلی فقط بعد از اجرای فاز تست.
