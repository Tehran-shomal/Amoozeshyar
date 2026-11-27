# درخواست تسهیلات

- مالک/route: Parsa؛ `/portal/financial-aid/`; `parsa/finance.html`; `ScholarshipForm`.
- مرجع: PDF صفحهٔ ۶۵ و نتیجهٔ ثبت در صفحهٔ ۴۳.
- هدف/کنترل: ثبت نوع تسهیلات و دلیلِ موجود در مدل، نمایش درخواست‌های همان student با status؛ هشدار روشن می‌کند مبلغ/شبا/پیوست PDF پشتیبانی نمی‌شوند.
- داده/API: ScholarshipApplication, Student, Constant؛ GET/POST API صفحه. redirect موفق `request_id` رکورد را دارد و GET نتیجه فقط درخواست متعلق به پروندهٔ جاری را نمایش می‌دهد.
- اعتبارسنجی/مجوز: applicant و pending status سروری؛ فقط `scholarship_type`, `scholarship_reason` در مدل فرم؛ lookup/status باید موجود باشد. owner از حساب جاری است و فیلد قابل ارسال نیست.
- خطا/محدودیت: مبلغ/حساب/برنامهٔ قسط/پیوست در مدل/فرم نیست؛ نتیجهٔ صفحهٔ ۴۳ صرفاً ثبت محلی و status جاری را گزارش می‌کند و تخصیص/تأیید نهایی را تضمین نمی‌کند.
- navigation: پرداخت‌ها؛ review API نیاز به role scholarship_officer/admin در implementation دارد (نیازمندی محصولی جداگانه تأیید نشده).
- آزمون/وابستگی: `test_portal_page_api_submits_valid_existing_form` در `apps/core/test_frontend.py` نتیجه و scope را هم بررسی می‌کند؛ نوشته شده و اجرا نشده؛ `apps/core/requests/test_services.py`; ScholarshipForm/selector.
- وضعیت: PDF صفحهٔ ۶۵ با فرم موجود تطبیق شد؛ ثبت و پیگیری DB-backed است اما فقط محلی، و مبلغ/شبا/مدرک به دروغ دریافت نمی‌شود. assertionهای محدودیت نتیجه افزوده شد ولی اجرا نشده؛ capture جاری احرازشده نداریم.
