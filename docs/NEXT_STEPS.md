# گام‌های بعدی و محدودیت‌های باقی‌مانده

این شاخه ممیزی، قراردادها، ۹۶ صفحهٔ PDF و مستندات ارائه را ثبت کرده و defectهای بازتولیدشده را رفع می‌کند؛ سامانه هنوز بازسازی ۱۰۰٪ همهٔ گردش‌کارهای PDF نیست. موارد زیر با شاهد یا منبع مشخص بسته شوند:

1. **منبع رفتار:** فایل `نیازمندی_های_آموزشیار.md` در checkout حاضر نیست. پیش از تعریف statusها، actorها، مهلت‌ها و transitions درخواست، منبع رسمی دانشگاه/مالک محصول به SDD اضافه شود.
2. **تطبیق مسئولیت تیم:** پیوست هفت مسئولیت را تعریف می‌کند، اما registry پنج گروه دارد؛ Miri مالک route نیست، Niousha/Pouya مشترک‌اند، و چند صفحهٔ PDF بین اعضا متفاوت map شده‌اند. پیش از جابه‌جایی ownerها، mapping تیمی تأیید شود.
3. **APIهای دامنه‌ای:** ۱۴ namespace مستقل خالی‌اند؛ API عمومی صفحه جای endpointهای staff برای حضور، نمره، مشاوره، کلاس، شهریه، ticket، خدمات دانشجویی، پایان‌نامه، بورسیه، افراد، گزارش، آزمون آنلاین، کارآموزی و اعلان نیست. برای هرکدام actor، permission، schema و lifecycle معتبر لازم است.
4. **Providerهای بیرونی:** درگاه پرداخت، ارسال ایمیل/SMS، task queue، صدور رسمی مدرک/کارت و سرویس دانشگاهی پیکربندی نشده‌اند. تا ارائهٔ قرارداد/credential از provider، عملیات موفق بیرونی نمایش داده نشود.
5. **شکاف صفحه و state:** تقویم event-based، Q&A راهنما، پاسخ/lifecycle کامل Ticket، result screens، برخی modal/حالت‌های PDF و جمع‌بندی صفحه انتخاب واحد هنوز پیاده نیستند؛ منبع schema/محتوا برای هر مورد لازم است.
6. **ثبت‌نام در مرورگر:** API و service ثبت/حذف در suite تست می‌شوند؛ seed محلی یک term فعال با registration window بسته و term دیگر بدون offering دارد. browser write test را در CI با fixture/clock کنترل‌شدهٔ تست اجرا کن، نه با تغییر seed یا دادهٔ اصلی.
7. **زمان seed:** ۲۰ هشدار datetime naive در `Term`, `Payment`, `CounselingAppointment`, و `OnlineClass` با timezone-aware fixture بازبینی شوند؛ تبدیل زمان بدون تعیین timezone مرجع انجام نشود.
8. **توسعهٔ browser QA:** capture فعلی هفت viewport و چهار مقایسهٔ نماینده دارد، نه همهٔ ۳۲ route/state. E2E پایدار برای فرم‌های هر workflow و keyboard/focus/modal به زیرساخت موجود پروژه اضافه شود، پس از فراهم‌شدن runner مجاز.
9. **محیط dependency:** نصب از PyPI به‌دلیل TLS/ساعت سیستم در تلاش قبلی ممکن نشد؛ اگر dependency جدید واقعاً لازم شد، clock/certificate محیط تعمیر شود، نه اینکه TLS verification دور زده شود.
10. **رگرسیون/هندآف:** قبل از هر ادعای تکمیل، تست‌های Python/Node، Django check، migration check، markdown link/page coverage، `git diff --check` و وضعیت branch دوباره بررسی شوند. کار روی branch `codex/full-system-audit` بماند؛ push/merge/PR در scope نیست.

## شواهد جاری

- آزمون کامل آخر: ۱۰۱ Python + ۱۴ Node پاس؛ جزئیات در [TEST_REPORT.md](TEST_REPORT.md).
- PDF mapping: ۹۶/۹۶ شماره؛ screen/API matrix: ۳۲ route؛ فایل ارائه: ۷ عضو + master.
- محدودیت مالکیت، unknownها و وضعیت هر صفحه در [SCREEN_API_MATRIX.md](SCREEN_API_MATRIX.md)، [BUSINESS_RULES.md](BUSINESS_RULES.md) و [DECISIONS.md](DECISIONS.md).
