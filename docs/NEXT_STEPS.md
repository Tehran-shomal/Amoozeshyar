# کارهای بعدی

این فهرست بر اساس شاهدهای ممیزی مرتب شده است؛ موردی که به رفتار/مجوز نامعلوم وابسته است، تا دریافت منبع رفتاری به‌عنوان کار تأییدنشده می‌ماند.

1. کنترل نهایی و commit قراردادهای API، ماتریس صفحه، business rules و decisions.
2. کنترل route coverage و PDF page numbers؛ commit mapping canonical و یک screen doc برای هر route/component/state واقعی.
3. اجرای browser visual smoke از همین clone و capture در هفت viewport؛ تا پایان آن ادعای تطبیق responsive/visual نکن.
4. برای هر defect بازتولیدشده، تست قرمز بنویس و سپس کمینهٔ fix؛ پس از آن Python/JS tests را تکرار کن.
5. warningهای naive datetime را با منبع timezone بازبینی کن؛ زمان fixtureها را بدون منبع معتبر تبدیل نکن.
6. APIهای دامنه‌ای خالی را تا روشن‌شدن actor، payload، permission، lifecycle و schema پیاده نکن؛ مدل‌های غایب مانند loan/installment، meal/dorm و audit/error log باز هستند.
7. gateway، صدور رسمی کارت/مدرک یا نتیجهٔ موفق provider بیرونی را شبیه‌سازی نکن.
8. هفت مستند presentation و master را از مالکیت واقعی کد و خروجی تست بساز؛ Miri که در repo مالکیت feature ندارد باید صریحاً همین‌طور گزارش شود.
9. در پایان full Python suite، Django check، migration check، Node tests، `git diff --check` و بررسی stage/branch؛ بدون push/merge/PR.

## اطلاعاتی که تکمیل را محدود می‌کند

- `نیازمندی_های_آموزشیار.md` در مخزن موجود نیست؛ SDD فقط شناسه‌ها و گروه‌بندی را دارد.
- APIهای مستقل ۱۴ اپ دامنه فعلاً خالی‌اند؛ API page موجود جایگزین قرارداد REST برای نقش staff نیست.
- درگاه پرداخت و سرویس‌های بیرونی پیکربندی نشده‌اند.
- وضعیت branch فعلی به‌تنهایی اثبات‌کنندهٔ صحت screenshotهای قدیمی نیست؛ screenshotها باید دوباره از همین clone گرفته شوند.
