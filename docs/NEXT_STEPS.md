# کارهای بعدی

این فهرست بر اساس شاهدهای ممیزی مرتب شده است؛ موردی که به رفتار/مجوز نامعلوم وابسته است، تا دریافت منبع رفتاری به‌عنوان کار تأییدنشده می‌ماند.

1. تکمیل `API_CONTRACTS.md`, `SCREEN_API_MATRIX.md`, `BUSINESS_RULES.md` و `DECISIONS.md` از روی view/service/form واقعی.
2. تولید `PDF_PAGE_MAPPING.md` با پوشش صریح ۹۶ صفحه؛ تفکیک route واقعی از screenshot state، modal، menu crop و operation-result.
3. ساخت یک مستند فنی برای هر screen واقعی در `docs/screens/`؛ ثبت URL، owner، داده، API، validation، permission، error و تست، و علامت‌زدن موارد ناموجود.
4. بازاجرای server-rendered صفحات و عکس‌برداری در هفت viewport درخواستی؛ مقایسهٔ login، dashboard، table/form، modal و صفحات مالی با reference images. هیچ ادعای تطبیق کامل پیش از این مرحله ثبت نشود.
5. بازبینی و رفع warningهای naive datetime در seed/test fixtures؛ تاریخ‌ها را بدون منبع timezone حدس نزن.
6. اگر رفتار معتبر در PDF یا منبع requirement مشخص شد، برای defect یک تست قرمز بنویس، سپس کمینهٔ fix را انجام بده و Python/JS tests را تکرار کن.
7. برای APIهای دامنه‌ای خالی، ابتدا نقش مصرف‌کننده، payload، permission، lifecycle و schema را مستند کن. مدل/endpoint جدید را فقط وقتی اضافه کن که رفتار منبع کافی دارد؛ مدل‌های غایب شامل loan/installment، meal/dorm و audit/error log هستند.
8. هرگز درگاه پرداخت، صدور رسمی کارت/مدرک، یا نتیجهٔ موفق عملیات بیرونی را شبیه‌سازی نکن؛ تا provider واقعی موجود نشده، محدودیت را در UI و API صریح نگه دار.
9. مستندهای `docs/presentation/01_Mobina.md` تا `07_Miri.md` و `MASTER_PRESENTATION.md` را از مالکیت واقعی کد و آزمون‌های پاس‌شده بساز.
10. پس از تغییرهای نهایی full Python suite، Django check، migration check، Node tests، `git diff --check` و بررسی stage/branch را انجام بده؛ هیچ push/merge/PR انجام نشود.

## اطلاعاتی که تکمیل را محدود می‌کند

- `نیازمندی_های_آموزشیار.md` در مخزن موجود نیست؛ SDD فقط شناسه‌ها و گروه‌بندی را دارد.
- APIهای مستقل ۱۴ اپ دامنه فعلاً خالی‌اند؛ API page موجود جایگزین قرارداد REST برای نقش staff نیست.
- درگاه پرداخت و سرویس‌های بیرونی پیکربندی نشده‌اند.
- وضعیت branch فعلی به‌تنهایی اثبات‌کنندهٔ صحت screenshotهای قدیمی نیست؛ screenshotها باید دوباره از همین clone گرفته شوند.
