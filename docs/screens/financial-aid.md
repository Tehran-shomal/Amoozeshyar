# درخواست تسهیلات

- مالک/route: Parsa؛ `/portal/financial-aid/`; `parsa/finance.html`; `ScholarshipForm`.
- مرجع: PDF صفحهٔ ۶۵.
- هدف/کنترل: ثبت نوع تسهیلات و دلیل، نمایش درخواست‌های همان student با status.
- داده/API: ScholarshipApplication, Student, Constant؛ GET/POST API صفحه.
- اعتبارسنجی/مجوز: applicant و pending status سروری؛ فقط `scholarship_type`, `scholarship_reason` در مدل فرم؛ lookup/status باید موجود باشد.
- خطا/محدودیت: مبلغ/حساب/برنامهٔ قسط/پیوست در مدل/فرم نیست؛ تأیید تسهیلات را تضمین نمی‌کند.
- navigation: پرداخت‌ها؛ review API نیاز به role scholarship_officer/admin در implementation دارد (نیازمندی محصولی جداگانه تأیید نشده).
- آزمون/وابستگی: `apps/core/test_frontend.py`, `apps/core/requests/test_services.py`; ScholarshipForm/selector.
- وضعیت: submission و پیگیری DB-backed؛ workflow کامل و PDF-only fields باز؛ screenshot تازه باز.
