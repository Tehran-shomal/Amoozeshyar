# برنامهٔ اجرای مالکیت هفت‌گانه و اتصال کامل صفحه‌ها

> این برنامه، تقسیم‌بندی تیمی پنج‌مالک قبلی را کنار می‌گذارد و اجرای صفحه‌ها را طبق هفت مالک جدید در شاخهٔ ایزوله ثبت می‌کند. دسته‌بندی کاربردی sidebar مستقل می‌ماند. فاز تست رسمی بنا به درخواست کاربر جداست.

> علامت `[x]` در این برنامه فقط به معنی اعمال/ثبت static تغییر است؛ pass بودن runtime یا تست را ثابت نمی‌کند. تأیید اجرایی در فاز بعد ثبت خواهد شد.

**هدف:** همهٔ routeهای پرتال به گروه جدید وصل شوند، API و عملیات واقعی هر صفحه روشن و کامل شود، و اسناد صفحه/گروه برای ارائه آماده باشند.

**طراحی:** Django monolith، API هم‌مبدأ session/CSRF، selector/form موجود و مالکیت دادهٔ دانشجو حفظ می‌شود. هفت manifest تیمی در `apps/core/frontend/<owner>/pages.py` تجمیع می‌شوند؛ `NAV_GROUPS` مستقل از مالکیت تیمی است و گروه‌ها/ترتیبش باید با صفحات منوی PDF (۱۳/۴/۵/۵/۳) تطبیق داشته باشد.

**مرجع:** `docs/superpowers/specs/2076-05-07-seven-team-full-pages-design.md` و بخش مالکیت جدید در پیوست MASTER.

## محدودیت‌های سراسری

- فقط روی `codex/full-system-audit` کار کن؛ main را تغییر نده، push/merge نکن، history را بازنویسی نکن.
- source checkout و DB اصلی را دست‌نخورده بگذار.
- PDF در clone نیست؛ تطبیق بصری مستند اما تأییدنشده می‌ماند.
- به درخواست کاربر، تست‌ها و QA مرورگر در فاز بعد اجرا می‌شوند. پیش از آن ادعای passing/completed ممنوع است.
- endpoint/provider بیرونی جعل نشود و دادهٔ seed جدید برای پرکردن صفحه ساخته نشود.

## کار ۱: نگاشت routeها و جایگزینی گروه‌بندی قدیمی

**فایل‌ها:** `apps/core/frontend/registry.py`, `metadata.py`, هفت پوشهٔ مالک، routeهای پنهان، template/staticهای گروهی.

- [x] ثبت هفت مالک جدید (Mobina, Shaghayegh, Parsa, Omid, Niousha, Shahsvand, Miri) در manifest فعال.
- [x] جابه‌جایی routeها طبق spec؛ hidden `selected-courses` متعلق به Shaghayegh و `evaluation-form` متعلق به Miri.
- [x] انتقال فرم/selector/template/staticهای پوشه‌های ترکیبی قدیمی؛ کد tracked فعال آن ماژول‌ها حذف شد.
- [x] حفظ URLهای کاربر؛ مالکیت تیمی از منوی محصول مستقل ماند. گروه‌ها و ترتیب `NAV_GROUPS` پس از مقایسهٔ برش‌های واقعی PDF به ساختار ۱۳/۴/۵/۵/۳ تغییر کرد.
- [x] نگه‌داشتن validation startup برای duplicate/unassigned/stray slug؛ اجرای آن تا فاز تست موکول است.

## کار ۲: مرور API و UI، صفحه‌به‌صفحه

**فایل‌ها:** selectorها/formها/templateها/staticها در هفت ماژول، `apps/core/frontend/api.py`, `docs/API_CONTRACTS.md`, `docs/SCREEN_API_MATRIX.md`, `docs/screens/`.

- [x] برای login، dashboard، term picker و هر ۳۲ route قابل منو/پنهان، روش خواندن و endpoint در matrix ثبت شد.
- [x] برای writeهای پشتیبانی‌شده endpoint/payload/validation/permission/status/error در قرارداد API ثبت شد؛ نمونه‌های request/response اضافه شد.
- [x] owner/profile scope فرم‌ها و read-only/unavailableهای فاقد workflow معتبر در selector/form و اسناد اعمال شد؛ اصلاح نمره و lookup کارآموزی نیز انجام شد.
- [ ] مرور نهایی runtime حالت‌های loading/empty/error/validation/success و UX همهٔ screenها در فاز QA؛ برای راهنما یک regression test نوشته شده اما هنوز اجرا نشده.
- [x] ثبت‌نام/حذف، فرم‌های درخواست و عملیات موجود به endpoint معتبر موجود متصل‌اند؛ موارد بی‌workflow به‌جای success ساختگی غیرفعال ماندند.
- [x] صفحه‌های مالی و صدور رسمی بدون provider واقعی mutation موفق نشان نمی‌دهند.
- [x] وضعیت Implemented/Partial/Unavailable/Unknown در matrix و screen docs ثبت شد؛ هیچ موردی به‌دلیل صرف انتقال مالک complete نام‌گذاری نشد.

## کار ۳: مالکیت داده و یکپارچگی backend

**فایل‌ها:** views/services/forms/selectors در دامنه‌های موجود، docs/SSOT/DECISIONS/BUSINESS_RULES.

- [x] scope پروفایل/ترم در API عمومی، enrollment و selectorها static بررسی و قرارداد آن ثبت شد.
- [ ] تمام حالت‌های malformed/lookup تکراری/submit مجدد با تست‌های فاز بعد بازبینی شوند؛ duplicate policyهای بدون منبع هنوز نامشخص‌اند.
- [x] migration یا تغییر دیتابیس اصلی اجرا نشد؛ مدل‌ها/transactionهای موجود حفظ شدند.
- [x] ruleهای بدون منبع Unknown و providerهای غایب در BUSINESS_RULES/NEXT_STEPS مستند شدند.

## کار ۴: مستندات گروه و route

**فایل‌ها:** ایجاد `docs/TEAM_OWNERSHIP.md`; بازنویسی هفت ارائهٔ عضو و `MASTER_PRESENTATION.md`; اصلاح ماتریس و تمام `docs/screens/*.md`; به‌روزرسانی progress/next/final.

- [x] هر هفت سند عضو نقش، صفحه، API، فایل، داده/مجوز، جریان، نمونهٔ request/response، محدودیت و مسیر ارائه را دارد.
- [x] URLهای مستقیم صفحه‌ها و ورود/داشبورد در ماتریس و ارائه درج شدند.
- [x] mapping شماره‌های ۹۶ صفحه و نبود فایل منبع/تطبیق تصویری تأییدنشده گزارش شده است.
- [x] لینک‌های Markdown زیر `docs/` و نام گروه‌ها با registry جدید بازبینی static شدند؛ لینک نسبی شکسته پیدا نشد.

## کار ۵: handoff و فاز تست جداگانه

- [x] اجرای تست‌ها به فاز بعد منتقل است و این فاز فقط وضعیت اجرا نشده را ثبت می‌کند.
- [x] `PROGRESS.md` شامل تغییرهای جاری، موارد ناتمام، اجرا نشدن تست و مسیر ادامه است.
- [x] گزارش نهایی تکمیل کلی را ادعا نمی‌کند؛ شرط تأیید screenها و آزمون‌های بعدی را ثبت می‌کند.

## معیار بازبینی داخلی برنامه

- ۷ مالک مطابق spec و تمام routeها دقیقاً یک مالک داشته باشند.
- routeهای عمومی user-facing و endpointهای API موجود حفظ شوند.
- جایگزینی گروه فقط ownership را عوض کند، نه منوی کاربردی یا مدل/داده را.
- هر اقدام خارجی یا rule نامعلوم صادقانه از قابلیت واقعی جدا شود.
