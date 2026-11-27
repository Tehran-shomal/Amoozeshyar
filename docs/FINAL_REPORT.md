# گزارش وضعیت جاری — بازسازی هفت‌گانهٔ آموزشیار

> اصلاح ۲۰۲۶-۱۱-۲۷: بندهای قدیمی این گزارش دربارهٔ migration و ذخیرهٔ پنج امتیاز ارزشیابی دیگر معتبر نیستند. schema تغییر نمی‌کند؛ فرم فعلی فقط `overall_rating`, `teaching_quality`, `behavior` را ذخیره می‌کند. هم‌ترازی پنج معیار PDF همچنان gap مستند است.

تاریخ: ۲۰۷۶-۰۵-۰۸ · branch: `codex/full-system-audit` · وضعیت: **در حال انجام؛ suite رسمی عمداً برای فاز بعد محفوظ است**

## خلاصهٔ قابل اتکا

تقسیم مالکیت پنج‌گانهٔ قبلی از رجیستری فعال کنار گذاشته شد و هفت مالک مطابق MASTER در کد و اسناد ایجاد شدند. routeهای مرورگر حفظ شده‌اند؛ فرم‌ها، selectorها و قالب‌های گروه‌های ترکیبی به پوشه‌های مالک جدید منتقل/تفکیک شدند. دسته‌بندی کاربردی sidebar نیز پس از دیدن PDF صفحات ۴–۸ به پنج گروه ۱۳/۴/۵/۵/۳ تغییر کرد؛ این گروه‌ها با مالکیت فنی یکی نیستند. درخواست‌های certificate با lookup موجود هماهنگ شدند.

در بررسی static فرم‌ها، enrollment قابل اعتراض به نمرهٔ واقعی، نوع کارآموزی به Constant فعال و انتخاب ارزشیابی به enrollmentهای بدون survey محدود شد. صفحهٔ راهنما اکنون چهار کارت پرسش‌وپاسخ و CTA پشتیبانی مطابق مرجع PDF دارد. نمونه‌های request/response به قرارداد مرکزی و هفت سند ارائه اضافه شدند؛ این اصلاح‌ها هنوز آزمون runtime ندارند.

**این گزارش تکمیل همهٔ قابلیت‌ها یا ۹۶ صفحه را اعلام نمی‌کند.** صفحات ۱–۱۴ به‌ترتیب با مرجع و UI مرور شده‌اند؛ source صفحات ۱۵–۲۹ توسعه/بازبینی شده اما capture جاری احرازشده نداریم و توالی بصری روی صفحهٔ ۱۹ متوقف است. صفحهٔ ۱۵ دادهٔ تقویم را از Term/امتحان/Attendance می‌گیرد ولی مناسبت عمومی/مهلت شهریه منبع ندارد؛ صفحهٔ ۱۶ Communication اعلان را owner-scope می‌کند؛ صفحهٔ ۱۷ پنج rating مستقل دارد و migration آن اجرا نشده؛ صفحهٔ ۱۸ فقط lookupهای واقعی اعلان را فیلتر می‌کند؛ صفحهٔ ۱۹ تنظیمات را به Person جاری وصل می‌کند ولی موبایل/provider ندارد. صفحات ۲۰–۲۳ به دادهٔ پرونده متصل‌اند؛ گروه چارت از requirement type می‌آید چون مدل گروه مستقل ندارد. صفحات ۲۴–۲۶ فقط فیلدهای واقعی Internship/TransferRequest/GraduationAudit را می‌پذیرند و gapهای schema را نمایش می‌دهند. صفحهٔ ۲۷ گیرنده را به استاد فعال همان نیمسال محدود می‌کند ولی thread/delivery بیرونی ندارد. صفحهٔ ۲۸ چهار FAQ مرجع دارد؛ API حداقل واحد حذف اضطراری را کنترل نمی‌کند و status علت انسداد را گزارش نمی‌دهد. صفحهٔ ۲۹ تیکت‌های root حساب و reply آخر واقعی را نمایش می‌دهد؛ مدل/API پیوست و پاسخ‌دهی از پورتال ندارند، و status اولیه از lookup فعال `open` می‌آید. Regressionهای صفحات ۲۰–۲۹ نوشته شده ولی طبق درخواست اجرا نشده‌اند؛ suite خودکار و mutation برای فاز بعد است. صفحه‌های ۱۰–۱۳ state پنج‌درسی ندارند، حد قانونی غیبت صفحهٔ ۱۴ نامعلوم است، و درگاه/صدور رسمی و workflowهای فاقد lookup همچنان unavailable هستند.

## وضعیت تحویل

صفحهٔ ۳۰ نیز در این ادامه به خطای واقعی `tuition_debt` وصل شد: modal مبلغ بدهی و حداکثر واحد را از پرونده می‌خواند، اما حداقل واحد از قواعد فعلی قابل استخراج نیست و درگاه پرداخت فعال نیست. regression نوشته شده ولی اجرا نشده است.

صفحات ۳۱–۳۲ به جریان ارزشیابی موجود متصل‌اند؛ Enrollment باید متعلق به همین پرونده/نیمسال و فعال باشد، ثبت تکراری رد می‌شود و پاسخ پس از ثبت قفل است. schema فقط `overall_rating`, `teaching_quality` و `behavior` را دارد؛ پنج معیار PDF و کد گروه کلاس در schema نیستند و به‌عنوان دادهٔ ذخیره‌شده ادعا نمی‌شوند.

صفحات ۳۳–۳۷ نیز از همین API/form و selector داده‌محور استفاده می‌کنند: صفحات فرم برای Enrollmentهای مختلف‌اند و صفحات فهرست وضعیت survey واقعی هر Enrollment فعال را نشان می‌دهند. regression فهرست برای رکورد کامل/در انتظار و منع مشاهدهٔ enrollment غیرمالک اضافه شد، اما اجرا نشده است.

| بخش | وضعیت واقعی |
|---|---|
| branch و دیتابیس | تغییرها فقط در clone ایزوله و `codex/full-system-audit`؛ DB اصلی untouched |
| تقسیم‌بندی جدید | در manifest فعال هفت گروه ثبت شده؛ بررسی startup/test در مرحلهٔ بعد |
| routeهای صفحه | slugهای موجود حفظ شده و در registry به مالک جدید map شده‌اند؛ بازبینی همهٔ viewها pending |
| API | API عمومی page و endpointهای موجود accounts/scheduling/enrollment فعال در معماری هستند؛ API اختصاصی همهٔ ۱۴ namespace خالی ساخته نشده |
| فرم graduation/certificate | از نوع lookup نامرتبط استفاده نمی‌کند؛ graduation و graduation-certificate write-disabled تا type/workflow معتبر فراهم شود |
| مستندات | TEAM_OWNERSHIP، API matrix، ۷ سند عضو، master و screen docs بازنویسی شده‌اند؛ بررسی static لینک‌های نسبی `docs/` بدون مورد شکسته |
| تست و browser QA | NOT RUN پس از این تغییر؛ برای فاز بعد |
| PDF visual verification | در جریان: ۹۶ شماره در mapping ثبت‌اند؛ تطبیق زندهٔ صفحات ۱–۱۴ گزارش شده، اما capture مجاز صفحهٔ ۱۹ در دسترس نیست و توالی تصویری از آن عبور نکرده. سورس/API صفحات ۲۰–۲۹ جداگانه بررسی/اصلاح شده‌اند. مرجع PNG همهٔ صفحات ۱–۹۶ در `docs/screens/` حاضر است؛ منبع: `C:\Users\repair\Downloads\Amoozeshyar.pdf`. |

## تقسیم‌بندی فعال

| گروه | دامنه |
|---|---|
| Mobina | login/dashboard، shell، settings، student card |
| Shaghayegh | enrollment/course selection/add-drop/status |
| Parsa | مالی |
| Omid | سوابق، transcript، curriculum، grade appeal |
| Niousha | schedule/calendar/attendance/exam card و Frontend Lead |
| Shahsvand | internship و درخواست‌های دانشجویی |
| Miri | faculty communications و خدمات عمومی، Shared Lead |

جزئیات تک‌تک URLها و APIها: [TEAM_OWNERSHIP.md](TEAM_OWNERSHIP.md). مسیرهای مستندات: `docs/screens/`, `docs/presentation/`, `docs/API_CONTRACTS.md`, `docs/SCREEN_API_MATRIX.md`.

## Git و ایمنی

- مسیر: `C:\Users\repair\Downloads\Amoozeshyar-audit-clone-3`
- branch: `codex/full-system-audit`; مبنای پیش از این تغییر: `66afe3eab2c9d1ee90ac9c0fb5639f5688973f752`
- تغییرهای این نوبت هنوز commit نشده‌اند؛ push، merge، PR و تغییر main انجام نشده.
- checkout و دیتابیس اصلی بیرون از clone دست‌نخورده‌اند؛ migration یا mutation داده اجرا نشده.

## موارد لازم قبل از اعلام تکمیل

۱) ادامهٔ بازبینی ترتیبی از صفحهٔ ۱۵ تا ۹۶ و cross-check route/API؛ ۲) اجرای suite و browser/viewport QA در فاز مورد توافق؛ ۳) ثبت نتیجهٔ واقعی در [PROGRESS.md](PROGRESS.md), [TEST_REPORT.md](TEST_REPORT.md), [NEXT_STEPS.md](NEXT_STEPS.md). معیار complete برای هر صفحه UI + API + persistence + permission + validation/error + شواهد تست است.
