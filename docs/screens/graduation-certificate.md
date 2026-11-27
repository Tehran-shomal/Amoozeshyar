# درخواست مدرک دانش‌آموختگی

- مالک/route: Shahsvand؛ `/portal/graduation-certificate/`; `shahsvand/graduation_certificate.html`; GET فقط‌خواندنی.
- مرجع: PDF صفحهٔ ۷۳.
- هدف/کنترل: نمایش پرونده، واحد گذرانده، جمع واحد چارت فعال، آخرین audit، محدودیت کتابخانه/مدارک و مسیر چهارمرحله‌ای درخواست گواهی؛ پیوند به بررسی شرایط و چارت.
- داده/API: Student, Curriculum, GraduationAudit و Constant؛ GET API صفحه از context صفحهٔ بررسی فراغت استفاده می‌کند؛ lookup مناسب این نوع در seed/code فعلی وجود ندارد.
- اعتبارسنجی/مجوز: mutation ارائه نمی‌شود تا نوع اشتباه به‌عنوان گواهی فراغت ذخیره نشود.
- خطا/محدودیت: unit countهای پرونده و چارت جداگانه‌اند و eligibility از آن‌ها حدس زده نمی‌شود؛ تسویهٔ کتابخانه/فایل مدارک و provider رسمی صدور موجود نیست؛ صفحه موفقیت صدور ادعا نمی‌کند.
- navigation: `/portal/graduation/` و `/portal/curriculum/`؛ برگشت از shell.
- آزمون/وابستگی: `test_graduation_certificate_page_uses_real_checks_without_fake_issuance` افزوده شده؛ اجرا نشده؛ Shahsvand selector و service-request lookups.
- وضعیت: چیدمان صفحهٔ ۷۳ از facts/audit واقعی و وضعیت unavailable ساخته شد؛ POST/صدور عمداً غیرفعال است؛ capture جاری احرازشده نداریم.
