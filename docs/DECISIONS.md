# تصمیم‌ها و فرض‌های اجرایی ممیزی

این تصمیم‌ها scope همین شاخهٔ ممیزی را محدود می‌کنند؛ تغییر معماری/مدل بدون منبع نیازمندی معتبر به این مرحله افزوده نمی‌شود.

| شناسه | تصمیم | دلیل و پیامد |
|---|---|---|
| D-01 | Django monolith و API هم‌مبدأ session/CSRF حفظ شود؛ DRF یا dependency جدید اضافه نشود. | API موجود، templateها، forms و browser client را به هم متصل می‌کند؛ افزودن framework در این درخواست ضرورت اثبات‌شده ندارد. |
| D-02 | مدل‌ها در `apps/core/models.py` و admin در `apps/core/admin.py` باقی بمانند. | قرارداد معماری پروژه و migrationهای موجود؛ از پراکندگی schema جلوگیری می‌کند. |
| D-03 | دادهٔ مرورگر فقط از selectorهای scoped به Person/Student جاری خوانده شود؛ شناسهٔ ارسالی مجوز دسترسی تلقی نشود. | حفظ جداسازی پرونده‌ها و جلوگیری از IDOR؛ تغییر این مرز مستلزم تست امنیتی است. |
| D-04 | پرداخت، صدور رسمی کارت/مدرک و provider بیرونی شبیه‌سازی نشوند. | هیچ credential/provider/قرارداد اتصال در checkout وجود ندارد؛ UI باید عدم دسترسی واقعی را نشان دهد. |
| D-05 | مدل/قواعد business جدید از ۱۵۲ شناسهٔ SDD یا تصویر PDF استنباط نشود. | منبع متنی SDD شامل شرح behavior و authorization نیست؛ ثبت ابهام امن‌تر از جعل گردش کار است. |
| D-06 | صفحه‌هایی که چند PDF state دارند یک route داده‌محور می‌مانند، مگر آن‌که route/behavior مستقل در کد وجود داشته باشد. | جلوگیری از routeهای نمایشیِ بی‌پشتوانه؛ PDF-only modal/result به‌صورت state/reference ثبت می‌شود. |
| D-07 | `selected-courses` و `evaluation-form` صفحهٔ واقعی‌اند اما در `HIDDEN_PAGE_SLUGS` از منوی اصلی پنهان‌اند. | navigation مالکیتی صریحاً همین دو slug را به‌عنوان مسیرهای از صفحهٔ والد معرفی کرده است. |
| D-08 | baseline تست و هر migration/seed فقط در clone ایزوله و SQLite آزمون اجرا شود. | checkout اصلی و دیتابیس کاربر خارج از scope تغییر است؛ DB تستی خودکار پس از suite پاک می‌شود. |
| D-09 | Git 2.56.0.windows.4 برای commit/ref نوشتن crash دارد؛ ref فقط با old-OID مورد انتظار در clone ممیزی تغییر کند. | commit checkpoint از Git plumbing (`hash-object` + `update-ref` با شرط old HEAD) ساخته و با log/status بررسی شد؛ source config/ref تغییر نمی‌کند. اگر این روش هم نامعتبر شود، تغییر ref متوقف می‌شود. |
| D-10 | screenshot مرجع و capture جاری جدا ثبت شوند؛ captureهای جاری فقط شاهد viewportهای نماینده‌اند، نه تطبیق ۹۶ صفحه. | هفت viewport در Edge capture و صفحه‌های PDF ۲، ۹، ۵۳، ۶۳ با نمونهٔ جاری مرور شدند؛ جزئیات در `TEST_REPORT.md`. |
| D-11 | warningهای datetime فعلی ثبت شوند و بدون منبع timezone fixtureها تغییر نکنند. | تغییر زمان seed ممکن است معنی داده را عوض کند؛ ممیزی فقط تعداد/فیلدها را گزارش می‌کند. |
| D-12 | تا زمان دستیابی به رفتار مستند برای requirementهای ناشناخته، وضعیت به‌صورت gap/unknown مستند شود و screen/API «کامل» برچسب نخورد. | معیار تکمیل شامل UI، navigation، API، persistence، validation، permission، error، test و documentation است؛ ظاهر به‌تنهایی کافی نیست. |
| D-13 | `finance.html` قطعهٔ قابل include است و نباید `portal_base.html` را دوباره extend کند. | render دوبارهٔ shell در هر سه route مالی با regression test بازتولید شد؛ حذف inheritance از fragment باعث یک shell می‌شود. |
| D-14 | border search table فقط روی wrapper باشد؛ input داخلی در responsive rule قاب دوم نسازد. | screenshot attendance در 768px و computed style قاب دوگانه را نشان داد؛ Node regression test RED/GREEN و capture پس از fix تأیید کرد. |

## تصمیم‌های نیازمند مالک محصول

پیش از افزودن مدل یا endpoint تازه باید منبع رسمی برای نقش‌های staff، lifecycle درخواست، شماره/اعتبار کارت، خروجی مدرک، نتیجهٔ مستقل عملیات، APIهای attendance/notification/internship، قواعد شهریه و درگاه پرداخت ثبت شود. تا آن زمان موارد در [BUSINESS_RULES.md](BUSINESS_RULES.md) و [NEXT_STEPS.md](NEXT_STEPS.md) باز می‌مانند.
